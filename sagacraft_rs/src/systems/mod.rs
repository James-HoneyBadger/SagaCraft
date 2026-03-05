pub mod basic_world;
pub mod inventory;
pub mod combat;
pub mod quests;

pub use basic_world::BasicWorldSystem;
pub use inventory::InventorySystem;
pub use combat::CombatSystem;
pub use quests::QuestSystem;

use crate::game_state::{AdventureGame, GameEvent};

pub trait System {
    /// Handle a typed player command. Return `Some(output)` to claim the command;
    /// returning `None` passes the command on to the next system.
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String>;

    /// Called after every command round when there are pending game events
    /// (monster kills, item pickups, room transitions, etc.).
    /// Return `Some(output)` to append an observer message (e.g. quest updates).
    /// The default implementation is a no-op.
    fn on_events(&mut self, _events: &[GameEvent], _game: &mut AdventureGame) -> Option<String> {
        None
    }
}