"""Daily Challenges System - time-limited procedural quests with bonus rewards."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import time


class ChallengeType(Enum):
    """Types of daily challenges."""
    COMBAT = "combat"
    EXPLORATION = "exploration"
    PUZZLE = "puzzle"
    DIALOGUE = "dialogue"
    SURVIVAL = "survival"
    CRAFTING = "crafting"


class ChallengeDifficulty(Enum):
    """Challenge difficulty levels."""
    EASY = 1
    NORMAL = 2
    HARD = 3
    EXTREME = 4


@dataclass
class DailyChallenge:
    """A daily challenge."""
    id: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    title: str
    description: str
    objective: str
    xp_reward: int
    gold_reward: int
    created_date: int  # Unix timestamp
    duration_hours: int = 24
    bonus_multiplier: float = 1.0  # Extra rewards for first completion


@dataclass
class PlayerChallengeProgress:
    """A player's progress on a daily challenge."""
    player_id: str
    challenge_id: str
    started_time: int
    completed: bool = False
    progress_percent: int = 0
    completion_time: Optional[int] = None
    bonus_collected: bool = False


class DailyChallengeSystem:
    """Manages daily challenges and player progression."""

    def __init__(self):
        self.challenges: Dict[str, DailyChallenge] = {}
        self.player_progress: Dict[str, Dict[str, PlayerChallengeProgress]] = {}
        self.challenge_rotations: Dict[int, List[str]] = {}  # day -> challenge_ids
        self.current_day: int = 0
        self.next_challenge_id = 0
        self._init_challenge_pool()

    def _init_challenge_pool(self) -> None:
        """Initialize a pool of challenges."""
        challenge_templates = [
            ("Goblin Hunt", ChallengeType.COMBAT, ChallengeDifficulty.NORMAL, "Defeat 10 goblins", 100, 500),
            ("Forest Scout", ChallengeType.EXPLORATION, ChallengeDifficulty.EASY, "Explore 5 new locations", 80, 400),
            ("Dragon Slayer", ChallengeType.COMBAT, ChallengeDifficulty.HARD, "Defeat 1 dragon", 200, 1000),
            ("Ancient Puzzle", ChallengeType.PUZZLE, ChallengeDifficulty.NORMAL, "Solve 3 puzzles", 120, 600),
            ("Legendary Loot", ChallengeType.EXPLORATION, ChallengeDifficulty.HARD, "Find 2 legendary items", 150, 800),
            ("Master Crafter", ChallengeType.CRAFTING, ChallengeDifficulty.NORMAL, "Craft 5 items", 110, 550),
            ("Diplomat", ChallengeType.DIALOGUE, ChallengeDifficulty.EASY, "Complete 3 dialogue quests", 90, 450),
            ("Survival Expert", ChallengeType.SURVIVAL, ChallengeDifficulty.HARD, "Survive for 1 hour", 180, 900),
        ]

        for i, (title, ctype, difficulty, objective, xp, gold) in enumerate(challenge_templates):
            challenge_id = f"challenge_{i}"
            self.challenges[challenge_id] = DailyChallenge(
                id=challenge_id,
                challenge_type=ctype,
                difficulty=difficulty,
                title=title,
                description=f"{title} - {difficulty.name} difficulty",
                objective=objective,
                xp_reward=xp,
                gold_reward=gold,
                created_date=int(time.time()),
                bonus_multiplier=1.5,  # 50% bonus
            )

    def get_today_challenges(self) -> List[DailyChallenge]:
        """Get challenges for today."""
        today = self._get_day_number()

        if today not in self.challenge_rotations:
            # Generate 3 random challenges for today
            import random
            selected_ids = random.sample(list(self.challenges.keys()), min(3, len(self.challenges)))
            self.challenge_rotations[today] = selected_ids

        return [self.challenges[cid] for cid in self.challenge_rotations[today]]

    def _get_day_number(self) -> int:
        """Get the current day number (days since epoch)."""
        return int(time.time()) // (24 * 3600)

    def start_challenge(self, player_id: str, challenge_id: str) -> Tuple[bool, str]:
        """Start a daily challenge."""
        if challenge_id not in self.challenges:
            return False, "Challenge not found"

        today_challenges = [c.id for c in self.get_today_challenges()]
        if challenge_id not in today_challenges:
            return False, "Challenge not available today"

        if player_id not in self.player_progress:
            self.player_progress[player_id] = {}

        # Check if already attempted
        if challenge_id in self.player_progress[player_id]:
            return False, "Already started this challenge today"

        progress = PlayerChallengeProgress(
            player_id=player_id,
            challenge_id=challenge_id,
            started_time=int(time.time()),
        )

        self.player_progress[player_id][challenge_id] = progress
        return True, f"Started challenge: {self.challenges[challenge_id].title}"

    def update_progress(self, player_id: str, challenge_id: str, progress_percent: int) -> None:
        """Update a challenge progress."""
        if player_id not in self.player_progress:
            return

        if challenge_id in self.player_progress[player_id]:
            progress = self.player_progress[player_id][challenge_id]
            progress.progress_percent = min(progress_percent, 100)

    def complete_challenge(self, player_id: str, challenge_id: str) -> Tuple[bool, str, Dict]:
        """Mark a challenge as completed."""
        if player_id not in self.player_progress or challenge_id not in self.player_progress[player_id]:
            return False, "Challenge not started", {}

        progress = self.player_progress[player_id][challenge_id]
        if progress.completed:
            return False, "Already completed", {}

        challenge = self.challenges[challenge_id]
        xp_reward = challenge.xp_reward
        gold_reward = challenge.gold_reward

        # Apply bonus if first completion today
        if not progress.bonus_collected:
            xp_reward = int(xp_reward * challenge.bonus_multiplier)
            gold_reward = int(gold_reward * challenge.bonus_multiplier)
            progress.bonus_collected = True

        progress.completed = True
        progress.completion_time = int(time.time())

        return True, f"Challenge completed!", {
            "xp": xp_reward,
            "gold": gold_reward,
            "title": challenge.title,
        }

    def get_player_progress(self, player_id: str) -> List[PlayerChallengeProgress]:
        """Get all challenges a player is working on."""
        return list(self.player_progress.get(player_id, {}).values())

    def get_available_challenges(self, player_id: str) -> List[DailyChallenge]:
        """Get challenges the player hasn't started yet."""
        player_started = set(self.player_progress.get(player_id, {}).keys())
        today_challenges = self.get_today_challenges()
        return [c for c in today_challenges if c.id not in player_started]

    def get_daily_summary(self, player_id: str) -> Dict:
        """Get summary of player's daily challenge progress."""
        progress_list = self.get_player_progress(player_id)
        completed = sum(1 for p in progress_list if p.completed)
        total = len(self.get_today_challenges())

        total_xp = 0
        total_gold = 0
        for p in progress_list:
            if p.completed:
                challenge = self.challenges[p.challenge_id]
                total_xp += challenge.xp_reward
                total_gold += challenge.gold_reward

        return {
            "completed": completed,
            "total": total,
            "xp_earned": total_xp,
            "gold_earned": total_gold,
            "completion_percent": (completed / total * 100) if total > 0 else 0,
        }

    def reset_daily_challenges(self) -> None:
        """Reset all player progress (call once per day)."""
        self.player_progress.clear()
