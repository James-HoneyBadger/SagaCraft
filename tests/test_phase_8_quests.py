"""
Phase VIII: Advanced Quest System - Test Suite

Comprehensive tests for quest creation, progression, chaining, and generation.
Tests cover objectives, stages, branching, rewards, and tracker mechanics.
"""

import sys
sys.path.insert(0, '/home/james/SagaCraft/src')

from sagacraft.systems.quests import (
    QuestObjective, QuestStage, QuestReward, Quest, QuestChain,
    QuestTracker, QuestGenerator, QuestValidator, QuestStatus,
    ObjectiveType, QuestDifficulty
)


def test_quest_objective_creation():
    """Test creating quest objectives."""
    objective = QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.KILL,
        description="Kill 5 goblins",
        target="goblin",
        required_count=5
    )
    
    assert objective.objective_id == "obj_1"
    assert objective.type == ObjectiveType.KILL
    assert objective.required_count == 5
    assert objective.current_count == 0
    assert not objective.is_complete()
    print("✓ Quest Objective Creation")


def test_quest_objective_progress():
    """Test objective progress tracking."""
    objective = QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.COLLECT,
        description="Collect 10 herbs",
        target="herb",
        required_count=10
    )
    
    progress = objective.progress(3)
    assert progress == 3
    assert objective.current_count == 3
    assert objective.get_progress_percentage() == 30
    
    objective.progress(7)
    assert objective.current_count == 10
    assert objective.is_complete()
    assert objective.get_progress_percentage() == 100
    print("✓ Quest Objective Progress")


def test_quest_stage_creation():
    """Test creating quest stages."""
    stage = QuestStage(
        stage_id="stage_1",
        stage_number=1,
        title="Gather herbs",
        description="Collect 10 herbs from the forest"
    )
    
    objective = QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.COLLECT,
        description="Collect 10 herbs",
        target="herb",
        required_count=10
    )
    
    stage.add_objective(objective)
    assert len(stage.objectives) == 1
    assert not stage.is_complete()
    print("✓ Quest Stage Creation")


def test_quest_stage_completion():
    """Test stage completion checking."""
    stage = QuestStage(
        stage_id="stage_1",
        stage_number=1,
        title="Kill enemies",
        description="Defeat 5 enemies"
    )
    
    obj1 = QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.KILL,
        description="Kill 5 enemies",
        target="enemy",
        required_count=5
    )
    
    obj2 = QuestObjective(
        objective_id="obj_2",
        type=ObjectiveType.COLLECT,
        description="Loot rare items",
        target="rare_item",
        required_count=2,
        is_optional=True
    )
    
    stage.add_objective(obj1)
    stage.add_objective(obj2)
    
    assert not stage.is_complete()
    
    obj1.progress(5)
    assert stage.is_complete()  # Optional doesn't block
    
    obj2.progress(2)
    assert stage.get_optional_completed() == 1
    print("✓ Quest Stage Completion")


def test_quest_creation():
    """Test creating complete quests."""
    stage = QuestStage(
        stage_id="stage_1",
        stage_number=1,
        title="Gather herbs",
        description="Collect 10 herbs"
    )
    
    stage.add_objective(QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.COLLECT,
        description="Collect 10 herbs",
        target="herb",
        required_count=10
    ))
    
    quest = Quest(
        quest_id="quest_1",
        title="Herbalist Request",
        description="An herbalist needs 10 herbs",
        giver_npc="Herbalist",
        stages=[stage],
        rewards=QuestReward(experience_points=100, gold=50),
        difficulty=QuestDifficulty.EASY
    )
    
    assert quest.quest_id == "quest_1"
    assert quest.status == QuestStatus.AVAILABLE
    assert quest.get_current_stage() == stage
    assert not quest.is_complete()
    print("✓ Quest Creation")


