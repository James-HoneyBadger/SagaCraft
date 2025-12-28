"""Dynamic Difficulty Scaling System - adjusts game difficulty based on player performance."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from collections import deque


class DifficultyLevel(Enum):
    """Difficulty scaling levels."""
    VERY_EASY = 0.5
    EASY = 0.75
    NORMAL = 1.0
    HARD = 1.25
    VERY_HARD = 1.5
    EXTREME = 2.0


@dataclass
class PerformanceMetric:
    """Tracks a single performance metric for difficulty calculation."""
    name: str
    value: float
    weight: float = 1.0
    threshold: float = 0.5  # Adjust difficulty when metric deviates by this %

    def calculate_deviation(self, expected: float) -> float:
        """Calculate % deviation from expected value."""
        if expected == 0:
            return 0.0
        return abs(self.value - expected) / expected


@dataclass
class DifficultyProfile:
    """Player's difficulty adjustment profile."""
    player_id: str
    current_level: DifficultyLevel = DifficultyLevel.NORMAL
    performance_history: deque = field(default_factory=lambda: deque(maxlen=50))
    last_adjustment_turn: int = 0
    adjustment_interval: int = 5  # Adjust every N turns
    win_streak: int = 0
    loss_streak: int = 0


class DifficultyScaler:
    """Manages dynamic difficulty scaling based on player performance."""

    def __init__(self):
        self.profiles: Dict[str, DifficultyProfile] = {}
        self.performance_targets: Dict[str, float] = {
            "win_rate": 0.6,  # 60% win rate optimal
            "combat_duration": 3.0,  # 3 turns average
            "damage_taken_ratio": 0.4,  # Take ~40% of enemy damage
            "resource_usage": 0.5,  # Use ~50% of resources
        }

    def create_profile(self, player_id: str) -> DifficultyProfile:
        """Create a new difficulty profile for a player."""
        profile = DifficultyProfile(player_id=player_id)
        self.profiles[player_id] = profile
        return profile

    def get_profile(self, player_id: str) -> DifficultyProfile:
        """Get or create a player's difficulty profile."""
        if player_id not in self.profiles:
            return self.create_profile(player_id)
        return self.profiles[player_id]

    def record_performance(
        self,
        player_id: str,
        metrics: Dict[str, float],
        combat_won: bool
    ) -> None:
        """Record player performance after combat."""
        profile = self.get_profile(player_id)

        # Track win/loss streak
        if combat_won:
            profile.win_streak += 1
            profile.loss_streak = 0
        else:
            profile.loss_streak += 1
            profile.win_streak = 0

        # Store performance data
        profile.performance_history.append({
            "metrics": metrics,
            "won": combat_won,
            "timestamp": len(profile.performance_history),
        })

        # Check if adjustment needed
        profile.last_adjustment_turn += 1
        if profile.last_adjustment_turn >= profile.adjustment_interval:
            self.adjust_difficulty(player_id)
            profile.last_adjustment_turn = 0

    def adjust_difficulty(self, player_id: str) -> DifficultyLevel:
        """Calculate and apply difficulty adjustment based on recent performance."""
        profile = self.get_profile(player_id)

        if len(profile.performance_history) < 5:
            return profile.current_level

        # Calculate average metrics
        recent = list(profile.performance_history)[-10:]
        avg_metrics: Dict[str, float] = {}
        win_count = sum(1 for r in recent if r["won"])
        recent_win_rate = win_count / len(recent) if recent else 0.0

        # Determine adjustment
        adjustments = 0
        if recent_win_rate > self.performance_targets["win_rate"] + 0.15:
            adjustments += 1  # Too easy
        elif recent_win_rate < self.performance_targets["win_rate"] - 0.15:
            adjustments -= 1  # Too hard

        # Apply adjustment
        if adjustments > 0:
            profile.current_level = self._increase_difficulty(profile.current_level)
        elif adjustments < 0:
            profile.current_level = self._decrease_difficulty(profile.current_level)

        return profile.current_level

    def _increase_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """Increase difficulty level."""
        levels = [
            DifficultyLevel.VERY_EASY,
            DifficultyLevel.EASY,
            DifficultyLevel.NORMAL,
            DifficultyLevel.HARD,
            DifficultyLevel.VERY_HARD,
            DifficultyLevel.EXTREME,
        ]
        idx = levels.index(current)
        return levels[min(idx + 1, len(levels) - 1)]

    def _decrease_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """Decrease difficulty level."""
        levels = [
            DifficultyLevel.VERY_EASY,
            DifficultyLevel.EASY,
            DifficultyLevel.NORMAL,
            DifficultyLevel.HARD,
            DifficultyLevel.VERY_HARD,
            DifficultyLevel.EXTREME,
        ]
        idx = levels.index(current)
        return levels[max(idx - 1, 0)]

    def apply_difficulty_multiplier(
        self, player_id: str, base_value: float, stat: str = "damage"
    ) -> float:
        """Apply difficulty scaling to a stat value."""
        profile = self.get_profile(player_id)
        multiplier = profile.current_level.value

        # Some stats scale inversely (rewards) to maintain fairness
        if stat in ["loot_quality", "xp_gain", "gold_gain"]:
            multiplier = 1.0 / multiplier  # Higher difficulty = better rewards

        return base_value * multiplier

    def get_difficulty_display(self, player_id: str) -> str:
        """Get human-readable difficulty display."""
        profile = self.get_profile(player_id)
        return f"{profile.current_level.name} ({profile.current_level.value}x)"
