"""Tests for Dynamic Difficulty Scaling System."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sagacraft.systems.difficulty import (
    DifficultyScaler,
    DifficultyLevel,
    DifficultyProfile,
    PerformanceMetric,
)


def test_create_profile() -> None:
    """Test creating a difficulty profile."""
    scaler = DifficultyScaler()
    profile = scaler.create_profile("player_1")

    assert profile.player_id == "player_1"
    assert profile.current_level == DifficultyLevel.NORMAL
    assert profile.win_streak == 0
    assert profile.loss_streak == 0


def test_get_or_create_profile() -> None:
    """Test getting or creating profiles."""
    scaler = DifficultyScaler()

    # Get non-existent creates it
    profile1 = scaler.get_profile("player_1")
    assert profile1.player_id == "player_1"

    # Get existing returns same
    profile2 = scaler.get_profile("player_1")
    assert profile1 is profile2


def test_record_win() -> None:
    """Test recording a win."""
    scaler = DifficultyScaler()
    profile = scaler.get_profile("player_1")

    scaler.record_performance("player_1", {"win_rate": 0.75}, combat_won=True)

    assert profile.win_streak == 1
    assert profile.loss_streak == 0
    assert len(profile.performance_history) == 1


def test_record_loss() -> None:
    """Test recording a loss."""
    scaler = DifficultyScaler()
    profile = scaler.get_profile("player_1")

    scaler.record_performance("player_1", {"win_rate": 0.25}, combat_won=False)

    assert profile.win_streak == 0
    assert profile.loss_streak == 1


def test_win_loss_streak_reset() -> None:
    """Test win/loss streak resets."""
    scaler = DifficultyScaler()
    profile = scaler.get_profile("player_1")

    # Build win streak
    for _ in range(3):
        scaler.record_performance("player_1", {}, combat_won=True)
    assert profile.win_streak == 3

    # Lose - resets
    scaler.record_performance("player_1", {}, combat_won=False)
    assert profile.win_streak == 0
    assert profile.loss_streak == 1


def test_difficulty_adjustment_too_easy() -> None:
    """Test difficulty increases when player is too good."""
    scaler = DifficultyScaler()
    profile = scaler.get_profile("player_1")

    # Simulate very high win rate
    for i in range(10):
        scaler.record_performance("player_1", {"win_rate": 0.90}, combat_won=True)

    assert profile.current_level != DifficultyLevel.NORMAL


def test_apply_difficulty_multiplier_damage() -> None:
    """Test difficulty multiplier application."""
    scaler = DifficultyScaler()
    profile = scaler.get_profile("player_1")
    profile.current_level = DifficultyLevel.HARD

    result = scaler.apply_difficulty_multiplier("player_1", 100.0, stat="damage")
    assert result == 125.0  # 1.25x multiplier


def test_apply_difficulty_multiplier_loot() -> None:
    """Test loot scaling (inverted multiplier)."""
    scaler = DifficultyScaler()
    profile = scaler.get_profile("player_1")
    profile.current_level = DifficultyLevel.HARD

    result = scaler.apply_difficulty_multiplier("player_1", 100.0, stat="loot_quality")
    assert result == 80.0  # Inverted: 1/1.25 = 0.8x


def test_difficulty_display() -> None:
    """Test difficulty display string."""
    scaler = DifficultyScaler()
    profile = scaler.get_profile("player_1")

    display = scaler.get_difficulty_display("player_1")
    assert "NORMAL" in display
    assert "1.0" in display


def test_extreme_difficulty() -> None:
    """Test reaching extreme difficulty."""
    scaler = DifficultyScaler()
    profile = scaler.get_profile("player_1")

    # Set to extreme
    profile.current_level = DifficultyLevel.EXTREME
    multiplier = scaler.apply_difficulty_multiplier("player_1", 100.0, stat="damage")
    assert multiplier == 200.0


def test_performance_metric() -> None:
    """Test performance metric deviation calculation."""
    metric = PerformanceMetric(name="win_rate", value=0.75, weight=1.0)
    # This tests that metric structure works
    assert metric.value == 0.75
    assert metric.name == "win_rate"


def test_difficulty_level_values() -> None:
    """Test all difficulty level values."""
    levels = [
        (DifficultyLevel.VERY_EASY, 0.5),
        (DifficultyLevel.EASY, 0.75),
        (DifficultyLevel.NORMAL, 1.0),
        (DifficultyLevel.HARD, 1.25),
        (DifficultyLevel.VERY_HARD, 1.5),
        (DifficultyLevel.EXTREME, 2.0),
    ]

    for level, expected_value in levels:
        assert level.value == expected_value


if __name__ == "__main__":
    test_create_profile()
    test_get_or_create_profile()
    test_record_win()
    test_record_loss()
    test_win_loss_streak_reset()
    test_difficulty_adjustment_too_easy()
    test_apply_difficulty_multiplier_damage()
    test_apply_difficulty_multiplier_loot()
    test_difficulty_display()
    test_extreme_difficulty()
    test_performance_metric()
    test_difficulty_level_values()
    print("✓ All difficulty tests passed!")
