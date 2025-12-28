"""
Phase VII: Enhanced Social & Party Features - Test Suite

Comprehensive tests for companion system, bonding, and party mechanics.
Tests cover:
- Companion creation and management
- Experience and leveling
- Bonding tier progression
- Party composition and formations
- Synergy calculations
- Damage/defense bonuses
"""

import sys
sys.path.insert(0, '/home/james/SagaCraft/src')

from sagacraft.systems.companions import (
    CompanionClass, CompanionStance, CompanionPersonality,
    Companion, BondingTier, BondingSystem,
    PartyFormation, PartySlot, PartyComposition,
    CompanionRecruiter, SynergyCalculator
)


def test_companion_creation():
    """Test basic companion creation."""
    companion = Companion(
        name="Thorne",
        title="Thorne the Ranger",
        companion_class=CompanionClass.RANGER,
        personality=CompanionPersonality.WILD
    )
    assert companion.name == "Thorne"
    assert companion.level == 1
    assert companion.hp == 100
    assert companion.is_recruited == False
    print("✓ Companion Creation")


def test_companion_experience():
    """Test companion experience and leveling."""
    companion = Companion(
        name="Aria",
        title="Aria the Mage",
        companion_class=CompanionClass.MAGE,
        personality=CompanionPersonality.MYSTICAL
    )
    
    levels_gained = companion.gain_experience(150)
    assert levels_gained == 1
    assert companion.level == 2
    assert companion.hp == 105
    assert companion.max_hp == 105
    
    levels_gained = companion.gain_experience(50)
    assert levels_gained == 0
    assert companion.level == 2
    print("✓ Companion Experience")


def test_companion_health():
    """Test companion health management."""
    companion = Companion(
        name="Kael",
        title="Kael the Fighter",
        companion_class=CompanionClass.FIGHTER,
        personality=CompanionPersonality.VALIANT
    )
    
    healing = companion.heal(30)
    assert healing == 0  # Already at full health
    
    companion.take_damage(50)
    assert companion.hp == 50
    
    healing = companion.heal(30)
    assert healing == 30
    assert companion.hp == 80
    
    damage = companion.take_damage(100)
    assert damage == 80
    assert companion.hp == 0
    assert not companion.is_alive()
    print("✓ Companion Health")


def test_companion_damage_bonus():
    """Test damage bonus calculations by class."""
    fighter = Companion(
        name="Fighter",
        title="Fighter",
        companion_class=CompanionClass.FIGHTER,
        personality=CompanionPersonality.VALIANT,
        attributes={"strength": 15, "dexterity": 10, "intelligence": 10, 
                   "constitution": 12, "wisdom": 10, "charisma": 10}
    )
    assert fighter.get_damage_bonus() == 5
    
    mage = Companion(
        name="Mage",
        title="Mage",
        companion_class=CompanionClass.MAGE,
        personality=CompanionPersonality.MYSTICAL,
        attributes={"strength": 8, "dexterity": 10, "intelligence": 16,
                   "constitution": 10, "wisdom": 12, "charisma": 10}
    )
    assert mage.get_damage_bonus() == 6
    print("✓ Companion Damage Bonus")


def test_companion_defense_bonus():
    """Test defense bonus calculations by class."""
    fighter = Companion(
        name="Fighter",
        title="Fighter",
        companion_class=CompanionClass.FIGHTER,
        personality=CompanionPersonality.VALIANT,
        attributes={"strength": 12, "dexterity": 10, "intelligence": 10,
                   "constitution": 14, "wisdom": 10, "charisma": 10}
    )
    assert fighter.get_defense_bonus() == 4
    
    rogue = Companion(
        name="Rogue",
        title="Rogue",
        companion_class=CompanionClass.ROGUE,
        personality=CompanionPersonality.CUNNING,
        attributes={"strength": 10, "dexterity": 14, "intelligence": 12,
                   "constitution": 10, "wisdom": 10, "charisma": 10}
    )
    assert rogue.get_defense_bonus() == 4
    print("✓ Companion Defense Bonus")


def test_memorable_moments():
    """Test memorable moments tracking."""
    companion = Companion(
        name="Lyria",
        title="Lyria the Cleric",
        companion_class=CompanionClass.CLERIC,
        personality=CompanionPersonality.LOYAL
    )
    
    companion.add_memorable_moment("First Meeting", "Met in tavern")
    companion.add_memorable_moment("Victory", "Defeated boss together")
    
    assert len(companion.memorable_moments) == 2
    assert "First Meeting" in companion.memorable_moments[0][0]
    print("✓ Memorable Moments")