def test_quest_stage_advancement():
    """Test advancing through quest stages."""
    stage1 = QuestStage(stage_id="stage_1", stage_number=1, title="Stage 1", description="")
    stage1.add_objective(QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.KILL,
        description="Kill 3 enemies",
        target="enemy",
        required_count=3
    ))
    
    stage2 = QuestStage(stage_id="stage_2", stage_number=2, title="Stage 2", description="")
    stage2.add_objective(QuestObjective(
        objective_id="obj_2",
        type=ObjectiveType.DELIVER,
        description="Report back",
        target="npc",
        required_count=1
    ))
    
    quest = Quest(
        quest_id="quest_1",
        title="Multi-stage quest",
        description="A quest with multiple stages",
        giver_npc="NPC",
        stages=[stage1, stage2],
        rewards=QuestReward(experience_points=200)
    )
    
    assert quest.get_current_stage() == stage1
    assert quest.current_stage_index == 0
    
    quest.advance_stage()
    assert quest.get_current_stage() == stage2
    assert quest.current_stage_index == 1
    
    assert not quest.advance_stage()  # Already at end
    print("✓ Quest Stage Advancement")


def test_quest_prerequisites():
    """Test quest prerequisite checking."""
    quest = Quest(
        quest_id="quest_2",
        title="Advanced quest",
        description="Requires completing quest 1",
        giver_npc="NPC",
        prerequisites=["quest_1"],
        stages=[QuestStage(
            stage_id="stage_1",
            stage_number=1,
            title="Complete",
            description="Complete this quest"
        )]
    )
    
    completed = set()
    assert not quest.can_accept(completed)
    
    completed.add("quest_1")
    assert quest.can_accept(completed)
    print("✓ Quest Prerequisites")


def test_quest_reward_scaling():
    """Test reward scaling by player level."""
    quest = Quest(
        quest_id="quest_1",
        title="Quest",
        description="A quest",
        giver_npc="NPC",
        quest_giver_level=5,
        stages=[QuestStage(stage_id="s1", stage_number=1, title="", description="")],
        rewards=QuestReward(experience_points=100, gold=50)
    )
    
    # Player at quest level = normal reward
    reward = quest.get_level_adjusted_rewards(5)
    assert reward.experience_points == 100
    
    # Player higher level = lower reward
    reward = quest.get_level_adjusted_rewards(12)
    assert reward.experience_points <= 100
    
    # Player lower level = bonus reward
    reward = quest.get_level_adjusted_rewards(2)
    assert reward.experience_points > 100
    print("✓ Quest Reward Scaling")


def test_quest_chain_creation():
    """Test creating quest chains."""
    quest1 = Quest(
        quest_id="quest_1",
        title="Quest 1",
        description="First quest",
        giver_npc="NPC",
        chain_id="chain_1",
        stages=[QuestStage(stage_id="s1", stage_number=1, title="", description="")]
    )
    
    quest2 = Quest(
        quest_id="quest_2",
        title="Quest 2",
        description="Second quest",
        giver_npc="NPC",
        chain_id="chain_1",
        prerequisites=["quest_1"],
        stages=[QuestStage(stage_id="s2", stage_number=1, title="", description="")]
    )
    
    chain = QuestChain(
        chain_id="chain_1",
        title="Hero's Journey",
        description="A long quest chain",
        quests=[quest1, quest2]
    )
    
    assert chain.chain_id == "chain_1"
    assert len(chain.quests) == 2
    assert chain.get_current_quest() == quest1
    assert not chain.is_complete
    
    chain.advance_quest()
    assert chain.get_current_quest() == quest2
    print("✓ Quest Chain Creation")


def test_quest_tracker_accept():
    """Test accepting quests."""
    tracker = QuestTracker()
    quest = Quest(
        quest_id="quest_1",
        title="Quest",
        description="Accept this quest",
        giver_npc="NPC",
        stages=[QuestStage(stage_id="s1", stage_number=1, title="", description="")]
    )
    
    assert tracker.accept_quest(quest)
    assert quest.status == QuestStatus.ACTIVE
    assert "quest_1" in tracker.active_quests
    assert tracker.get_active_count() == 1
    
    # Can't accept same quest twice
    assert not tracker.accept_quest(quest)
    print("✓ Quest Tracker Accept")


