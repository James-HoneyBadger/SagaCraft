use crate::game_state::{AdventureGame, MonsterStatus};
use crate::systems::System;

#[derive(Debug, Default)]
pub struct BasicWorldSystem;

impl System for BasicWorldSystem {
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String> {
        match command {
            "look" | "l" => {
                Some(game.look())
            }
            "go" | "move" => {
                if let Some(dir) = args.first() {
                    match game.move_player(dir) {
                        Some(desc) => Some(desc),
                        None => Some(format!("You can't go {}.", dir)),
                    }
                } else {
                    Some("Go where?".to_string())
                }
            }
            dir if ["north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"].contains(&dir) => {
                match game.move_player(dir) {
                    Some(desc) => Some(desc),
                    None => Some("You can't go that way.".to_string()),
                }
            }
            "say" | "shout" | "yell" => {
                let text = args.join(" ");
                if text.is_empty() {
                    Some("Say what?".to_string())
                } else {
                    // Check if any NPC in the room shares the keyword
                    let monsters = game.get_monsters_in_room(game.player.current_room);
                    let npc_names: Vec<String> = monsters.iter()
                        .filter(|m| m.friendliness != MonsterStatus::Hostile)
                        .map(|m| m.name.clone())
                        .collect();
                    if npc_names.is_empty() {
                        Some(format!("You say: \"{}\"", text))
                    } else {
                        Some(format!("You say: \"{}\"\n{} turns to face you.", text, npc_names[0]))
                    }
                }
            }
            _ => None,
        }
    }
}