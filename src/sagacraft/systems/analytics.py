"""Player Analytics & Insights System - track gameplay metrics and provide recommendations."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import time


class PlayerActivity(Enum):
    """Types of player activities tracked."""
    COMBAT_ENGAGE = "combat_engage"
    QUEST_START = "quest_start"
    QUEST_COMPLETE = "quest_complete"
    AREA_VISIT = "area_visit"
    ITEM_EQUIP = "item_equip"
    SKILL_LEARN = "skill_learn"
    DIALOGUE_CHOICE = "dialogue_choice"
    DEATH = "death"
    LEVEL_UP = "level_up"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    SESSION_START = "session_start"
    SESSION_END = "session_end"


@dataclass
class ActivityLog:
    """Record of a single activity."""
    activity_type: PlayerActivity
    timestamp: int
    data: Dict = field(default_factory=dict)


@dataclass
class PlayerSession:
    """A gaming session."""
    session_id: str
    player_id: str
    start_time: int
    end_time: Optional[int] = None
    duration_seconds: int = 0
    areas_visited: List[str] = field(default_factory=list)
    quests_completed: int = 0
    combat_encounters: int = 0
    xp_gained: int = 0
    items_collected: int = 0


@dataclass
class PlayerStats:
    """Aggregated player statistics."""
    player_id: str
    total_playtime_hours: float = 0.0
    total_sessions: int = 0
    total_quests_completed: int = 0
    total_combat_encounters: int = 0
    avg_session_length_minutes: float = 0.0
    most_visited_area: Optional[str] = None
    least_visited_area: Optional[str] = None
    favorite_quest_type: Optional[str] = None
    death_count: int = 0
    total_xp_earned: int = 0
    total_items_collected: int = 0


@dataclass
class PlayerInsight:
    """An insight or recommendation for a player."""
    insight_id: str
    player_id: str
    title: str
    description: str
    recommendation: str
    insight_type: str  # "behavior", "progression", "challenge", "reward"
    priority: int  # 1-5, higher is more important
    generated_time: int


class AnalyticsSystem:
    """Tracks and analyzes player behavior and provides insights."""

    def __init__(self):
        self.activity_logs: Dict[str, List[ActivityLog]] = {}  # player_id -> activities
        self.sessions: Dict[str, PlayerSession] = {}
        self.player_stats: Dict[str, PlayerStats] = {}
        self.insights: Dict[str, List[PlayerInsight]] = {}
        self.next_insight_id = 0
        self.area_popularity: Dict[str, int] = {}  # area_id -> visit_count
        self.quest_popularity: Dict[str, int] = {}  # quest_id -> completion_count

    def log_activity(self, player_id: str, activity: PlayerActivity, data: Optional[Dict] = None) -> None:
        """Log a player activity."""
        if player_id not in self.activity_logs:
            self.activity_logs[player_id] = []

        log = ActivityLog(
            activity_type=activity,
            timestamp=int(time.time()),
            data=data or {}
        )
        self.activity_logs[player_id].append(log)

        # Update area/quest popularity
        if activity == PlayerActivity.AREA_VISIT and data and "area_id" in data:
            area_id = data["area_id"]
            self.area_popularity[area_id] = self.area_popularity.get(area_id, 0) + 1

        if activity == PlayerActivity.QUEST_COMPLETE and data and "quest_id" in data:
            quest_id = data["quest_id"]
            self.quest_popularity[quest_id] = self.quest_popularity.get(quest_id, 0) + 1

    def start_session(self, player_id: str, session_id: str) -> PlayerSession:
        """Start a new gaming session."""
        session = PlayerSession(
            session_id=session_id,
            player_id=player_id,
            start_time=int(time.time())
        )
        self.sessions[session_id] = session
        self.log_activity(player_id, PlayerActivity.SESSION_START, {"session_id": session_id})
        return session

    def end_session(self, session_id: str) -> Optional[PlayerSession]:
        """End a gaming session."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        session.end_time = int(time.time())
        session.duration_seconds = session.end_time - session.start_time

        self.log_activity(session.player_id, PlayerActivity.SESSION_END, {
            "session_id": session_id,
            "duration_seconds": session.duration_seconds
        })

        self._update_player_stats(session.player_id)
        return session

    def _update_player_stats(self, player_id: str) -> None:
        """Recalculate player statistics."""
        if player_id not in self.player_stats:
            self.player_stats[player_id] = PlayerStats(player_id=player_id)

        stats = self.player_stats[player_id]
        activities = self.activity_logs.get(player_id, [])

        # Calculate totals
        total_session_time = 0
        session_count = 0
        quests_completed = 0
        combat_count = 0
        xp_earned = 0
        items_collected = 0
        deaths = 0
        area_visits: Dict[str, int] = {}

        for activity in activities:
            if activity.activity_type == PlayerActivity.SESSION_END:
                session_count += 1
                if "duration_seconds" in activity.data:
                    total_session_time += activity.data["duration_seconds"]

            elif activity.activity_type == PlayerActivity.QUEST_COMPLETE:
                quests_completed += 1

            elif activity.activity_type == PlayerActivity.COMBAT_ENGAGE:
                combat_count += 1

            elif activity.activity_type == PlayerActivity.LEVEL_UP:
                if "xp" in activity.data:
                    xp_earned += activity.data["xp"]

            elif activity.activity_type == PlayerActivity.ITEM_EQUIP:
                items_collected += 1

            elif activity.activity_type == PlayerActivity.DEATH:
                deaths += 1

            elif activity.activity_type == PlayerActivity.AREA_VISIT:
                if "area_id" in activity.data:
                    area_id = activity.data["area_id"]
                    area_visits[area_id] = area_visits.get(area_id, 0) + 1

        stats.total_playtime_hours = total_session_time / 3600.0
        stats.total_sessions = session_count
        stats.total_quests_completed = quests_completed
        stats.total_combat_encounters = combat_count
        stats.avg_session_length_minutes = (total_session_time / session_count / 60.0) if session_count > 0 else 0
        stats.total_xp_earned = xp_earned
        stats.total_items_collected = items_collected
        stats.death_count = deaths

        # Find most/least visited areas
        if area_visits:
            stats.most_visited_area = max(area_visits, key=area_visits.get)
            stats.least_visited_area = min(area_visits, key=area_visits.get)

    def get_stats(self, player_id: str) -> PlayerStats:
        """Get player statistics."""
        if player_id not in self.player_stats:
            self.player_stats[player_id] = PlayerStats(player_id=player_id)
        return self.player_stats[player_id]

    def generate_insights(self, player_id: str) -> List[PlayerInsight]:
        """Generate AI insights and recommendations for a player."""
        stats = self.get_stats(player_id)
        new_insights = []

        # Check if player hasn't played much
        if stats.total_sessions < 3:
            insight = PlayerInsight(
                insight_id=f"insight_{self.next_insight_id}",
                player_id=player_id,
                title="Welcome Adventurer!",
                description="You're just starting your journey. Keep playing to unlock more features!",
                recommendation="Complete your first 5 quests to unlock special rewards.",
                insight_type="progression",
                priority=3,
                generated_time=int(time.time())
            )
            new_insights.append(insight)
            self.next_insight_id += 1

        # Check if player explores less traveled areas
        if stats.most_visited_area and stats.least_visited_area:
            if stats.least_visited_area != stats.most_visited_area:
                least_visits = self.area_popularity.get(stats.least_visited_area, 0)
                most_visits = self.area_popularity.get(stats.most_visited_area, 0)
                if most_visits > 0 and least_visits < most_visits // 3:
                    insight = PlayerInsight(
                        insight_id=f"insight_{self.next_insight_id}",
                        player_id=player_id,
                        title="Explore Hidden Areas",
                        description=f"You haven't explored {stats.least_visited_area} much.",
                        recommendation=f"Visit {stats.least_visited_area} to discover new challenges and rewards!",
                        insight_type="exploration",
                        priority=2,
                        generated_time=int(time.time())
                    )
                    new_insights.append(insight)
                    self.next_insight_id += 1

        # Check for high death count
        if stats.death_count > 10 and stats.total_quests_completed < 5:
            insight = PlayerInsight(
                insight_id=f"insight_{self.next_insight_id}",
                player_id=player_id,
                title="Difficulty Challenge",
                description="You're struggling with combat. Consider adjusting difficulty or upgrading equipment.",
                recommendation="Try easier quests or upgrade your gear. Don't give up!",
                insight_type="challenge",
                priority=4,
                generated_time=int(time.time())
            )
            new_insights.append(insight)
            self.next_insight_id += 1

        # Check for progress achievement
        if stats.total_quests_completed >= 10:
            insight = PlayerInsight(
                insight_id=f"insight_{self.next_insight_id}",
                player_id=player_id,
                title="Quest Master!",
                description="You've completed 10 quests! You're becoming a true adventurer.",
                recommendation="Try harder difficulty quests for greater rewards.",
                insight_type="reward",
                priority=2,
                generated_time=int(time.time())
            )
            new_insights.append(insight)
            self.next_insight_id += 1

        # Store insights
        if player_id not in self.insights:
            self.insights[player_id] = []
        self.insights[player_id].extend(new_insights)

        return new_insights

    def get_trending_areas(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get trending areas by visit count."""
        sorted_areas = sorted(self.area_popularity.items(), key=lambda x: x[1], reverse=True)
        return sorted_areas[:limit]

    def get_trending_quests(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get trending quests by completion count."""
        sorted_quests = sorted(self.quest_popularity.items(), key=lambda x: x[1], reverse=True)
        return sorted_quests[:limit]

    def get_player_recommendations(self, player_id: str) -> List[str]:
        """Get personalized quest/area recommendations based on play history."""
        stats = self.get_stats(player_id)
        recommendations = []

        if stats.total_quests_completed < 5:
            recommendations.append("Complete beginner quests to learn the basics")

        if stats.total_combat_encounters == 0:
            recommendations.append("Try combat encounters to unlock combat skills")

        if stats.total_playtime_hours > 10 and stats.death_count > stats.total_quests_completed:
            recommendations.append("Consider increasing game difficulty for better rewards")

        trending_quests = self.get_trending_quests(3)
        if trending_quests:
            quest_ids = [q[0] for q in trending_quests]
            recommendations.append(f"Try trending quests: {', '.join(quest_ids)}")

        return recommendations

    def export_analytics_summary(self, player_id: str) -> Dict:
        """Export player analytics as a summary."""
        stats = self.get_stats(player_id)
        return {
            "player_id": player_id,
            "total_playtime_hours": round(stats.total_playtime_hours, 2),
            "total_sessions": stats.total_sessions,
            "avg_session_minutes": round(stats.avg_session_length_minutes, 1),
            "quests_completed": stats.total_quests_completed,
            "combat_encounters": stats.total_combat_encounters,
            "deaths": stats.death_count,
            "xp_earned": stats.total_xp_earned,
            "items_collected": stats.total_items_collected,
            "most_visited_area": stats.most_visited_area,
            "least_visited_area": stats.least_visited_area,
            "trending_areas": self.get_trending_areas(5),
            "trending_quests": self.get_trending_quests(5),
            "recommendations": self.get_player_recommendations(player_id)
        }
