use crate::systems::System;
use std::collections::HashMap;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ItemType {
    Weapon,
    Armor,
    Treasure,
    Readable,
    Edible,
    Drinkable,
    Container,
    Normal,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum MonsterStatus {
    Friendly,
    Neutral,
    Hostile,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub item_type: ItemType,
    pub weight: i32,
    pub value: i32,
    pub is_weapon: bool,
    pub weapon_type: i32, // 1=axe, 2=bow, 3=club, 4=spear, 5=sword
    pub weapon_dice: i32,
    pub weapon_sides: i32,
    pub is_armor: bool,
    pub armor_value: i32,
    pub is_takeable: bool,
    pub is_wearable: bool,
    pub location: i32, // 0=inventory, -1=worn, room_id or monster_id
}

impl Item {
    pub fn new(
        id: i32,
        name: String,
        description: String,
        item_type: ItemType,
        weight: i32,
        value: i32,
    ) -> Self {
        Self {
            id,
            name,
            description,
            item_type,
            weight,
            value,
            is_weapon: false,
            weapon_type: 0,
            weapon_dice: 1,
            weapon_sides: 6,
            is_armor: false,
            armor_value: 0,
            is_takeable: true,
            is_wearable: false,
            location: 0,
        }
    }

    pub fn get_damage(&self) -> i32 {
        if !self.is_weapon {
            return 0;
        }
        use rand::Rng;
        let mut rng = rand::thread_rng();
        (0..self.weapon_dice)
            .map(|_| rng.gen_range(1..=self.weapon_sides))
            .sum()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Monster {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub room_id: i32,
    pub hardiness: i32,
    pub agility: i32,
    pub friendliness: MonsterStatus,
    pub courage: i32,
    pub weapon_id: Option<i32>,
    pub armor_worn: i32,
    pub gold: i32,
    pub is_dead: bool,
    pub current_health: Option<i32>,
}

impl Monster {
    pub fn new(
        id: i32,
        name: String,
        description: String,
        room_id: i32,
        hardiness: i32,
        agility: i32,
        friendliness: MonsterStatus,
        courage: i32,
    ) -> Self {
        let current_health = Some(hardiness);
        Self {
            id,
            name,
            description,
            room_id,
            hardiness,
            agility,
            friendliness,
            courage,
            weapon_id: None,
            armor_worn: 0,
            gold: 0,
            is_dead: false,
            current_health,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Room {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub exits: HashMap<String, i32>, // direction -> room_id
    pub is_dark: bool,
}

impl Room {
    pub fn new(id: i32, name: String, description: String) -> Self {
        Self {
            id,
            name,
            description,
            exits: HashMap::new(),
            is_dark: false,
        }
    }

    pub fn get_exit(&self, direction: &str) -> Option<i32> {
        self.exits.get(&direction.to_lowercase()).copied()
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Player {
    pub name: String,
    pub hardiness: i32,
    pub agility: i32,
    pub charisma: i32,
    pub weapon_ability: HashMap<i32, i32>, // weapon_type -> ability
    pub armor_expertise: i32,
    pub gold: i32,
    pub current_room: i32,
    pub current_health: Option<i32>,
    pub inventory: Vec<i32>, // item IDs
    pub equipped_weapon: Option<i32>,
    pub equipped_armor: Option<i32>,
}

impl Player {
    pub fn new() -> Self {
        let mut weapon_ability = HashMap::new();
        for i in 1..=5 {
            weapon_ability.insert(i, 5);
        }
        Self {
            name: "Adventurer".to_string(),
            hardiness: 12,
            agility: 12,
            charisma: 12,
            weapon_ability,
            armor_expertise: 0,
            gold: 200,
            current_room: 1,
            current_health: Some(12),
            inventory: Vec::new(),
            equipped_weapon: None,
            equipped_armor: None,
        }
    }
}
pub struct AdventureGame {
    pub adventure_file: String,
    pub rooms: HashMap<i32, Room>,
    pub items: HashMap<i32, Item>,
    pub monsters: HashMap<i32, Monster>,
    pub player: Player,
    pub companions: Vec<String>, // Party members
    pub turn_count: i32,
    pub game_over: bool,
    pub adventure_title: String,
    pub adventure_intro: String,
    pub effects: Vec<serde_json::Value>, // Special events
    pub systems: Vec<Box<dyn System>>,
    pub quests: Vec<serde_json::Value>, // Quest definitions
}

impl AdventureGame {
    pub fn new(adventure_file: String) -> Self {
        Self {
            adventure_file,
            rooms: HashMap::new(),
            items: HashMap::new(),
            monsters: HashMap::new(),
            player: Player::new(),
            companions: Vec::new(),
            turn_count: 0,
            game_over: false,
            adventure_title: String::new(),
            adventure_intro: String::new(),
            effects: Vec::new(),
            systems: Vec::new(),
            quests: Vec::new(),
        }
    }

    pub fn load_adventure(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let data: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(&self.adventure_file)?)?;

        self.adventure_title = data.get("title").and_then(|v| v.as_str()).unwrap_or("Untitled Adventure").to_string();
        self.adventure_intro = data.get("intro").and_then(|v| v.as_str()).unwrap_or("").to_string();

        // Load rooms
        if let Some(rooms) = data.get("rooms").and_then(|v| v.as_array()) {
            for room_data in rooms {
                let room = Room {
                    id: room_data.get("id").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                    name: room_data.get("name").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    description: room_data.get("description").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    exits: room_data.get("exits").and_then(|v| v.as_object())
                        .map(|obj| obj.iter().map(|(k, v)| (k.clone(), v.as_i64().unwrap_or(0) as i32)).collect())
                        .unwrap_or_default(),
                    is_dark: room_data.get("is_dark").and_then(|v| v.as_bool()).unwrap_or(false),
                };
                self.rooms.insert(room.id, room);
            }
        }

        // Load items
        if let Some(items) = data.get("items").and_then(|v| v.as_array()) {
            for item_data in items {
                let item = Item {
                    id: item_data.get("id").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                    name: item_data.get("name").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    description: item_data.get("description").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    item_type: match item_data.get("type").and_then(|v| v.as_str()) {
                        Some("weapon") => ItemType::Weapon,
                        Some("armor") => ItemType::Armor,
                        Some("treasure") => ItemType::Treasure,
                        Some("readable") => ItemType::Readable,
                        Some("edible") => ItemType::Edible,
                        Some("drinkable") => ItemType::Drinkable,
                        Some("container") => ItemType::Container,
                        _ => ItemType::Normal,
                    },
                    weight: item_data.get("weight").and_then(|v| v.as_i64()).unwrap_or(1) as i32,
                    value: item_data.get("value").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                    is_weapon: item_data.get("is_weapon").and_then(|v| v.as_bool()).unwrap_or(false),
                    weapon_type: item_data.get("weapon_type").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                    weapon_dice: item_data.get("weapon_dice").and_then(|v| v.as_i64()).unwrap_or(1) as i32,
                    weapon_sides: item_data.get("weapon_sides").and_then(|v| v.as_i64()).unwrap_or(6) as i32,
                    is_armor: item_data.get("is_armor").and_then(|v| v.as_bool()).unwrap_or(false),
                    armor_value: item_data.get("armor_value").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                    is_takeable: item_data.get("is_takeable").and_then(|v| v.as_bool()).unwrap_or(true),
                    is_wearable: item_data.get("is_wearable").and_then(|v| v.as_bool()).unwrap_or(false),
                    location: item_data.get("location").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                };
                self.items.insert(item.id, item);
            }
        }

        // Load monsters
        if let Some(monsters) = data.get("monsters").and_then(|v| v.as_array()) {
            for mon_data in monsters {
                let friendliness = match mon_data.get("friendliness").and_then(|v| v.as_str()) {
                    Some("friendly") => MonsterStatus::Friendly,
                    Some("hostile") => MonsterStatus::Hostile,
                    _ => MonsterStatus::Neutral,
                };
                let monster = Monster::new(
                    mon_data.get("id").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                    mon_data.get("name").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    mon_data.get("description").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    mon_data.get("room_id").and_then(|v| v.as_i64()).unwrap_or(1) as i32,
                    mon_data.get("hardiness").and_then(|v| v.as_i64()).unwrap_or(10) as i32,
                    mon_data.get("agility").and_then(|v| v.as_i64()).unwrap_or(10) as i32,
                    friendliness,
                    mon_data.get("courage").and_then(|v| v.as_i64()).unwrap_or(100) as i32,
                );
                // Set additional fields
                let mut monster = monster;
                monster.weapon_id = mon_data.get("weapon_id").and_then(|v| v.as_i64()).map(|v| v as i32);
                monster.armor_worn = mon_data.get("armor_worn").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
                monster.gold = mon_data.get("gold").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
                self.monsters.insert(monster.id, monster);
            }
        }

        // Load effects
        if let Some(effects) = data.get("effects").and_then(|v| v.as_array()) {
            self.effects = effects.clone();
        }

        // Load quests
        if let Some(quests) = data.get("quests").and_then(|v| v.as_array()) {
            self.quests = quests.clone();
        }

        // Set player starting position
        self.player.current_room = data.get("start_room").and_then(|v| v.as_i64()).unwrap_or(1) as i32;

        println!("\n{:=^60}", "");
        println!("{:^60}", self.adventure_title);
        println!("{:=^60}\n", "");
        if !self.adventure_intro.is_empty() {
            println!("{}", self.adventure_intro);
            println!();
        }

        Ok(())
    }

    pub fn get_current_room(&self) -> Option<&Room> {
        self.rooms.get(&self.player.current_room)
    }

    pub fn get_items_in_room(&self, room_id: i32) -> Vec<&Item> {
        self.items.values()
            .filter(|item| item.location == room_id)
            .collect()
    }

    pub fn get_monsters_in_room(&self, room_id: i32) -> Vec<&Monster> {
        self.monsters.values()
            .filter(|m| m.room_id == room_id && !m.is_dead)
            .collect()
    }

    pub fn look(&self) {
        if let Some(room) = self.get_current_room() {
            println!("\n{}", room.name);
            println!("{}", "-".repeat(room.name.len()));
            println!("{}", room.description);

            // Show exits
            if !room.exits.is_empty() {
                let exits: Vec<String> = room.exits.keys().cloned().collect();
                println!("\nObvious exits: {}", exits.join(", "));
            } else {
                println!("\nNo obvious exits.");
            }
        } else {
            println!("You are in a void.");
        }

        // Show items
        let items = self.get_items_in_room(self.player.current_room);
        if !items.is_empty() {
            println!("\nYou see:");
            for item in items {
                println!("  - {}", item.name);
            }
        }

        // Show monsters
        let monsters = self.get_monsters_in_room(self.player.current_room);
        if !monsters.is_empty() {
            println!("\nPresent:");
            for monster in monsters {
                let status = match monster.friendliness {
                    MonsterStatus::Friendly => " (friendly)",
                    MonsterStatus::Hostile => " (hostile)",
                    MonsterStatus::Neutral => "",
                };
                println!("  - {}{}", monster.name, status);
            }
        }
    }

    pub fn move_player(&mut self, direction: &str) -> bool {
        if let Some(room) = self.get_current_room() {
            if let Some(new_room_id) = room.get_exit(direction) {
                if self.rooms.contains_key(&new_room_id) {
                    self.player.current_room = new_room_id;
                    self.turn_count += 1;
                    return true;
                }
            }
        }
        false
    }

    pub fn take_item(&mut self, item_name: &str) -> bool {
        let room_items = self.get_items_in_room(self.player.current_room);
        for item in room_items {
            if item.name.to_lowercase().contains(&item_name.to_lowercase()) && item.is_takeable {
                let mut item = (*item).clone();
                item.location = 0; // inventory
                self.player.inventory.push(item.id);
                // Update the item in the hashmap
                if let Some(item_ref) = self.items.get_mut(&item.id) {
                    item_ref.location = 0;
                }
                return true;
            }
        }
        false
    }

    pub fn drop_item(&mut self, item_name: &str) -> bool {
        for &item_id in &self.player.inventory {
            if let Some(item) = self.items.get(&item_id) {
                if item.name.to_lowercase().contains(&item_name.to_lowercase()) {
                    // Remove from inventory
                    self.player.inventory.retain(|&id| id != item_id);
                    // Put in current room
                    if let Some(item_ref) = self.items.get_mut(&item_id) {
                        item_ref.location = self.player.current_room;
                    }
                    return true;
                }
            }
        }
        false
    }

    pub fn add_system(&mut self, system: Box<dyn System>) {
        self.systems.push(system);
    }

    pub fn process_command(&mut self, command: &str) -> Vec<String> {
        let parts: Vec<&str> = command.split_whitespace().collect();
        let cmd = parts.first().unwrap_or(&"");
        let args: Vec<&str> = parts.iter().skip(1).cloned().collect();

        let mut systems = std::mem::take(&mut self.systems);
        let mut result = None;
        for system in &mut systems {
            let output = system.on_command(cmd, &args, self);
            if let Some(output) = output {
                result = Some(vec![output]);
                break;
            }
        }
        self.systems = systems;
        result.unwrap_or_else(|| vec![format!("Unknown command: {}", command)])
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GameState {
    pub world: HashMap<String, Room>,
    pub player: Player,
    pub variables: HashMap<String, String>,
    pub is_over: bool,
}

impl GameState {
    pub fn new(player_name: impl Into<String>) -> Self {
        let mut player = Player::new();
        player.name = player_name.into();
        player.current_room = 1;

        let village = Room::new(1, "Quiet Village".to_string(), "A small village with a single cobblestone path and a warm lantern glow.".to_string());
        let forest = Room::new(2, "Whispering Forest".to_string(), "Tall pines sway as if sharing secrets. The village lies south.".to_string());

        let mut world = HashMap::new();
        world.insert(village.id.to_string(), village);
        world.insert(forest.id.to_string(), forest);

        Self {
            world,
            player,
            variables: HashMap::new(),
            is_over: false,
        }
    }

    // pub fn from_adventure(
    //     player_name: impl Into<String>,
    //     adventure: crate::adventure::Adventure,
    // ) -> Result<Self, crate::adventure::AdventureError> {
    //     adventure.into_game_state(player_name)
    // }

    pub fn current_room(&self) -> &Room {
        self.world
            .get(&self.player.current_room.to_string())
            .expect("player location must exist")
    }

    pub fn current_room_mut(&mut self) -> &mut Room {
        self.world
            .get_mut(&self.player.current_room.to_string())
            .expect("player location must exist")
    }
}
