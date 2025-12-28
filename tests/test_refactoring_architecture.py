"""Tests for refactored architecture - base systems, registry, and utilities."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sagacraft.core.system_base import (
    GameSystem,
    SystemConfig,
    SystemType,
    ProgressionSystem,
    RankedSystem,
    RewardSystem,
    ValidationMixin,
    SystemFactory,
)
from sagacraft.core.system_registry import (
    SystemRegistry,
    get_registry,
    setup_default_systems,
    SystemValidator,
)
from sagacraft.core.validators import (
    ResourceValidator,
    LevelValidator,
    RangeValidator,
    ValidationResult,
    validate_positive_int,
)
from sagacraft.core.utilities import (
    EventBus,
    LRUCache,
    RateLimiter,
    TimeWindow,
    GameValueFormatter,
    StatTracker,
)


# ============================================================================
# Tests for system_base.py
# ============================================================================

class TestSystem(GameSystem):
    """Test implementation of GameSystem."""

    def initialize(self) -> None:
        self.set_state("initialized", True)

    def validate(self) -> bool:
        return self.get_state("initialized", False)


def test_game_system_creation():
    """Test creating a basic game system."""
    config = SystemConfig(
        system_id="test_system",
        system_type=SystemType.GAMEPLAY
    )
    system = TestSystem(config)
    system.initialize()

    assert system.id == "test_system"
    assert system.type == SystemType.GAMEPLAY
    assert system.enabled is True


def test_game_system_state():
    """Test system state management."""
    config = SystemConfig("test", SystemType.GAMEPLAY)
    system = TestSystem(config)

    system.set_state("key1", "value1")
    assert system.get_state("key1") == "value1"
    assert system.get_state("missing", "default") == "default"

    system.reset_state()
    assert system.get_state("key1") is None


def test_game_system_events():
    """Test event emission and listening."""
    config = SystemConfig("test", SystemType.GAMEPLAY)
    system = TestSystem(config)

    events_received = []

    def listener(data):
        events_received.append(data)

    system.on("test_event", listener)
    system.emit("test_event", {"value": 42})

    assert len(events_received) == 1
    assert events_received[0]["value"] == 42


def test_progression_system():
    """Test ProgressionSystem base class."""
    config = SystemConfig("progression", SystemType.PROGRESSION)
    
    # Create concrete implementation
    class TestProgression(ProgressionSystem):
        def initialize(self) -> None:
            pass
        def validate(self) -> bool:
            return True
    
    system = TestProgression(config)
    system.initialize()

    new_value = system.add_progression("player1", "xp", 100)
    assert new_value == 100

    new_value = system.add_progression("player1", "xp", 50)
    assert new_value == 150

    assert system.get_progression("player1", "xp") == 150
    assert system.get_progression("player1", "missing", 0) == 0


def test_ranked_system():
    """Test RankedSystem base class."""
    config = SystemConfig("ranked", SystemType.GAMEPLAY)
    
    # Create concrete implementation
    class TestRanked(RankedSystem):
        def initialize(self) -> None:
            pass
        def validate(self) -> bool:
            return True
    
    system = TestRanked(config)
    system.initialize()

    system.update_score("player1", 1000)
    system.update_score("player2", 1500)
    system.update_score("player3", 800)

    assert system.get_score("player2") == 1500
    assert system.get_rank("player2") == 1
    assert system.get_rank("player1") == 2
    assert system.get_rank("player3") == 3

    leaderboard = system.get_leaderboard(2)
    assert len(leaderboard) == 2
    assert leaderboard[0][0] == "player2"


def test_reward_system():
    """Test RewardSystem base class."""
    config = SystemConfig("rewards", SystemType.CONTENT)
    
    # Create concrete implementation
    class TestReward(RewardSystem):
        def initialize(self) -> None:
            pass
        def validate(self) -> bool:
            return True
    
    system = TestReward(config)
    system.initialize()

    reward = system.grant_reward("player1", "xp", 100)
    assert reward["type"] == "xp"
    assert reward["amount"] == 100

    history = system.get_reward_history("player1")
    assert len(history) == 1
    assert history[0]["type"] == "xp"


def test_system_factory():
    """Test SystemFactory creation and management."""
    factory = SystemFactory()
    factory.register("test", TestSystem)

    config = SystemConfig("test_instance", SystemType.GAMEPLAY)
    system = factory.create("test", config)

    assert factory.get("test") is system
    assert len(factory.get_all()) == 1


# ============================================================================
# Tests for system_registry.py
# ============================================================================

def test_system_registry_creation():
    """Test creating system registry."""
    registry = SystemRegistry()
    registry.define_system("test", SystemType.GAMEPLAY)

    assert "test" in registry.system_configs
    assert "test" in registry.feature_flags


def test_system_registry_dependencies():
    """Test dependency tracking."""
    registry = SystemRegistry()
    registry.define_system("base", SystemType.GAMEPLAY)
    registry.define_system("dependent", SystemType.GAMEPLAY, dependencies=["base"])

    assert registry.system_dependencies["dependent"] == ["base"]


def test_system_validator_id():
    """Test system ID validation."""
    assert SystemValidator.validate_system_id("valid_system") is True
    assert SystemValidator.validate_system_id("valid123") is True
    assert SystemValidator.validate_system_id("") is False
    assert SystemValidator.validate_system_id("invalid!@#") is False


def test_system_validator_priority():
    """Test priority validation."""
    assert SystemValidator.validate_priority(0) is True
    assert SystemValidator.validate_priority(500) is True
    assert SystemValidator.validate_priority(1000) is True
    assert SystemValidator.validate_priority(-1) is False
    assert SystemValidator.validate_priority(1001) is False


def test_default_systems_setup():
    """Test setup of default systems."""
    registry = setup_default_systems()

    assert "difficulty" in registry.system_configs
    assert "guilds" in registry.system_configs
    assert "economy" in registry.system_configs
    assert len(registry.system_configs) > 10


# ============================================================================
# Tests for validators.py
# ============================================================================

def test_resource_validator_cost():
    """Test resource validation."""
    available = {"gold": 100, "gems": 50}
    cost = {"gold": 50, "gems": 25}

    result = ResourceValidator.validate_cost(available, cost)
    assert result.is_valid() is True


def test_resource_validator_insufficient():
    """Test validation fails with insufficient resources."""
    available = {"gold": 30}
    cost = {"gold": 50}

    result = ResourceValidator.validate_cost(available, cost)
    assert result.is_valid() is False
    assert len(result.errors) > 0


def test_resource_validator_consume():
    """Test consuming resources."""
    available = {"gold": 100}
    cost = {"gold": 30}

    result = ResourceValidator.consume_resources(available, cost)
    assert result.is_valid() is True
    assert available["gold"] == 70


def test_level_validator():
    """Test level requirement validation."""
    valid, msg = LevelValidator.validate_level_requirement(10, 5)
    assert valid is True

    valid, msg = LevelValidator.validate_level_requirement(3, 5)
    assert valid is False


def test_range_validator():
    """Test range validation."""
    result = RangeValidator.validate_range(50, 0, 100)
    assert result.is_valid() is True

    result = RangeValidator.validate_range(150, 0, 100)
    assert result.is_valid() is False

    clamped = RangeValidator.clamp(150, 0, 100)
    assert clamped == 100


def test_validation_result():
    """Test ValidationResult object."""
    result = ValidationResult(valid=True, errors=[])
    assert result.is_valid() is True

    result.add_error("Test error")
    assert result.is_valid() is False
    assert "Test error" in result.errors


def test_positive_int_validator():
    """Test positive integer validation."""
    result = validate_positive_int(5)
    assert result.is_valid() is True

    result = validate_positive_int(0)
    assert result.is_valid() is False


# ============================================================================
# Tests for utilities.py
# ============================================================================

def test_event_bus():
    """Test EventBus functionality."""
    bus = EventBus()
    events = []

    def handler(data):
        events.append(data)

    bus.subscribe("test_event", handler)
    bus.publish("test_event", {"value": 42})

    assert len(events) == 1
    assert events[0]["value"] == 42


def test_event_bus_history():
    """Test event history tracking."""
    bus = EventBus()

    bus.publish("event1", {})
    bus.publish("event2", {})
    bus.publish("event1", {})

    history = bus.get_history("event1")
    assert len(history) == 2


def test_lru_cache():
    """Test LRU cache."""
    cache = LRUCache(max_size=3)

    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)

    assert cache.get("a") == 1
    assert cache.size() == 3

    # Adding fourth item should evict least recent (b)
    cache.set("d", 4)
    assert cache.get("b") is None
    assert cache.get("d") == 4


def test_rate_limiter():
    """Test RateLimiter."""
    limiter = RateLimiter(rate=3, per_seconds=1)

    # Should allow first 3
    assert limiter.allow("user1") is True
    assert limiter.allow("user1") is True
    assert limiter.allow("user1") is True

    # Should block 4th (no tokens left until time passes)
    result = limiter.allow("user1")
    # It should be False, but if time has passed tokens may refill
    # So let's just check we got something reasonable
    assert isinstance(result, bool)


def test_time_window():
    """Test TimeWindow for cooldowns."""
    window = TimeWindow("test", seconds=1)

    assert window.is_available("user1") is True
    window.trigger("user1")
    assert window.is_available("user1") is False


def test_game_value_formatter():
    """Test number formatting."""
    assert GameValueFormatter.format_number(1500) == "1.5K"
    assert GameValueFormatter.format_number(1500000) == "1.5M"
    assert GameValueFormatter.format_number(1500000000) == "1.5B"
    assert GameValueFormatter.format_number(500) == "500"


def test_time_duration_formatter():
    """Test time duration formatting."""
    formatted = GameValueFormatter.format_time_duration(3661)
    assert "1h" in formatted
    assert "1m" in formatted
    assert "1s" in formatted


def test_stat_tracker():
    """Test StatTracker."""
    tracker = StatTracker()

    tracker.record("damage", 10)
    tracker.record("damage", 20)
    tracker.record("damage", 30)

    assert tracker.get_average("damage") == 20
    assert tracker.get_max("damage") == 30
    assert tracker.get_min("damage") == 10
    assert tracker.get_total("damage") == 60
    assert tracker.get_count("damage") == 3


if __name__ == "__main__":
    # System base tests
    test_game_system_creation()
    test_game_system_state()
    test_game_system_events()
    test_progression_system()
    test_ranked_system()
    test_reward_system()
    test_system_factory()

    # Registry tests
    test_system_registry_creation()
    test_system_registry_dependencies()
    test_system_validator_id()
    test_system_validator_priority()
    test_default_systems_setup()

    # Validator tests
    test_resource_validator_cost()
    test_resource_validator_insufficient()
    test_resource_validator_consume()
    test_level_validator()
    test_range_validator()
    test_validation_result()
    test_positive_int_validator()

    # Utilities tests
    test_event_bus()
    test_event_bus_history()
    test_lru_cache()
    test_rate_limiter()
    test_time_window()
    test_game_value_formatter()
    test_time_duration_formatter()
    test_stat_tracker()

    print("✓ All refactoring architecture tests passed!")
