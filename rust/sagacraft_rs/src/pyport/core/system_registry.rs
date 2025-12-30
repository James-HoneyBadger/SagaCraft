use serde_json::Value;
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SystemType {
    Progression,
    Gameplay,
    Social,
    Content,
    Infrastructure,
}

#[derive(Debug, Clone, PartialEq)]
pub struct SystemConfig {
    pub system_id: String,
    pub system_type: SystemType,
    pub enabled: bool,
    pub priority: i32,
    pub metadata: HashMap<String, Value>,
}

impl SystemConfig {
    pub fn new(system_id: impl Into<String>, system_type: SystemType) -> Self {
        Self {
            system_id: system_id.into(),
            system_type,
            enabled: true,
            priority: 0,
            metadata: HashMap::new(),
        }
    }
}

pub trait GameSystem: 'static {
    fn id(&self) -> &str;
    fn system_type(&self) -> SystemType;
    fn enabled(&self) -> bool;

    fn enable(&mut self);
    fn disable(&mut self);

    fn initialize(&mut self) -> Result<(), String>;
    fn validate(&self) -> bool;
}

type SystemCtor = Box<dyn Fn(SystemConfig) -> Box<dyn GameSystem>>;

pub struct SystemFactory {
    ctors: HashMap<String, SystemCtor>,
    systems: HashMap<String, Box<dyn GameSystem>>,
}

impl SystemFactory {
    pub fn new() -> Self {
        Self {
            ctors: HashMap::new(),
            systems: HashMap::new(),
        }
    }

    pub fn register(&mut self, system_id: impl Into<String>, ctor: SystemCtor) {
        self.ctors.insert(system_id.into(), ctor);
    }

    pub fn create(&mut self, system_id: &str, config: SystemConfig) -> Result<(), String> {
        let ctor = self
            .ctors
            .get(system_id)
            .ok_or_else(|| format!("system not registered: {system_id}"))?;
        let mut sys = ctor(config);
        sys.initialize()?;
        self.systems.insert(system_id.to_string(), sys);
        Ok(())
    }

    pub fn get(&self, system_id: &str) -> Option<&dyn GameSystem> {
        self.systems.get(system_id).map(|s| s.as_ref())
    }

    pub fn get_mut(&mut self, system_id: &str) -> Option<&mut (dyn GameSystem + '_)> {
        self.systems.get_mut(system_id).map(move |s| s.as_mut())
    }

    pub fn shutdown_all(&mut self) {
        self.systems.clear();
    }

    pub fn get_by_type(&self, system_type: SystemType) -> Vec<&dyn GameSystem> {
        self.systems
            .values()
            .filter_map(|s| {
                if s.system_type() == system_type {
                    Some(s.as_ref())
                } else {
                    None
                }
            })
            .collect()
    }

    pub fn get_all(&self) -> HashMap<String, &dyn GameSystem> {
        self.systems
            .iter()
            .map(|(k, v)| (k.clone(), v.as_ref()))
            .collect()
    }

