"""Prestige System - reset progression for hardcore players with exclusive rewards."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class PrestigeRank(Enum):
    """Prestige rank levels."""
    NONE = 0
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    PLATINUM = 4
    DIAMOND = 5
    ETERNAL = 6


@dataclass
class PrestigeReward:
    """Reward for reaching a prestige rank."""
    rank: PrestigeRank
    name: str
    description: str
    cosmetics: List[str] = field(default_factory=list)  # Cosmetic IDs
    stat_bonuses: Dict[str, float] = field(default_factory=dict)
    exclusive_title: str = ""


@dataclass
class PlayerPrestigeRecord:
    """Tracks a player's prestige history."""
    player_id: str
    current_rank: PrestigeRank = PrestigeRank.NONE
    total_prestiges: int = 0  # Times completely reset
    prestige_xp: int = 0  # XP toward next prestige
    prestige_xp_required: int = 100000  # XP needed for prestige
    earned_rewards: Set[str] = field(default_factory=set)  # Reward IDs earned
    exclusive_cosmetics: List[str] = field(default_factory=list)
    playtime_hours: float = 0.0
    highest_level_achieved: int = 1


class PrestigeSystem:
    """Manages prestige progression and exclusive rewards."""

    def __init__(self):
        self.player_records: Dict[str, PlayerPrestigeRecord] = {}
        self.prestige_rewards: Dict[PrestigeRank, PrestigeReward] = {}
        self._init_prestige_rewards()

    def _init_prestige_rewards(self) -> None:
        """Initialize prestige rank rewards."""
        self.prestige_rewards[PrestigeRank.BRONZE] = PrestigeReward(
            rank=PrestigeRank.BRONZE,
            name="Bronze Star",
            description="First prestige achieved",
            stat_bonuses={"xp_gain": 0.05},
            exclusive_title="Initiate",
        )

        self.prestige_rewards[PrestigeRank.SILVER] = PrestigeReward(
            rank=PrestigeRank.SILVER,
            name="Silver Star",
            description="Reached 2 prestiges",
            stat_bonuses={"xp_gain": 0.10, "loot_quality": 0.05},
            exclusive_title="Veteran",
        )

        self.prestige_rewards[PrestigeRank.GOLD] = PrestigeReward(
            rank=PrestigeRank.GOLD,
            name="Gold Star",
            description="Reached 3 prestiges",
            stat_bonuses={"xp_gain": 0.15, "loot_quality": 0.10},
            exclusive_title="Master",
        )

        self.prestige_rewards[PrestigeRank.PLATINUM] = PrestigeReward(
            rank=PrestigeRank.PLATINUM,
            name="Platinum Star",
            description="Reached 4 prestiges",
            stat_bonuses={"xp_gain": 0.20, "loot_quality": 0.15},
            exclusive_title="Legend",
        )

        self.prestige_rewards[PrestigeRank.DIAMOND] = PrestigeReward(
            rank=PrestigeRank.DIAMOND,
            name="Diamond Star",
            description="Reached 5 prestiges",
            stat_bonuses={"xp_gain": 0.25, "loot_quality": 0.20},
            exclusive_title="Immortal",
        )

        self.prestige_rewards[PrestigeRank.ETERNAL] = PrestigeReward(
            rank=PrestigeRank.ETERNAL,
            name="Eternal Star",
            description="Reached 6+ prestiges",
            stat_bonuses={"xp_gain": 0.30, "loot_quality": 0.25},
            exclusive_title="Eternal",
        )

    def get_player_record(self, player_id: str) -> PlayerPrestigeRecord:
        """Get or create player prestige record."""
        if player_id not in self.player_records:
            self.player_records[player_id] = PlayerPrestigeRecord(player_id=player_id)
        return self.player_records[player_id]

    def can_prestige(self, player_id: str, current_level: int) -> Tuple[bool, str]:
        """Check if player can prestige."""
        record = self.get_player_record(player_id)

        # Must be max level
        if current_level < 50:
            return False, "Must reach level 50 to prestige"

        # Must have enough prestige XP
        if record.prestige_xp < record.prestige_xp_required:
            return False, f"Need {record.prestige_xp_required - record.prestige_xp} more prestige XP"

        return True, "Ready to prestige"

    def prestige(self, player_id: str) -> Tuple[bool, str]:
        """Perform a prestige reset."""
        record = self.get_player_record(player_id)

        if record.prestige_xp < record.prestige_xp_required:
            return False, "Not enough prestige XP"

        # Perform reset
        record.total_prestiges += 1
        record.prestige_xp -= record.prestige_xp_required
        record.prestige_xp_required = int(record.prestige_xp_required * 1.1)  # Increase requirement

        # Update rank
        if record.total_prestiges == 1:
            record.current_rank = PrestigeRank.BRONZE
        elif record.total_prestiges == 2:
            record.current_rank = PrestigeRank.SILVER
        elif record.total_prestiges == 3:
            record.current_rank = PrestigeRank.GOLD
        elif record.total_prestiges == 4:
            record.current_rank = PrestigeRank.PLATINUM
        elif record.total_prestiges == 5:
            record.current_rank = PrestigeRank.DIAMOND
        elif record.total_prestiges >= 6:
            record.current_rank = PrestigeRank.ETERNAL

        # Award rank reward
        reward = self.prestige_rewards.get(record.current_rank)
        if reward:
            record.earned_rewards.add(reward.name)
            record.exclusive_cosmetics.extend(reward.cosmetics)

        return True, f"Prestiged to {record.current_rank.name}! Character reset to level 1."

    def gain_prestige_xp(self, player_id: str, xp_amount: int) -> int:
        """Gain prestige XP (from regular XP)."""
        record = self.get_player_record(player_id)
        # Convert ~1% of regular XP to prestige XP
        prestige_xp = int(xp_amount * 0.01)
        record.prestige_xp += prestige_xp
        return prestige_xp

    def get_prestige_display(self, player_id: str) -> str:
        """Get prestige display for UI."""
        record = self.get_player_record(player_id)
        if record.current_rank == PrestigeRank.NONE:
            return "No Prestige"

        progress = (record.prestige_xp / record.prestige_xp_required) * 100
        return f"{record.current_rank.name} ★ ({progress:.0f}%)"

    def get_prestige_bonuses(self, player_id: str) -> Dict[str, float]:
        """Get stat bonuses from prestige."""
        record = self.get_player_record(player_id)
        reward = self.prestige_rewards.get(record.current_rank)
        if reward:
            return reward.stat_bonuses.copy()
        return {}

    def get_exclusive_title(self, player_id: str) -> str:
        """Get exclusive title for prestige rank."""
        record = self.get_player_record(player_id)
        reward = self.prestige_rewards.get(record.current_rank)
        if reward and reward.exclusive_title:
            return f"the {reward.exclusive_title}"
        return ""

    def record_playtime(self, player_id: str, hours: float) -> None:
        """Record playtime for prestige tracking."""
        record = self.get_player_record(player_id)
        record.playtime_hours += hours

    def record_level_achievement(self, player_id: str, level: int) -> None:
        """Record highest level achieved."""
        record = self.get_player_record(player_id)
        if level > record.highest_level_achieved:
            record.highest_level_achieved = level

    def get_prestige_stats(self, player_id: str) -> Dict:
        """Get detailed prestige statistics."""
        record = self.get_player_record(player_id)
        return {
            "rank": record.current_rank.name,
            "total_prestiges": record.total_prestiges,
            "prestige_xp": record.prestige_xp,
            "prestige_xp_required": record.prestige_xp_required,
            "playtime_hours": record.playtime_hours,
            "highest_level": record.highest_level_achieved,
        }


from typing import Tuple
