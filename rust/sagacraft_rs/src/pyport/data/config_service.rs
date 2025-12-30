use serde_json::{Map, Value};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

use crate::pyport::core::services::Service;

pub struct ConfigService {
    pub config_dir: PathBuf,
    config: Map<String, Value>,
    plugin_configs: HashMap<String, Map<String, Value>>,
}

impl ConfigService {
    pub fn new(config_dir: impl Into<PathBuf>) -> Self {
        Self {
            config_dir: config_dir.into(),
            config: Map::new(),
            plugin_configs: HashMap::new(),
        }
    }

    fn engine_config_path(&self) -> PathBuf {
        self.config_dir.join("engine.json")
    }

    fn plugins_dir(&self) -> PathBuf {
        self.config_dir.join("plugins")
    }

    pub fn load_engine_config(&mut self) -> Result<(), String> {
        let path = self.engine_config_path();
        if !path.exists() {
            self.config = default_engine_config();
            self.save_engine_config()?;
            return Ok(());
        }

        let s = fs::read_to_string(&path).map_err(|e| format!("read {path:?}: {e}"))?;
        let v: Value = serde_json::from_str(&s).map_err(|e| format!("parse json {path:?}: {e}"))?;
        self.config = match v {
            Value::Object(m) => m,
            _ => Map::new(),
        };
        Ok(())
    }

    pub fn save_engine_config(&self) -> Result<(), String> {
        fs::create_dir_all(&self.config_dir)
            .map_err(|e| format!("create config dir {:?}: {e}", self.config_dir))?;
        let path = self.engine_config_path();
        let s = serde_json::to_string_pretty(&Value::Object(self.config.clone()))
            .map_err(|e| format!("serialize json: {e}"))?;
        fs::write(&path, s).map_err(|e| format!("write {path:?}: {e}"))?;
        Ok(())
    }

    pub fn load_plugin_configs(&mut self) -> Result<(), String> {
        let plugins_dir = self.plugins_dir();
        if !plugins_dir.exists() {
            return Ok(());
        }

        let entries = fs::read_dir(&plugins_dir)
            .map_err(|e| format!("read dir {plugins_dir:?}: {e}"))?;
        for ent in entries {
            let ent = ent.map_err(|e| format!("read dir entry: {e}"))?;
            let path = ent.path();
            if path.extension().and_then(|s| s.to_str()) != Some("json") {
                continue;
            }

            let plugin_name = path
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("unknown")
                .to_string();

            let s = fs::read_to_string(&path).map_err(|e| format!("read {path:?}: {e}"))?;
            let v: Value =
                serde_json::from_str(&s).map_err(|e| format!("parse json {path:?}: {e}"))?;
            if let Value::Object(m) = v {
                self.plugin_configs.insert(plugin_name, m);
            }
        }

        Ok(())
    }

    pub fn get(&self, key: &str, default: Value) -> Value {
        get_dotted(&Value::Object(self.config.clone()), key).unwrap_or(default)
    }

    pub fn set(&mut self, key: &str, value: Value) {
        set_dotted(&mut self.config, key, value);
    }

    pub fn get_plugin(&self, plugin: &str, key: &str, default: Value) -> Value {
        match self.plugin_configs.get(plugin) {
            Some(m) => get_dotted(&Value::Object(m.clone()), key).unwrap_or(default),
            None => default,
        }
    }

    pub fn set_plugin(&mut self, plugin: &str, key: &str, value: Value) {
        let entry = self
            .plugin_configs
            .entry(plugin.to_string())
            .or_insert_with(Map::new);
        set_dotted(entry, key, value);
    }

    pub fn save_all(&self) -> Result<(), String> {
        self.save_engine_config()?;

        let plugins_dir = self.plugins_dir();
        fs::create_dir_all(&plugins_dir)
            .map_err(|e| format!("create plugins dir {plugins_dir:?}: {e}"))?;

        for (name, cfg) in &self.plugin_configs {
            let path = plugins_dir.join(format!("{name}.json"));
            let s = serde_json::to_string_pretty(&Value::Object(cfg.clone()))
                .map_err(|e| format!("serialize plugin json: {e}"))?;
            fs::write(&path, s).map_err(|e| format!("write {path:?}: {e}"))?;
        }

        Ok(())
    }

    pub fn config_dir(&self) -> &Path {
        &self.config_dir
    }
}

impl Service for ConfigService {
    fn name(&self) -> &'static str {
        "ConfigService"
    }

    fn initialize(&mut self, _config: &HashMap<String, Value>) -> Result<(), String> {
        fs::create_dir_all(&self.config_dir)
            .map_err(|e| format!("create config dir {:?}: {e}", self.config_dir))?;
        self.load_engine_config()?;
        self.load_plugin_configs()?;
        Ok(())
    }

    fn shutdown(&mut self) -> Result<(), String> {
        self.save_all()
    }
}

fn default_engine_config() -> Map<String, Value> {
    let v = serde_json::json!({
        "engine": {
            "name": "SagaCraft",
            "version": "3.0.0",
            "enable_event_history": false
        },
        "gameplay": {
            "auto_save": true,
            "save_interval": 5,
            "difficulty": "normal"
        },
        "ui": {
            "theme": "dark",
            "font_size": 12,
            "color_enabled": true
        }
    });

    match v {
        Value::Object(m) => m,
        _ => Map::new(),
    }
}

fn get_dotted(root: &Value, key: &str) -> Option<Value> {
    let mut cur = root;
    for part in key.split('.') {
        match cur {
            Value::Object(m) => {
                cur = m.get(part)?;
            }
            _ => return None,
        }
    }
    Some(cur.clone())
}

fn set_dotted(root: &mut Map<String, Value>, key: &str, value: Value) {
    let mut parts = key.split('.').peekable();
    let mut cur: &mut Map<String, Value> = root;

    while let Some(part) = parts.next() {
        if parts.peek().is_none() {
            cur.insert(part.to_string(), value);
            return;
        }

        let next = cur
            .entry(part.to_string())
            .or_insert_with(|| Value::Object(Map::new()));

        if !next.is_object() {
            *next = Value::Object(Map::new());
        }

        // safe because we just ensured it is an object
        cur = next.as_object_mut().expect("object");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dotted_get_set_roundtrip() {
        let mut s = ConfigService::new("/tmp/sagacraft_test_config_service_unused");
        s.set("engine.name", Value::String("X".to_string()));
        assert_eq!(s.get("engine.name", Value::Null), Value::String("X".to_string()));
    }
}
