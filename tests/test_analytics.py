"""Tests for the Analytics system."""

import unittest
import time
from sagacraft.systems.analytics import (
    AnalyticsSystem,
    PlayerActivity,
    ActivityLog,
)


class TestAnalyticsSystem(unittest.TestCase):
    """Test the analytics system."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = AnalyticsSystem()
        self.player_id = "test_player_1"

    def test_log_activity(self):
        """Test logging an activity."""
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.QUEST_START,
            {"quest_id": "quest_1"}
        )

        logs = self.analytics.activity_logs[self.player_id]
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].activity_type, PlayerActivity.QUEST_START)
        self.assertEqual(logs[0].data["quest_id"], "quest_1")

    def test_session_tracking(self):
        """Test session start and end."""
        session = self.analytics.start_session(self.player_id, "session_1")
        self.assertEqual(session.player_id, self.player_id)
        self.assertIsNotNone(session.start_time)

        time.sleep(1.1)  # Sleep to ensure measurable duration
        ended_session = self.analytics.end_session("session_1")
        self.assertIsNotNone(ended_session)
        self.assertIsNotNone(ended_session.end_time)
        self.assertGreaterEqual(ended_session.duration_seconds, 1)

    def test_area_popularity_tracking(self):
        """Test area visit tracking."""
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.AREA_VISIT,
            {"area_id": "forest_1"}
        )
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.AREA_VISIT,
            {"area_id": "forest_1"}
        )
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.AREA_VISIT,
            {"area_id": "castle_1"}
        )

        self.assertEqual(self.analytics.area_popularity["forest_1"], 2)
        self.assertEqual(self.analytics.area_popularity["castle_1"], 1)

    def test_quest_popularity_tracking(self):
        """Test quest completion tracking."""
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.QUEST_COMPLETE,
            {"quest_id": "deliver_letter"}
        )
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.QUEST_COMPLETE,
            {"quest_id": "deliver_letter"}
        )

        self.assertEqual(self.analytics.quest_popularity["deliver_letter"], 2)

    def test_player_stats_generation(self):
        """Test player stats calculation."""
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.QUEST_COMPLETE,
            {"quest_id": "q1"}
        )
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.COMBAT_ENGAGE,
            {}
        )
        self.analytics.log_activity(
            self.player_id,
            PlayerActivity.LEVEL_UP,
            {"xp": 100}
        )

        self._update_stats(self.player_id)
        stats = self.analytics.get_stats(self.player_id)

        self.assertEqual(stats.total_quests_completed, 1)
        self.assertEqual(stats.total_combat_encounters, 1)
        self.assertEqual(stats.total_xp_earned, 100)

    def test_insights_generation(self):
        """Test insight generation."""
        insights = self.analytics.generate_insights(self.player_id)
        # New player should get welcome insight
        self.assertGreater(len(insights), 0)
        self.assertEqual(insights[0].title, "Welcome Adventurer!")

    def test_trending_areas(self):
        """Test trending area calculation."""
        self.analytics.log_activity("p1", PlayerActivity.AREA_VISIT, {"area_id": "forest"})
        self.analytics.log_activity("p2", PlayerActivity.AREA_VISIT, {"area_id": "forest"})
        self.analytics.log_activity("p3", PlayerActivity.AREA_VISIT, {"area_id": "cave"})

        trending = self.analytics.get_trending_areas(2)
        self.assertEqual(trending[0][0], "forest")
        self.assertEqual(trending[0][1], 2)

    def test_trending_quests(self):
        """Test trending quest calculation."""
        self.analytics.log_activity("p1", PlayerActivity.QUEST_COMPLETE, {"quest_id": "rescue"})
        self.analytics.log_activity("p2", PlayerActivity.QUEST_COMPLETE, {"quest_id": "rescue"})
        self.analytics.log_activity("p3", PlayerActivity.QUEST_COMPLETE, {"quest_id": "explore"})

        trending = self.analytics.get_trending_quests(2)
        self.assertEqual(trending[0][0], "rescue")
        self.assertEqual(trending[0][1], 2)

    def test_player_recommendations(self):
        """Test recommendation generation."""
        recommendations = self.analytics.get_player_recommendations(self.player_id)
        self.assertGreater(len(recommendations), 0)
        # New player should get beginner recommendations
        self.assertTrue(any("beginner" in r.lower() for r in recommendations))

    def test_analytics_export(self):
        """Test analytics summary export."""
        summary = self.analytics.export_analytics_summary(self.player_id)

        self.assertIn("player_id", summary)
        self.assertIn("total_playtime_hours", summary)
        self.assertIn("total_sessions", summary)
        self.assertIn("recommendations", summary)

    def _update_stats(self, player_id: str) -> None:
        """Helper to update stats."""
        self.analytics._update_player_stats(player_id)


if __name__ == "__main__":
    unittest.main()
