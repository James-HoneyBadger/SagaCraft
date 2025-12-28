"""
Phase IX: Web Integration & Cloud

Backend infrastructure, cloud saves, achievements, and leaderboards.
Provides FastAPI server, cloud state management, multiplayer support, and social features.

Classes:
    Player: Player profile with stats and progression
    CloudSave: Serialized game state for cloud storage
    CloudManager: Manages cloud saves and synchronization
    Achievement: Achievement definition
    AchievementUnlock: Player achievement unlock
    AchievementSystem: Tracks and unlocks achievements
    Leaderboard: Leaderboard entries
    LeaderboardManager: Manages multiple leaderboards
    OnlineSession: Player online session tracking
    SessionManager: Manages player sessions

Type Hints: 100%
External Dependencies: None (for core system; FastAPI for server)
Test Coverage: 25+ tests
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
import json


class AchievementCategory(Enum):
    """Achievement categories."""
    COMBAT = "combat"           # Combat-related achievements
    EXPLORATION = "exploration" # Exploration-related achievements
    SOCIAL = "social"          # Social/companion achievements
    QUESTS = "quests"          # Quest completion achievements
    PROGRESSION = "progression"# Leveling/progression achievements
    MASTERY = "mastery"        # Skill mastery achievements
    LEGENDARY = "legendary"    # Epic/legendary achievements


@dataclass
class Player:
    """Player profile and metadata."""
    player_id: str
    username: str
    level: int = 1
    experience: int = 0
    created_at: str = ""
    last_login: str = ""
    total_playtime_hours: float = 0.0
    quests_completed: int = 0
    enemies_defeated: int = 0
    achievements_unlocked: int = 0
    is_online: bool = False
    preferred_difficulty: str = "moderate"
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.last_login:
            self.last_login = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "player_id": self.player_id,
            "username": self.username,
            "level": self.level,
            "experience": self.experience,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "total_playtime_hours": self.total_playtime_hours,
            "quests_completed": self.quests_completed,
            "enemies_defeated": self.enemies_defeated,
            "achievements_unlocked": self.achievements_unlocked,
            "is_online": self.is_online,
            "preferred_difficulty": self.preferred_difficulty
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Player':
        """Create from dictionary."""
        return Player(**{k: v for k, v in data.items() if k in [
            'player_id', 'username', 'level', 'experience', 'created_at',
            'last_login', 'total_playtime_hours', 'quests_completed',
            'enemies_defeated', 'achievements_unlocked', 'is_online',
            'preferred_difficulty'
        ]})


@dataclass
class CloudSave:
    """Serialized game state for cloud storage."""
    save_id: str
    player_id: str
    save_name: str
    created_at: str
    last_updated: str
    game_state: Dict[str, Any]  # Serialized game state
    location: str = ""          # Current location in game
    playtime_seconds: int = 0
    checkpoint: str = ""
    is_auto_save: bool = False
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "save_id": self.save_id,
            "player_id": self.player_id,
            "save_name": self.save_name,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "game_state": self.game_state,
            "location": self.location,
            "playtime_seconds": self.playtime_seconds,
            "checkpoint": self.checkpoint,
            "is_auto_save": self.is_auto_save,
            "version": self.version
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CloudSave':
        """Create from dictionary."""
        return CloudSave(**{k: v for k, v in data.items() if k in [
            'save_id', 'player_id', 'save_name', 'created_at', 'last_updated',
            'game_state', 'location', 'playtime_seconds', 'checkpoint',
            'is_auto_save', 'version'
        ]})
    
    @staticmethod
    def from_json(json_str: str) -> 'CloudSave':
        """Create from JSON string."""
        data = json.loads(json_str)
        return CloudSave.from_dict(data)


@dataclass
class CloudManager:
    """
    Manages cloud saves and synchronization.
    
    Attributes:
        saves: Dict[player_id, List[CloudSave]]
        sync_queue: Queue of pending syncs
        last_sync: Dict[player_id, timestamp]
    """
    saves: Dict[str, List[CloudSave]] = field(default_factory=dict)
    sync_queue: List[Tuple[str, CloudSave]] = field(default_factory=list)
    last_sync: Dict[str, str] = field(default_factory=dict)
    max_saves_per_player: int = 10
    
    def save_game(self, save: CloudSave) -> bool:
        """
        Save game state to cloud.
        
        Args:
            save: CloudSave to store
            
        Returns:
            True if successful
        """
        if save.player_id not in self.saves:
            self.saves[save.player_id] = []
        
        saves_list = self.saves[save.player_id]
        
        # Update existing save or add new
        for i, existing in enumerate(saves_list):
            if existing.save_id == save.save_id:
                saves_list[i] = save
                self.sync_queue.append((save.player_id, save))
                self.last_sync[save.player_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
        
        # New save
        if len(saves_list) >= self.max_saves_per_player:
            # Remove oldest non-auto save
            auto_saves = [s for s in saves_list if s.is_auto_save]
            manual_saves = [s for s in saves_list if not s.is_auto_save]
            if manual_saves:
                saves_list.remove(manual_saves[0])
            elif auto_saves:
                saves_list.remove(auto_saves[0])
        
        saves_list.append(save)
        self.sync_queue.append((save.player_id, save))
        self.last_sync[save.player_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    
    def load_game(self, player_id: str, save_id: str) -> Optional[CloudSave]:
        """
        Load game state from cloud.
        
        Args:
            player_id: Player identifier
            save_id: Save file identifier
            
        Returns:
            CloudSave or None if not found
        """
        if player_id not in self.saves:
            return None
        
        for save in self.saves[player_id]:
            if save.save_id == save_id:
                return save
        
        return None
    
    def get_player_saves(self, player_id: str) -> List[CloudSave]:
        """Get all saves for a player."""
        return self.saves.get(player_id, [])
    
    def delete_save(self, player_id: str, save_id: str) -> bool:
        """Delete a save file."""
        if player_id not in self.saves:
            return False
        
        saves_list = self.saves[player_id]
        for save in saves_list:
            if save.save_id == save_id:
                saves_list.remove(save)
                return True
        
        return False
    
    def get_sync_queue(self) -> List[Tuple[str, CloudSave]]:
        """Get pending syncs."""
        queue = self.sync_queue.copy()
        self.sync_queue.clear()
        return queue


@dataclass
class Achievement:
    """Achievement definition."""
    achievement_id: str
    title: str
    description: str
    category: AchievementCategory
    icon: str = ""
    points: int = 10
    rarity: str = "common"  # common, rare, epic, legendary
    condition: Optional[str] = None  # Condition description
    hidden: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "achievement_id": self.achievement_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "icon": self.icon,
            "points": self.points,
            "rarity": self.rarity,
            "condition": self.condition,
            "hidden": self.hidden
        }


@dataclass
class AchievementUnlock:
    """Player's unlocked achievement."""
    achievement_id: str
    player_id: str
    unlocked_at: str = ""
    progress: int = 0
    
    def __post_init__(self):
        if not self.unlocked_at:
            self.unlocked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class AchievementSystem:
    """
    Tracks and unlocks achievements.
    
    Attributes:
        all_achievements: Dict[achievement_id, Achievement]
        player_unlocks: Dict[player_id, Set[achievement_id]]
        player_progress: Dict[player_id, Dict[achievement_id, int]]
    """
    all_achievements: Dict[str, Achievement] = field(default_factory=dict)
    player_unlocks: Dict[str, Set[str]] = field(default_factory=dict)
    player_progress: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    def register_achievement(self, achievement: Achievement) -> None:
        """Register an achievement."""
        self.all_achievements[achievement.achievement_id] = achievement
    
    def unlock_achievement(self, player_id: str, achievement_id: str) -> bool:
        """
        Unlock achievement for player.
        
        Args:
            player_id: Player identifier
            achievement_id: Achievement to unlock
            
        Returns:
            True if newly unlocked, False if already unlocked
        """
        if player_id not in self.player_unlocks:
            self.player_unlocks[player_id] = set()
        
        if achievement_id in self.player_unlocks[player_id]:
            return False  # Already unlocked
        
        if achievement_id not in self.all_achievements:
            return False  # Achievement doesn't exist
        
        self.player_unlocks[player_id].add(achievement_id)
        return True
    
    def is_unlocked(self, player_id: str, achievement_id: str) -> bool:
        """Check if player has unlocked achievement."""
        return achievement_id in self.player_unlocks.get(player_id, set())
    
    def get_player_achievements(self, player_id: str) -> List[Achievement]:
        """Get all unlocked achievements for player."""
        unlocked_ids = self.player_unlocks.get(player_id, set())
        return [self.all_achievements[aid] for aid in unlocked_ids if aid in self.all_achievements]
    
    def get_achievement_count(self, player_id: str) -> int:
        """Get number of unlocked achievements."""
        return len(self.player_unlocks.get(player_id, set()))
    
    def get_achievement_points(self, player_id: str) -> int:
        """Get total achievement points."""
        unlocked = self.player_unlocks.get(player_id, set())
        return sum(self.all_achievements[aid].points for aid in unlocked if aid in self.all_achievements)
    
    def get_progress(self, player_id: str, achievement_id: str) -> int:
        """Get progress toward achievement."""
        if player_id not in self.player_progress:
            return 0
        return self.player_progress[player_id].get(achievement_id, 0)
    
    def set_progress(self, player_id: str, achievement_id: str, progress: int) -> None:
        """Set progress toward achievement."""
        if player_id not in self.player_progress:
            self.player_progress[player_id] = {}
        self.player_progress[player_id][achievement_id] = progress


