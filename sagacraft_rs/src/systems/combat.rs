use crate::game_state::AdventureGame;
use crate::systems::System;

#[derive(Debug, Default)]
pub struct CombatSystem;

impl System for CombatSystem {
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String> {
        match command {
            "attack" | "fight" => {
                if let Some(target) = args.first() {
                    self.attack_monster(game, target)
                } else {
                    Some("Attack what?".to_string())
                }
            }
            "status" | "stats" => {
                Some(self.show_status(game))
            }
            _ => None,
        }
    }
}

impl CombatSystem {
    fn attack_monster(&self, game: &mut AdventureGame, target_name: &str) -> Option<String> {
        let monsters = game.get_monsters_in_room(game.player.current_room);
        for monster in monsters {
            if monster.name.to_lowercase().contains(&target_name.to_lowercase()) {
                // Simple combat: player attacks monster
                let damage = game.player.weapon_ability[&1]; // Assume sword
                let mut monster = monster.clone();
                if let Some(ref mut health) = monster.current_health {
                    *health -= damage;
                    if *health <= 0 {
                        monster.is_dead = true;
                        // Update in game
                        if let Some(m) = game.monsters.get_mut(&monster.id) {
                            m.is_dead = true;
                        }
                        return Some(format!("You defeat the {}!", monster.name));
                    } else {
                        return Some(format!("You attack the {} for {} damage. It has {} health left.", monster.name, damage, health));
                    }
                }
            }
        }
        Some(format!("There's no {} here to attack.", target_name))
    }

    fn show_status(&self, game: &mut AdventureGame) -> String {
        format!("Player: {}\nHealth: {}/{}\nGold: {}\nLocation: Room {}",
            game.player.name,
            game.player.current_health.unwrap_or(0),
            game.player.hardiness,
            game.player.gold,
            game.player.current_room
        )
    }
}