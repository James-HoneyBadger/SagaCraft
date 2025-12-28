#!/usr/bin/env python3
"""SagaCraft - Advanced Combat System (Phase III)

Implements tactical combat with special moves, status effects, and dynamic AI.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
import random
from datetime import datetime, timedelta


class DamageType(Enum):
    """Types of damage"""
    PHYSICAL = "physical"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    SHADOW = "shadow"


class StatusEffect(Enum):
    """Status effects that can be applied"""
    POISONED = "poisoned"
    BURNING = "burning"
    FROZEN = "frozen"
    STUNNED = "stunned"
    SHOCKED = "shocked"
    BLESSED = "blessed"
    CURSED = "cursed"
    BLEEDING = "bleeding"


class CombatAction(Enum):
    """Types of combat actions"""
    ATTACK = "attack"
    SPECIAL = "special"
    DEFEND = "defend"
    CAST_SPELL = "cast_spell"
    USE_ITEM = "use_item"
    RETREAT = "retreat"


class AIBehavior(Enum):
    """AI behaviors for enemies"""
    AGGRESSIVE = "aggressive"      # Always attack
    DEFENSIVE = "defensive"        # Defend/heal often
    TACTICAL = "tactical"          # Balanced approach
    HEALER = "healer"              # Support allies
    RANGED = "ranged"              # Stay at distance


@dataclass
class DamageRoll:
    """Result of a damage calculation"""
    base_damage: int
    critical: bool = False
    critical_multiplier: float = 1.5
    modifier: float = 1.0
    resistance: float = 0.0
    
    @property
    def total_damage(self) -> int:
        """Calculate total damage"""
        damage = self.base_damage * self.modifier
        
        if self.critical:
            damage *= self.critical_multiplier
        
        # Apply resistance (reduce damage)
        damage *= (1.0 - self.resistance)
        
        return max(1, int(damage))  # Minimum 1 damage


@dataclass
class StatusEffectInstance:
    """An active status effect on a character"""
    effect: StatusEffect
    duration_turns: int
    damage_per_turn: int = 0
    applied_time: datetime = field(default_factory=datetime.now)
    
    def is_active(self) -> bool:
        """Check if effect is still active"""
        return self.duration_turns > 0
    
    def process_turn(self) -> int:
        """Process one turn of the effect, return damage dealt"""
        self.duration_turns -= 1
        return self.damage_per_turn if self.is_active() else 0


@dataclass
class CombatMove:
    """A special combat move/ability"""
    id: str
    name: str
    description: str
    action_type: CombatAction
    base_damage: int = 0
    accuracy: float = 1.0  # 0-1
    critical_chance: float = 0.1  # 0-1
    cooldown_turns: int = 0
    energy_cost: int = 0
    mana_cost: int = 0
    damage_type: DamageType = DamageType.PHYSICAL
    status_effects: List[Tuple[StatusEffect, int]] = field(default_factory=list)  # (effect, duration)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, CombatMove) and self.id == other.id


@dataclass
class CombatantStats:
    """Stats for a combatant"""
    max_health: int = 100
    health: int = 100
    max_mana: int = 50
    mana: int = 50
    max_energy: int = 100
    energy: int = 100
    armor: int = 0  # Reduces physical damage
    magic_resistance: float = 0.0  # 0-1
    fire_resistance: float = 0.0
    cold_resistance: float = 0.0
    poison_resistance: float = 0.0
    accuracy_bonus: float = 0.0
    critical_chance_bonus: float = 0.0
    
    def take_damage(self, damage: int) -> int:
        """
        Take damage, applying armor
        
        Returns: Actual damage taken
        """
        # Armor reduces damage
        actual_damage = max(1, damage - self.armor // 5)
        self.health -= actual_damage
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal and return amount actually healed"""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health
    
    def is_alive(self) -> bool:
        """Check if still alive"""
        return self.health > 0


@dataclass
class Combatant:
    """A character in combat"""
    id: str
    name: str
    stats: CombatantStats
    level: int = 1
    moves: List[CombatMove] = field(default_factory=list)
    active_effects: List[StatusEffectInstance] = field(default_factory=list)
    move_cooldowns: Dict[str, int] = field(default_factory=dict)
    ai_behavior: AIBehavior = AIBehavior.AGGRESSIVE
    
    def get_available_moves(self) -> List[CombatMove]:
        """Get moves that are ready to use"""
        available = []
        for move in self.moves:
            # Check if off cooldown
            if self.move_cooldowns.get(move.id, 0) == 0:
                # Check resource costs
                if move.energy_cost <= self.stats.energy:
                    if move.mana_cost <= self.stats.mana:
                        available.append(move)
        return available
    
    def use_move(self, move: CombatMove) -> bool:
        """
        Attempt to use a move
        
        Returns: True if successful
        """
        if move not in self.get_available_moves():
            return False
        
        self.stats.energy -= move.energy_cost
        self.stats.mana -= move.mana_cost
        self.move_cooldowns[move.id] = move.cooldown_turns
        return True
    
    def add_status_effect(self, effect: StatusEffect, duration: int, damage_per_turn: int = 0) -> None:
        """Add a status effect"""
        instance = StatusEffectInstance(effect, duration, damage_per_turn)
        self.active_effects.append(instance)
    
    def remove_effect(self, effect: StatusEffect) -> None:
        """Remove a status effect"""
        self.active_effects = [e for e in self.active_effects if e.effect != effect]
    
    def has_effect(self, effect: StatusEffect) -> bool:
        """Check if has a status effect"""
        return any(e.effect == effect for e in self.active_effects)
    
    def process_turn(self) -> int:
        """
        Process end of turn (damage from effects, cooldown reduction)
        
        Returns: Damage taken from effects
        """
        total_damage = 0
        
        # Process status effects
        effects_to_remove = []
        for effect in self.active_effects:
            damage = effect.process_turn()
            total_damage += damage
            if not effect.is_active():
                effects_to_remove.append(effect)
        
        # Remove expired effects
        for effect in effects_to_remove:
            self.active_effects.remove(effect)
        
        # Reduce cooldowns
        for move_id in self.move_cooldowns:
            self.move_cooldowns[move_id] = max(0, self.move_cooldowns[move_id] - 1)
        
        # Natural energy regeneration
        self.stats.energy = min(self.stats.max_energy, self.stats.energy + 10)
        
        # Natural mana regeneration
        self.stats.mana = min(self.stats.max_mana, self.stats.mana + 5)
        
        return total_damage
    
    def is_alive(self) -> bool:
        """Check if combatant is alive"""
        return self.stats.is_alive()
    
    def is_stunned(self) -> bool:
        """Check if stunned"""
        return self.has_effect(StatusEffect.STUNNED)


