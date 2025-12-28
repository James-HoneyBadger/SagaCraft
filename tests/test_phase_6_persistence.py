"""
Phase VI: Persistent World & Consequences - Comprehensive Tests

Tests for world persistence including:
- NPC memory and history
- Location persistence
- Quest state tracking
- World flags and variables
- Consequence application
- Faction system
- Ending determination
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sagacraft.systems.persistence import (
    Consequence, ConsequenceType, NPCMemory, Location, FactionSystem,
    WorldState, ConsequenceCascade
)


def test_npc_memory_creation():
    """Test NPC memory creation and initialization."""
    memory = NPCMemory("merchant")
    
    assert memory.npc_name == "merchant"
    assert not memory.encountered
    assert memory.relationship_level == 0
    assert len(memory.dialogue_history) == 0
    assert len(memory.notes) == 0


def test_npc_memory_dialogue_tracking():
    """Test tracking NPC dialogue history."""
    memory = NPCMemory("guard")
    
    memory.record_dialogue("greeting_1")
    memory.record_dialogue("quest_offer")
    
    assert memory.encountered
    assert "greeting_1" in memory.dialogue_history
    assert "quest_offer" in memory.dialogue_history
    assert memory.has_dialogue_history("greeting_1")
    assert not memory.has_dialogue_history("unknown_dialogue")


def test_npc_memory_relationship():
    """Test NPC relationship tracking."""
    memory = NPCMemory("elder")
    
    assert memory.relationship_level == 0
    assert memory.get_relationship_tier() == "neutral"
    
    memory.modify_relationship(30)
    assert memory.relationship_level == 30
    assert memory.get_relationship_tier() == "liked"
    
    memory.modify_relationship(50)
    assert memory.relationship_level == 80
    assert memory.get_relationship_tier() == "loved"
    
    # Test clamping
    memory.modify_relationship(50)
    assert memory.relationship_level == 100
    assert memory.get_relationship_tier() == "loved"


def test_npc_memory_negative_relationship():
    """Test negative NPC relationships."""
    memory = NPCMemory("villain")
    
    memory.modify_relationship(-80)
    assert memory.relationship_level == -80
    assert memory.get_relationship_tier() == "hated"
    
    memory.modify_relationship(-50)
    assert memory.relationship_level == -100
    assert memory.get_relationship_tier() == "hated"


def test_npc_memory_death_state():
    """Test NPC death state tracking."""
    memory = NPCMemory("king")
    
    assert not memory.is_dead
    memory.is_dead = True
    assert memory.get_relationship_tier() == "dead"


def test_npc_memory_gone_state():
    """Test NPC gone state."""
    memory = NPCMemory("wanderer")
    
    memory.is_gone = True
    assert memory.get_relationship_tier() == "gone"


def test_location_creation():
    """Test location creation."""
    location = Location("tavern", "A cozy tavern with good ale")
    
    assert location.name == "tavern"
    assert not location.is_destroyed
    assert not location.is_sealed
    assert not location.visited


def test_location_visits():
    """Test location visit tracking."""
    location = Location("dungeon", "A dark dungeon")
    
    location.visit()
    assert location.visited
    assert location.visit_count == 1
    
    location.visit()
    assert location.visit_count == 2


def test_location_npc_management():
    """Test NPC presence in location."""
    location = Location("castle", "A grand castle")
    
    location.add_npc("king")
    location.add_npc("guard")
    
    assert location.has_npc("king")
    assert location.has_npc("guard")
    assert not location.has_npc("merchant")
    
    location.remove_npc("king")
    assert not location.has_npc("king")
    assert location.has_npc("guard")


def test_location_item_management():
    """Test items in location."""
    location = Location("treasure_room", "Shiny treasures everywhere")
    
    location.add_item("gold_sword")
    location.add_item("ancient_amulet")
    
    assert location.has_item("gold_sword")
    assert location.has_item("ancient_amulet")
    
    location.remove_item("gold_sword")
    assert not location.has_item("gold_sword")
    assert location.has_item("ancient_amulet")


def test_faction_system():
    """Test faction attitude system."""
    factions = FactionSystem()
    
    # Check initial attitudes
    assert factions.get_attitude("guild") == 0
    
    # Modify attitudes
    factions.modify_attitude("guild", 30)
    assert factions.get_attitude("guild") == 30
    
    factions.modify_attitude("nobles", -80)
    assert factions.is_hostile("nobles")
    assert not factions.is_hostile("guild")
    
    factions.set_attitude("rebels", 60)
    assert factions.is_friendly("rebels")


def test_faction_attitude_clamping():
    """Test faction attitudes are clamped to -100/100."""
    factions = FactionSystem()
    
    factions.set_attitude("guild", 150)
    assert factions.get_attitude("guild") == 100
    
    factions.set_attitude("guild", -150)
    assert factions.get_attitude("guild") == -100


def test_world_state_creation():
    """Test world state initialization."""
    world = WorldState("test_world")
    
    assert world.world_name == "test_world"
    assert len(world.npc_memories) == 0
    assert len(world.locations) == 0
    assert len(world.active_quests) == 0


def test_world_npc_memory_creation():
    """Test creating NPC memory in world."""
    world = WorldState("kingdom")
    
    memory = world.create_npc_memory("trader")
    assert memory.npc_name == "trader"
    
    # Get same memory
    same_memory = world.get_npc_memory("trader")
    assert same_memory is memory


def test_world_npc_dialogue_recording():
    """Test recording NPC dialogue."""
    world = WorldState("kingdom")
    
    world.record_npc_dialogue("sage", "greeting_1")
    memory = world.get_npc_memory("sage")
    
    assert memory.encountered
    assert "greeting_1" in memory.dialogue_history


def test_world_npc_relationship():
    """Test world NPC relationship management."""
    world = WorldState("kingdom")
    
    assert world.get_npc_relationship("mysterious_stranger") == 0
    
    world.modify_npc_relationship("mysterious_stranger", 25)
    assert world.get_npc_relationship("mysterious_stranger") == 25


def test_world_npc_death():
    """Test marking NPC as dead."""
    world = WorldState("kingdom")
    
    world.mark_npc_dead("villain", "defeated in battle")
    
    assert not world.is_npc_alive("villain")
    memory = world.get_npc_memory("villain")
    assert memory.is_dead


def test_world_location_creation():
    """Test creating locations in world."""
    world = WorldState("kingdom")
    
    loc = world.create_location("blacksmith", "A forge")
    assert loc.name == "blacksmith"
    
    same_loc = world.get_location("blacksmith")
    assert same_loc is loc


def test_world_location_destruction():
    """Test destroying locations."""
    world = WorldState("kingdom")
    world.create_location("tower", "A tall tower")
    
    world.destroy_location("tower")
    
    location = world.get_location("tower")
    assert location.is_destroyed
    assert not world.is_location_accessible("tower")


def test_world_location_sealing():
    """Test sealing locations."""
    world = WorldState("kingdom")
    world.create_location("vault", "A secure vault")
    
    world.seal_location("vault", "magical seal placed")
    
    location = world.get_location("vault")
    assert location.is_sealed
    assert not world.is_location_accessible("vault")


def test_world_item_management():
    """Test item availability tracking."""
    world = WorldState("kingdom")
    
    world.make_item_available("sword", "blacksmith")
    assert world.is_item_available("sword")
    assert world.get_item_location("sword") == "blacksmith"
    
    world.remove_item("sword")
    assert not world.is_item_available("sword")


def test_world_quest_management():
    """Test quest state tracking."""
    world = WorldState("kingdom")
    
    world.activate_quest("defeat_dragon")
    assert "defeat_dragon" in world.active_quests
    
    world.complete_quest("defeat_dragon")
    assert "defeat_dragon" not in world.active_quests
    assert "defeat_dragon" in world.completed_quests


def test_world_quest_blocking():
    """Test blocking quests."""
    world = WorldState("kingdom")
    
    assert not world.is_quest_blocked("rescue_princess")
    
    world.block_quest("rescue_princess")
    assert world.is_quest_blocked("rescue_princess")
    
    world.enable_quest("rescue_princess")
    assert not world.is_quest_blocked("rescue_princess")


def test_world_flags():
    """Test world flag management."""
    world = WorldState("kingdom")
    
    world.set_world_flag("dragon_defeated", True)
    assert world.get_world_flag("dragon_defeated")
    
    world.set_world_flag("dragon_defeated", False)
    assert not world.get_world_flag("dragon_defeated")


def test_world_faction_attitudes():
    """Test world faction system integration."""
    world = WorldState("kingdom")
    
    world.set_faction_attitude("guild", 75)
    assert world.get_faction_attitude("guild") == 75


def test_consequence_npc_death():
    """Test consequence application for NPC death."""
    world = WorldState("kingdom")
    consequence = Consequence(
        ConsequenceType.NPC_DEATH,
        "tyrant",
        reason="slain by hero"
    )
    
    consequence.apply(world)
    
    assert not world.is_npc_alive("tyrant")
    memory = world.get_npc_memory("tyrant")
    assert memory.is_dead


def test_consequence_location_destruction():
    """Test location destruction consequence."""
    world = WorldState("kingdom")
    world.create_location("village", "A small village")
    
    consequence = Consequence(
        ConsequenceType.LOCATION_DESTROYED,
        "village",
        reason="burned down"
    )
    consequence.apply(world)
    
    assert not world.is_location_accessible("village")


def test_consequence_quest_blocking():
    """Test quest blocking consequence."""
    world = WorldState("kingdom")
    consequence = Consequence(
        ConsequenceType.QUEST_BLOCKED,
        "find_artifact"
    )
    consequence.apply(world)
    
    assert world.is_quest_blocked("find_artifact")


def test_consequence_relationship_change():
    """Test relationship change consequence."""
    world = WorldState("kingdom")
    consequence = Consequence(
        ConsequenceType.RELATIONSHIP_CHANGED,
        "king",
        {"change": 50}
    )
    consequence.apply(world)
    
    assert world.get_npc_relationship("king") == 50


def test_consequence_history():
    """Test consequence history tracking."""
    world = WorldState("kingdom")
    consequence = Consequence(
        ConsequenceType.WORLD_FLAG,
        "major_event",
        {"value": True}
    )
    consequence.apply(world)
    
    assert len(world.consequence_history) == 1
    assert world.consequence_history[0] is consequence


def test_world_ending_determination():
    """Test possible ending calculation."""
    world = WorldState("kingdom")
    
    # Start with neutral
    endings = world.get_possible_endings()
    assert "neutral" in endings
    
    # Complete many quests
    for i in range(15):
        world.completed_quests.add(f"quest_{i}")
    
    endings = world.get_possible_endings()
    assert "hero" in endings
    
    # Gain noble favor
    world.set_faction_attitude("nobles", 60)
    endings = world.get_possible_endings()
    assert "noble_favor" in endings


def test_consequence_cascade_npc_death():
    """Test cascading consequences from NPC death."""
    world = WorldState("kingdom")
    world.create_npc_memory("questgiver")
    world.activate_quest("retrieve_item")
    
    cascade = ConsequenceCascade(world)
    consequences = cascade.apply_npc_death("questgiver", "assassinated")
    
    assert len(consequences) > 1
    assert not world.is_npc_alive("questgiver")
    assert world.is_dialogue_locked("questgiver", "all_dialogue")
    assert world.is_quest_blocked("retrieve_item")


def test_consequence_cascade_location_destruction():
    """Test cascading consequences from location destruction."""
    world = WorldState("kingdom")
    world.create_location("armory", "A weapons store")
    world.make_item_available("legendary_sword", "armory")
    
    location = world.get_location("armory")
    location.add_npc("armorer")
    
    cascade = ConsequenceCascade(world)
    consequences = cascade.apply_location_destruction("armory", "earthquake")
    
    assert len(consequences) > 1
    assert not world.is_location_accessible("armory")
    assert not world.is_item_available("legendary_sword")
    assert world.is_npc_alive("armorer") == False or not world.get_npc_memory("armorer").encountered


def test_consequence_cascade_faction_war():
    """Test cascading consequences from faction war."""
    world = WorldState("kingdom")
    
    cascade = ConsequenceCascade(world)
    consequences = cascade.apply_faction_war("guild", "nobles")
    
    assert len(consequences) >= 2
    assert world.get_faction_attitude("guild") == -100
    assert world.get_faction_attitude("nobles") == -100


def test_world_serialization():
    """Test world state serialization."""
    world = WorldState("save_test")
    world.create_npc_memory("hero")
    world.activate_quest("main_quest")
    world.set_world_flag("story_started", True)
    
    data = world.to_dict()
    
    assert data["world_name"] == "save_test"
    assert data["npc_count"] == 1
    assert data["active_quests"] == 1


def test_world_json_serialization():
    """Test JSON serialization."""
    world = WorldState("json_test")
    world.create_location("town", "A bustling town")
    
    json_str = world.to_json()
    assert isinstance(json_str, str)
    assert "json_test" in json_str


def run_all_tests():
    """Run all persistence tests."""
    tests = [
        ("NPC Memory: Creation", test_npc_memory_creation),
        ("NPC Memory: Dialogue Tracking", test_npc_memory_dialogue_tracking),
        ("NPC Memory: Relationship", test_npc_memory_relationship),
        ("NPC Memory: Negative Relationship", test_npc_memory_negative_relationship),
        ("NPC Memory: Death State", test_npc_memory_death_state),
        ("NPC Memory: Gone State", test_npc_memory_gone_state),
        ("Location: Creation", test_location_creation),
        ("Location: Visits", test_location_visits),
        ("Location: NPC Management", test_location_npc_management),
        ("Location: Item Management", test_location_item_management),
        ("Faction System: Basic", test_faction_system),
        ("Faction System: Clamping", test_faction_attitude_clamping),
        ("World State: Creation", test_world_state_creation),
        ("World State: NPC Memory", test_world_npc_memory_creation),
        ("World State: Dialogue Recording", test_world_npc_dialogue_recording),
        ("World State: NPC Relationship", test_world_npc_relationship),
        ("World State: NPC Death", test_world_npc_death),
        ("World State: Location Creation", test_world_location_creation),
        ("World State: Location Destruction", test_world_location_destruction),
        ("World State: Location Sealing", test_world_location_sealing),
        ("World State: Item Management", test_world_item_management),
        ("World State: Quest Management", test_world_quest_management),
        ("World State: Quest Blocking", test_world_quest_blocking),
        ("World State: Flags", test_world_flags),
        ("World State: Faction Attitudes", test_world_faction_attitudes),
        ("Consequence: NPC Death", test_consequence_npc_death),
        ("Consequence: Location Destruction", test_consequence_location_destruction),
        ("Consequence: Quest Blocking", test_consequence_quest_blocking),
        ("Consequence: Relationship Change", test_consequence_relationship_change),
        ("Consequence: History", test_consequence_history),
        ("World Endings: Determination", test_world_ending_determination),
        ("Cascade: NPC Death", test_consequence_cascade_npc_death),
        ("Cascade: Location Destruction", test_consequence_cascade_location_destruction),
        ("Cascade: Faction War", test_consequence_cascade_faction_war),
        ("World Serialization: Dict", test_world_serialization),
        ("World Serialization: JSON", test_world_json_serialization),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*70)
    print("PHASE VI: PERSISTENT WORLD & CONSEQUENCES - TEST RESULTS")
    print("="*70 + "\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name}: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name}: {type(e).__name__}: {str(e)}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)}")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