def test_bonding_system_modification():
    """Test bonding points modification."""
    bonding = BondingSystem()
    
    points, tier = bonding.modify_bonding("Thorne", 50)
    assert points == 50
    assert tier == BondingTier.FRIEND
    
    points, tier = bonding.modify_bonding("Thorne", 75)
    assert points == 125
    assert tier == BondingTier.CLOSE_FRIEND
    print("✓ Bonding Modification")


def test_bonding_tier_progression():
    """Test all bonding tier transitions."""
    bonding = BondingSystem()
    
    # Stranger (< -100)
    bonding.modify_bonding("Companion", -150)
    tier = bonding.get_bonding_tier("Companion")
    assert tier == BondingTier.STRANGER
    
    # Acquaintance (-100 to 0)
    bonding2 = BondingSystem()
    bonding2.modify_bonding("Companion", -50)
    tier = bonding2.get_bonding_tier("Companion")
    assert tier == BondingTier.ACQUAINTANCE
    
    # Friend (0 to 75)
    bonding3 = BondingSystem()
    bonding3.modify_bonding("Companion", 50)
    tier = bonding3.get_bonding_tier("Companion")
    assert tier == BondingTier.FRIEND
    
    # Close Friend (75 to 150)
    bonding4 = BondingSystem()
    bonding4.modify_bonding("Companion", 100)
    tier = bonding4.get_bonding_tier("Companion")
    assert tier == BondingTier.CLOSE_FRIEND
    
    # Soulbound (150+)
    bonding5 = BondingSystem()
    bonding5.modify_bonding("Companion", 200)
    tier = bonding5.get_bonding_tier("Companion")
    assert tier == BondingTier.SOULBOUND
    print("✓ Bonding Tier Progression")


def test_bonding_clamping():
    """Test bonding points clamping."""
    bonding = BondingSystem()
    
    points, tier = bonding.modify_bonding("Companion", 300)
    assert points == 250  # Clamped to max
    
    points, tier = bonding.modify_bonding("Companion", -600)
    assert points == -250  # Clamped to min
    print("✓ Bonding Clamping")


def test_bonding_tier_unlocks():
    """Test ability/storyline unlocks at each tier."""
    bonding = BondingSystem()
    
    bonding.modify_bonding("Companion", 50)  # Friend tier
    assert "basic_combo" in bonding.unlocked_abilities.get("Companion", set())
    assert "backstory" in bonding.unlocked_storylines.get("Companion", set())
    
    bonding.modify_bonding("Companion", 50)  # Close Friend tier
    assert "special_attack" in bonding.unlocked_abilities.get("Companion", set())
    assert "personal_quest" in bonding.unlocked_storylines.get("Companion", set())
    
    bonding.modify_bonding("Companion", 100)  # Soulbound tier
    assert "ultimate_ability" in bonding.unlocked_abilities.get("Companion", set())
    assert "soulbound_ending" in bonding.unlocked_storylines.get("Companion", set())
    print("✓ Bonding Tier Unlocks")


def test_bonding_percentage():
    """Test bonding percentage calculation."""
    bonding = BondingSystem()
    
    bonding.modify_bonding("Companion", 0)
    assert bonding.get_bonding_percentage("Companion") == 50
    
    bonding.modify_bonding("Companion", 250)
    assert bonding.get_bonding_percentage("Companion") == 100
    
    bonding.modify_bonding("Companion", -500)
    assert bonding.get_bonding_percentage("Companion") == 0
    print("✓ Bonding Percentage")


def test_party_slot_assignment():
    """Test party slot assignment."""
    companion = Companion(
        name="Thorne",
        title="Thorne",
        companion_class=CompanionClass.RANGER,
        personality=CompanionPersonality.WILD
    )
    
    slot = PartySlot("front_left")
    assert slot.companion is None
    
    slot.assign_companion(companion, CompanionStance.AGGRESSIVE)
    assert slot.companion == companion
    assert companion.is_active
    assert slot.stance == CompanionStance.AGGRESSIVE
    
    slot.clear()
    assert slot.companion is None
    assert not companion.is_active
    print("✓ Party Slot Assignment")


def test_party_composition_creation():
    """Test party composition creation."""
    party = PartyComposition("Adventurers", PartyFormation.BALANCED)
    
    assert party.party_name == "Adventurers"
    assert party.formation == PartyFormation.BALANCED
    assert len(party.slots) == 5
    assert party.get_active_count() == 0
    assert not party.is_full()
    print("✓ Party Composition Creation")