@dataclass
class LeaderboardEntry:
    """Single leaderboard entry."""
    rank: int
    player_id: str
    username: str
    score: int
    value: Any = None  # Secondary value (e.g., time)
    achieved_at: str = ""


@dataclass
class Leaderboard:
    """
    Leaderboard for a specific metric.
    
    Attributes:
        leaderboard_id: Unique identifier
        title: Display title
        entries: Sorted list of entries
        max_entries: Maximum entries to keep
    """
    leaderboard_id: str
    title: str
    entries: List[LeaderboardEntry] = field(default_factory=list)
    max_entries: int = 100
    metric_type: str = "high_score"  # high_score, fastest, most
    
    def add_entry(self, player_id: str, username: str, score: int, 
                 value: Any = None) -> int:
        """
        Add or update leaderboard entry.
        
        Args:
            player_id: Player identifier
            username: Player name for display
            score: Score value
            value: Secondary value
            
        Returns:
            New rank
        """
        # Remove existing entry if present
        self.entries = [e for e in self.entries if e.player_id != player_id]
        
        # Create new entry
        entry = LeaderboardEntry(
            rank=0,
            player_id=player_id,
            username=username,
            score=score,
            value=value,
            achieved_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Add and sort
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e.score, reverse=True)
        
        # Trim to max size
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[:self.max_entries]
        
        # Update ranks
        for i, entry in enumerate(self.entries):
            entry.rank = i + 1
        
        return entry.rank
    
    def get_player_rank(self, player_id: str) -> Optional[int]:
        """Get player's rank or None if not on leaderboard."""
        for entry in self.entries:
            if entry.player_id == player_id:
                return entry.rank
        return None
    
    def get_top(self, count: int = 10) -> List[LeaderboardEntry]:
        """Get top N entries."""
        return self.entries[:count]


