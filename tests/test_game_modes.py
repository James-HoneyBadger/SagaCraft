"""Tests for Custom Game Modes System."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sagacraft.systems.game_modes import (
    GameModeManager,
    GameMode,
    GameModeRules,
    ModePlaySession,
)


def test_game_mode_enum() -> None:
    """Test game mode enum values."""
    assert GameMode.NORMAL.value == "normal"
    assert GameMode.HARDCORE.value == "hardcore"
    assert GameMode.PERMADEATH.value == "permadeath"


def test_default_modes_created() -> None:
    """Test default game modes are initialized."""
    manager = GameModeManager()

    assert GameMode.NORMAL in manager.modes
    assert GameMode.HARDCORE in manager.modes
    assert GameMode.PERMADEATH in manager.modes
    assert GameMode.SPEEDRUN in manager.modes
    assert GameMode.PUZZLE_ONLY in manager.modes


def test_get_normal_mode_rules() -> None:
    """Test getting normal mode rules."""
    manager = GameModeManager()
    rules = manager.get_mode_rules(GameMode.NORMAL)

    assert rules.mode == GameMode.NORMAL
    assert rules.allows_respawn is True
    assert rules.allows_save_load is True
    assert rules.difficulty_multiplier == 1.0
    assert rules.xp_multiplier == 1.0


def test_get_hardcore_mode_rules() -> None:
    """Test hardcore mode rules."""
    manager = GameModeManager()
    rules = manager.get_mode_rules(GameMode.HARDCORE)

    assert rules.allows_respawn is False
    assert rules.max_deaths_allowed == 3
    assert rules.difficulty_multiplier == 1.5
    assert rules.xp_multiplier == 2.0


def test_get_permadeath_mode_rules() -> None:
    """Test permadeath mode rules."""
    manager = GameModeManager()
    rules = manager.get_mode_rules(GameMode.PERMADEATH)

    assert rules.allows_respawn is False
    assert rules.allows_save_load is False
    assert rules.max_deaths_allowed == 1
    assert rules.score_multiplier == 5.0


def test_create_session() -> None:
    """Test creating a game mode session."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.NORMAL, 1000)

    assert session.player_id == "player_1"
    assert session.mode == GameMode.NORMAL
    assert session.start_time == 1000
    assert session.deaths_count == 0
    assert session.completed is False


def test_is_action_allowed_respawn() -> None:
    """Test checking if respawn is allowed."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.NORMAL, 1000)

    allowed, msg = manager.is_action_allowed(session.session_id, "respawn")
    assert allowed is True

    session2 = manager.create_session("player_2", GameMode.HARDCORE, 1000)
    allowed, msg = manager.is_action_allowed(session2.session_id, "respawn")
    assert allowed is False


def test_is_action_allowed_save() -> None:
    """Test checking if saving is allowed."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.NORMAL, 1000)

    allowed, msg = manager.is_action_allowed(session.session_id, "save_game")
    assert allowed is True

    session2 = manager.create_session("player_2", GameMode.IRON_MAN, 1000)
    allowed, msg = manager.is_action_allowed(session2.session_id, "save_game")
    assert allowed is False


def test_is_action_allowed_combat() -> None:
    """Test checking if combat is allowed."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.NORMAL, 1000)

    allowed, msg = manager.is_action_allowed(session.session_id, "use_combat")
    assert allowed is True

    session2 = manager.create_session("player_2", GameMode.PUZZLE_ONLY, 1000)
    allowed, msg = manager.is_action_allowed(session2.session_id, "use_combat")
    assert allowed is False


def test_record_death() -> None:
    """Test recording deaths in a session."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.NORMAL, 1000)

    alive, msg = manager.record_death(session.session_id)
    assert alive is True
    assert session.deaths_count == 1


def test_record_death_permadeath_limit() -> None:
    """Test permadeath mode ends after exceeding 1 death."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.PERMADEATH, 1000)

    # First death is allowed
    alive, msg = manager.record_death(session.session_id)
    assert alive is True
    assert session.deaths_count == 1
    
    # Second death triggers game over (1 > max of 1)
    alive, msg = manager.record_death(session.session_id)
    assert alive is False
    assert session.abandoned is True


def test_record_death_hardcore_limit() -> None:
    """Test hardcore mode allows 3 deaths."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.HARDCORE, 1000)

    # Deaths 1-3 allowed
    for _ in range(3):
        alive, msg = manager.record_death(session.session_id)
        assert alive is True

    # Death 4 ends game
    alive, msg = manager.record_death(session.session_id)
    assert alive is False


