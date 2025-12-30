use serde_json::Value;
use std::collections::HashMap;

/// Rough port of Python's Service base class.
///
/// In Python, services are initialized with a config dict and can be shutdown.
pub trait Service {
    fn name(&self) -> &'static str;

    fn initialize(&mut self, _config: &HashMap<String, Value>) -> Result<(), String> {
        Ok(())
    }

    fn shutdown(&mut self) -> Result<(), String> {
        Ok(())
    }
}