def test_quest_tracker_complete():
    """Test completing quests."""
    tracker = QuestTracker()
    quest = Quest(
        quest_id="quest_1",
        title="Quest",
        description="Complete this",
        giver_npc="NPC",
        stages=[QuestStage(stage_id="s1", stage_number=1, title="", description="")]
    )
    
    tracker.accept_quest(quest)
    assert tracker.complete_quest("quest_1")
    
    assert quest.status == QuestStatus.COMPLETED
    assert "quest_1" in tracker.completed_quests
    assert "quest_1" not in tracker.active_quests
    assert tracker.get_completed_count() == 1
    print("✓ Quest Tracker Complete")


def test_quest_tracker_fail():
    """Test failing quests."""
    tracker = QuestTracker()
    quest = Quest(
        quest_id="quest_1",
        title="Quest",
        description="This might fail",
        giver_npc="NPC",
        stages=[QuestStage(stage_id="s1", stage_number=1, title="", description="")]
    )
    
    tracker.accept_quest(quest)
    assert tracker.fail_quest("quest_1")
    
    assert quest.status == QuestStatus.FAILED
    assert "quest_1" in tracker.failed_quests
    assert "quest_1" not in tracker.active_quests
    print("✓ Quest Tracker Fail")


def test_quest_generator_kill():
    """Test generating kill quests."""
    quest = QuestGenerator.generate_kill_quest(
        "kill_quest_1",
        QuestDifficulty.MODERATE,
        "Guard Captain"
    )
    
    assert quest.quest_id == "kill_quest_1"
    assert quest.giver_npc == "Guard Captain"
    assert quest.is_radiant
    assert len(quest.stages) == 1
    
    stage = quest.get_current_stage()
    assert stage is not None
    assert len(stage.objectives) == 1
    assert stage.objectives[0].type == ObjectiveType.KILL
    print("✓ Quest Generator Kill")


def test_quest_generator_collect():
    """Test generating collect quests."""
    quest = QuestGenerator.generate_collect_quest(
        "collect_quest_1",
        QuestDifficulty.EASY,
        "Herbalist"
    )
    
    assert quest.quest_id == "collect_quest_1"
    assert quest.giver_npc == "Herbalist"
    assert quest.is_radiant
    
    stage = quest.get_current_stage()
    assert stage is not None
    assert stage.objectives[0].type == ObjectiveType.COLLECT
    print("✓ Quest Generator Collect")


def test_quest_generator_explore():
    """Test generating explore quests."""
    quest = QuestGenerator.generate_explore_quest(
        "explore_quest_1",
        QuestDifficulty.HARD,
        "Scout Master"
    )
    
    assert quest.quest_id == "explore_quest_1"
    assert quest.giver_npc == "Scout Master"
    assert quest.is_radiant
    
    stage = quest.get_current_stage()
    assert stage is not None
    assert len(stage.objectives) >= 2  # Multiple locations to explore
    assert all(o.type == ObjectiveType.EXPLORE for o in stage.objectives)
    print("✓ Quest Generator Explore")


def test_quest_validator_complete():
    """Test quest completion validation."""
    objective = QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.KILL,
        description="Kill 5 enemies",
        target="enemy",
        required_count=5
    )
    
    stage = QuestStage(
        stage_id="stage_1",
        stage_number=1,
        title="Kill enemies",
        description=""
    )
    stage.add_objective(objective)
    
    quest = Quest(
        quest_id="quest_1",
        title="Quest",
        description="",
        giver_npc="NPC",
        stages=[stage]
    )
    
    assert not QuestValidator.validate_quest_complete(quest)
    
    objective.progress(5)
    assert QuestValidator.validate_quest_complete(quest)
    print("✓ Quest Validator Complete")


