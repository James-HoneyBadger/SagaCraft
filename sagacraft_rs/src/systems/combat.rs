use rand::Rng;
use crate::game_state::{AdventureGame, GameEvent, MonsterStatus};
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
        // Collect matching monster id first to avoid borrow conflicts
        let monster_id = game
            .get_monsters_in_room(game.player.current_room)
            .iter()
            .find(|m| m.name.to_lowercase().contains(&target_name.to_lowercase()))
            .map(|m| m.id);

        let Some(monster_id) = monster_id else {
            return Some(format!("There's no {} here to attack.", target_name));
        };

        // Don't allow attacking non-hostile NPCs
        if let Some(m) = game.monsters.get(&monster_id) {
            if m.friendliness != MonsterStatus::Hostile {
                return Some(format!(
                    "You can't bring yourself to attack the friendly {}.",
                    m.name
                ));
            }
        }

        // Determine player damage using equipped weapon, or unarmed fallback
        let player_damage = if let Some(weapon_id) = game.player.equipped_weapon {
            if let Some(weapon) = game.items.get(&weapon_id) {
                weapon.get_damage()
            } else {
                rand::thread_rng().gen_range(1..=4)
            }
        } else {
            let best = game.player.weapon_ability.values().copied().max().unwrap_or(1);
            rand::thread_rng().gen_range(1..=best.max(4))
        };

        let mut output = String::new();

        // Apply player's attack to monster
        if let Some(monster) = game.monsters.get_mut(&monster_id) {
            let health = monster.current_health.get_or_insert(monster.hardiness);
            *health -= player_damage;

            if *health <= 0 {
                monster.is_dead = true;
                let name = monster.name.clone();
                let room_id = monster.room_id;
                let gold = monster.gold;
                game.player.gold += gold;
                let mut msg = format!("You defeat the {}!", name);
                if gold > 0 {
                    msg.push_str(&format!(" (+{} gold)", gold));
                }
                game.events.push(GameEvent::MonsterKilled { monster_name: name, room_id });
                return Some(msg);
            } else {
                output.push_str(&format!(
                    "You attack the {} for {} damage. It has {} health remaining.",
                    monster.name, player_damage, health
                ));
            }
        } else {
            return Some(format!("There's no {} here to attack.", target_name));
        }

        // Monster counter-attack (if still alive)
        let counter = self.monster_counter_attack(game, monster_id);
        output.push('\n');
        output.push_str(&counter);

        Some(output)
    }

    fn monster_counter_attack(&self, game: &mut AdventureGame, monster_id: i32) -> String {
        let (monster_dmg, monster_name) = if let Some(m) = game.monsters.get(&monster_id) {
            // Simple damage: 1 to (agility / 3 + 1)
            let max_dmg = (m.agility / 3 + 1).max(2);
            let dmg = rand::thread_rng().gen_range(1..=max_dmg);
            (dmg, m.name.clone())
        } else {
            return String::new();
        };

        // Reduce by player armor
        let armor_reduction = if let Some(armor_id) = game.player.equipped_armor {
            game.items.get(&armor_id).map_or(0, |a| a.armor_value)
        } else {
            0
        };
        let net_damage = (monster_dmg - armor_reduction).max(0);

        // Apply damage and immediately copy the result so the mutable borrow ends
        // before we read game.player.hardiness (avoids split-borrow conflict).
        let current_hp = {
            let hp = game.player.current_health.get_or_insert(game.player.hardiness);
            *hp -= net_damage;
            *hp
        };

        if current_hp <= 0 {
            game.game_over = true;
            format!(
                "The {} strikes back for {} damage. You have been slain!",
                monster_name, net_damage
            )
        } else {
            format!(
                "The {} strikes back for {} damage. Your health: {}/{}.",
                monster_name, net_damage, current_hp, game.player.hardiness
            )
        }
    }

    fn show_status(&self, game: &AdventureGame) -> String {
        let weapon_name = game.player.equipped_weapon
            .and_then(|id| game.items.get(&id))
            .map(|w| w.name.as_str())
            .unwrap_or("none");
        let armor_name = game.player.equipped_armor
            .and_then(|id| game.items.get(&id))
            .map(|a| a.name.as_str())
            .unwrap_or("none");
        let (carry_cur, carry_max) = game.carry_weight();
        format!(
            "Player: {}\nHealth: {}/{}\nLevel: {}  XP: {}\nGold: {}\nWeapon: {}\nArmor: {}\nCarrying: {}/{} weight\nLocation: Room {}",
            game.player.name,
            game.player.current_health.unwrap_or(0),
            game.player.hardiness,
            game.player.level,
            game.player.experience_points,
            game.player.gold,
            weapon_name,
            armor_name,
            carry_cur, carry_max,
            game.player.current_room,
        )
    }
}