class CombatResolver:
    """Resolves combat interactions"""
    
    @staticmethod
    def calculate_hit_chance(attacker: Combatant, defender: Combatant, move: CombatMove) -> float:
        """Calculate hit chance (0-1)"""
        base_accuracy = move.accuracy
        attacker_bonus = 1.0 + (attacker.stats.accuracy_bonus / 100.0)
        
        # Chance to miss reduces accuracy
        dodge_chance = 0.1 + (defender.level * 0.02)  # Higher level = better dodge
        
        return min(1.0, base_accuracy * attacker_bonus * (1.0 - dodge_chance))
    
    @staticmethod
    def calculate_critical_chance(attacker: Combatant, defender: Combatant, move: CombatMove) -> float:
        """Calculate critical hit chance"""
        base_crit = move.critical_chance
        attacker_bonus = attacker.stats.critical_chance_bonus / 100.0
        level_bonus = (attacker.level - defender.level) * 0.01
        
        return min(0.75, base_crit + attacker_bonus + level_bonus)
    
    @staticmethod
    def resolve_attack(
        attacker: Combatant,
        defender: Combatant,
        move: CombatMove
    ) -> Dict:
        """
        Resolve a combat move
        
        Returns: Combat result dictionary
        """
        result = {
            "attacker": attacker.name,
            "defender": defender.name,
            "move": move.name,
            "hit": False,
            "damage": 0,
            "critical": False,
            "effects_applied": [],
            "message": ""
        }
        
        # Check hit chance
        if random.random() > CombatResolver.calculate_hit_chance(attacker, defender, move):
            result["message"] = f"{attacker.name}'s attack missed!"
            return result
        
        result["hit"] = True
        
        # Check for critical hit
        is_critical = random.random() < CombatResolver.calculate_critical_chance(attacker, defender, move)
        result["critical"] = is_critical
        
        # Calculate damage
        base_damage = move.base_damage + (attacker.level // 2)
        roll = DamageRoll(
            base_damage=base_damage,
            critical=is_critical,
            critical_multiplier=1.5
        )
        
        # Apply resistances based on damage type
        if move.damage_type == DamageType.FIRE:
            roll.resistance = defender.stats.fire_resistance
        elif move.damage_type == DamageType.COLD:
            roll.resistance = defender.stats.cold_resistance
        elif move.damage_type == DamageType.POISON:
            roll.resistance = defender.stats.poison_resistance
        else:
            roll.resistance = defender.stats.magic_resistance
        
        actual_damage = defender.stats.take_damage(roll.total_damage)
        result["damage"] = actual_damage
        
        # Apply status effects
        for effect, duration in move.status_effects:
            if random.random() < 0.6:  # 60% chance to apply
                defender.add_status_effect(effect, duration)
                result["effects_applied"].append(f"{effect.value}")
        
        # Generate message
        crit_text = " CRITICAL HIT!" if is_critical else ""
        result["message"] = f"{attacker.name} used {move.name} against {defender.name} for {actual_damage} damage!{crit_text}"
        
        return result


class CombatAI:
    """AI decision making for combat"""
    
    @staticmethod
    def choose_action(combatant: Combatant, enemies: List[Combatant]) -> Tuple[CombatMove, Combatant]:
        """
        AI chooses an action
        
        Returns: (Move to use, Target combatant)
        """
        available_moves = combatant.get_available_moves()
        
        if not available_moves:
            # Default attack if no moves available
            default_move = CombatMove(
                id="basic_attack",
                name="Basic Attack",
                description="A basic attack",
                action_type=CombatAction.ATTACK,
                base_damage=10
            )
            target = min(enemies, key=lambda e: e.stats.health)
            return default_move, target
        
        # Choose move based on behavior
        if combatant.ai_behavior == AIBehavior.AGGRESSIVE:
            move = max(available_moves, key=lambda m: m.base_damage)
        elif combatant.ai_behavior == AIBehavior.DEFENSIVE:
            move = random.choice(available_moves)
        elif combatant.ai_behavior == AIBehavior.TACTICAL:
            # Prioritize high-damage moves but consider situation
            move = random.choices(
                available_moves,
                weights=[m.base_damage for m in available_moves],
                k=1
            )[0]
        else:
            move = random.choice(available_moves)
        
        # Choose target
        target = min(enemies, key=lambda e: e.stats.health)  # Target weakest enemy
        
        return move, target


__all__ = [
    "DamageType",
    "StatusEffect",
    "CombatAction",
    "AIBehavior",
    "DamageRoll",
    "StatusEffectInstance",
    "CombatMove",
    "CombatantStats",
    "Combatant",
    "CombatResolver",
    "CombatAI",
]
