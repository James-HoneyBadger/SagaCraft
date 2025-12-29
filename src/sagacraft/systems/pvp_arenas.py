"""PvP Arenas System - seasonal ranked combat with matchmaking."""

from dataclasses import dataclass
from enum import Enum
import random
import time
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

        # Enhanced feature state (kept explicit to avoid dynamic hasattr state)
        self.tournaments: Dict[str, Dict] = {}
        self.spectators: Dict[str, List[str]] = {}

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
            timestamp=int(time.time()),
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

    # Enhanced Features: Tournaments and Spectator Mode

    def create_tournament(
        self, tournament_id: str, name: str, max_players: int = 8, prize_pool: Dict = None
    ) -> Tuple[bool, str]:
        """Create a tournament with bracket system."""
        if tournament_id in self.tournaments:
            return False, "Tournament already exists"

        tournament = {
            "tournament_id": tournament_id,
            "name": name,
            "max_players": max_players,
            "players": [],
            "bracket": [],
            "current_round": 0,
            "prize_pool": prize_pool or {"1st": "Champion Title", "2nd": "Runner-up Trophy"},
            "status": "registration",  # registration, in_progress, completed
            "winner": None,
        }

        self.tournaments[tournament_id] = tournament
        return True, f"Tournament '{name}' created"

    def register_for_tournament(self, tournament_id: str, player_id: str) -> Tuple[bool, str]:
        """Register player for tournament."""
        if tournament_id not in self.tournaments:
            return False, "Tournament not found"

        tournament = self.tournaments[tournament_id]

        if tournament["status"] != "registration":
            return False, "Tournament registration is closed"

        if player_id in tournament["players"]:
            return False, "Already registered"

        if len(tournament["players"]) >= tournament["max_players"]:
            return False, "Tournament is full"

        tournament["players"].append(player_id)

        # Auto-start if full
        if len(tournament["players"]) == tournament["max_players"]:
            self._start_tournament(tournament_id)

        return True, f"Registered for '{tournament['name']}'"

    def _start_tournament(self, tournament_id: str) -> None:
        """Start tournament and generate bracket."""
        tournament = self.tournaments[tournament_id]
        tournament["status"] = "in_progress"
        tournament["current_round"] = 1

        # Create bracket (simple single-elimination)
        players = tournament["players"].copy()
        random.shuffle(players)

        bracket = []
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                bracket.append({
                    "match_id": f"{tournament_id}_r1_m{i//2}",
                    "player1": players[i],
                    "player2": players[i + 1],
                    "winner": None,
                    "round": 1,
                })

        tournament["bracket"] = bracket

    def complete_tournament_match(
        self, tournament_id: str, match_id: str, winner_id: str
    ) -> Tuple[bool, Dict]:
        """Complete a tournament match."""
        if tournament_id not in self.tournaments:
            return False, {}

        tournament = self.tournaments[tournament_id]
        
        # Find and update match
        match = next((m for m in tournament["bracket"] if m["match_id"] == match_id), None)
        if not match:
            return False, {}

        match["winner"] = winner_id

        # Check if round complete
        current_round = tournament["current_round"]
        round_matches = [m for m in tournament["bracket"] if m["round"] == current_round]
        
        if all(m["winner"] for m in round_matches):
            # Advance to next round
            winners = [m["winner"] for m in round_matches]
            
            if len(winners) == 1:
                # Tournament complete
                tournament["status"] = "completed"
                tournament["winner"] = winners[0]
                return True, {"tournament_complete": True, "winner": winners[0]}
            
            # Create next round
            tournament["current_round"] += 1
            next_round = tournament["current_round"]
            
            for i in range(0, len(winners), 2):
                if i + 1 < len(winners):
                    tournament["bracket"].append({
                        "match_id": f"{tournament_id}_r{next_round}_m{i//2}",
                        "player1": winners[i],
                        "player2": winners[i + 1],
                        "winner": None,
                        "round": next_round,
                    })

        return True, {"round_complete": False}

    def get_tournament_bracket(self, tournament_id: str) -> Dict:
        """Get tournament bracket information."""
        if tournament_id not in self.tournaments:
            return {}

        tournament = self.tournaments[tournament_id]
        return {
            "name": tournament["name"],
            "status": tournament["status"],
            "current_round": tournament["current_round"],
            "bracket": tournament["bracket"],
            "winner": tournament.get("winner"),
        }

    def start_spectating(self, spectator_id: str, match_id: str) -> Tuple[bool, str]:
        """Start spectating a match."""
        if match_id not in self.spectators:
            self.spectators[match_id] = []

        if spectator_id in self.spectators[match_id]:
            return False, "Already spectating this match"

        self.spectators[match_id].append(spectator_id)
        return True, f"Now spectating match {match_id}"

    def stop_spectating(self, spectator_id: str, match_id: str) -> Tuple[bool, str]:
        """Stop spectating a match."""
        if match_id not in self.spectators:
            return False, "Not spectating this match"

        if spectator_id in self.spectators[match_id]:
            self.spectators[match_id].remove(spectator_id)
            return True, "Stopped spectating"

        return False, "Not spectating this match"

    def get_spectators(self, match_id: str) -> List[str]:
        """Get list of spectators for a match."""
        if match_id not in self.spectators:
            return []

        return self.spectators[match_id].copy()

    def get_live_matches(self) -> List[Dict]:
        """Get list of matches available for spectating."""
        # Return recent matches that are considered "live" (in progress)
        live_matches = []
        for match in self.match_history[-10:]:  # Last 10 matches
            if match.duration_seconds == 0:  # Still in progress
                live_matches.append({
                    "match_id": match.match_id,
                    "player1_id": match.player1_id,
                    "player2_id": match.player2_id,
                    "timestamp": match.timestamp,
                    "spectators": len(self.get_spectators(match.match_id)),
                })

        return live_matches

    def get_seasonal_rankings(self, rank: Optional[ArenaRank] = None) -> List[Dict]:
        """Get seasonal rankings, optionally filtered by rank."""
        rankings = []
        
        for player_id, stats in self.player_stats.items():
            if rank is None or stats.current_rank == rank:
                rankings.append({
                    "player_id": player_id,
                    "rating": stats.rating,
                    "rank": stats.current_rank.value,
                    "wins": stats.seasonal_wins,
                    "losses": stats.seasonal_losses,
                    "win_rate": (stats.seasonal_wins / (stats.seasonal_wins + stats.seasonal_losses) * 100)
                    if (stats.seasonal_wins + stats.seasonal_losses) > 0 else 0,
                })

        return sorted(rankings, key=lambda x: x["rating"], reverse=True)

    def reset_season(self) -> None:
        """Reset seasonal stats for all players."""
        for stats in self.player_stats.values():
            stats.seasonal_wins = 0
            stats.seasonal_losses = 0
            stats.matches_this_season = 0
            stats.win_streak = 0
            stats.loss_streak = 0
            # Soft reset rating (move 50% toward 1500)
            stats.rating = int(stats.rating + (1500 - stats.rating) * 0.5)
            stats.current_rank = self._rating_to_rank(stats.rating)

    def get_rank_distribution(self) -> Dict[str, int]:
        """Get distribution of players across ranks."""
        distribution = {rank.value: 0 for rank in ArenaRank}
        
        for stats in self.player_stats.values():
            distribution[stats.current_rank.value] += 1

        return distribution

