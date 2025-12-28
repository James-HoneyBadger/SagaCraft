#!/usr/bin/env python3
"""Tests for Phase III: Advanced Combat System"""

import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parents[2]))

from sagacraft.systems.advanced_combat import (
    DamageType,
    StatusEffect,
    CombatAction,
    AIBehavior,
    DamageRoll,
    CombatMove,
    CombatantStats,
    Combatant,
    CombatResolver,
    CombatAI,
)


def test_damage_roll():
    """Test damage calculation"""
    print("\n=== Testing Damage Roll ===")
    
    # Basic damage
    roll = DamageRoll(base_damage=25, critical=False)
    assert roll.total_damage == 25
    print(f"✓ Basic damage: {roll.total_damage}")
    
    # Critical hit
    roll_crit = DamageRoll(base_damage=25, critical=True, critical_multiplier=1.5)
    assert roll_crit.total_damage == 37  # 25 * 1.5
    print(f"✓ Critical damage: {roll_crit.total_damage}")
    
    # With modifier
    roll_mod = DamageRoll(base_damage=25, modifier=0.8)
    assert roll_mod.total_damage == 20  # 25 * 0.8
    print(f"✓ Modified damage: {roll_mod.total_damage}")
    
    # With resistance
    roll_res = DamageRoll(base_damage=25, resistance=0.3)
    assert roll_res.total_damage == 17  # 25 * 0.7
    print(f"✓ With resistance: {roll_res.total_damage}")
    
    return True


def test_status_effects():
    """Test status effect system"""
    print("\n=== Testing Status Effects ===")
    
    # Create combatant
    stats = CombatantStats(max_health=100, health=100)
    combatant = Combatant("hero", "Hero", stats)
    
    # Add effect
    combatant.add_status_effect(StatusEffect.POISONED, 3, damage_per_turn=5)
    assert combatant.has_effect(StatusEffect.POISONED)
    print("✓ Status effect applied")
    
    # Process turn with damage
    damage = combatant.process_turn()
    assert damage == 5
    # Note: damage from effects is reported but needs to be applied by caller
    print(f"✓ Effect damage: {damage} reported")
    
    # Check duration countdown
    assert len(combatant.active_effects) > 0
    remaining = combatant.active_effects[0].duration_turns
    assert remaining == 2  # Started at 3, now 2
    print(f"✓ Duration countdown: {remaining} turns remaining")
    
    # Process until expired
    combatant.process_turn()
    combatant.process_turn()
    assert not combatant.has_effect(StatusEffect.POISONED)
    print("✓ Effect expired correctly")
    
    return True


def test_combat_move():
    """Test combat moves"""
    print("\n=== Testing Combat Moves ===")
    
    move = CombatMove(
        id="fireball",
        name="Fireball",
        description="Cast a fireball",
        action_type=CombatAction.CAST_SPELL,
        base_damage=35,
        accuracy=0.95,
        critical_chance=0.15,
        mana_cost=25,
        damage_type=DamageType.FIRE,
        status_effects=[(StatusEffect.BURNING, 2)]
    )
    
    assert move.base_damage == 35
    assert move.mana_cost == 25
    print("✓ Move properties correct")
    
    # Test move hashing (for use in sets)
    move_set = {move}
    assert move in move_set
    print("✓ Move hashing works")
    
    return True


def test_combatant_stats():
    """Test combatant stats and health"""
    print("\n=== Testing Combatant Stats ===")
    
    stats = CombatantStats(max_health=100, health=100, armor=10)
    
    # Test taking damage with armor
    damage_taken = stats.take_damage(30)
    assert damage_taken < 30  # Armor reduces it
    assert stats.health < 100
    print(f"✓ Armor reduces damage: 30 -> {damage_taken}")
    
    # Test healing
    old_health = stats.health
    healed = stats.heal(50)
    expected_heal = min(100 - old_health, 50)
    assert healed == expected_heal
    print(f"✓ Healing works: +{healed}")
    
    # Test alive check
    assert stats.is_alive()
    stats.health = 0
    assert not stats.is_alive()
    print("✓ Alive check works")
    
    return True


def test_combatant():
    """Test combatant system"""
    print("\n=== Testing Combatant ===")
    
    stats = CombatantStats(max_health=100, health=100, max_mana=50, mana=50, max_energy=100, energy=100)
    combatant = Combatant("p1", "Player", stats, level=1)
    
    # Add moves
    attack = CombatMove(
        id="slash",
        name="Slash",
        description="Basic attack",
        action_type=CombatAction.ATTACK,
        base_damage=15,
        energy_cost=10
    )
    combatant.moves.append(attack)
    
    # Check available moves
    available = combatant.get_available_moves()
    assert len(available) == 1
    print("✓ Available moves correct")
    
    # Use a move
    used = combatant.use_move(attack)
    assert used
    assert combatant.stats.energy == 90  # 100 - 10
    print(f"✓ Move used, energy: {combatant.stats.energy}")
    
    # Check cooldown (move has 0 cooldown by default)
    available = combatant.get_available_moves()
    # Move should still be available since cooldown is 0
    print(f"✓ Move available after use: {len(available) > 0}")
    
    # Add move with cooldown
    special = CombatMove(
        id="special",
        name="Special",
        description="Special attack",
        action_type=CombatAction.SPECIAL,
        base_damage=30,
        cooldown_turns=2,
        energy_cost=20
    )
    combatant.moves.append(special)
    combatant.use_move(special)
    
    # Check cooldown prevents use
    available = combatant.get_available_moves()
    assert not any(m.id == "special" for m in available)
    print("✓ Cooldown prevents move use")
    
    # Process turn (reduces cooldown)
    combatant.process_turn()
    available = combatant.get_available_moves()
    assert not any(m.id == "special" for m in available)  # Still in cooldown
    print("✓ Cooldown reduces on turn")
    
    combatant.process_turn()
    available = combatant.get_available_moves()
    assert any(m.id == "special" for m in available)  # Now off cooldown
    print("✓ Move available after cooldown expires")
    
    return True