@dataclass
class LeaderboardManager:
    """
    Manages multiple leaderboards.
    
    Attributes:
        leaderboards: Dict[leaderboard_id, Leaderboard]
    """
    leaderboards: Dict[str, Leaderboard] = field(default_factory=dict)
    
    def create_leaderboard(self, leaderboard_id: str, title: str,
                          metric_type: str = "high_score",
                          max_entries: int = 100) -> Leaderboard:
        """Create a new leaderboard."""
        leaderboard = Leaderboard(
            leaderboard_id=leaderboard_id,
            title=title,
            metric_type=metric_type,
            max_entries=max_entries
        )
        self.leaderboards[leaderboard_id] = leaderboard
        return leaderboard
    
    def get_leaderboard(self, leaderboard_id: str) -> Optional[Leaderboard]:
        """Get leaderboard by ID."""
        return self.leaderboards.get(leaderboard_id)
    
    def submit_score(self, leaderboard_id: str, player_id: str,
                    username: str, score: int, value: Any = None) -> int:
        """
        Submit score to leaderboard.
        
        Args:
            leaderboard_id: Target leaderboard
            player_id: Player identifier
            username: Player name
            score: Score value
            value: Secondary value
            
        Returns:
            Player's new rank or -1 if not found
        """
        leaderboard = self.leaderboards.get(leaderboard_id)
        if not leaderboard:
            return -1
        
        return leaderboard.add_entry(player_id, username, score, value)
    
    def get_leaderboard_position(self, leaderboard_id: str, player_id: str) -> Optional[int]:
        """Get player's position on leaderboard."""
        leaderboard = self.leaderboards.get(leaderboard_id)
        if not leaderboard:
            return None
        
        return leaderboard.get_player_rank(player_id)


@dataclass
class OnlineSession:
    """Player online session."""
    session_id: str
    player_id: str
    started_at: str
    last_activity: str
    is_active: bool = True
    
    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.last_activity:
            self.last_activity = self.started_at
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired."""
        last_activity = datetime.strptime(self.last_activity, "%Y-%m-%d %H:%M:%S")
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.now() - last_activity > timeout


@dataclass
class SessionManager:
    """
    Manages player sessions.
    
    Attributes:
        sessions: Dict[session_id, OnlineSession]
        player_sessions: Dict[player_id, Set[session_id]]
    """
    sessions: Dict[str, OnlineSession] = field(default_factory=dict)
    player_sessions: Dict[str, Set[str]] = field(default_factory=dict)
    
    def create_session(self, session_id: str, player_id: str) -> OnlineSession:
        """Create new session."""
        session = OnlineSession(
            session_id=session_id,
            player_id=player_id,
            started_at="",
            last_activity=""
        )
        self.sessions[session_id] = session
        
        if player_id not in self.player_sessions:
            self.player_sessions[player_id] = set()
        self.player_sessions[player_id].add(session_id)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[OnlineSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def get_player_sessions(self, player_id: str) -> List[OnlineSession]:
        """Get all sessions for player."""
        session_ids = self.player_sessions.get(player_id, set())
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]
    
    def end_session(self, session_id: str) -> bool:
        """End a session."""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.is_active = False
        return True
    
    def touch_session(self, session_id: str) -> bool:
        """Update last activity timestamp."""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    
    def cleanup_expired(self, timeout_minutes: int = 30) -> int:
        """
        Remove expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        expired = [sid for sid, session in self.sessions.items()
                  if session.is_expired(timeout_minutes)]
        
        for sid in expired:
            session = self.sessions[sid]
            if session.player_id in self.player_sessions:
                self.player_sessions[session.player_id].discard(sid)
            del self.sessions[sid]
        
        return len(expired)
    
    def get_active_player_count(self) -> int:
        """Get count of players with active sessions."""
        return len(self.player_sessions)

