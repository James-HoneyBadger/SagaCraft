#!/usr/bin/env python3
"""Tests for Phase II: Skill/Leveling/Class System"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from sagacraft.systems.progression import (
    CharacterClass,
    Attribute,
    Skill,
    SkillTree,
    ClassDefinition,
    CharacterAttributes,
    CharacterProgression,
    ProgressionSystem,
    get_experience_for_level,
    get_difficulty_multiplier,
)


def test_character_attributes():
    """Test character attributes"""
    print("\n=== Testing Character Attributes ===")
    
    attrs = CharacterAttributes(strength=12, intelligence=14)
    
    # Test retrieval
    assert attrs.get_attribute(Attribute.STRENGTH) == 12
    assert attrs.get_attribute(Attribute.INTELLIGENCE) == 14
    print("✓ Attribute retrieval works")
    
    # Test modification
    attrs.set_attribute(Attribute.WISDOM, 16)
    assert attrs.wisdom == 16
    print("✓ Attribute modification works")
    
    # Test serialization
    data = attrs.to_dict()
    assert data["strength"] == 12
    assert data["wisdom"] == 16
    print("✓ Serialization works")
    
    # Test deserialization
    attrs2 = CharacterAttributes.from_dict(data)
    assert attrs2.strength == attrs.strength
    assert attrs2.wisdom == attrs.wisdom
    print("✓ Deserialization works")
    
    return True


def test_character_progression():
    """Test character progression"""
    print("\n=== Testing Character Progression ===")
    
    prog = CharacterProgression()
    
    # Test initial state
    assert prog.level == 1
    assert prog.experience == 0
    assert prog.skill_points == 0
    print("✓ Initial state correct")
    
    # Test XP addition without level up
    prog.add_experience(100)
    assert prog.level == 1
    assert prog.experience == 100
    print("✓ Experience addition works")
    
    # Test level up
    initial_xp_needed = prog.experience_to_next_level
    prog.add_experience(initial_xp_needed)
    assert prog.level == 2
    assert prog.skill_points == 2
    print(f"✓ Level up works (now level {prog.level})")
    
    # Test experience scaling
    assert prog.experience_to_next_level > initial_xp_needed
    print(f"✓ Experience scaling: {initial_xp_needed} -> {prog.experience_to_next_level}")
    
    # Test skill learning
    prog.learned_skills.add("fireball")
    assert "fireball" in prog.learned_skills
    print("✓ Skill tracking works")
    
    # Test serialization
    data = prog.to_dict()
    assert data["level"] == 2
    assert "fireball" in data["learned_skills"]
    print("✓ Serialization works")
    
    # Test deserialization
    prog2 = CharacterProgression.from_dict(data)
    assert prog2.level == prog.level
    assert prog2.learned_skills == prog.learned_skills
    print("✓ Deserialization works")
    
    return True


def test_skill_system():
    """Test skill system"""
    print("\n=== Testing Skill System ===")
    
    # Create skills
    skill1 = Skill(
        id="fireball",
        name="Fireball",
        description="Launch a ball of fire",
        level_required=1,
        damage_bonus=25,
        critical_chance=0.1,
        mana_cost=30,
        category="magic"
    )
    
    skill2 = Skill(
        id="inferno",
        name="Inferno",
        description="Massive fire explosion",
        level_required=5,
        prerequisites=["fireball"],
        damage_bonus=50,
        critical_chance=0.2,
        mana_cost=60,
        category="magic"
    )
    
    # Create skill tree
    tree = SkillTree(
        name="Fire Mage",
        class_type=CharacterClass.MAGE
    )
    tree.add_skill(skill1)
    tree.add_skill(skill2)
    
    assert len(tree.skills) == 2
    print("✓ Skill tree creation works")
    
    # Test availability at level 1
    available = tree.get_available_skills(1, set())
    assert any(s.id == "fireball" for s in available)
    assert not any(s.id == "inferno" for s in available)  # Too high level
    print("✓ Level-based availability works")
    
    # Test prerequisite checking
    available = tree.get_available_skills(5, set())
    assert not any(s.id == "inferno" for s in available)  # Missing prerequisite
    
    available = tree.get_available_skills(5, {"fireball"})
    assert any(s.id == "inferno" for s in available)  # Prerequisite met
    print("✓ Prerequisite checking works")
    
    return True


def test_class_definitions():
    """Test class definitions"""
    print("\n=== Testing Class Definitions ===")
    
    warrior = ClassDefinition(
        class_type=CharacterClass.WARRIOR,
        description="Strong fighter",
        primary_attribute=Attribute.STRENGTH,
        attribute_bonuses={Attribute.STRENGTH: 3, Attribute.CONSTITUTION: 2},
        starting_health=150,
        starting_mana=25,
        starting_abilities=["slash", "block"]
    )
    
    # Test attribute bonuses
    assert warrior.get_attribute_bonus(Attribute.STRENGTH) == 3
    assert warrior.get_attribute_bonus(Attribute.CONSTITUTION) == 2
    assert warrior.get_attribute_bonus(Attribute.INTELLIGENCE) == 0
    print("✓ Attribute bonuses work")
    
    # Test serialization
    data = warrior.to_dict()
    assert data["class_type"] == "warrior"
    assert data["starting_health"] == 150
    assert "slash" in data["starting_abilities"]
    print("✓ Serialization works")
    
    return True


def test_progression_system():
    """Test the full progression system"""
    print("\n=== Testing Progression System ===")
    
    system = ProgressionSystem()
    
    # Test class definitions are registered
    assert len(system.class_definitions) == 5
    print(f"✓ {len(system.class_definitions)} classes registered")
    
    # Test getting a class
    warrior = system.get_class_definition(CharacterClass.WARRIOR)
    assert warrior is not None
    assert warrior.class_type == CharacterClass.WARRIOR
    print("✓ Class retrieval works")
    
    # Test character creation
    char_data = system.create_character("Aragorn", CharacterClass.WARRIOR)
    assert char_data is not None
    assert char_data["name"] == "Aragorn"
    assert char_data["class"] == "warrior"
    assert char_data["health"] == 150
    assert char_data["attributes"]["strength"] == 13  # 10 + 3 bonus
    print("✓ Character creation works")
    
    # Test mage creation with different starting values
    mage_data = system.create_character("Gandalf", CharacterClass.MAGE)
    assert mage_data["mana"] == 150
    assert mage_data["attributes"]["intelligence"] == 13  # 10 + 3 bonus
    print("✓ Class-specific attributes work")
    
    return True


def test_experience_scaling():
    """Test experience requirements and scaling"""
    print("\n=== Testing Experience Scaling ===")
    
    # Check experience requirement increases
    level1_xp = get_experience_for_level(1)
    level5_xp = get_experience_for_level(5)
    level10_xp = get_experience_for_level(10)
    
    assert level1_xp == 0
    assert level5_xp > level1_xp
    assert level10_xp > level5_xp
    print(f"✓ XP scaling: L1={level1_xp}, L5={level5_xp}, L10={level10_xp}")
    
    # Verify quadratic-ish growth
    ratio = level10_xp / level5_xp
    assert ratio > 1.5, "Level 10 should require significantly more XP than level 5"
    print(f"✓ Quadratic growth confirmed (ratio: {ratio:.2f}x)")
    
    return True


def test_difficulty_scaling():
    """Test difficulty multipliers"""
    print("\n=== Testing Difficulty Scaling ===")
    
    # Same level
    mult_same = get_difficulty_multiplier(5, 5)
    assert mult_same == 1.0
    print(f"✓ Same level: {mult_same}x")
    
    # Higher enemy
    mult_higher = get_difficulty_multiplier(5, 7)
    assert mult_higher > 1.0
    print(f"✓ Higher enemy: {mult_higher}x")
    
    # Lower enemy
    mult_lower = get_difficulty_multiplier(5, 3)
    assert mult_lower < 1.0
    print(f"✓ Lower enemy: {mult_lower}x")
    
    # Verify scaling is reasonable (should be approximately symmetric)
    ratio_up = mult_higher / mult_same
    ratio_down = mult_same / mult_lower
    assert abs(ratio_up - ratio_down) < 0.1, f"Ratios should be similar: {ratio_up} vs {ratio_down}"
    print(f"✓ Scaling is approximately symmetric (up: {ratio_up:.2f}x, down: {ratio_down:.2f}x)")
    
    return True


def run_all_tests():
    """Run all Phase II tests"""
    print("\n" + "="*60)
    print("SAGACRAFT PHASE II: PROGRESSION SYSTEM TESTS")
    print("="*60)
    
    tests = [
        ("Character Attributes", test_character_attributes),
        ("Character Progression", test_character_progression),
        ("Skill System", test_skill_system),
        ("Class Definitions", test_class_definitions),
        ("Progression System", test_progression_system),
        ("Experience Scaling", test_experience_scaling),
        ("Difficulty Scaling", test_difficulty_scaling),
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
