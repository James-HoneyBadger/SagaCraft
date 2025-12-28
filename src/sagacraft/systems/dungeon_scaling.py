"""Dungeon Scaling System - adventures adjust complexity based on party composition."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class DungeonDifficulty(Enum):
    """Difficulty scaling levels."""
    EASY = 0.7
    NORMAL = 1.0
    HARD = 1.3
    EXTREME = 1.6


@dataclass
class DungeonScaler:
    """Scales dungeon difficulty based on party."""
    base_difficulty: DungeonDifficulty
    party_size: int
    average_party_level: int
    has_healer: bool = False
    has_tank: bool = False
    has_dps: bool = False
    synergy_bonus: float = 0.0


class DungeonScalingSystem:
    """Manages dynamic dungeon difficulty adjustment."""

    def __init__(self):
        self.active_dungeons: Dict[str, DungeonScaler] = {}

    def analyze_party(
        self,
        party_members: List[Dict],
        base_level: int = 1,
    ) -> DungeonScaler:
        """Analyze party composition and calculate scaling."""
        party_size = len(party_members)
        total_level = sum(m.get("level", 1) for m in party_members)
        avg_level = total_level // party_size if party_size > 0 else 1

        # Detect roles
        has_healer = any(m.get("class") == "Paladin" or m.get("class") == "Druid" for m in party_members)
        has_tank = any(m.get("class") == "Warrior" for m in party_members)
        has_dps = any(m.get("class") in ["Mage", "Rogue", "Ranger"] for m in party_members)

        # Calculate synergy bonus
        synergy = 0.0
        if has_tank and has_dps:
            synergy += 0.1
        if has_healer and (has_tank or has_dps):
            synergy += 0.1
        if party_size >= 4:
            synergy += 0.05

        scaler = DungeonScaler(
            base_difficulty=DungeonDifficulty.NORMAL,
            party_size=party_size,
            average_party_level=avg_level,
            has_healer=has_healer,
            has_tank=has_tank,
            has_dps=has_dps,
            synergy_bonus=synergy,
        )

        return scaler

    def calculate_scaled_stats(
        self, base_health: int, base_damage: int, scaler: DungeonScaler
    ) -> Tuple[int, int]:
        """Calculate enemy stats after difficulty scaling."""
        # Difficulty multiplier
        diff_mult = scaler.base_difficulty.value

        # Party size adjustment (smaller parties = harder)
        size_mult = 1.0 + (4 - scaler.party_size) * 0.1

        # Level adjustment
        level_diff = scaler.average_party_level - 1
        level_mult = 1.0 + (level_diff * 0.05)

        # Apply synergy reduction (well-composed party gets help)
        total_mult = (diff_mult * size_mult * level_mult) - scaler.synergy_bonus

        scaled_health = int(base_health * total_mult)
        scaled_damage = int(base_damage * total_mult)

        return max(1, scaled_health), max(1, scaled_damage)

    def get_scaling_info(self, scaler: DungeonScaler) -> Dict:
        """Get human-readable scaling information."""
        diff_mult = scaler.base_difficulty.value
        size_mult = 1.0 + (4 - scaler.party_size) * 0.1
        total = diff_mult * size_mult - scaler.synergy_bonus

        return {
            "party_size": scaler.party_size,
            "avg_level": scaler.average_party_level,
            "difficulty": scaler.base_difficulty.name,
            "difficulty_multiplier": f"{diff_mult:.2f}x",
            "party_composition_bonus": f"{scaler.synergy_bonus:.2f}" if scaler.synergy_bonus > 0 else "None",
            "final_multiplier": f"{total:.2f}x",
            "estimated_duration": self._estimate_duration(total),
        }

    def _estimate_duration(self, multiplier: float) -> str:
        """Estimate dungeon duration based on scaling."""
        base_minutes = 30
        estimated = int(base_minutes * multiplier)
        return f"{estimated} minutes"

    def should_scale_up(self, scaler: DungeonScaler) -> bool:
        """Check if dungeon should scale up."""
        return scaler.average_party_level >= 20 and scaler.party_size >= 3

    def should_scale_down(self, scaler: DungeonScaler) -> bool:
        """Check if dungeon should scale down."""
        return scaler.party_size == 1 or (scaler.average_party_level < 5 and scaler.party_size < 2)

    def get_recommended_difficulty(self, scaler: DungeonScaler) -> DungeonDifficulty:
        """Get recommended difficulty for a party."""
        if self.should_scale_down(scaler):
            return DungeonDifficulty.EASY

        if scaler.average_party_level >= 30 and scaler.party_size >= 4:
            return DungeonDifficulty.HARD

        if scaler.average_party_level >= 20:
            return DungeonDifficulty.HARD

        if scaler.average_party_level >= 15:
            return DungeonDifficulty.NORMAL

        return DungeonDifficulty.EASY
