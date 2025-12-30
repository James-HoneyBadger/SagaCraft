use crate::game_state::AdventureGame;
use crate::systems::System;

#[derive(Debug, Default)]
pub struct InventorySystem;

impl System for InventorySystem {
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String> {
        match command {
            "inventory" | "inv" | "i" => {
                if game.player.inventory.is_empty() {
                    Some("Your inventory is empty.".to_string())
                } else {
                    let mut result = "Inventory:\n".to_string();
                    for &item_id in &game.player.inventory {
                        if let Some(item) = game.items.get(&item_id) {
                            result.push_str(&format!("  - {}\n", item.name));
                        }
                    }
                    Some(result.trim_end().to_string())
                }
            }
            "take" | "get" => {
                if let Some(item_name) = args.first() {
                    if game.take_item(item_name) {
                        Some("Taken.".to_string())
                    } else {
                        Some("You can't take that.".to_string())
                    }
                } else {
                    Some("Take what?".to_string())
                }
            }
            "drop" => {
                if let Some(item_name) = args.first() {
                    if game.drop_item(item_name) {
                        Some("Dropped.".to_string())
                    } else {
                        Some("You don't have that.".to_string())
                    }
                } else {
                    Some("Drop what?".to_string())
                }
            }
            _ => None,
        }
    }
}