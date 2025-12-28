"""Battle Pass System - seasonal progression with cosmetic unlocks."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class BattlePassTier(Enum):
    """Battle pass tier levels."""
    FREE = "free"  # Free tier
    PREMIUM = "premium"  # Paid tier


@dataclass
class BattlePassReward:
    """A reward in the battle pass."""
    id: str
    name: str
    tier: int  # 1-100
    rarity: str  # common, rare, epic, legendary
    reward_type: str  # cosmetic_skin, emote, mount_skin, weapon_skin, etc
    is_free: bool = False  # Available in free tier


@dataclass
class BattlePassSeason:
    """A battle pass season."""
    season_id: str
    name: str
    number: int  # Season 1, 2, etc
    description: str
    start_date: int  # Unix timestamp
    end_date: int  # Unix timestamp
    total_tiers: int = 100
    free_rewards: List[BattlePassReward] = field(default_factory=list)
    premium_rewards: List[BattlePassReward] = field(default_factory=list)
    theme: str = ""  # Season theme (e.g., "Ancient Ruins")


@dataclass
class PlayerBattlePassProgress:
    """A player's progress in current season."""
    player_id: str
    season_id: str
    current_tier: int = 1
    xp_accumulated: int = 0
    tier_xp_required: int = 1000  # XP needed per tier
    has_premium: bool = False
    unlocked_rewards: List[str] = field(default_factory=list)


class BattlePassSystem:
    """Manages seasonal battle pass progression."""

    def __init__(self):
        self.seasons: Dict[str, BattlePassSeason] = {}
        self.current_season_id: Optional[str] = None
        self.player_progress: Dict[str, PlayerBattlePassProgress] = {}
        self.all_rewards: Dict[str, BattlePassReward] = {}

    def create_season(self, season: BattlePassSeason) -> None:
        """Create a new battle pass season."""
        self.seasons[season.season_id] = season
        self.current_season_id = season.season_id

        # Index all rewards
        for reward in season.free_rewards + season.premium_rewards:
            self.all_rewards[reward.id] = reward

    def get_current_season(self) -> Optional[BattlePassSeason]:
        """Get the currently active season."""
        if self.current_season_id:
            return self.seasons.get(self.current_season_id)
        return None

    def get_player_progress(self, player_id: str) -> Optional[PlayerBattlePassProgress]:
        """Get a player's current season progress."""
        return self.player_progress.get(player_id)

    def join_season(self, player_id: str, season_id: str, has_premium: bool = False) -> PlayerBattlePassProgress:
        """Join a season."""
        progress = PlayerBattlePassProgress(
            player_id=player_id,
            season_id=season_id,
            has_premium=has_premium,
        )
        self.player_progress[player_id] = progress
        return progress

    def gain_xp(self, player_id: str, xp_amount: int) -> Tuple[bool, str, int]:
        """Gain XP in battle pass."""
        progress = self.get_player_progress(player_id)
        if not progress:
            return False, "Not in any season", 0

        progress.xp_accumulated += xp_amount

        # Check for tier ups
        tiers_gained = 0
        while progress.xp_accumulated >= progress.tier_xp_required:
            if progress.current_tier >= 100:
                break

            progress.xp_accumulated -= progress.tier_xp_required
            progress.current_tier += 1
            tiers_gained += 1

            # Auto-unlock rewards
            self._unlock_tier_rewards(player_id, progress.current_tier)

        return True, f"Gained {xp_amount} XP", tiers_gained

    def _unlock_tier_rewards(self, player_id: str, tier: int) -> None:
        """Automatically unlock rewards for reaching a tier."""
        progress = self.get_player_progress(player_id)
        if not progress:
            return

        season = self.seasons.get(progress.season_id)
        if not season:
            return

        # Unlock free rewards at this tier
        for reward in season.free_rewards:
            if reward.tier == tier and reward.id not in progress.unlocked_rewards:
                progress.unlocked_rewards.append(reward.id)

        # Unlock premium rewards if player has premium
        if progress.has_premium:
            for reward in season.premium_rewards:
                if reward.tier == tier and reward.id not in progress.unlocked_rewards:
                    progress.unlocked_rewards.append(reward.id)

    def purchase_premium(self, player_id: str) -> Tuple[bool, str]:
        """Purchase premium battle pass."""
        progress = self.get_player_progress(player_id)
        if not progress:
            return False, "Must join a season first"

        if progress.has_premium:
            return False, "Already have premium"

        progress.has_premium = True

        # Unlock all previous premium rewards
        season = self.seasons.get(progress.season_id)
        if season:
            for reward in season.premium_rewards:
                if reward.tier <= progress.current_tier:
                    if reward.id not in progress.unlocked_rewards:
                        progress.unlocked_rewards.append(reward.id)

        return True, "Premium battle pass purchased!"

    def get_unlocked_rewards(self, player_id: str) -> List[BattlePassReward]:
        """Get all unlocked rewards for a player."""
        progress = self.get_player_progress(player_id)
        if not progress:
            return []

        rewards = []
        for reward_id in progress.unlocked_rewards:
            if reward_id in self.all_rewards:
                rewards.append(self.all_rewards[reward_id])
        return rewards

    def get_tier_progress(self, player_id: str) -> Dict:
        """Get detailed tier progress."""
        progress = self.get_player_progress(player_id)
        if not progress:
            return {}

        progress_pct = (progress.xp_accumulated / progress.tier_xp_required) * 100
        return {
            "current_tier": progress.current_tier,
            "total_tiers": 100,
            "xp": progress.xp_accumulated,
            "xp_required": progress.tier_xp_required,
            "progress_percent": progress_pct,
            "has_premium": progress.has_premium,
        }


from typing import Tuple