def test_party_add_remove_companions():
    """Test adding and removing companions from party."""
    party = PartyComposition("Heroes", PartyFormation.BALANCED)
    
    thorne = Companion("Thorne", "Thorne", CompanionClass.RANGER, CompanionPersonality.WILD)
    aria = Companion("Aria", "Aria", CompanionClass.MAGE, CompanionPersonality.MYSTICAL)
    kael = Companion("Kael", "Kael", CompanionClass.FIGHTER, CompanionPersonality.VALIANT)
    
    assert party.add_to_party(thorne, "front_left")
    assert party.add_to_party(aria, "back_left")
    assert party.add_to_party(kael, "back_right")
    
    assert party.get_active_count() == 3
    assert party.is_full()
    
    removed = party.remove_from_party("front_left")
    assert removed == thorne
    assert party.get_active_count() == 2
    assert not thorne.is_active
    print("✓ Party Add/Remove Companions")


def test_party_change_stance():
    """Test changing companion stance."""
    party = PartyComposition("Heroes", PartyFormation.AGGRESSIVE)
    companion = Companion("Thorne", "Thorne", CompanionClass.RANGER, CompanionPersonality.WILD)
    
    party.add_to_party(companion, "front_left")
    assert party.slots["front_left"].stance == CompanionStance.AGGRESSIVE
    
    assert party.change_stance("front_left", CompanionStance.DEFENSIVE)
    assert party.slots["front_left"].stance == CompanionStance.DEFENSIVE
    print("✓ Party Change Stance")


def test_party_formation_changes():
    """Test party formation changes."""
    party = PartyComposition("Heroes", PartyFormation.AGGRESSIVE)
    
    assert party.get_formation_bonus() == 15
    
    party.change_formation(PartyFormation.DEFENSIVE)
    assert party.get_formation_bonus() == -5
    
    party.change_formation(PartyFormation.BALANCED)
    assert party.get_formation_bonus() == 10
    print("✓ Party Formation Changes")


def test_party_formation_bonuses():
    """Test all formation bonuses."""
    formations = {
        PartyFormation.FRONTLINE: 5,
        PartyFormation.BALANCED: 10,
        PartyFormation.AGGRESSIVE: 15,
        PartyFormation.DEFENSIVE: -5,
        PartyFormation.SUPPORT: 0,
    }
    
    for formation, expected_bonus in formations.items():
        party = PartyComposition("Test", formation)
        assert party.get_formation_bonus() == expected_bonus
    
    print("✓ Party Formation Bonuses")


def test_companion_recruiter_recruitment():
    """Test recruiting companions."""
    recruiter = CompanionRecruiter()
    companion = Companion("Thorne", "Thorne", CompanionClass.RANGER, CompanionPersonality.WILD)
    
    assert recruiter.recruit_companion(companion)
    assert companion.is_recruited
    assert recruiter.recruited_count == 1
    
    # Can't recruit same companion twice
    assert not recruiter.recruit_companion(companion)
    
    # Can retrieve by name
    retrieved = recruiter.get_companion("Thorne")
    assert retrieved == companion
    print("✓ Companion Recruiter Recruitment")


def test_companion_recruiter_release():
    """Test releasing companions."""
    recruiter = CompanionRecruiter()
    companion = Companion("Thorne", "Thorne", CompanionClass.RANGER, CompanionPersonality.WILD)
    
    recruiter.recruit_companion(companion)
    assert recruiter.get_companion("Thorne") is not None
    
    assert recruiter.release_companion("Thorne")
    assert recruiter.get_companion("Thorne") is None
    assert not companion.is_recruited
    print("✓ Companion Recruiter Release")


def test_companion_recruiter_party_creation():
    """Test creating parties through recruiter."""
    recruiter = CompanionRecruiter()
    
    party = recruiter.create_party("Heroes", PartyFormation.BALANCED)
    assert recruiter.active_party == party
    assert recruiter.get_active_party() == party
    print("✓ Companion Recruiter Party Creation")


def test_synergy_fighter_rogue():
    """Test Fighter + Rogue synergy."""
    party = PartyComposition("Heroes", PartyFormation.BALANCED)
    fighter = Companion("Fighter", "Fighter", CompanionClass.FIGHTER, CompanionPersonality.VALIANT)
    rogue = Companion("Rogue", "Rogue", CompanionClass.ROGUE, CompanionPersonality.CUNNING)
    
    party.add_to_party(fighter, "front_left")
    party.add_to_party(rogue, "back_left")
    
    bonus = SynergyCalculator.calculate_synergy(party)
    assert bonus >= 5
    print("✓ Synergy Fighter + Rogue")


def test_synergy_mage_cleric():
    """Test Mage + Cleric synergy."""
    party = PartyComposition("Heroes", PartyFormation.SUPPORT)
    mage = Companion("Mage", "Mage", CompanionClass.MAGE, CompanionPersonality.MYSTICAL)
    cleric = Companion("Cleric", "Cleric", CompanionClass.CLERIC, CompanionPersonality.LOYAL)
    
    party.add_to_party(mage, "back_left")
    party.add_to_party(cleric, "back_right")
    
    bonus = SynergyCalculator.calculate_synergy(party)
    assert bonus >= 10
    print("✓ Synergy Mage + Cleric")


