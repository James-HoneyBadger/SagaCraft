use crate::game_state::{AdventureGame, MonsterStatus};
use crate::systems::System;

#[derive(Debug, Default)]
pub struct BasicWorldSystem;

impl BasicWorldSystem {
    /// Expand single-letter direction abbreviations to full words so exit
    /// keys in the adventure JSON ("north", "south" …) are matched reliably.
    fn expand_direction(dir: &str) -> &str {
        match dir {
            "n" => "north",
            "s" => "south",
            "e" => "east",
            "w" => "west",
            "u" => "up",
            "d" => "down",
            other => other,
        }
    }
}

impl System for BasicWorldSystem {
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String> {
        match command {
            "help" | "?" => {
                Some(Self::help_text())
            }
            "look" | "l" => {
                Some(game.look())
            }
            "go" | "move" => {
                if let Some(dir) = args.first() {
                    let full = Self::expand_direction(dir);
                    match game.move_player(full) {
                        Some(desc) => Some(desc),
                        None => Some(format!("You can't go {}.", full)),
                    }
                } else {
                    Some("Go where?".to_string())
                }
            }
            dir if ["north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"].contains(&dir) => {
                let full = Self::expand_direction(dir);
                match game.move_player(full) {
                    Some(desc) => Some(desc),
                    None => Some("You can't go that way.".to_string()),
                }
            }
            "say" | "shout" | "yell" => {
                let text = args.join(" ");
                if text.is_empty() {
                    Some("Say what?".to_string())
                } else {
                    // Collect all non-hostile NPCs in the room
                    let monsters = game.get_monsters_in_room(game.player.current_room);
                    let npc_names: Vec<String> = monsters.iter()
                        .filter(|m| m.friendliness != MonsterStatus::Hostile)
                        .map(|m| m.name.clone())
                        .collect();
                    let mut response = format!("You say: \"{}\"", text);
                    if !npc_names.is_empty() {
                        for npc in &npc_names {
                            response.push_str(&format!("\n{} turns to face you.", npc));
                        }
                    }
                    Some(response)
                }
            }
            _ => None,
        }
    }
}

impl BasicWorldSystem {
    fn help_text() -> String {
        [
            "Commands:",
            "  look / l                    Look around",
            "  inventory / i / inv         Show inventory",
            "  n/s/e/w/u/d                 Move in a direction",
            "  take <item>                 Pick up an item",
            "  drop <item>                 Drop an item",
            "  equip/wield/wear <item>     Equip a weapon or armor",
            "  unequip/remove <slot>       Unequip weapon or armor",
            "  use <item>                  Use/consume an item",
            "  examine / x <item>          Examine an item",
            "  attack / fight <monster>    Attack a monster",
            "  flee / run                  Attempt to flee combat",
            "  say / shout / yell <text>   Speak",
            "  status / stats              Show player status & XP",
            "  quests / journal            Show quest journal",
            "  accept <quest_id>           Accept a quest",
            "  complete <quest_id>         Complete a quest",
            "  help / ?                    Show this help",
        ].join("\n")
    }
}