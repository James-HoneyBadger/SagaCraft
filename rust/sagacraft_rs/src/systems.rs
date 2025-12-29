use crate::command::{Command, Direction};
use crate::engine::{EngineEvent, EngineOutput};
use crate::game_state::GameState;

pub trait System {
    fn name(&self) -> &'static str;

    fn on_event(&mut self, state: &mut GameState, event: &EngineEvent) -> EngineOutput;
}

#[derive(Default)]
pub struct BasicWorldSystem;

impl System for BasicWorldSystem {
    fn name(&self) -> &'static str {
        "basic_world"
    }

    fn on_event(&mut self, state: &mut GameState, event: &EngineEvent) -> EngineOutput {
        let EngineEvent::Command(cmd) = event;

        match cmd {
            Command::Help => EngineOutput::lines([
                "Commands:",
                "  look | l", 
                "  north/south/east/west (or n/s/e/w)",
                "  go <direction>",
                "  take <item>",
                "  drop <item>",
                "  inv | i",
                "  quit",
            ]),

            Command::Look => {
                let room = state.current_room();
                let mut out = EngineOutput::new();
                out.push(format!("{}", room.title));
                out.push(room.description.clone());

                if !room.items.is_empty() {
                    out.push("You see:".to_string());
                    for item in &room.items {
                        out.push(format!("- {}", item.name));
                    }
                }

                if !room.exits.is_empty() {
                    let mut exits: Vec<_> = room.exits.keys().cloned().collect();
                    exits.sort();
                    out.push(format!("Exits: {}", exits.join(", ")));
                }

                out
            }

            Command::Move(dir) => {
                let direction_key = match dir {
                    Direction::North => "north",
                    Direction::South => "south",
                    Direction::East => "east",
                    Direction::West => "west",
                };

                let dest = {
                    let room = state.current_room();
                    room.exits.get(direction_key).cloned()
                };

                match dest {
                    Some(room_id) => {
                        state.player.location = room_id;
                        EngineOutput::line(format!("You travel {}.", dir))
                    }
                    None => EngineOutput::line("You can't go that way."),
                }
            }

            Command::Quit => {
                state.is_over = true;
                EngineOutput::line("Goodbye.")
            }

            Command::Unknown(raw) => EngineOutput::line(format!("I don't understand: {raw}")),

            _ => EngineOutput::none(),
        }
    }
}

#[derive(Default)]
pub struct InventorySystem;

impl System for InventorySystem {
    fn name(&self) -> &'static str {
        "inventory"
    }

    fn on_event(&mut self, state: &mut GameState, event: &EngineEvent) -> EngineOutput {
        let EngineEvent::Command(cmd) = event;

        match cmd {
            Command::Inventory => {
                if state.player.inventory.is_empty() {
                    return EngineOutput::line("Your inventory is empty.");
                }

                let mut out = EngineOutput::new();
                out.push("You are carrying:".to_string());
                for item in &state.player.inventory {
                    out.push(format!("- {}", item.name));
                }
                out
            }

            Command::Take(name) => {
                let item = state.current_room_mut().remove_item_named(name);
                match item {
                    Some(i) => {
                        state.player.inventory.push(i.clone());
                        EngineOutput::line(format!("You take the {}.", i.name))
                    }
                    None => EngineOutput::line("You don't see that here."),
                }
            }

            Command::Drop(name) => {
                let idx = state
                    .player
                    .inventory
                    .iter()
                    .position(|i| i.name.eq_ignore_ascii_case(name));

                match idx {
                    Some(i) => {
                        let item = state.player.inventory.remove(i);
                        state.current_room_mut().add_item(item.clone());
                        EngineOutput::line(format!("You drop the {}.", item.name))
                    }
                    None => EngineOutput::line("You aren't carrying that."),
                }
            }

            _ => EngineOutput::none(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::engine::{Engine, EngineEvent};

    #[test]
    fn look_prints_room_title() {
        let mut engine = Engine::new("Tester");
        let out = engine.step(EngineEvent::Command(Command::Look));
        assert!(out.lines.iter().any(|l| l.contains("Quiet Village")));
    }

    #[test]
    fn take_moves_item_to_inventory() {
        let mut engine = Engine::new("Tester");
        let out = engine.step(EngineEvent::Command(Command::Take("Ancient Key".to_string())));
        assert!(out.lines.iter().any(|l| l.contains("You take")));
        assert!(engine.state.player.has_item_named("Ancient Key"));
    }
}
