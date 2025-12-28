"""Custom Game Modes System - hardcore, permadeath, speedrun, puzzle-only modes."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Tuple


class GameMode(Enum):
    """Available game modes with different rule sets."""
    NORMAL = "normal"  # Standard gameplay
    HARDCORE = "hardcore"  # No respawning, limited resources
    PERMADEATH = "permadeath"  # Single life, character permanently deleted on death
    SPEEDRUN = "speedrun"  # Race against time to complete objectives
    PUZZLE_ONLY = "puzzle_only"  # No combat, puzzle solving only
    IRON_MAN = "iron_man"  # No saving/loading, one save only
    PACIFIST = "pacifist"  # Complete without killing enemies
    CUSTOM = "custom"  # Player-defined rules


@dataclass
class GameModeRules:
    """Rules defining how a game mode modifies base game."""
    mode: GameMode
    allows_respawn: bool = True
    allows_save_load: bool = True
    allows_combat: bool = True
    allows_dialogue: bool = True
    allows_resource_management: bool = True
    allows_fast_travel: bool = True
    difficulty_multiplier: float = 1.0
    xp_multiplier: float = 1.0
    loot_multiplier: float = 1.0
    time_limit_minutes: Optional[int] = None  # For speedrun
    max_deaths_allowed: Optional[int] = None  # For limited lives
    required_objectives: List[str] = field(default_factory=list)
    restricted_items: List[str] = field(default_factory=list)  # Items that can't be used
    restricted_skills: List[str] = field(default_factory=list)  # Skills that can't be used
    score_multiplier: float = 1.0  # Leaderboard impact


@dataclass
class ModePlaySession:
    """Tracks a single playthrough in a game mode."""
    session_id: str
    player_id: str
    mode: GameMode
    start_time: int  # Unix timestamp
    end_time: Optional[int] = None
    objectives_completed: List[str] = field(default_factory=list)
    deaths_count: int = 0
    final_score: int = 0
    completed: bool = False
    abandoned: bool = False


class GameModeManager:
    """Manages game modes and their rule enforcement."""

    def __init__(self):
        self.modes: Dict[GameMode, GameModeRules] = {}
        self.active_sessions: Dict[str, ModePlaySession] = {}
        self.mode_achievements: Dict[GameMode, List[str]] = {}
        self._init_default_modes()

    def _init_default_modes(self) -> None:
        """Initialize default game modes."""
        self.modes[GameMode.NORMAL] = GameModeRules(
            mode=GameMode.NORMAL,
            difficulty_multiplier=1.0,
            xp_multiplier=1.0,
            loot_multiplier=1.0,
        )

        self.modes[GameMode.HARDCORE] = GameModeRules(
            mode=GameMode.HARDCORE,
            allows_respawn=False,
            max_deaths_allowed=3,
            difficulty_multiplier=1.5,
            xp_multiplier=2.0,
            loot_multiplier=2.0,
            score_multiplier=3.0,
        )

        self.modes[GameMode.PERMADEATH] = GameModeRules(
            mode=GameMode.PERMADEATH,
            allows_respawn=False,
            allows_save_load=False,
            max_deaths_allowed=1,
            difficulty_multiplier=2.0,
            xp_multiplier=3.0,
            loot_multiplier=3.0,
            score_multiplier=5.0,
        )

        self.modes[GameMode.SPEEDRUN] = GameModeRules(
            mode=GameMode.SPEEDRUN,
            time_limit_minutes=60,
            difficulty_multiplier=1.0,
            xp_multiplier=1.5,
            loot_multiplier=1.5,
            score_multiplier=2.0,
        )

        self.modes[GameMode.PUZZLE_ONLY] = GameModeRules(
            mode=GameMode.PUZZLE_ONLY,
            allows_combat=False,
            difficulty_multiplier=0.5,
            xp_multiplier=0.75,
            loot_multiplier=0.5,
            score_multiplier=0.5,
            required_objectives=["solve_all_puzzles"],
        )

        self.modes[GameMode.IRON_MAN] = GameModeRules(
            mode=GameMode.IRON_MAN,
            allows_save_load=False,
            max_deaths_allowed=0,
            difficulty_multiplier=1.75,
            xp_multiplier=2.5,
            loot_multiplier=2.0,
            score_multiplier=4.0,
        )

        self.modes[GameMode.PACIFIST] = GameModeRules(
            mode=GameMode.PACIFIST,
            allows_combat=False,
            difficulty_multiplier=0.8,
            xp_multiplier=1.2,
            loot_multiplier=0.8,
            score_multiplier=1.5,
            required_objectives=["complete_without_killing"],
        )

    def create_session(self, player_id: str, mode: GameMode, start_time: int) -> ModePlaySession:
        """Create a new game mode session."""
        session = ModePlaySession(
            session_id=f"{player_id}_{mode.value}_{start_time}",
            player_id=player_id,
            mode=mode,
            start_time=start_time,
        )
        self.active_sessions[session.session_id] = session
        return session

    def get_mode_rules(self, mode: GameMode) -> GameModeRules:
        """Get rules for a specific game mode."""
        return self.modes.get(mode, self.modes[GameMode.NORMAL])

    def is_action_allowed(self, session_id: str, action: str) -> Tuple[bool, str]:
        """Check if an action is allowed in the current game mode."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False, "Session not found"

        rules = self.get_mode_rules(session.mode)

        # Check action against mode rules
        action_checks = {
            "respawn": rules.allows_respawn,
            "save_game": rules.allows_save_load,
            "load_game": rules.allows_save_load,
            "use_combat": rules.allows_combat,
            "use_dialogue": rules.allows_dialogue,
            "manage_resources": rules.allows_resource_management,
            "fast_travel": rules.allows_fast_travel,
        }

        if action in action_checks:
            allowed = action_checks[action]
            if not allowed:
                return False, f"Action '{action}' not allowed in {session.mode.value} mode"

        return True, "Action allowed"

    def record_death(self, session_id: str) -> Tuple[bool, str]:
        """Record a death in the session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False, "Session not found"

        rules = self.get_mode_rules(session.mode)
        session.deaths_count += 1

        # Check if game over
        if rules.max_deaths_allowed is not None:
            if session.deaths_count > rules.max_deaths_allowed:
                session.abandoned = True
                return False, f"Game Over! Max deaths exceeded in {session.mode.value} mode"

        return True, "Death recorded"

    def complete_objective(self, session_id: str, objective: str) -> None:
        """Mark an objective as completed in a session."""
        session = self.active_sessions.get(session_id)
        if session and objective not in session.objectives_completed:
            session.objectives_completed.append(objective)

    def end_session(self, session_id: str, final_score: int) -> ModePlaySession:
        """End a game mode session and calculate final score."""
        session = self.active_sessions.get(session_id)
        if session:
            session.end_time = int(__import__("time").time())
            session.final_score = final_score
            session.completed = True
        return session

    def calculate_leaderboard_score(self, session: ModePlaySession) -> int:
        """Calculate a player's score for the leaderboard."""
        rules = self.get_mode_rules(session.mode)
        base_score = session.final_score
        
        # Apply mode multiplier
        mode_adjusted = int(base_score * rules.score_multiplier)
        
        # Death penalty (for modes with deaths)
        death_penalty = session.deaths_count * 100 if rules.max_deaths_allowed is not None else 0
        
        # Objective bonus
        objective_bonus = len(session.objectives_completed) * 50
        
        return max(0, mode_adjusted + objective_bonus - death_penalty)

    def add_custom_mode(self, mode_name: str, rules: GameModeRules) -> None:
        """Allow players to define custom modes (stored per-player)."""
        # This would typically be stored in a custom_modes dict per player
        # For now, we just validate the rules
        if mode_name and isinstance(rules, GameModeRules):
            custom_enum = GameMode.CUSTOM
            # In production, you'd create a unique custom mode key per player
            pass

    def get_mode_description(self, mode: GameMode) -> str:
        """Get human-readable description of a game mode."""
        descriptions = {
            GameMode.NORMAL: "Standard gameplay with all features enabled.",
            GameMode.HARDCORE: "No respawning, limited resources. Higher rewards.",
            GameMode.PERMADEATH: "Single life. Character permanently lost on death.",
            GameMode.SPEEDRUN: "Race against time to complete objectives.",
            GameMode.PUZZLE_ONLY: "No combat. Solve puzzles to progress.",
            GameMode.IRON_MAN: "No saving/loading. Single save only.",
            GameMode.PACIFIST: "Complete game without killing enemies.",
        }
        return descriptions.get(mode, "Unknown mode")
