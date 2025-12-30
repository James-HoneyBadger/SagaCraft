use crate::command::Command;
use crate::adventure::{Adventure, AdventureError};
use crate::game_state::GameState;
// use crate::systems::{BasicWorldSystem, InventorySystem, System};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EngineOutput {
    pub lines: Vec<String>,
}

impl EngineOutput {
    pub fn new() -> Self {
        Self { lines: Vec::new() }
    }

    pub fn none() -> Self {
        Self::new()
    }

    pub fn line(line: impl Into<String>) -> Self {
        Self { lines: vec![line.into()] }
    }

    pub fn lines<const N: usize>(lines: [&'static str; N]) -> Self {
        Self {
            lines: lines.into_iter().map(|s| s.to_string()).collect(),
        }
    }

    pub fn push(&mut self, line: impl Into<String>) {
        self.lines.push(line.into());
    }

    pub fn extend(&mut self, other: EngineOutput) {
        self.lines.extend(other.lines);
    }

    pub fn is_empty(&self) -> bool {
        self.lines.is_empty()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EngineEvent {
    Command(Command),
}

pub struct Engine {
    pub state: GameState,
    systems: Vec<Box<dyn System>>,
}

impl Engine {
    pub fn new(player_name: impl Into<String>) -> Self {
        let state = GameState::new(player_name);
        let mut systems: Vec<Box<dyn System>> = Vec::new();
        systems.push(Box::new(InventorySystem::default()));
        systems.push(Box::new(BasicWorldSystem::default()));

        Self { state, systems }
    }

    pub fn from_adventure(
        player_name: impl Into<String>,
        adventure: Adventure,
    ) -> Result<Self, AdventureError> {
        let state = GameState::from_adventure(player_name, adventure)?;
        let mut systems: Vec<Box<dyn System>> = Vec::new();
        systems.push(Box::new(InventorySystem::default()));
        systems.push(Box::new(BasicWorldSystem::default()));

        Ok(Self { state, systems })
    }

    pub fn load_from_path(
        player_name: impl Into<String>,
        path: impl AsRef<std::path::Path>,
    ) -> Result<Self, AdventureError> {
        let adv = Adventure::load_json_file(path)?;
        Self::from_adventure(player_name, adv)
    }

    pub fn add_system(&mut self, system: Box<dyn System>) {
        self.systems.push(system);
    }

    pub fn step(&mut self, event: EngineEvent) -> EngineOutput {
        let mut out = EngineOutput::new();
        for system in &mut self.systems {
            let part = system.on_event(&mut self.state, &event);
            if !part.is_empty() {
                out.extend(part);
            }
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::command::{Command, Direction};

    #[test]
    fn moving_updates_location() {
        let mut engine = Engine::new("Tester");
        assert_eq!(engine.state.player.location, "village");
        let _ = engine.step(EngineEvent::Command(Command::Move(Direction::North)));
        assert_eq!(engine.state.player.location, "forest");
    }

    #[test]
    fn quit_sets_game_over() {
        let mut engine = Engine::new("Tester");
        assert!(!engine.state.is_over);
        let _ = engine.step(EngineEvent::Command(Command::Quit));
        assert!(engine.state.is_over);
    }
}
