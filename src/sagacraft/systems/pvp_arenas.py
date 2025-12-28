"""PvP Arenas System - seasonal ranked combat with matchmaking."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class ArenaRank(Enum):
    """PvP rank tiers."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"


@dataclass
class PvPStats:
    """Player PvP statistics."""
    player_id: str
    wins: int = 0
    losses: int = 0
    current_rank: ArenaRank = ArenaRank.BRONZE
    rating: int = 1000
    seasonal_wins: int = 0
    seasonal_losses: int = 0
    matches_this_season: int = 0
    best_rating: int = 1000
    win_streak: int = 0
    loss_streak: int = 0


@dataclass
class PvPMatch:
    """A PvP match record."""
    match_id: str
    player1_id: str
    player2_id: str
    winner_id: str
    rating_change: int
    timestamp: int
    duration_seconds: int


class PvPArenaSystem:
    """Manages PvP matches and ranked seasons."""

    def __init__(self):
        self.player_stats: Dict[str, PvPStats] = {}
        self.match_history: List[PvPMatch] = []
        self.matchmaking_queue: List[str] = []
        self.next_match_id = 0
        self.elo_k_factor = 32  # Rating change per match

    def get_stats(self, player_id: str) -> PvPStats:
        """Get PvP stats for a player."""
        if player_id not in self.player_stats:
            self.player_stats[player_id] = PvPStats(player_id=player_id)
        return self.player_stats[player_id]

    def queue_for_match(self, player_id: str) -> Tuple[bool, str]:
        """Queue a player for ranked PvP."""
        if player_id in self.matchmaking_queue:
            return False, "Already in queue"

        self.matchmaking_queue.append(player_id)

        if len(self.matchmaking_queue) >= 2:
            self._create_match()

        return True, "Added to matchmaking queue"

    def _create_match(self) -> None:
        """Create a match from two queued players."""
        if len(self.matchmaking_queue) < 2:
            return

        player1 = self.matchmaking_queue.pop(0)
        player2 = self.matchmaking_queue.pop(0)

        match_id = f"pvp_match_{self.next_match_id}"
        self.next_match_id += 1

        match = PvPMatch(
            match_id=match_id,
            player1_id=player1,
            player2_id=player2,
            winner_id=player1,  # Placeholder
            rating_change=0,
            timestamp=int(__import__("time").time()),
            duration_seconds=0,
        )

        self.match_history.append(match)

    def record_match_result(
        self, match_id: str, winner_id: str, duration_seconds: int
    ) -> Tuple[bool, Dict]:
        """Record the result of a match."""
        match = next((m for m in self.match_history if m.match_id == match_id), None)
        if not match:
            return False, {}

        loser_id = match.player2_id if winner_id == match.player1_id else match.player1_id

        winner_stats = self.get_stats(winner_id)
        loser_stats = self.get_stats(loser_id)

        # Calculate rating changes (simplified ELO)
        rating_diff = loser_stats.rating - winner_stats.rating
        change = self.elo_k_factor if rating_diff < 0 else int(self.elo_k_factor * 1.5)

        winner_stats.wins += 1
        winner_stats.seasonal_wins += 1
        winner_stats.rating += change
        winner_stats.win_streak += 1
        winner_stats.loss_streak = 0

        loser_stats.losses += 1
        loser_stats.seasonal_losses += 1
        loser_stats.rating = max(800, loser_stats.rating - change)
        loser_stats.loss_streak += 1
        loser_stats.win_streak = 0

        # Update rank based on rating
        winner_stats.current_rank = self._rating_to_rank(winner_stats.rating)
        loser_stats.current_rank = self._rating_to_rank(loser_stats.rating)

        if winner_stats.rating > winner_stats.best_rating:
            winner_stats.best_rating = winner_stats.rating

        match.winner_id = winner_id
        match.rating_change = change
        match.duration_seconds = duration_seconds

        return True, {
            "winner_rating_change": change,
            "loser_rating_change": -change,
            "winner_new_rating": winner_stats.rating,
            "loser_new_rating": loser_stats.rating,
        }

    def _rating_to_rank(self, rating: int) -> ArenaRank:
        """Convert rating to rank."""
        if rating < 1200:
            return ArenaRank.BRONZE
        elif rating < 1400:
            return ArenaRank.SILVER
        elif rating < 1600:
            return ArenaRank.GOLD
        elif rating < 1800:
            return ArenaRank.PLATINUM
        elif rating < 2000:
            return ArenaRank.DIAMOND
        else:
            return ArenaRank.MASTER

    def get_leaderboard(self, limit: int = 100) -> List[Tuple[str, int, ArenaRank]]:
        """Get PvP leaderboard."""
        sorted_players = sorted(
            self.player_stats.items(), key=lambda x: x[1].rating, reverse=True
        )
        return [
            (pid, stats.rating, stats.current_rank)
            for pid, stats in sorted_players[:limit]
        ]

    def get_match_history(self, player_id: str, limit: int = 10) -> List[PvPMatch]:
        """Get match history for a player."""
        matches = [
            m for m in self.match_history
            if m.player1_id == player_id or m.player2_id == player_id
        ]
        return matches[-limit:]
