use serde_json::Value;
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

use crate::pyport::core::services::Service;

pub struct IOService {
    base_dir: PathBuf,
    adventures_dir: PathBuf,
    saves_dir: PathBuf,
}

impl IOService {
    pub fn new(base_dir: impl Into<PathBuf>) -> Self {
        let base_dir = base_dir.into();
        let adventures_dir = base_dir.join("adventures");
        let saves_dir = base_dir.join("saves");
        Self {
            base_dir,
            adventures_dir,
            saves_dir,
        }
    }

    pub fn load_json(&self, file_path: &Path) -> Result<Option<HashMap<String, Value>>, String> {
        match fs::read_to_string(file_path) {
            Ok(content) => match serde_json::from_str(&content) {
                Ok(data) => Ok(Some(data)),
                Err(e) => {
                    eprintln!("Invalid JSON in {:?}: {}", file_path, e);
                    Ok(None)
                }
            },
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
                eprintln!("File not found: {:?}", file_path);
                Ok(None)
            }
            Err(e) => Err(format!("Error loading {:?}: {}", file_path, e)),
        }
    }

    pub fn save_json(&self, file_path: &Path, data: &HashMap<String, Value>, indent: usize) -> Result<bool, String> {
        if let Some(parent) = file_path.parent() {
            fs::create_dir_all(parent).map_err(|e| format!("create dir {:?}: {}", parent, e))?;
        }
        let content = serde_json::to_string_pretty(data).map_err(|e| format!("serialize json: {}", e))?;
        fs::write(file_path, content).map_err(|e| format!("write file {:?}: {}", file_path, e))?;
        Ok(true)
    }

    pub fn load_adventure(&self, adventure_name: &str) -> Result<Option<HashMap<String, Value>>, String> {
        let adventure_path = self.adventures_dir.join(format!("{}.json", adventure_name));
        self.load_json(&adventure_path)
    }

    pub fn list_adventures(&self) -> Result<Vec<String>, String> {
        if !self.adventures_dir.exists() {
            return Ok(vec![]);
        }
        let mut adventures = vec![];
        for entry in fs::read_dir(&self.adventures_dir).map_err(|e| format!("read dir {:?}: {}", self.adventures_dir, e))? {
            let entry = entry.map_err(|e| format!("read entry: {}", e))?;
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("json") {
                if let Some(stem) = path.file_stem().and_then(|s| s.to_str()) {
                    adventures.push(stem.to_string());
                }
            }
        }
        Ok(adventures)
    }

    pub fn save_game(&self, save_name: &str, game_state: &HashMap<String, Value>) -> Result<bool, String> {
        let save_path = self.saves_dir.join(format!("{}.json", save_name));
        self.save_json(&save_path, game_state, 2)
    }

    pub fn load_game(&self, save_name: &str) -> Result<Option<HashMap<String, Value>>, String> {
        let save_path = self.saves_dir.join(format!("{}.json", save_name));
        self.load_json(&save_path)
    }

    pub fn list_saves(&self) -> Result<Vec<String>, String> {
        if !self.saves_dir.exists() {
            return Ok(vec![]);
        }
        let mut saves = vec![];
        for entry in fs::read_dir(&self.saves_dir).map_err(|e| format!("read dir {:?}: {}", self.saves_dir, e))? {
            let entry = entry.map_err(|e| format!("read entry: {}", e))?;
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("json") {
                if let Some(stem) = path.file_stem().and_then(|s| s.to_str()) {
                    saves.push(stem.to_string());
                }
            }
        }
        Ok(saves)
    }

    pub fn delete_save(&self, save_name: &str) -> Result<bool, String> {
        let save_path = self.saves_dir.join(format!("{}.json", save_name));
        match fs::remove_file(&save_path) {
            Ok(()) => Ok(true),
            Err(e) => {
                eprintln!("Error deleting save {}: {}", save_name, e);
                Ok(false)
            }
        }
    }
}

impl Service for IOService {
    fn name(&self) -> &'static str {
        "IOService"
    }

    fn initialize(&mut self, config: &HashMap<String, Value>) -> Result<(), String> {
        // Create directories
        fs::create_dir_all(&self.adventures_dir).map_err(|e| format!("create adventures dir: {}", e))?;
        fs::create_dir_all(&self.saves_dir).map_err(|e| format!("create saves dir: {}", e))?;

        // Override paths from config
        if let Some(Value::String(adventures_dir)) = config.get("adventures_dir") {
            self.adventures_dir = PathBuf::from(adventures_dir);
        }
        if let Some(Value::String(saves_dir)) = config.get("saves_dir") {
            self.saves_dir = PathBuf::from(saves_dir);
        }

        Ok(())
    }

    fn shutdown(&mut self) -> Result<(), String> {
        // Nothing needed for basic I/O
        Ok(())
    }
}