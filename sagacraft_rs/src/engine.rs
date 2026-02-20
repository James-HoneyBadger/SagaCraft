use crate::command::Command;
use crate::game_state::AdventureGame;
use crate::systems::{BasicWorldSystem, CombatSystem, InventorySystem};
use crate::systems::quests::QuestSystem;

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

impl Default for EngineOutput {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EngineEvent {
    Command(Command),
}

/// High-level engine that wraps `AdventureGame` and provides a typed event API.
pub struct Engine {
    pub game: AdventureGame,
}

impl Engine {
    pub fn new(adventure_path: impl Into<String>) -> Self {
        let mut game = AdventureGame::new(adventure_path.into());
        game.add_system(Box::new(BasicWorldSystem::default()));
        game.add_system(Box::new(InventorySystem::default()));
        game.add_system(Box::new(CombatSystem::default()));
        game.add_system(Box::new(QuestSystem::new()));
        Self { game }
    }

    pub fn load_from_path(
        adventure_path: impl Into<String>,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        let mut engine = Self::new(adventure_path);
        engine.game.load_adventure()?;
        Ok(engine)
    }

    pub fn step(&mut self, event: EngineEvent) -> EngineOutput {
        let cmd_str = match &event {
            EngineEvent::Command(cmd) => command_to_string(cmd),
        };

        if cmd_str == "quit" {
            self.game.game_over = true;
            return EngineOutput::line("Goodbye!");
        }

        let results = self.game.process_command(&cmd_str);
        let mut out = EngineOutput::new();
        for line in results {
            out.push(line);
        }
        out
    }

    pub fn look(&self) -> String {
        self.game.look()
    }

    pub fn is_over(&self) -> bool {
        self.game.game_over
    }
}

fn command_to_string(cmd: &Command) -> String {
    match cmd {
        Command::Help => "help".to_string(),
        Command::Look => "look".to_string(),
        Command::Inventory => "inventory".to_string(),
        Command::Move(dir) => dir.to_string(),
        Command::Take(item) => format!("take {}", item),
        Command::Drop(item) => format!("drop {}", item),
        Command::Use(item) => format!("use {}", item),
        Command::Equip(item) => format!("equip {}", item),
        Command::Examine(item) => format!("examine {}", item),
        Command::Say(text) => format!("say {}", text),
        Command::Quit => "quit".to_string(),
        Command::Unknown(s) => s.clone(),
    }
}
