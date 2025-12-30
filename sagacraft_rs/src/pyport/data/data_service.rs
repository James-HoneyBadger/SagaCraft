use serde_json::Value;
use std::collections::HashMap;

use crate::pyport::core::services::Service;

pub struct DataService {
    data_store: HashMap<String, HashMap<i64, Value>>,
}

impl DataService {
    pub fn new() -> Self {
        let mut data_store = HashMap::new();
        data_store.insert("rooms".to_string(), HashMap::new());
        data_store.insert("items".to_string(), HashMap::new());
        data_store.insert("monsters".to_string(), HashMap::new());
        Self { data_store }
    }

    // Room operations
    pub fn add_room(&mut self, room_id: i64, room_data: Value) {
        self.data_store.get_mut("rooms").unwrap().insert(room_id, room_data);
    }

    pub fn get_room(&self, room_id: i64) -> Option<&Value> {
        self.data_store["rooms"].get(&room_id)
    }

    pub fn get_all_rooms(&self) -> &HashMap<i64, Value> {
        &self.data_store["rooms"]
    }

    pub fn remove_room(&mut self, room_id: i64) {
        self.data_store.get_mut("rooms").unwrap().remove(&room_id);
    }

    // Item operations
    pub fn add_item(&mut self, item_id: i64, item_data: Value) {
        self.data_store.get_mut("items").unwrap().insert(item_id, item_data);
    }

    pub fn get_item(&self, item_id: i64) -> Option<&Value> {
        self.data_store["items"].get(&item_id)
    }

    pub fn get_all_items(&self) -> &HashMap<i64, Value> {
        &self.data_store["items"]
    }

    pub fn find_items_by_location(&self, location: i64) -> Vec<&Value> {
        self.data_store["items"]
            .values()
            .filter(|item| {
                if let Some(Value::Number(loc)) = item.get("location") {
                    loc.as_i64() == Some(location)
                } else {
                    false
                }
            })
            .collect()
    }

    pub fn remove_item(&mut self, item_id: i64) {
        self.data_store.get_mut("items").unwrap().remove(&item_id);
    }

    // Monster operations
    pub fn add_monster(&mut self, monster_id: i64, monster_data: Value) {
        self.data_store.get_mut("monsters").unwrap().insert(monster_id, monster_data);
    }

    pub fn get_monster(&self, monster_id: i64) -> Option<&Value> {
        self.data_store["monsters"].get(&monster_id)
    }

    pub fn get_all_monsters(&self) -> &HashMap<i64, Value> {
        &self.data_store["monsters"]
    }

    pub fn find_monsters_by_room(&self, room_id: i64) -> Vec<&Value> {
        self.data_store["monsters"]
            .values()
            .filter(|monster| {
                if let Some(Value::Number(rid)) = monster.get("room_id") {
                    rid.as_i64() == Some(room_id)
                } else {
                    false
                }
            })
            .collect()
    }

    pub fn remove_monster(&mut self, monster_id: i64) {
        self.data_store.get_mut("monsters").unwrap().remove(&monster_id);
    }

    // Generic operations
    pub fn add_entity(&mut self, entity_type: &str, entity_id: i64, entity_data: Value) {
        self.data_store
            .entry(entity_type.to_string())
            .or_insert_with(HashMap::new)
            .insert(entity_id, entity_data);
    }

    pub fn get_entity(&self, entity_type: &str, entity_id: i64) -> Option<&Value> {
        self.data_store.get(entity_type)?.get(&entity_id)
    }

    pub fn clear_all(&mut self) {
        for store in self.data_store.values_mut() {
            store.clear();
        }
    }

    pub fn import_data(&mut self, data: HashMap<String, HashMap<i64, Value>>) {
        if let Some(rooms) = data.get("rooms") {
            self.data_store.insert("rooms".to_string(), rooms.clone());
        }
        if let Some(items) = data.get("items") {
            self.data_store.insert("items".to_string(), items.clone());
        }
        if let Some(monsters) = data.get("monsters") {
            self.data_store.insert("monsters".to_string(), monsters.clone());
        }
    }

    pub fn export_data(&self) -> HashMap<String, HashMap<i64, Value>> {
        let mut result = HashMap::new();
        result.insert("rooms".to_string(), self.data_store["rooms"].clone());
        result.insert("items".to_string(), self.data_store["items"].clone());
        result.insert("monsters".to_string(), self.data_store["monsters"].clone());
        result
    }
}

impl Service for DataService {
    fn name(&self) -> &'static str {
        "DataService"
    }

    fn initialize(&mut self, _config: &HashMap<String, Value>) -> Result<(), String> {
        // Logger equivalent would be println! or proper logging
        Ok(())
    }

    fn shutdown(&mut self) -> Result<(), String> {
        self.data_store.clear();
        Ok(())
    }
}