"""Seasonal Content System - limited-time events with unique rewards."""

from dataclasses import dataclass, field
from enum import Enum
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
        current_time = int(__import__("time").time())
        season = self.get_current_season()
        if not season:
            return []

        return [e for e in season.events if e.start_date <= current_time <= e.end_date]

    def participate_in_event(self, player_id: str, event_id: str) -> Tuple[bool, str]:
        """Participate in a seasonal event."""
        event = self.events.get(event_id)
        if not event:
            return False, "Event not found"

        current_time = int(__import__("time").time())
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