def test_complete_objective() -> None:
    """Test marking objectives as completed."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.SPEEDRUN, 1000)

    manager.complete_objective(session.session_id, "reach_checkpoint_1")
    assert "reach_checkpoint_1" in session.objectives_completed

    manager.complete_objective(session.session_id, "defeat_boss")
    assert len(session.objectives_completed) == 2


def test_objective_not_duplicated() -> None:
    """Test same objective isn't recorded twice."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.NORMAL, 1000)

    manager.complete_objective(session.session_id, "objective_1")
    manager.complete_objective(session.session_id, "objective_1")

    assert session.objectives_completed.count("objective_1") == 1


def test_end_session() -> None:
    """Test ending a session."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.NORMAL, 1000)

    ended_session = manager.end_session(session.session_id, final_score=1000)

    assert ended_session.completed is True
    assert ended_session.final_score == 1000
    assert ended_session.end_time is not None


def test_calculate_leaderboard_score_normal() -> None:
    """Test leaderboard score calculation for normal mode."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.NORMAL, 1000)

    manager.complete_objective(session.session_id, "obj1")
    manager.complete_objective(session.session_id, "obj2")
    manager.record_death(session.session_id)

    manager.end_session(session.session_id, final_score=1000)

    score = manager.calculate_leaderboard_score(session)
    # 1000 * 1.0 (normal) + 100 (2 objectives * 50) - 0 (no max_deaths_allowed for normal)
    assert score == 1100


def test_calculate_leaderboard_score_hardcore() -> None:
    """Test leaderboard score with mode multiplier."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.HARDCORE, 1000)

    manager.end_session(session.session_id, final_score=500)

    score = manager.calculate_leaderboard_score(session)
    # 500 * 3.0 (hardcore multiplier) = 1500
    assert score == 1500


def test_puzzle_only_no_combat() -> None:
    """Test puzzle-only mode disables combat."""
    manager = GameModeManager()
    session = manager.create_session("player_1", GameMode.PUZZLE_ONLY, 1000)

    allowed, msg = manager.is_action_allowed(session.session_id, "use_combat")
    assert allowed is False


def test_speedrun_has_time_limit() -> None:
    """Test speedrun mode has time limit."""
    manager = GameModeManager()
    rules = manager.get_mode_rules(GameMode.SPEEDRUN)

    assert rules.time_limit_minutes == 60


def test_mode_description() -> None:
    """Test mode description strings."""
    manager = GameModeManager()

    desc = manager.get_mode_description(GameMode.NORMAL)
    assert "Standard" in desc

    desc = manager.get_mode_description(GameMode.HARDCORE)
    assert "No respawn" in desc

    desc = manager.get_mode_description(GameMode.PERMADEATH)
    assert "permanently" in desc


def test_pacifist_mode() -> None:
    """Test pacifist mode rules."""
    manager = GameModeManager()
    rules = manager.get_mode_rules(GameMode.PACIFIST)

    assert rules.allows_combat is False
    assert "complete_without_killing" in rules.required_objectives


if __name__ == "__main__":
    test_game_mode_enum()
    test_default_modes_created()
    test_get_normal_mode_rules()
    test_get_hardcore_mode_rules()
    test_get_permadeath_mode_rules()
    test_create_session()
    test_is_action_allowed_respawn()
    test_is_action_allowed_save()
    test_is_action_allowed_combat()
    test_record_death()
    test_record_death_permadeath_limit()
    test_record_death_hardcore_limit()
    test_complete_objective()
    test_objective_not_duplicated()
    test_end_session()
    test_calculate_leaderboard_score_normal()
    test_calculate_leaderboard_score_hardcore()
    test_puzzle_only_no_combat()
    test_speedrun_has_time_limit()
    test_mode_description()
    test_pacifist_mode()
    print("✓ All game mode tests passed!")
