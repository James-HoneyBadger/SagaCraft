"""Tests for Enhanced PvP Arena System."""

import unittest
from sagacraft.systems.pvp_arenas import (
    PvPArenaSystem,
    ArenaRank,
)


class TestEnhancedPvPArenas(unittest.TestCase):
    """Test enhanced PvP features."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = PvPArenaSystem()

    def test_create_tournament(self):
        """Test creating a tournament."""
        success, msg = self.system.create_tournament(
            "tourney_1", "Grand Championship", max_players=8
        )

        self.assertTrue(success)
        self.assertIn("tourney_1", self.system.tournaments)

    def test_register_for_tournament(self):
        """Test registering for tournament."""
        self.system.create_tournament("tourney_1", "Test", max_players=4)

        success, msg = self.system.register_for_tournament("tourney_1", "player1")

        self.assertTrue(success)
        self.assertIn("player1", self.system.tournaments["tourney_1"]["players"])

    def test_tournament_auto_start(self):
        """Test tournament auto-starts when full."""
        self.system.create_tournament("tourney_1", "Test", max_players=2)

        self.system.register_for_tournament("tourney_1", "player1")
        self.system.register_for_tournament("tourney_1", "player2")

        tournament = self.system.tournaments["tourney_1"]
        self.assertEqual(tournament["status"], "in_progress")
        self.assertGreater(len(tournament["bracket"]), 0)

    def test_complete_tournament_match(self):
        """Test completing tournament match."""
        self.system.create_tournament("tourney_1", "Test", max_players=2)
        self.system.register_for_tournament("tourney_1", "player1")
        self.system.register_for_tournament("tourney_1", "player2")

        tournament = self.system.tournaments["tourney_1"]
        match_id = tournament["bracket"][0]["match_id"]

        success, result = self.system.complete_tournament_match(
            "tourney_1", match_id, "player1"
        )

        self.assertTrue(success)
        self.assertTrue(result.get("tournament_complete"))

    def test_tournament_bracket_generation(self):
        """Test tournament bracket is generated correctly."""
        self.system.create_tournament("tourney_1", "Test", max_players=4)

        for i in range(4):
            self.system.register_for_tournament("tourney_1", f"player{i}")

        tournament = self.system.tournaments["tourney_1"]
        self.assertEqual(len(tournament["bracket"]), 2)  # 4 players = 2 matches

    def test_get_tournament_bracket(self):
        """Test getting tournament bracket info."""
        self.system.create_tournament("tourney_1", "Test", max_players=2)

        bracket_info = self.system.get_tournament_bracket("tourney_1")

        self.assertEqual(bracket_info["name"], "Test")
        self.assertEqual(bracket_info["status"], "registration")

    def test_start_spectating(self):
        """Test starting spectator mode."""
        # Create a match
        self.system.queue_for_match("player1")
        self.system.queue_for_match("player2")

        match = self.system.match_history[-1]

        success, msg = self.system.start_spectating("spectator1", match.match_id)

        self.assertTrue(success)
        self.assertIn("spectator1", self.system.spectators[match.match_id])

    def test_stop_spectating(self):
        """Test stopping spectator mode."""
        self.system.queue_for_match("player1")
        self.system.queue_for_match("player2")

        match = self.system.match_history[-1]
        self.system.start_spectating("spectator1", match.match_id)

        success, msg = self.system.stop_spectating("spectator1", match.match_id)

        self.assertTrue(success)
        self.assertNotIn("spectator1", self.system.spectators[match.match_id])

    def test_get_spectators(self):
        """Test getting list of spectators."""
        self.system.queue_for_match("player1")
        self.system.queue_for_match("player2")

        match = self.system.match_history[-1]
        self.system.start_spectating("spectator1", match.match_id)
        self.system.start_spectating("spectator2", match.match_id)

        spectators = self.system.get_spectators(match.match_id)

        self.assertEqual(len(spectators), 2)
        self.assertIn("spectator1", spectators)

    def test_get_live_matches(self):
        """Test getting live matches."""
        self.system.queue_for_match("player1")
        self.system.queue_for_match("player2")

        live_matches = self.system.get_live_matches()

        self.assertGreater(len(live_matches), 0)
        self.assertIn("match_id", live_matches[0])

    def test_get_seasonal_rankings(self):
        """Test getting seasonal rankings."""
        # Create some stats
        self.system.get_stats("player1").seasonal_wins = 10
        self.system.get_stats("player1").seasonal_losses = 2
        self.system.get_stats("player1").rating = 1500

        rankings = self.system.get_seasonal_rankings()

        self.assertGreater(len(rankings), 0)
        self.assertIn("win_rate", rankings[0])

    def test_reset_season(self):
        """Test resetting season stats."""
        stats = self.system.get_stats("player1")
        stats.seasonal_wins = 50
        stats.seasonal_losses = 10
        stats.rating = 2000

        self.system.reset_season()

        self.assertEqual(stats.seasonal_wins, 0)
        self.assertEqual(stats.seasonal_losses, 0)
        self.assertLess(stats.rating, 2000)  # Soft reset

    def test_get_rank_distribution(self):
        """Test getting rank distribution."""
        # Create players at different ranks
        self.system.get_stats("player1").rating = 1000
        self.system.get_stats("player1").current_rank = ArenaRank.BRONZE
        
        self.system.get_stats("player2").rating = 1500
        self.system.get_stats("player2").current_rank = ArenaRank.GOLD

        distribution = self.system.get_rank_distribution()

        self.assertEqual(distribution["bronze"], 1)
        self.assertEqual(distribution["gold"], 1)

    def test_tournament_full_registration_fails(self):
        """Test registration fails when tournament is full."""
        self.system.create_tournament("tourney_1", "Test", max_players=2)

        self.system.register_for_tournament("tourney_1", "player1")
        self.system.register_for_tournament("tourney_1", "player2")

        success, msg = self.system.register_for_tournament("tourney_1", "player3")

        self.assertFalse(success)
        self.assertIn("full", msg.lower())

    def test_duplicate_spectator_fails(self):
        """Test duplicate spectator registration fails."""
        self.system.queue_for_match("player1")
        self.system.queue_for_match("player2")

        match = self.system.match_history[-1]
        self.system.start_spectating("spectator1", match.match_id)

        success, msg = self.system.start_spectating("spectator1", match.match_id)

        self.assertFalse(success)

    def test_seasonal_win_rate_calculation(self):
        """Test win rate calculation in seasonal rankings."""
        stats = self.system.get_stats("player1")
        stats.seasonal_wins = 7
        stats.seasonal_losses = 3
        stats.rating = 1400

        rankings = self.system.get_seasonal_rankings()

        player_ranking = next(r for r in rankings if r["player_id"] == "player1")
        self.assertEqual(player_ranking["win_rate"], 70.0)

    def test_filter_seasonal_rankings_by_rank(self):
        """Test filtering seasonal rankings by rank."""
        self.system.get_stats("player1").current_rank = ArenaRank.GOLD
        self.system.get_stats("player1").rating = 1500
        
        self.system.get_stats("player2").current_rank = ArenaRank.SILVER
        self.system.get_stats("player2").rating = 1300

        rankings = self.system.get_seasonal_rankings(rank=ArenaRank.GOLD)

        self.assertEqual(len(rankings), 1)
        self.assertEqual(rankings[0]["player_id"], "player1")


if __name__ == "__main__":
    unittest.main()