def test_quest_validator_objective_progress():
    """Test objective progress validation."""
    objective = QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.COLLECT,
        description="Collect 10 items",
        target="item",
        required_count=10
    )
    
    assert QuestValidator.validate_objective_progress(objective, 5)
    objective.progress(5)
    
    assert QuestValidator.validate_objective_progress(objective, 5)
    objective.progress(5)
    
    assert not QuestValidator.validate_objective_progress(objective, 1)  # Would exceed
    print("✓ Quest Validator Objective Progress")


def test_optional_objectives():
    """Test optional objectives don't block completion."""
    stage = QuestStage(
        stage_id="stage_1",
        stage_number=1,
        title="Quest stage",
        description=""
    )
    
    required = QuestObjective(
        objective_id="required",
        type=ObjectiveType.KILL,
        description="Kill 3 enemies",
        target="enemy",
        required_count=3,
        is_optional=False
    )
    
    optional = QuestObjective(
        objective_id="optional",
        type=ObjectiveType.COLLECT,
        description="Collect rare loot",
        target="rare",
        required_count=2,
        is_optional=True
    )
    
    stage.add_objective(required)
    stage.add_objective(optional)
    
    assert not stage.is_complete()
    
    required.progress(3)
    assert stage.is_complete()  # Optional not required
    assert stage.get_optional_completed() == 0
    
    optional.progress(2)
    assert stage.get_optional_completed() == 1
    print("✓ Optional Objectives")


def test_full_quest_workflow():
    """Test complete quest workflow from acceptance to completion."""
    tracker = QuestTracker()
    
    # Create multi-stage quest
    stage1 = QuestStage(
        stage_id="stage_1",
        stage_number=1,
        title="Gather herbs",
        description="Collect 5 herbs"
    )
    stage1.add_objective(QuestObjective(
        objective_id="obj_1",
        type=ObjectiveType.COLLECT,
        description="Collect herbs",
        target="herb",
        required_count=5
    ))
    
    stage2 = QuestStage(
        stage_id="stage_2",
        stage_number=2,
        title="Deliver herbs",
        description="Return to herbalist"
    )
    stage2.add_objective(QuestObjective(
        objective_id="obj_2",
        type=ObjectiveType.DELIVER,
        description="Deliver herbs",
        target="herbalist",
        required_count=1
    ))
    
    quest = Quest(
        quest_id="herbalist_quest",
        title="Herbalist's Request",
        description="Collect and deliver herbs",
        giver_npc="Herbalist",
        stages=[stage1, stage2],
        rewards=QuestReward(experience_points=250, gold=100),
        difficulty=QuestDifficulty.EASY
    )
    
    # Accept quest
    assert tracker.accept_quest(quest)
    assert tracker.get_active_count() == 1
    
    # Progress stage 1
    current_obj = quest.get_current_stage().objectives[0]
    current_obj.progress(5)
    assert current_obj.is_complete()
    
    # Advance to stage 2
    assert quest.advance_stage()
    
    # Complete stage 2
    current_obj = quest.get_current_stage().objectives[0]
    current_obj.progress(1)
    
    # Mark quest complete
    assert tracker.complete_quest("herbalist_quest")
    assert tracker.get_completed_count() == 1
    assert tracker.get_active_count() == 0
    print("✓ Full Quest Workflow")


def run_all_tests():
    """Run all Phase VIII tests."""
    print("\n" + "="*70)
    print("PHASE VIII: ADVANCED QUEST SYSTEM - TEST SUITE")
    print("="*70 + "\n")
    
    tests = [
        test_quest_objective_creation,
        test_quest_objective_progress,
        test_quest_stage_creation,
        test_quest_stage_completion,
        test_quest_creation,
        test_quest_stage_advancement,
        test_quest_prerequisites,
        test_quest_reward_scaling,
        test_quest_chain_creation,
        test_quest_tracker_accept,
        test_quest_tracker_complete,
        test_quest_tracker_fail,
        test_quest_generator_kill,
        test_quest_generator_collect,
        test_quest_generator_explore,
        test_quest_validator_complete,
        test_quest_validator_objective_progress,
        test_optional_objectives,
        test_full_quest_workflow,
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

