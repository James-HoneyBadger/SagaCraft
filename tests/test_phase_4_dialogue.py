"""
Phase IV: Dialogue Tree System - Comprehensive Tests

Tests for dialogue tree implementation including:
- Dialogue node structure and navigation
- Conditional dialogue branches
- Dialogue consequences
- Relationship tracking
- Quest integration
- Complex dialogue scenarios
- DialogueBuilder fluent API
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sagacraft.systems.dialogue import (
    DialogueConditionType, DialogueEventType, DialogueCondition,
    DialogueConsequence, DialogueOption, DialogueNode, DialogueState,
    DialogueTree, DialogueManager, DialogueBuilder
)


def test_dialogue_condition_level_minimum():
    """Test level minimum condition."""
    condition = DialogueCondition(
        DialogueConditionType.LEVEL_MINIMUM,
        {"level": 5}
    )
    
    player_state = {"level": 3}
    dialogue_state = DialogueState()
    
    assert not condition.is_met(player_state, dialogue_state), "Should fail with level 3"
    
    player_state["level"] = 5
    assert condition.is_met(player_state, dialogue_state), "Should pass with level 5"
    
    player_state["level"] = 10
    assert condition.is_met(player_state, dialogue_state), "Should pass with level 10"


def test_dialogue_condition_attribute():
    """Test attribute-based conditions."""
    condition = DialogueCondition(
        DialogueConditionType.ATTRIBUTE,
        {"attribute": "STR", "value": 15, "operator": ">="}
    )
    
    player_state = {"attributes": {"STR": 10}}
    dialogue_state = DialogueState()
    
    assert not condition.is_met(player_state, dialogue_state), "Should fail with STR 10"
    
    player_state["attributes"]["STR"] = 15
    assert condition.is_met(player_state, dialogue_state), "Should pass with STR 15"
    
    player_state["attributes"]["STR"] = 20
    assert condition.is_met(player_state, dialogue_state), "Should pass with STR 20"


def test_dialogue_condition_skill_required():
    """Test skill requirement conditions."""
    condition = DialogueCondition(
        DialogueConditionType.SKILL_REQUIRED,
        {"skill": "persuasion"}
    )
    
    player_state = {"skills": set()}
    dialogue_state = DialogueState()
    
    assert not condition.is_met(player_state, dialogue_state), "Should fail without skill"
    
    player_state["skills"].add("persuasion")
    assert condition.is_met(player_state, dialogue_state), "Should pass with skill"


def test_dialogue_condition_flag():
    """Test flag-based conditions."""
    condition = DialogueCondition(
        DialogueConditionType.FLAG,
        {"flag": "met_merchant", "value": True}
    )
    
    dialogue_state = DialogueState()
    player_state = {}
    
    assert not condition.is_met(player_state, dialogue_state), "Should fail without flag"
    
    dialogue_state.set_flag("met_merchant", True)
    assert condition.is_met(player_state, dialogue_state), "Should pass with flag set"
    
    dialogue_state.set_flag("met_merchant", False)
    assert not condition.is_met(player_state, dialogue_state), "Should fail when flag unset"


def test_dialogue_condition_relationship():
    """Test relationship-based conditions."""
    condition = DialogueCondition(
        DialogueConditionType.RELATIONSHIP,
        {"npc": "merchant", "level": 50}
    )
    
    dialogue_state = DialogueState()
    player_state = {}
    
    assert not condition.is_met(player_state, dialogue_state), "Should fail with 0 relationship"
    
    dialogue_state.modify_relationship("merchant", 30)
    assert not condition.is_met(player_state, dialogue_state), "Should fail with 30 relationship"
    
    dialogue_state.modify_relationship("merchant", 25)
    assert condition.is_met(player_state, dialogue_state), "Should pass with 55 relationship"


def test_dialogue_consequence_flag():
    """Test flag consequences."""
    consequence = DialogueConsequence(
        DialogueEventType.FLAG_SET,
        {"flag": "quest_accepted"}
    )
    
    dialogue_state = DialogueState()
    player_state = {}
    
    assert not dialogue_state.get_flag("quest_accepted")
    consequence.apply(player_state, dialogue_state)
    assert dialogue_state.get_flag("quest_accepted")


def test_dialogue_consequence_relationship():
    """Test relationship modification consequences."""
    consequence = DialogueConsequence(
        DialogueEventType.RELATIONSHIP_CHANGE,
        {"npc": "merchant", "change": 15}
    )
    
    dialogue_state = DialogueState()
    player_state = {}
    
    assert dialogue_state.get_relationship("merchant") == 0
    consequence.apply(player_state, dialogue_state)
    assert dialogue_state.get_relationship("merchant") == 15


def test_dialogue_consequence_quest():
    """Test quest start consequence."""
    consequence = DialogueConsequence(
        DialogueEventType.QUEST_START,
        {"quest_id": "retrieve_amulet"}
    )
    
    dialogue_state = DialogueState()
    player_state = {}
    
    assert "retrieve_amulet" not in dialogue_state.active_quests
    consequence.apply(player_state, dialogue_state)
    assert "retrieve_amulet" in dialogue_state.active_quests


def test_dialogue_option_availability():
    """Test dialogue option availability with conditions."""
    option = DialogueOption(
        "opt_1",
        "I'm quite wealthy.",
        conditions=[
            DialogueCondition(
                DialogueConditionType.ATTRIBUTE,
                {"attribute": "CHA", "value": 16, "operator": ">="}
            )
        ]
    )
    
    player_state = {"attributes": {"CHA": 10}}
    dialogue_state = DialogueState()
    
    assert not option.is_available(player_state, dialogue_state)
    
    player_state["attributes"]["CHA"] = 18
    assert option.is_available(player_state, dialogue_state)


def test_dialogue_option_consequences():
    """Test dialogue option consequences are applied."""
    option = DialogueOption(
        "opt_1",
        "I'll help you.",
        consequences=[
            DialogueConsequence(
                DialogueEventType.QUEST_START,
                {"quest_id": "save_village"}
            ),
            DialogueConsequence(
                DialogueEventType.RELATIONSHIP_CHANGE,
                {"npc": "elder", "change": 10}
            )
        ]
    )
    
    player_state = {}
    dialogue_state = DialogueState()
    
    option.apply_consequences(player_state, dialogue_state)
    
    assert "save_village" in dialogue_state.active_quests
    assert dialogue_state.get_relationship("elder") == 10


def test_dialogue_node_available_options():
    """Test getting available options from a dialogue node."""
    options = [
        DialogueOption("opt_1", "Nice to meet you."),
        DialogueOption(
            "opt_2",
            "Kneel before me!",
            conditions=[
                DialogueCondition(
                    DialogueConditionType.ATTRIBUTE,
                    {"attribute": "STR", "value": 18, "operator": ">="}
                )
            ]
        ),
        DialogueOption("opt_3", "Leave quietly.", next_node_id=None)
    ]
    
    node = DialogueNode("greeting", "Guard", "What's your business?", options)
    
    player_state = {"attributes": {"STR": 10}}
    dialogue_state = DialogueState()
    
    available = node.get_available_options(player_state, dialogue_state)
    assert len(available) == 2
    assert options[0] in available
    assert options[2] in available
    assert options[1] not in available


def test_dialogue_tree_validation():
    """Test dialogue tree validation."""
    tree = DialogueTree("greeting_tree", "Guard")
    
    # Add valid nodes
    root = DialogueNode("root", "Guard", "Who goes there?")
    option = DialogueOption("opt_1", "Friend", "friend_node")
    root.options.append(option)
    
    friend_node = DialogueNode("friend_node", "Guard", "Very well, pass through.")
    
    tree.add_node(root)
    tree.add_node(friend_node)
    
    assert tree.validate(), "Valid tree should pass validation"
    
    # Test with broken reference
    root.options[0].next_node_id = "nonexistent_node"
    assert not tree.validate(), "Tree with broken reference should fail validation"


def test_dialogue_tree_navigation():
    """Test navigating through dialogue tree."""
    tree = DialogueTree("quest_tree", "Merchant")
    
    # Create dialogue nodes
    greeting = DialogueNode("greeting", "Merchant", "Welcome to my shop!")
    greeting.options.append(DialogueOption("opt_quest", "I have a task for you.", "quest_offer"))
    
    quest_offer = DialogueNode("quest_offer", "Merchant", "I need rare spices from the East.")
    quest_offer.options.append(DialogueOption("opt_accept", "I'll do it.", "accept_quest"))
    quest_offer.options.append(DialogueOption("opt_refuse", "Not interested.", None))
    
    accept_node = DialogueNode("accept_quest", "Merchant", "Excellent! Return when you succeed.")
    
    tree.add_node(greeting)
    tree.add_node(quest_offer)
    tree.add_node(accept_node)
    
    assert tree.get_root_node().node_id == "greeting"
    assert tree.get_next_node("greeting", "opt_quest").node_id == "quest_offer"
    assert tree.get_next_node("quest_offer", "opt_accept").node_id == "accept_quest"
    assert tree.get_next_node("quest_offer", "opt_refuse") is None


def test_dialogue_manager_conversation():
    """Test managing dialogue conversations."""
    manager = DialogueManager()
    
    # Create and register a dialogue tree
    tree = DialogueTree("vendor_tree", "Vendor")
    
    greeting = DialogueNode("greeting", "Vendor", "Welcome!")
    greeting.options.append(DialogueOption("opt_buy", "What are you selling?", "selling"))
    
    selling = DialogueNode("selling", "Vendor", "Fine wares!")
    selling.options.append(DialogueOption("opt_leave", "I'll pass.", None))
    
    tree.add_node(greeting)
    tree.add_node(selling)
    manager.register_tree(tree)
    
    # Start conversation
    player_state = {}
    node = manager.start_conversation("vendor_tree", "Vendor")
    assert node.node_id == "greeting"
    
    # Check available options
    options = manager.get_available_options("Vendor", player_state)
    assert len(options) == 1
    assert options[0].option_id == "opt_buy"
    
    # Choose option
    next_node = manager.choose_option("Vendor", "opt_buy", player_state)
    assert next_node.node_id == "selling"
    
    # End conversation
    next_node = manager.choose_option("Vendor", "opt_leave", player_state)
    assert next_node is None
    assert not manager.has_active_conversation("Vendor")


def test_dialogue_builder():
    """Test DialogueBuilder fluent API."""
    tree = (DialogueBuilder("main_quest", "Quest Giver")
            .add_node("start", "Quest Giver", "I need your help!")
            .add_option("opt_1", "What do you need?", "quest_details")
            .add_option("opt_2", "I'm not interested.", None)
            .add_node("quest_details", "Quest Giver", "Find the lost relic.")
            .add_option("opt_accept", "I'll find it!", "accepted")
            .add_option("opt_decline", "Too dangerous.", None)
            .add_condition_to_option(
                "opt_accept",
                DialogueCondition(DialogueConditionType.LEVEL_MINIMUM, {"level": 10})
            )
            .add_consequence_to_option(
                "opt_accept",
                DialogueConsequence(
                    DialogueEventType.QUEST_START,
                    {"quest_id": "find_relic"}
                )
            )
            .add_node("accepted", "Quest Giver", "Thank you!")
            .build())
    
    assert tree.validate()
    assert len(tree.nodes) == 3
    assert tree.get_root_node().node_id == "start"


def test_complex_dialogue_scenario():
    """Test a complex dialogue scenario with conditions and consequences."""
    manager = DialogueManager()
    
    # Create a branching dialogue with conditions
    builder = (DialogueBuilder("merchant_bargain", "Merchant")
               .add_node("greeting", "Merchant", "Welcome, traveler!")
               .add_option("opt_haggle_poor", "These prices are too high! (Requires CHA 12)", "haggle_attempt")
               .add_option("opt_accept", "Fair enough, I'll buy.", None)
               .add_condition_to_option(
                   "opt_haggle_poor",
                   DialogueCondition(DialogueConditionType.ATTRIBUTE, {"attribute": "CHA", "value": 12, "operator": ">="})
               )
               .add_consequence_to_option(
                   "opt_haggle_poor",
                   DialogueConsequence(DialogueEventType.RELATIONSHIP_CHANGE, {"npc": "Merchant", "change": -5})
               )
               .add_node("haggle_attempt", "Merchant", "You dare bargain with me?")
               .add_option("opt_apologize", "My apologies...", None)
               .add_consequence_to_option(
                   "opt_apologize",
                   DialogueConsequence(DialogueEventType.RELATIONSHIP_CHANGE, {"npc": "Merchant", "change": 5})
               ))
    
    tree = builder.build()
    manager.register_tree(tree)
    
    # Test with low CHA player
    player_state_weak = {"attributes": {"CHA": 10}}
    manager.start_conversation("merchant_bargain", "Merchant")
    options = manager.get_available_options("Merchant", player_state_weak)
    
    assert len(options) == 1
    assert options[0].option_id == "opt_accept"
    
    # Test with high CHA player
    player_state_strong = {"attributes": {"CHA": 16}}
    manager.end_conversation("Merchant")
    manager.start_conversation("merchant_bargain", "Merchant")
    options = manager.get_available_options("Merchant", player_state_strong)
    
    assert len(options) == 2
    option_ids = [opt.option_id for opt in options]
    assert "opt_haggle_poor" in option_ids
    assert "opt_accept" in option_ids


def test_dialogue_state_tracking():
    """Test dialogue state tracking."""
    state = DialogueState()
    
    # Track choices
    state.record_choice("opt_1")
    state.record_choice("opt_2")
    assert "opt_1" in state.chosen_dialogues
    assert "opt_2" in state.chosen_dialogues
    
    # Track visited nodes
    state.record_dialogue("node_1")
    state.record_dialogue("node_2")
    assert "node_1" in state.dialogue_history
    assert "node_2" in state.dialogue_history
    
    # Manage flags
    state.set_flag("questline_started", True)
    assert state.get_flag("questline_started")
    
    state.set_flag("questline_started", False)
    assert not state.get_flag("questline_started")
    
    # Manage relationships
    state.modify_relationship("Elder", 20)
    assert state.get_relationship("Elder") == 20
    
    state.modify_relationship("Elder", 15)
    assert state.get_relationship("Elder") == 35
    
    # Test clamping (0-100)
    state.modify_relationship("Elder", 100)
    assert state.get_relationship("Elder") == 100
    
    state.modify_relationship("Elder", 1)
    assert state.get_relationship("Elder") == 100  # Clamped at 100


def run_all_tests():
    """Run all dialogue tests."""
    tests = [
        ("Dialogue Condition: Level Minimum", test_dialogue_condition_level_minimum),
        ("Dialogue Condition: Attribute", test_dialogue_condition_attribute),
        ("Dialogue Condition: Skill Required", test_dialogue_condition_skill_required),
        ("Dialogue Condition: Flag", test_dialogue_condition_flag),
        ("Dialogue Condition: Relationship", test_dialogue_condition_relationship),
        ("Dialogue Consequence: Flag", test_dialogue_consequence_flag),
        ("Dialogue Consequence: Relationship", test_dialogue_consequence_relationship),
        ("Dialogue Consequence: Quest", test_dialogue_consequence_quest),
        ("Dialogue Option: Availability", test_dialogue_option_availability),
        ("Dialogue Option: Consequences", test_dialogue_option_consequences),
        ("Dialogue Node: Available Options", test_dialogue_node_available_options),
        ("Dialogue Tree: Validation", test_dialogue_tree_validation),
        ("Dialogue Tree: Navigation", test_dialogue_tree_navigation),
        ("Dialogue Manager: Conversation", test_dialogue_manager_conversation),
        ("Dialogue Builder: Fluent API", test_dialogue_builder),
        ("Complex Dialogue: Scenario", test_complex_dialogue_scenario),
        ("Dialogue State: Tracking", test_dialogue_state_tracking),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*70)
    print("PHASE IV: DIALOGUE TREE SYSTEM - TEST RESULTS")
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
