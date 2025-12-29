use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Item {
    pub id: String,
    pub name: String,
    pub description: String,
}

impl Item {
    pub fn new(id: impl Into<String>, name: impl Into<String>, description: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            name: name.into(),
            description: description.into(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Player {
    pub name: String,
    pub location: String,
    pub inventory: Vec<Item>,
    pub flags: HashSet<String>,
}

impl Player {
    pub fn new(name: impl Into<String>, start_location: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            location: start_location.into(),
            inventory: Vec::new(),
            flags: HashSet::new(),
        }
    }

    pub fn has_item_named(&self, name: &str) -> bool {
        self.inventory
            .iter()
            .any(|i| i.name.eq_ignore_ascii_case(name))
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Room {
    pub id: String,
    pub title: String,
    pub description: String,
    pub exits: HashMap<String, String>, // direction -> room id
    pub items: Vec<Item>,
}

impl Room {
    pub fn new(id: impl Into<String>, title: impl Into<String>, description: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            title: title.into(),
            description: description.into(),
            exits: HashMap::new(),
            items: Vec::new(),
        }
    }

    pub fn with_exit(mut self, direction: impl Into<String>, dest_room: impl Into<String>) -> Self {
        self.exits.insert(direction.into(), dest_room.into());
        self
    }

    pub fn with_item(mut self, item: Item) -> Self {
        self.items.push(item);
        self
    }

    pub fn remove_item_named(&mut self, name: &str) -> Option<Item> {
        let idx = self
            .items
            .iter()
            .position(|i| i.name.eq_ignore_ascii_case(name))?;
        Some(self.items.remove(idx))
    }

    pub fn add_item(&mut self, item: Item) {
        self.items.push(item);
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
        let player = Player::new(player_name, "village");

        let village = Room::new(
            "village",
            "Quiet Village",
            "A small village with a single cobblestone path and a warm lantern glow.",
        )
        .with_exit("north", "forest")
        .with_item(Item::new(
            "key",
            "Ancient Key",
            "A tarnished key that seems to hum faintly.",
        ));

        let forest = Room::new(
            "forest",
            "Whispering Forest",
            "Tall pines sway as if sharing secrets. The village lies south.",
        )
        .with_exit("south", "village");

        let mut world = HashMap::new();
        world.insert(village.id.clone(), village);
        world.insert(forest.id.clone(), forest);

        Self {
            world,
            player,
            variables: HashMap::new(),
            is_over: false,
        }
    }

    pub fn current_room(&self) -> &Room {
        self.world
            .get(&self.player.location)
            .expect("player location must exist")
    }

    pub fn current_room_mut(&mut self) -> &mut Room {
        self.world
            .get_mut(&self.player.location)
            .expect("player location must exist")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn world_has_two_rooms() {
        let s = GameState::new("Tester");
        assert!(s.world.contains_key("village"));
        assert!(s.world.contains_key("forest"));
    }

    #[test]
    fn village_has_key_item() {
        let s = GameState::new("Tester");
        let room = s.world.get("village").unwrap();
        assert!(room.items.iter().any(|i| i.name == "Ancient Key"));
    }
}
