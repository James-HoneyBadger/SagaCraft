use serde_json::Value;
use std::collections::HashMap;
use std::fs;
use std::path::Path;

/// Read and parse an adventure JSON file.
///
/// # Errors
/// - If the file can't be read
/// - If the file isn't valid JSON
/// - If the parsed JSON isn't an object
pub fn read_adventure_data(adventure_file: &Path) -> Result<HashMap<String, Value>, String> {
    let content = fs::read_to_string(adventure_file)
        .map_err(|e| format!("read file {:?}: {}", adventure_file, e))?;

    let data: Value = serde_json::from_str(&content)
        .map_err(|e| format!("parse json {:?}: {}", adventure_file, e))?;

    match data {
        Value::Object(map) => Ok(map),
        _ => Err("Adventure JSON must be an object at the top level".to_string()),
    }
}