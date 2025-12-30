pub mod basic_world;
pub mod inventory;
pub mod combat;
pub mod quests;

pub use basic_world::BasicWorldSystem;
pub use inventory::InventorySystem;
pub use combat::CombatSystem;
pub use quests::QuestSystem;

use crate::game_state::AdventureGame;

pub trait System {
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String>;
}