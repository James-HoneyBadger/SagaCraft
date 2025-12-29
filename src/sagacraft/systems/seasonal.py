"""Seasonal Content System - limited-time events with unique rewards."""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Dict, List, Optional, Tuple


class EventType(Enum):
    """Types of seasonal events."""
    FESTIVAL = "festival"
    DUNGEON_RAID = "dungeon_raid"
    WORLD_BOSS = "world_boss"
    INVASION = "invasion"
    TOURNAMENT = "tournament"
    STORYLINE = "storyline"


@dataclass
class SeasonalEvent:
    """A limited-time seasonal event."""
    event_id: str
    name: str
    event_type: EventType
    description: str
    start_date: int  # Unix timestamp
    end_date: int
    level_requirement: int = 1
    unique_rewards: List[str] = field(default_factory=list)
    story_chapters: List[str] = field(default_factory=list)
    participation_count: int = 0
    completion_rate: float = 0.0


@dataclass
class Season:
    """A game season with multiple events."""
    season_id: str
    name: str
    number: int
    start_date: int
    end_date: int
    theme: str
    events: List[SeasonalEvent] = field(default_factory=list)
    seasonal_cosmetics: List[str] = field(default_factory=list)
    story_progression: int = 0  # 0-100%


@dataclass
class PlayerSeasonProgress:
    """Player's progress in current season."""
    player_id: str
    season_id: str
    events_participated: List[str] = field(default_factory=list)
    events_completed: List[str] = field(default_factory=list)
    season_pass_tier: int = 1
    cosmetics_earned: List[str] = field(default_factory=list)
    story_progress: int = 0


