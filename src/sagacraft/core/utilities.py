"""Utility helpers for common system operations."""

from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


T = TypeVar("T")


class EventBus:
    """Centralized event bus for system communication."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: List[tuple] = []
        self._max_history = 1000

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event."""
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from an event."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

    def publish(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Publish an event."""
        data = data or {}
        
        # Record history
        self._event_history.append((event_type, data))
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Notify subscribers
        for handler in self._subscribers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")

    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[tuple]:
        """Get event history."""
        if event_type:
            return [(e, d) for e, d in self._event_history if e == event_type][-limit:]
        return self._event_history[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()


class LRUCache(Generic[T]):
    """Least-Recently-Used cache for storing values."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, T] = {}
        self.access_order: List[str] = []

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Get value from cache."""
        if key not in self.cache:
            return default

        # Move to end (most recently used)
        self.access_order.remove(key)
        self.access_order.append(key)

        return self.cache[key]

    def set(self, key: str, value: T) -> None:
        """Set value in cache."""
        if key in self.cache:
            self.access_order.remove(key)

        self.cache[key] = value
        self.access_order.append(key)

        # Evict least recently used if over capacity
        while len(self.cache) > self.max_size:
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.access_order.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


class RateLimiter:
    """Rate limiter using token bucket algorithm."""

    def __init__(self, rate: int, per_seconds: int = 1):
        self.rate = rate
        self.per_seconds = per_seconds
        self.tokens: Dict[str, int] = {}
        self.last_refill: Dict[str, float] = {}

    def allow(self, identifier: str) -> bool:
        """Check if action is allowed for identifier."""
        import time

        current_time = time.time()

        if identifier not in self.tokens:
            self.tokens[identifier] = self.rate
            self.last_refill[identifier] = current_time
            return True

        # Refill tokens
        time_passed = current_time - self.last_refill[identifier]
        tokens_to_add = int(time_passed / self.per_seconds * self.rate)

        if tokens_to_add > 0:
            self.tokens[identifier] = min(
                self.rate,
                self.tokens[identifier] + tokens_to_add
            )
            self.last_refill[identifier] = current_time

        # Check if we have tokens
        if self.tokens[identifier] > 0:
            self.tokens[identifier] -= 1
            return True

        return False

    def reset(self, identifier: str) -> None:
        """Reset rate limit for identifier."""
        self.tokens.pop(identifier, None)
        self.last_refill.pop(identifier, None)


class WeightedRandomSelector:
    """Select random item based on weights."""

    def __init__(self, items: Dict[str, int]):
        self.items = items
        self.total_weight = sum(items.values())

    def select(self) -> Optional[str]:
        """Select random item based on weights."""
        if not self.items or self.total_weight <= 0:
            return None

        import random
        pick = random.randint(1, self.total_weight)

        current = 0
        for item, weight in self.items.items():
            current += weight
            if pick <= current:
                return item

        return None

    def select_multiple(self, count: int, allow_duplicates: bool = False) -> List[str]:
        """Select multiple items."""
        selected = []
        for _ in range(count):
            item = self.select()
            if item:
                selected.append(item)
                if not allow_duplicates:
                    self.items[item] = 0  # Temporarily exclude
                    self.total_weight -= item
        return selected


@dataclass
class TimeWindow:
    """Represents a time window for rate limiting/cooldowns."""
    name: str
    seconds: int
    last_trigger: Dict[str, float] = None

    def __post_init__(self):
        if self.last_trigger is None:
            self.last_trigger = {}

    def is_available(self, identifier: str) -> bool:
        """Check if time window has passed."""
        import time
        current_time = time.time()
        last = self.last_trigger.get(identifier, 0)
        return current_time - last >= self.seconds

    def trigger(self, identifier: str) -> None:
        """Mark identifier as triggered now."""
        import time
        self.last_trigger[identifier] = time.time()

    def get_remaining(self, identifier: str) -> float:
        """Get remaining time until available."""
        import time
        current_time = time.time()
        last = self.last_trigger.get(identifier, 0)
        remaining = self.seconds - (current_time - last)
        return max(0, remaining)


class GameValueFormatter:
    """Format game values for display."""

    @staticmethod
    def format_number(value: int | float, suffix: str = "") -> str:
        """Format large numbers with K/M/B notation."""
        if isinstance(value, float):
            value = int(value)

        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f}B{suffix}"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M{suffix}"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K{suffix}"
        else:
            return f"{value}{suffix}"

    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format percentage value."""
        return f"{value * 100:.{decimals}f}%"

    @staticmethod
    def format_time_duration(seconds: int) -> str:
        """Format seconds to readable duration."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)

    @staticmethod
    def format_distance(meters: int) -> str:
        """Format distance value."""
        if meters >= 1000:
            return f"{meters / 1000:.1f}km"
        return f"{meters}m"


class BitvectorFlags:
    """Efficient boolean flags using bitwise operations."""

    def __init__(self, initial: int = 0):
        self.flags = initial

    def set(self, flag: int) -> None:
        """Set a flag."""
        self.flags |= (1 << flag)

    def unset(self, flag: int) -> None:
        """Unset a flag."""
        self.flags &= ~(1 << flag)

    def has(self, flag: int) -> bool:
        """Check if flag is set."""
        return (self.flags & (1 << flag)) != 0

    def toggle(self, flag: int) -> None:
        """Toggle a flag."""
        self.flags ^= (1 << flag)

    def set_all(self, flags: List[int]) -> None:
        """Set multiple flags."""
        for flag in flags:
            self.set(flag)

    def clear(self) -> None:
        """Clear all flags."""
        self.flags = 0

    def to_int(self) -> int:
        """Get flags as integer."""
        return self.flags


class StatTracker:
    """Track statistics over time."""

    def __init__(self):
        self.stats: Dict[str, List[int | float]] = defaultdict(list)

    def record(self, stat_name: str, value: int | float) -> None:
        """Record a statistic value."""
        self.stats[stat_name].append(value)

    def get_average(self, stat_name: str) -> float:
        """Get average value."""
        values = self.stats.get(stat_name, [])
        return sum(values) / len(values) if values else 0.0

    def get_max(self, stat_name: str) -> int | float:
        """Get maximum value."""
        values = self.stats.get(stat_name, [])
        return max(values) if values else 0

    def get_min(self, stat_name: str) -> int | float:
        """Get minimum value."""
        values = self.stats.get(stat_name, [])
        return min(values) if values else 0

    def get_total(self, stat_name: str) -> int | float:
        """Get total/sum value."""
        return sum(self.stats.get(stat_name, []))

    def get_count(self, stat_name: str) -> int:
        """Get count of recorded values."""
        return len(self.stats.get(stat_name, []))

    def clear(self, stat_name: Optional[str] = None) -> None:
        """Clear statistics."""
        if stat_name:
            self.stats[stat_name].clear()
        else:
            self.stats.clear()

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all statistics with computed values."""
        result = {}
        for stat_name in self.stats:
            result[stat_name] = {
                "average": self.get_average(stat_name),
                "max": self.get_max(stat_name),
                "min": self.get_min(stat_name),
                "total": self.get_total(stat_name),
                "count": self.get_count(stat_name),
            }
        return result