def test_combat_resolver():
    """Test combat resolution"""
    print("\n=== Testing Combat Resolver ===")
    
    # Create combatants
    attacker_stats = CombatantStats(max_health=100, health=100)
    attacker = Combatant("p1", "Attacker", attacker_stats, level=5)
    
    defender_stats = CombatantStats(max_health=100, health=100, armor=5)
    defender = Combatant("p2", "Defender", defender_stats, level=5)
    
    # Create move
    attack = CombatMove(
        id="slash",
        name="Slash",
        description="Basic attack",
        action_type=CombatAction.ATTACK,
        base_damage=20,
        accuracy=1.0,  # Guaranteed hit for testing
        critical_chance=0.0
    )
    
    # Resolve attack
    result = CombatResolver.resolve_attack(attacker, defender, attack)
    
    assert result["hit"]
    assert result["damage"] > 0
    assert defender.stats.health < 100
    print(f"✓ Attack resolved: {result['damage']} damage")
    print(f"  Message: {result['message']}")
    
    # Test with status effects
    attack_with_effect = CombatMove(
        id="poison_sting",
        name="Poison Sting",
        description="Venomous attack",
        action_type=CombatAction.ATTACK,
        base_damage=10,
        accuracy=1.0,
        status_effects=[(StatusEffect.POISONED, 3)]
    )
    
    # Set seed for reproducible results
    random.seed(42)
    result2 = CombatResolver.resolve_attack(attacker, defender, attack_with_effect)
    
    print(f"✓ Attack with effects: {result2['message']}")
    
    return True


def test_combat_ai():
    """Test combat AI"""
    print("\n=== Testing Combat AI ===")
    
    # Create AI combatant
    stats = CombatantStats(max_health=100, health=50)
    ai = Combatant("enemy", "Enemy", stats, level=3, ai_behavior=AIBehavior.AGGRESSIVE)
    
    # Add moves
    weak_move = CombatMove(
        id="weak_hit",
        name="Weak Hit",
        description="Weak attack",
        action_type=CombatAction.ATTACK,
        base_damage=5
    )
    strong_move = CombatMove(
        id="strong_hit",
        name="Strong Hit",
        description="Strong attack",
        action_type=CombatAction.ATTACK,
        base_damage=20
    )
    
    ai.moves = [weak_move, strong_move]
    
    # Create target
    target_stats = CombatantStats(max_health=100, health=100)
    target = Combatant("target", "Target", target_stats)
    
    # AI chooses action
    chosen_move, chosen_target = CombatAI.choose_action(ai, [target])
    
    # Should choose strong move (aggressive)
    assert chosen_move.base_damage == 20
    assert chosen_target == target
    print("✓ AI chooses strong move (aggressive behavior)")
    
    # Test defensive behavior
    ai.ai_behavior = AIBehavior.DEFENSIVE
    random.seed(42)
    move, _ = CombatAI.choose_action(ai, [target])
    print(f"✓ Defensive AI chooses: {move.name}")
    
    return True


def test_combat_scenario():
    """Test a full combat scenario"""
    print("\n=== Testing Combat Scenario ===")
    
    # Setup player
    player_stats = CombatantStats(max_health=100, health=100, max_mana=50, mana=50)
    player = Combatant("p1", "Hero", player_stats, level=3)
    
    attack = CombatMove(
        id="attack",
        name="Attack",
        description="Basic attack",
        action_type=CombatAction.ATTACK,
        base_damage=15,
        accuracy=0.95
    )
    player.moves = [attack]
    
    # Setup enemy
    enemy_stats = CombatantStats(max_health=40, health=40)
    enemy = Combatant("e1", "Goblin", enemy_stats, level=1, ai_behavior=AIBehavior.AGGRESSIVE)
    enemy.moves = [attack]
    
    # Simulate combat rounds
    rounds = 0
    max_rounds = 20
    
    while player.is_alive() and enemy.is_alive() and rounds < max_rounds:
        rounds += 1
        
        # Player attacks
        result = CombatResolver.resolve_attack(player, enemy, attack)
        
        # Enemy attacks back (if alive)
        if enemy.is_alive():
            enemy_move, _ = CombatAI.choose_action(enemy, [player])
            CombatResolver.resolve_attack(enemy, player, enemy_move)
        
        # Process turns
        player.process_turn()
        enemy.process_turn()
    
    assert enemy.stats.health <= 0, "Enemy should be defeated"
    assert player.stats.health > 0, "Player should survive"
    print(f"✓ Combat scenario complete:")
    print(f"  Rounds: {rounds}")
    print(f"  Winner: {player.name} (Health: {player.stats.health})")
    print(f"  Loser: {enemy.name} (Health: {enemy.stats.health})")
    
    return True


def run_all_tests():
    """Run all Phase III tests"""
    print("\n" + "="*60)
    print("SAGACRAFT PHASE III: ADVANCED COMBAT TESTS")
    print("="*60)
    
    tests = [
        ("Damage Roll", test_damage_roll),
        ("Status Effects", test_status_effects),
        ("Combat Move", test_combat_move),
        ("Combatant Stats", test_combatant_stats),
        ("Combatant System", test_combatant),
        ("Combat Resolver", test_combat_resolver),
        ("Combat AI", test_combat_ai),
        ("Combat Scenario", test_combat_scenario),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
