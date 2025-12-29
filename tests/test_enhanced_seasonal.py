"""Tests for Enhanced Seasonal Content System."""

import unittest
import time
from sagacraft.systems.seasonal import (
    SeasonalContentSystem,
    Season,
    SeasonalEvent,
    EventType,
)


class TestEnhancedSeasonalContent(unittest.TestCase):
    """Test enhanced seasonal features."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = SeasonalContentSystem()
        
        # Create a test season
        season = Season(
            season_id="season_1",
            name="Winter Festival",
            number=1,
            start_date=int(time.time()) - 1000,
            end_date=int(time.time()) + 100000,
            theme="winter",
        )
        self.system.create_season(season)

    def test_create_tournament(self):
        """Test creating a tournament event."""
        success, msg = self.system.create_tournament(
            "tourney_1", "Champion's Cup", brackets=16
        )

        self.assertTrue(success)
        self.assertIn("tourney_1", self.system.events)
        self.assertEqual(self.system.events["tourney_1"].event_type, EventType.TOURNAMENT)

    def test_register_for_tournament(self):
        """Test registering for tournament."""
        self.system.create_tournament("tourney_1", "Test Tournament")

        success, msg = self.system.register_for_tournament("player1", "tourney_1")

        self.assertTrue(success)
        self.assertIn("player1", self.system.tournament_registrations["tourney_1"])

    def test_duplicate_tournament_registration(self):
        """Test duplicate registration fails."""
        self.system.create_tournament("tourney_1", "Test Tournament")
        self.system.register_for_tournament("player1", "tourney_1")

        success, msg = self.system.register_for_tournament("player1", "tourney_1")

        self.assertFalse(success)

    def test_spawn_world_boss(self):
        """Test spawning world boss."""
        success, msg = self.system.spawn_world_boss(
            "boss_1", "Ancient Dragon", health=500000, duration_hours=48
        )

        self.assertTrue(success)
        self.assertIn("boss_1", self.system.events)
        self.assertEqual(self.system.boss_health["boss_1"]["max"], 500000)

    def test_damage_world_boss(self):
        """Test dealing damage to world boss."""
        self.system.spawn_world_boss("boss_1", "Dragon", health=1000)

        success, result = self.system.damage_world_boss("player1", "boss_1", 300)

        self.assertTrue(success)
        self.assertEqual(result["damage_dealt"], 300)
        self.assertEqual(result["boss_health"], 700)

    def test_defeat_world_boss(self):
        """Test defeating world boss."""
        self.system.spawn_world_boss("boss_1", "Dragon", health=1000)

        success, result = self.system.damage_world_boss("player1", "boss_1", 1000)

        self.assertTrue(success)
        self.assertTrue(result["defeated"])
        self.assertEqual(result["boss_health"], 0)

    def test_advance_season_pass(self):
        """Test advancing season pass."""
        success, result = self.system.advance_season_pass("player1", tiers=7)

        self.assertTrue(success)
        self.assertEqual(result["new_tier"], 8)  # Started at 1
        self.assertGreater(len(result["rewards"]), 0)

    def test_earn_season_xp(self):
        """Test earning season XP."""
        success, result = self.system.earn_season_xp("player1", 2500)

        self.assertTrue(success)
        self.assertEqual(result["total_xp"], 2500)

    def test_season_pass_tier_rewards(self):
        """Test season pass rewards at specific tiers."""
        success, result = self.system.advance_season_pass("player1", tiers=10)

        self.assertTrue(success)
        # Should have rewards at tier 5 and 10
        self.assertGreaterEqual(len(result["rewards"]), 2)

    def test_create_seasonal_storyline(self):
        """Test creating seasonal storyline."""
        chapters = ["Chapter 1", "Chapter 2", "Chapter 3"]
        success, msg = self.system.create_seasonal_storyline(
            "story_1", "The Winter Tale", chapters
        )

        self.assertTrue(success)
        self.assertIn("story_1", self.system.events)
        self.assertEqual(len(self.system.events["story_1"].story_chapters), 3)

    def test_get_leaderboard_events(self):
        """Test leaderboard by events completed."""
        # Create events and complete them
        event = SeasonalEvent(
            "event_1", "Test Event", EventType.FESTIVAL,
            "Test", int(time.time()) - 100, int(time.time()) + 100
        )
        self.system.events["event_1"] = event
        
        self.system.participate_in_event("player1", "event_1")
        self.system.complete_event("player1", "event_1")

        leaderboard = self.system.get_leaderboard(metric="events_completed")

        self.assertGreater(len(leaderboard), 0)
        self.assertEqual(leaderboard[0]["player_id"], "player1")

    def test_get_leaderboard_season_pass(self):
        """Test leaderboard by season pass tier."""
        self.system.advance_season_pass("player1", tiers=10)
        self.system.advance_season_pass("player2", tiers=5)

        leaderboard = self.system.get_leaderboard(metric="season_pass", limit=5)

        self.assertEqual(len(leaderboard), 2)
        self.assertEqual(leaderboard[0]["player_id"], "player1")
        self.assertEqual(leaderboard[0]["score"], 11)  # Started at 1

    def test_boss_contributions_tracking(self):
        """Test tracking player contributions to boss."""
        self.system.spawn_world_boss("boss_1", "Dragon", health=1000)

        self.system.damage_world_boss("player1", "boss_1", 300)
        self.system.damage_world_boss("player2", "boss_1", 200)

        self.assertEqual(self.system.boss_contributions["boss_1"]["player1"], 300)
        self.assertEqual(self.system.boss_contributions["boss_1"]["player2"], 200)


if __name__ == "__main__":
    unittest.main()
