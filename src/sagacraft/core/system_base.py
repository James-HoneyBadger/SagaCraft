"""Base classes and mixins for all game systems - enables efficient architecture."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable
from collections import defaultdict


class SystemType(Enum):
    """Categories of game systems."""
    PROGRESSION = "progression"
    GAMEPLAY = "gameplay"
    SOCIAL = "social"
    CONTENT = "content"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class SystemConfig:
    """Base configuration for any game system."""
    system_id: str
    system_type: SystemType
    enabled: bool = True
    priority: int = 0  # Higher = executes first
    metadata: Dict[str, Any] = field(default_factory=dict)


class GameSystem(ABC):
    """
    Base class for all game systems. Provides common functionality
    and enforces consistent interface across all systems.
    """

    def __init__(self, config: SystemConfig):
        self.config = config
        self.id = config.system_id
        self.type = config.system_type
        self.enabled = config.enabled
        self.priority = config.priority
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._state: Dict[str, Any] = {}

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the system. Called once on startup."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate system state. Return True if valid."""
        pass

    def on(self, event: str, listener: Callable) -> None:
        """Register an event listener."""
        self._listeners[event].append(listener)

    def emit(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to all listeners."""
        for listener in self._listeners.get(event, []):
            listener(data or {})

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get system state by key."""
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """Set system state by key."""
        self._state[key] = value

    def reset_state(self) -> None:
        """Reset all system state."""
        self._state.clear()

    def enable(self) -> None:
        """Enable this system."""
        self.enabled = True
        self.emit("system:enabled")

    def disable(self) -> None:
        """Disable this system."""
        self.enabled = False
        self.emit("system:disabled")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.config.metadata.get(key, default)


class ProgressionSystem(GameSystem):
    """Base class for systems with progression tracking."""

    def __init__(self, config: SystemConfig):
        super().__init__(config)
        self.progression_data: Dict[str, Dict[str, int]] = defaultdict(dict)

    def add_progression(self, player_id: str, key: str, amount: int) -> int:
        """Add to progression and return new value."""
        current = self.progression_data[player_id].get(key, 0)
        new_value = current + amount
        self.progression_data[player_id][key] = new_value
        self.emit("progression:updated", {
            "player_id": player_id,
            "key": key,
            "old_value": current,
            "new_value": new_value,
        })
        return new_value

    def get_progression(self, player_id: str, key: str, default: int = 0) -> int:
        """Get progression value."""
        return self.progression_data[player_id].get(key, default)

    def reset_progression(self, player_id: str) -> None:
        """Reset player progression."""
        self.progression_data[player_id].clear()


class RankedSystem(GameSystem):
    """Base class for systems with ranking/leaderboards."""

    def __init__(self, config: SystemConfig):
        super().__init__(config)
        self.rankings: List[tuple] = []  # List of (player_id, score)
        self.player_scores: Dict[str, int] = {}

    def update_score(self, player_id: str, score: int) -> int:
        """Update player score and return rank."""
        self.player_scores[player_id] = score
        self._recompute_rankings()
        return self.get_rank(player_id)

    def get_score(self, player_id: str) -> int:
        """Get player score."""
        return self.player_scores.get(player_id, 0)

    def get_rank(self, player_id: str) -> int:
        """Get player rank (1-based)."""
        for rank, (pid, _) in enumerate(self.rankings, 1):
            if pid == player_id:
                return rank
        return len(self.rankings) + 1

    def get_leaderboard(self, top_n: int = 10) -> List[tuple]:
        """Get top N leaderboard entries."""
        return self.rankings[:top_n]

    def _recompute_rankings(self) -> None:
        """Recompute rankings from scores."""
        self.rankings = sorted(
            self.player_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )


class RewardSystem(GameSystem):
    """Base class for systems that grant rewards."""

    def __init__(self, config: SystemConfig):
        super().__init__(config)
        self.reward_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def grant_reward(
        self,
        player_id: str,
        reward_type: str,
        amount: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Grant a reward to a player."""
        reward = {
            "type": reward_type,
            "amount": amount,
            "metadata": metadata or {},
            "timestamp": len(self.reward_history[player_id]),
        }
        self.reward_history[player_id].append(reward)
        self.emit("reward:granted", {
            "player_id": player_id,
            "reward": reward,
        })
        return reward

    def get_reward_history(self, player_id: str) -> List[Dict[str, Any]]:
        """Get player reward history."""
        return self.reward_history[player_id]


class ValidationMixin:
    """Mixin for systems that need validation logic."""

    def validate_player_exists(self, player_id: str) -> bool:
        """Validate that player exists in system."""
        if not player_id:
            return False
        return hasattr(self, "players") and player_id in getattr(self, "players", {})

    def validate_level_requirement(self, player_level: int, required_level: int) -> bool:
        """Check if player meets level requirement."""
        return player_level >= required_level

    def validate_resource_cost(
        self,
        player_resources: Dict[str, int],
        cost: Dict[str, int]
    ) -> bool:
        """Check if player has sufficient resources."""
        for resource, amount in cost.items():
            if player_resources.get(resource, 0) < amount:
                return False
        return True


class CacheMixin:
    """Mixin for systems that need caching."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache: Dict[str, tuple] = {}  # (value, timestamp)
        self._cache_ttl = 300  # 5 minutes default

    def set_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a cached value with TTL."""
        import time
        self._cache[key] = (value, time.time(), ttl or self._cache_ttl)

    def get_cache(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        import time
        if key not in self._cache:
            return None

        value, timestamp, ttl = self._cache[key]
        if time.time() - timestamp > ttl:
            del self._cache[key]
            return None
        return value

    def clear_cache(self, key: Optional[str] = None) -> None:
        """Clear cache for a key or all cache."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()


class SerializableMixin:
    """Mixin for systems that need to save/load state."""

    def serialize(self) -> Dict[str, Any]:
        """Serialize system state to dict."""
        if hasattr(self, "_state"):
            return dict(self._state)
        return {}

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize system state from dict."""
        if hasattr(self, "_state"):
            self._state.update(data)


T = TypeVar("T", bound=GameSystem)


class SystemFactory(Generic[T]):
    """Factory for creating and managing game systems."""

    def __init__(self):
        self.systems: Dict[str, GameSystem] = {}
        self.system_classes: Dict[str, type] = {}

    def register(self, system_id: str, system_class: type) -> None:
        """Register a system class."""
        self.system_classes[system_id] = system_class

    def create(self, system_id: str, config: SystemConfig) -> GameSystem:
        """Create a system instance."""
        if system_id not in self.system_classes:
            raise ValueError(f"Unknown system: {system_id}")

        system = self.system_classes[system_id](config)
        system.initialize()
        self.systems[system_id] = system
        return system

    def get(self, system_id: str) -> Optional[GameSystem]:
        """Get registered system."""
        return self.systems.get(system_id)

    def get_all(self) -> Dict[str, GameSystem]:
        """Get all registered systems."""
        return dict(self.systems)

    def get_by_type(self, system_type: SystemType) -> List[GameSystem]:
        """Get all systems of a type."""
        return [s for s in self.systems.values() if s.type == system_type]

    def remove(self, system_id: str) -> None:
        """Remove a system."""
        self.systems.pop(system_id, None)

    def shutdown_all(self) -> None:
        """Shutdown all systems."""
        for system in self.systems.values():
            system.disable()
        self.systems.clear()