def test_synergy_all_different():
    """Test synergy with all different classes."""
    party = PartyComposition("Heroes", PartyFormation.BALANCED)
    fighter = Companion("Fighter", "Fighter", CompanionClass.FIGHTER, CompanionPersonality.VALIANT)
    rogue = Companion("Rogue", "Rogue", CompanionClass.ROGUE, CompanionPersonality.CUNNING)
    mage = Companion("Mage", "Mage", CompanionClass.MAGE, CompanionPersonality.MYSTICAL)
    
    party.add_to_party(fighter, "front_left")
    party.add_to_party(rogue, "back_left")
    party.add_to_party(mage, "back_right")
    
    bonus = SynergyCalculator.calculate_synergy(party)
    assert bonus >= 5  # Diversity bonus at minimum
    print("✓ Synergy All Different Classes")


def test_synergy_class_pair():
    """Test synergy calculation for specific class pairs."""
    bonus = SynergyCalculator.get_class_pair_bonus(CompanionClass.FIGHTER, CompanionClass.ROGUE)
    assert bonus == 5
    
    bonus = SynergyCalculator.get_class_pair_bonus(CompanionClass.MAGE, CompanionClass.CLERIC)
    assert bonus == 10
    
    bonus = SynergyCalculator.get_class_pair_bonus(CompanionClass.FIGHTER, CompanionClass.PALADIN)
    assert bonus == 15
    print("✓ Synergy Class Pairs")


def test_synergy_single_companion():
    """Test synergy with single companion (no bonus)."""
    party = PartyComposition("Solo", PartyFormation.AGGRESSIVE)
    companion = Companion("Thorne", "Thorne", CompanionClass.RANGER, CompanionPersonality.WILD)
    
    party.add_to_party(companion, "front_left")
    
    bonus = SynergyCalculator.calculate_synergy(party)
    assert bonus == 0  # No synergy with single companion
    print("✓ Synergy Single Companion")


def test_full_workflow():
    """Test complete game workflow."""
    # Create recruiter
    recruiter = CompanionRecruiter()
    
    # Create companions
    thorne = Companion("Thorne", "Thorne the Ranger", CompanionClass.RANGER, CompanionPersonality.WILD)
    aria = Companion("Aria", "Aria the Mage", CompanionClass.MAGE, CompanionPersonality.MYSTICAL)
    kael = Companion("Kael", "Kael the Fighter", CompanionClass.FIGHTER, CompanionPersonality.VALIANT)
    
    # Recruit all
    assert recruiter.recruit_companion(thorne)
    assert recruiter.recruit_companion(aria)
    assert recruiter.recruit_companion(kael)
    assert recruiter.recruited_count == 3
    
    # Create party
    party = recruiter.create_party("Hero Party", PartyFormation.BALANCED)
    assert party.add_to_party(thorne, "front_left")
    assert party.add_to_party(aria, "back_left")
    assert party.add_to_party(kael, "back_right")
    
    # Bond with companions
    recruiter.bonding_system.modify_bonding("Thorne", 50)
    recruiter.bonding_system.modify_bonding("Aria", 100)
    
    # Level up
    thorne.gain_experience(200)
    aria.gain_experience(300)
    
    # Check state
    assert thorne.level == 2
    assert aria.level == 3
    assert recruiter.bonding_system.get_bonding_tier("Thorne") == BondingTier.FRIEND
    assert recruiter.bonding_system.get_bonding_tier("Aria") == BondingTier.CLOSE_FRIEND
    
    print("✓ Full Workflow")


def run_all_tests():
    """Run all Phase VII tests."""
    print("\n" + "="*70)
    print("PHASE VII: ENHANCED SOCIAL & PARTY FEATURES - TEST SUITE")
    print("="*70 + "\n")
    
    tests = [
        test_companion_creation,
        test_companion_experience,
        test_companion_health,
        test_companion_damage_bonus,
        test_companion_defense_bonus,
        test_memorable_moments,
        test_bonding_system_modification,
        test_bonding_tier_progression,
        test_bonding_clamping,
        test_bonding_tier_unlocks,
        test_bonding_percentage,
        test_party_slot_assignment,
        test_party_composition_creation,
        test_party_add_remove_companions,
        test_party_change_stance,
        test_party_formation_changes,
        test_party_formation_bonuses,
        test_companion_recruiter_recruitment,
        test_companion_recruiter_release,
        test_companion_recruiter_party_creation,
        test_synergy_fighter_rogue,
        test_synergy_mage_cleric,
        test_synergy_all_different,
        test_synergy_class_pair,
        test_synergy_single_companion,
        test_full_workflow,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)}")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