class SeasonalContentSystem:
    """Manages seasonal events and content."""

    def __init__(self):
        self.seasons: Dict[str, Season] = {}
        self.current_season_id: Optional[str] = None
        self.events: Dict[str, SeasonalEvent] = {}
        self.player_progress: Dict[str, PlayerSeasonProgress] = {}

        # Enhanced feature state (kept explicit to avoid dynamic hasattr state)
        self.tournament_registrations: Dict[str, List[str]] = {}
        self.boss_health: Dict[str, Dict[str, int]] = {}
        self.boss_contributions: Dict[str, Dict[str, int]] = {}
        self.season_xp: Dict[str, int] = {}

    def create_season(self, season: Season) -> None:
        """Create a new season."""
        self.seasons[season.season_id] = season
        self.current_season_id = season.season_id

        # Index events
        for event in season.events:
            self.events[event.event_id] = event

    def get_current_season(self) -> Optional[Season]:
        """Get current active season."""
        if self.current_season_id:
            return self.seasons.get(self.current_season_id)
        return None

    def get_active_events(self) -> List[SeasonalEvent]:
        """Get all currently active events."""
        current_time = int(time.time())
        season = self.get_current_season()
        if not season:
            return []

        return [e for e in season.events if e.start_date <= current_time <= e.end_date]

    def participate_in_event(self, player_id: str, event_id: str) -> Tuple[bool, str]:
        """Participate in a seasonal event."""
        event = self.events.get(event_id)
        if not event:
            return False, "Event not found"

        current_time = int(time.time())
        if not (event.start_date <= current_time <= event.end_date):
            return False, "Event is not currently active"

        progress = self._get_progress(player_id)
        if event_id in progress.events_participated:
            return False, "Already participated in this event"

        progress.events_participated.append(event_id)
        event.participation_count += 1

        return True, f"Joined {event.name}"

    def complete_event(self, player_id: str, event_id: str) -> Tuple[bool, List[str]]:
        """Mark an event as completed."""
        event = self.events.get(event_id)
        if not event:
            return False, []

        progress = self._get_progress(player_id)
        if event_id in progress.events_completed:
            return False, []

        if event_id not in progress.events_participated:
            return False, []

        progress.events_completed.append(event_id)

        # Award cosmetics
        rewards = event.unique_rewards.copy()
        progress.cosmetics_earned.extend(rewards)

        # Update story progression
        if event.story_chapters:
            progress.story_progress += 10

        return True, rewards

    def _get_progress(self, player_id: str) -> PlayerSeasonProgress:
        """Get or create player season progress."""
        if player_id not in self.player_progress:
            season_id = self.current_season_id or "unknown"
            self.player_progress[player_id] = PlayerSeasonProgress(
                player_id=player_id, season_id=season_id
            )
        return self.player_progress[player_id]

    def get_event_rewards(self, event_id: str) -> List[str]:
        """Get rewards for an event."""
        event = self.events.get(event_id)
        if event:
            return event.unique_rewards
        return []

    def get_seasonal_cosmetics(self) -> List[str]:
        """Get all cosmetics available this season."""
        season = self.get_current_season()
        if season:
            return season.seasonal_cosmetics
        return []

    def get_story_progress(self, player_id: str) -> Dict:
        """Get player's story progression."""
        progress = self._get_progress(player_id)
        return {
            "current_chapter": progress.story_progress // 10,
            "total_chapters": 10,
            "progress_percent": progress.story_progress,
        }

    def get_season_summary(self, player_id: str) -> Dict:
        """Get player's season summary."""
        progress = self._get_progress(player_id)
        season = self.get_current_season()

        return {
            "season_name": season.name if season else "Unknown",
            "events_completed": len(progress.events_completed),
            "cosmetics_earned": len(progress.cosmetics_earned),
            "story_progress": progress.story_progress,
            "pass_tier": progress.season_pass_tier,
        }

    # Enhanced Features: Tournaments, World Bosses, and Progression

    def create_tournament(
        self, event_id: str, name: str, brackets: int = 8, prize_pool: List[str] = None
    ) -> Tuple[bool, str]:
        """Create a tournament event."""
        if event_id in self.events:
            return False, "Tournament already exists"

        event = SeasonalEvent(
            event_id=event_id,
            name=name,
            event_type=EventType.TOURNAMENT,
            description=f"Compete in {brackets}-player tournament",
            start_date=int(time.time()),
            end_date=int(time.time()) + 604800,  # 7 days
            unique_rewards=prize_pool or ["Champion Trophy", "Victory Banner"],
        )

        self.events[event_id] = event

        # Add to current season if exists
        if self.current_season_id and self.current_season_id in self.seasons:
            self.seasons[self.current_season_id].events.append(event)

        return True, f"Tournament '{name}' created"

    def register_for_tournament(self, player_id: str, event_id: str) -> Tuple[bool, str]:
        """Register player for tournament."""
        event = self.events.get(event_id)
        if not event or event.event_type != EventType.TOURNAMENT:
            return False, "Tournament not found"

        if event_id not in self.tournament_registrations:
            self.tournament_registrations[event_id] = []

        if player_id in self.tournament_registrations[event_id]:
            return False, "Already registered"

        self.tournament_registrations[event_id].append(player_id)
        return True, f"Registered for {event.name}"

    def spawn_world_boss(
        self, event_id: str, boss_name: str, health: int = 1000000, duration_hours: int = 24
    ) -> Tuple[bool, str]:
        """Spawn a world boss event."""
        if event_id in self.events:
            return False, "Boss event already exists"

        event = SeasonalEvent(
            event_id=event_id,
            name=f"World Boss: {boss_name}",
            event_type=EventType.WORLD_BOSS,
            description=f"Defeat {boss_name} with the community",
            start_date=int(time.time()),
            end_date=int(time.time()) + (duration_hours * 3600),
            unique_rewards=["Legendary Weapon", "Boss Title"],
        )

        self.events[event_id] = event

        self.boss_health[event_id] = {"current": health, "max": health}

        # Add to current season
        if self.current_season_id and self.current_season_id in self.seasons:
            self.seasons[self.current_season_id].events.append(event)

        return True, f"World boss '{boss_name}' has appeared!"

    def damage_world_boss(self, player_id: str, event_id: str, damage: int) -> Tuple[bool, Dict]:
        """Deal damage to world boss."""
        event = self.events.get(event_id)
        if not event or event.event_type != EventType.WORLD_BOSS:
            return False, {}

        if event_id not in self.boss_health:
            return False, {}

        boss = self.boss_health[event_id]
        boss["current"] = max(0, boss["current"] - damage)

        # Track contributions
        if event_id not in self.boss_contributions:
            self.boss_contributions[event_id] = {}

        self.boss_contributions[event_id][player_id] = (
            self.boss_contributions[event_id].get(player_id, 0) + damage
        )

        # Check if defeated
        defeated = boss["current"] == 0

        return True, {
            "damage_dealt": damage,
            "boss_health": boss["current"],
            "boss_max_health": boss["max"],
            "defeated": defeated,
            "percentage": (boss["current"] / boss["max"]) * 100 if boss["max"] > 0 else 0,
        }

    def advance_season_pass(self, player_id: str, tiers: int = 1) -> Tuple[bool, Dict]:
        """Advance player's season pass tier."""
        progress = self._get_progress(player_id)
        
        old_tier = progress.season_pass_tier
        progress.season_pass_tier += tiers

        # Grant tier rewards
        rewards = []
        for tier in range(old_tier + 1, progress.season_pass_tier + 1):
            if tier % 5 == 0:  # Every 5 tiers
                rewards.append(f"Tier {tier} Cosmetic")
            if tier % 10 == 0:  # Every 10 tiers
                rewards.append(f"Tier {tier} Legendary")

        progress.cosmetics_earned.extend(rewards)

        return True, {
            "old_tier": old_tier,
            "new_tier": progress.season_pass_tier,
            "rewards": rewards,
        }

    def earn_season_xp(self, player_id: str, xp_amount: int) -> Tuple[bool, Dict]:
        """Award season XP that progresses the pass."""
        current_xp = self.season_xp.get(player_id, 0)
        new_xp = current_xp + xp_amount
        self.season_xp[player_id] = new_xp

        # Calculate tier progression (1000 XP per tier)
        xp_per_tier = 1000
        tiers_gained = (new_xp // xp_per_tier) - (current_xp // xp_per_tier)

        result = {"xp_gained": xp_amount, "total_xp": new_xp}

        if tiers_gained > 0:
            success, tier_data = self.advance_season_pass(player_id, tiers_gained)
            result.update(tier_data)

        return True, result

    def create_seasonal_storyline(
        self, event_id: str, name: str, chapters: List[str], rewards_per_chapter: List[str] = None
    ) -> Tuple[bool, str]:
        """Create a seasonal story event with chapters."""
        if event_id in self.events:
            return False, "Storyline already exists"

        event = SeasonalEvent(
            event_id=event_id,
            name=name,
            event_type=EventType.STORYLINE,
            description=f"Experience the {name} story",
            start_date=int(time.time()),
            end_date=int(time.time()) + 2592000,  # 30 days
            story_chapters=chapters,
            unique_rewards=rewards_per_chapter or ["Story Emblem"],
        )

        self.events[event_id] = event

        # Add to current season
        if self.current_season_id and self.current_season_id in self.seasons:
            self.seasons[self.current_season_id].events.append(event)

        return True, f"Seasonal storyline '{name}' created with {len(chapters)} chapters"

    def get_leaderboard(self, metric: str = "events_completed", limit: int = 10) -> List[Dict]:
        """Get seasonal leaderboard."""
        if metric == "events_completed":
            ranked = sorted(
                self.player_progress.items(),
                key=lambda x: len(x[1].events_completed),
                reverse=True,
            )[:limit]
            return [
                {"player_id": p[0], "score": len(p[1].events_completed), "rank": i + 1}
                for i, p in enumerate(ranked)
            ]
        elif metric == "cosmetics_earned":
            ranked = sorted(
                self.player_progress.items(),
                key=lambda x: len(x[1].cosmetics_earned),
                reverse=True,
            )[:limit]
            return [
                {"player_id": p[0], "score": len(p[1].cosmetics_earned), "rank": i + 1}
                for i, p in enumerate(ranked)
            ]
        elif metric == "season_pass":
            ranked = sorted(
                self.player_progress.items(),
                key=lambda x: x[1].season_pass_tier,
                reverse=True,
            )[:limit]
            return [
                {"player_id": p[0], "score": p[1].season_pass_tier, "rank": i + 1}
                for i, p in enumerate(ranked)
            ]

        return []
