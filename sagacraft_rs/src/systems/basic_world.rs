use crate::game_state::AdventureGame;
use crate::systems::System;

#[derive(Debug, Default)]
pub struct BasicWorldSystem;

impl System for BasicWorldSystem {
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String> {
        match command {
            "look" | "l" => {
                game.look();
                None
            }
            "go" | "move" => {
                if let Some(dir) = args.first() {
                    if game.move_player(dir) {
                        Some(format!("You move {}.", dir))
                    } else {
                        Some(format!("You can't go {}.", dir))
                    }
                } else {
                    Some("Go where?".to_string())
                }
            }
            dir if ["north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"].contains(&dir) => {
                if game.move_player(dir) {
                    Some(format!("You move {}.", dir))
                } else {
                    Some("You can't go that way.".to_string())
                }
            }
            _ => None,
        }
    }
}