    pub fn has_system(&self, system_id: &str) -> bool {
        self.systems.contains_key(system_id)
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct FeatureFlag {
    pub name: String,
    pub enabled: bool,
    pub metadata: HashMap<String, Value>,
}

pub struct SystemRegistry {
    pub factory: SystemFactory,
    pub feature_flags: HashMap<String, FeatureFlag>,
    pub system_configs: HashMap<String, SystemConfig>,
    pub system_dependencies: HashMap<String, Vec<String>>,
    initialized: bool,
}

impl SystemRegistry {
    pub fn new() -> Self {
        Self {
            factory: SystemFactory::new(),
            feature_flags: HashMap::new(),
            system_configs: HashMap::new(),
            system_dependencies: HashMap::new(),
            initialized: false,
        }
    }

    pub fn define_system(
        &mut self,
        system_id: impl Into<String>,
        system_type: SystemType,
        enabled: bool,
        priority: i32,
        dependencies: Vec<String>,
        metadata: HashMap<String, Value>,
    ) {
        let system_id = system_id.into();
        let mut config = SystemConfig::new(system_id.clone(), system_type);
        config.enabled = enabled;
        config.priority = priority;
        config.metadata = metadata;

        self.system_configs.insert(system_id.clone(), config);
        self.system_dependencies
            .insert(system_id.clone(), dependencies);
        self.feature_flags.insert(
            system_id.clone(),
            FeatureFlag {
                name: system_id.clone(),
                enabled,
                metadata: HashMap::new(),
            },
        );
    }

    pub fn enable_system(&mut self, system_id: &str) {
        if let Some(flag) = self.feature_flags.get_mut(system_id) {
            flag.enabled = true;
        }
        if let Some(sys) = self.factory.get_mut(system_id) {
            sys.enable();
        }
    }

    pub fn disable_system(&mut self, system_id: &str) {
        if let Some(flag) = self.feature_flags.get_mut(system_id) {
            flag.enabled = false;
        }
        if let Some(sys) = self.factory.get_mut(system_id) {
            sys.disable();
        }
    }

    pub fn is_enabled(&self, system_id: &str) -> bool {
        self.feature_flags
            .get(system_id)
            .map(|f| f.enabled)
            .unwrap_or(false)
    }

    pub fn create_system(&mut self, system_id: &str) -> Result<(), String> {
        let config = self
            .system_configs
            .get(system_id)
            .cloned()
            .ok_or_else(|| format!("System {system_id} not configured"))?;
        self.factory.create(system_id, config)
    }

    pub fn initialize_all(&mut self, system_ids: Option<Vec<String>>) -> Result<(), String> {
        let mut systems_to_init = system_ids.unwrap_or_else(|| self.system_configs.keys().cloned().collect());

        systems_to_init.sort_by(|a, b| {
            let pa = self.system_configs.get(a).map(|c| c.priority).unwrap_or(0);
            let pb = self.system_configs.get(b).map(|c| c.priority).unwrap_or(0);
            pb.cmp(&pa)
        });

        for system_id in systems_to_init {
            if !self.is_enabled(&system_id) {
                continue;
            }

            let deps = self
                .system_dependencies
                .get(&system_id)
                .cloned()
                .unwrap_or_default();
            for dep in deps {
                if !self.factory.has_system(&dep) {
                    return Err(format!("Dependency {dep} not initialized for {system_id}"));
                }
            }

            if !self.factory.has_system(&system_id) {
                self.create_system(&system_id)?;
            }
        }

        self.initialized = true;
        Ok(())
    }

    pub fn shutdown_all(&mut self) {
        self.factory.shutdown_all();
        self.initialized = false;
    }

    pub fn validate_dependencies(&self, system_id: &str) -> bool {
        let deps = self
            .system_dependencies
            .get(system_id)
            .cloned()
            .unwrap_or_default();
        deps.into_iter().all(|d| self.factory.has_system(&d))
    }

    pub fn is_initialized(&self) -> bool {
        self.initialized
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    struct DummySystem {
        config: SystemConfig,
    }

    impl DummySystem {
        fn new(config: SystemConfig) -> Self {
            Self { config }
        }
    }

    impl GameSystem for DummySystem {
        fn id(&self) -> &str {
            &self.config.system_id
        }

        fn system_type(&self) -> SystemType {
            self.config.system_type.clone()
        }

        fn enabled(&self) -> bool {
            self.config.enabled
        }

        fn enable(&mut self) {
            self.config.enabled = true;
        }

        fn disable(&mut self) {
            self.config.enabled = false;
        }

        fn initialize(&mut self) -> Result<(), String> {
            Ok(())
        }

        fn validate(&self) -> bool {
            true
        }
    }

    #[test]
    fn initialize_all_respects_dependencies() {
        let mut r = SystemRegistry::new();

        r.factory.register(
            "a",
            Box::new(|cfg| Box::new(DummySystem::new(cfg))),
        );
        r.factory.register(
            "b",
            Box::new(|cfg| Box::new(DummySystem::new(cfg))),
        );

        r.define_system(
            "a",
            SystemType::Gameplay,
            true,
            10,
            vec![],
            HashMap::new(),
        );
        r.define_system(
            "b",
            SystemType::Gameplay,
            true,
            9,
            vec!["a".to_string()],
            HashMap::new(),
        );

        // If we request b only, it should error because a not initialized.
        assert!(r.initialize_all(Some(vec!["b".to_string()])).is_err());

        // Initialize a then b works.
        r.shutdown_all();
        r.initialize_all(Some(vec!["a".to_string(), "b".to_string()]))
            .unwrap();
        assert!(r.is_initialized());
        assert!(r.factory.has_system("a"));
        assert!(r.factory.has_system("b"));
    }
}
