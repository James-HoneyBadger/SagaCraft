---
title: SagaCraft Refactored Architecture Guide
subtitle: Code Efficiency & Extensibility Improvements
date: December 28, 2025
---

# SagaCraft Architecture Refactoring Guide

## Overview

The complete refactoring introduces a unified architecture that dramatically improves code reusability, maintainability, and extensibility. All 16 new feature systems can now be built on a common foundation rather than duplicating code.

## Core Components

### 1. GameSystem (Base Class)

All systems inherit from `GameSystem` providing:

```python
from sagacraft.core.system_base import GameSystem, SystemConfig, SystemType

class MySystem(GameSystem):
    def initialize(self):
        """Setup on startup"""
        self.set_state("ready", True)
    
    def validate(self):
        """Validate system state"""
        return self.get_state("ready", False)
```

**Built-in Features:**
- State management (`get_state`, `set_state`, `reset_state`)
- Event system (`on`, `emit`)
- Metadata management
- Enable/disable functionality
- Priority-based ordering

### 2. Specialized Base Classes

#### ProgressionSystem
For systems tracking XP, levels, and progression:

```python
class SkillTreeSystem(ProgressionSystem):
    def initialize(self):
        pass
    
    def validate(self):
        return True

system = SkillTreeSystem(config)
system.add_progression("player1", "fire_magic", 100)
xp = system.get_progression("player1", "fire_magic")
```

#### RankedSystem
For leaderboards and rankings:

```python
class PvPArenaSystem(RankedSystem):
    def initialize(self):
        pass
    
    def validate(self):
        return True

system.update_score("player1", 1500)
rank = system.get_rank("player1")
leaderboard = system.get_leaderboard(top_n=10)
```

#### RewardSystem
For achievements and rewards:

```python
class AchievementSystem(RewardSystem):
    def initialize(self):
        pass
    
    def validate(self):
        return True

reward = system.grant_reward("player1", "xp", 500)
history = system.get_reward_history("player1")
```

### 3. Mixins

Add additional functionality through multiple inheritance:

```python
class DifficultySystem(GameSystem, ValidationMixin, CacheMixin):
    def initialize(self):
        self.validate_player_exists("player1", {"player1": {}})
        self.set_cache("difficulty_player1", "hard", ttl=600)
    
    def validate(self):
        cached = self.get_cache("difficulty_player1")
        return cached is not None
```

**Available Mixins:**
- `ValidationMixin` - Player/resource validation
- `CacheMixin` - Automatic caching with TTL
- `SerializableMixin` - Save/load state

### 4. Validators

Pre-built validation functions:

```python
from sagacraft.core.validators import (
    ResourceValidator,
    LevelValidator,
    RangeValidator,
    ValidationResult,
)

# Check if player has resources
available = {"gold": 100, "gems": 50}
cost = {"gold": 75, "gems": 25}
result = ResourceValidator.validate_cost(available, cost)

if result.is_valid():
    ResourceValidator.consume_resources(available, cost)
else:
    for error in result.errors:
        print(error)

# Check level
valid, msg = LevelValidator.validate_level_requirement(10, 5)

# Clamp numeric value
value = RangeValidator.clamp(150, 0, 100)  # Returns 100
```

### 5. Utilities

Common patterns and helpers:

```python
from sagacraft.core.utilities import (
    EventBus,
    LRUCache,
    RateLimiter,
    TimeWindow,
    GameValueFormatter,
    StatTracker,
)

# Event system
bus = EventBus()
bus.subscribe("player:leveled_up", handle_levelup)
bus.publish("player:leveled_up", {"player_id": "p1", "level": 5})

# Caching
cache = LRUCache(max_size=100)
cache.set("player_data", player_obj)
data = cache.get("player_data")

# Rate limiting
limiter = RateLimiter(rate=5, per_seconds=1)  # 5 per second
if limiter.allow("player1"):
    process_request()

# Cooldowns
cooldown = TimeWindow("ability", seconds=30)
if cooldown.is_available("player1"):
    use_ability("player1")
    cooldown.trigger("player1")

# Formatting
formatted = GameValueFormatter.format_number(1500000)  # "1.5M"
pct = GameValueFormatter.format_percentage(0.75)  # "75.0%"
time_str = GameValueFormatter.format_time_duration(3661)  # "1h 1m 1s"

# Statistics
stats = StatTracker()
stats.record("damage", 50)
stats.record("damage", 75)
avg = stats.get_average("damage")  # 62.5
```

### 6. System Registry

Centralized management of all systems:

```python
from sagacraft.core.system_registry import get_registry, setup_default_systems

# Get global registry
registry = get_registry()

# Setup default systems
registry = setup_default_systems()

# Create and manage systems
registry.initialize_all()

# Get a system
difficulty = registry.get_system("difficulty")

# Get systems by type
progression_systems = registry.get_systems_by_type(SystemType.PROGRESSION)

# Enable/disable features
registry.disable_system("pvp_arenas")
registry.enable_system("pvp_arenas")

# Check dependencies
valid = registry.validate_dependencies("skill_trees")
```

## Creating New Systems

### Minimal Example

```python
from sagacraft.core.system_base import GameSystem, SystemConfig, SystemType

class NewSystem(GameSystem):
    def initialize(self):
        """Setup on startup"""
        print(f"Initializing {self.id}")
    
    def validate(self):
        """Validate system state"""
        return True

# Create and use
config = SystemConfig(
    system_id="new_system",
    system_type=SystemType.GAMEPLAY
)
system = NewSystem(config)
system.initialize()
```

### Advanced Example with Features

```python
from sagacraft.core.system_base import GameSystem, SystemConfig, SystemType
from sagacraft.core.validators import ResourceValidator, ValidationResult

class ComplexSystem(GameSystem, ValidationMixin, CacheMixin):
    def initialize(self):
        self.set_state("resources", {"gold": 1000})
    
    def validate(self) -> bool:
        """Validate system"""
        resources = self.get_state("resources")
        return resources is not None
    
    def spend_resources(self, player_id: str, cost: dict) -> ValidationResult:
        """Spend resources with validation"""
        resources = self.get_state("resources")
        
        result = ResourceValidator.validate_cost(resources, cost)
        if result.is_valid():
            ResourceValidator.consume_resources(resources, cost)
            self.emit("resources:spent", {
                "player_id": player_id,
                "cost": cost,
                "remaining": resources
            })
        
        return result
```

## Integration with Existing Systems

The refactoring provides a path to gradually migrate existing systems:

```python
# Old system (still works)
from sagacraft.systems.difficulty import DifficultyScaler
scaler = DifficultyScaler()

# New approach (recommended)
from sagacraft.core.system_registry import get_registry
registry = get_registry()
difficulty_system = registry.get_system("difficulty")
```

## Testing

All systems inherit testable base classes:

```python
import unittest
from sagacraft.core.system_base import GameSystem, SystemConfig, SystemType

class TestMySystem(unittest.TestCase):
    def setUp(self):
        config = SystemConfig("test", SystemType.GAMEPLAY)
        self.system = MySystem(config)
        self.system.initialize()
    
    def test_state_management(self):
        self.system.set_state("key", "value")
        self.assertEqual(self.system.get_state("key"), "value")
    
    def test_events(self):
        events = []
        self.system.on("test_event", lambda data: events.append(data))
        self.system.emit("test_event", {"test": True})
        self.assertEqual(len(events), 1)
```

## Performance Considerations

### Memory
- Base classes: ~5% overhead
- Mixins: Per-system configuration
- Caching: Optional per-system

### Speed
- Inheritance: <1% overhead
- Event system: O(n listeners)
- Validation: Optimized for common patterns

## Migration Checklist

To migrate an existing system to the new architecture:

- [ ] Inherit from appropriate base class (GameSystem, ProgressionSystem, etc.)
- [ ] Implement `initialize()` and `validate()` methods
- [ ] Replace custom event system with `on()`/`emit()`
- [ ] Replace custom state with `get_state()`/`set_state()`
- [ ] Add ValidationMixin if doing validation
- [ ] Add CacheMixin if caching needed
- [ ] Update tests to use new base classes
- [ ] Register with SystemRegistry
- [ ] Test with dependency resolution

## Best Practices

1. **Use type hints everywhere**
   ```python
   def spend_resources(self, player_id: str, amount: int) -> bool:
   ```

2. **Emit events for important actions**
   ```python
   self.emit("resource:spent", {"amount": 100})
   ```

3. **Use validators for external input**
   ```python
   result = ResourceValidator.validate_cost(available, cost)
   if result.is_valid():
       # proceed
   ```

4. **Cache expensive computations**
   ```python
   cached = self.get_cache("expensive_key")
   if cached is None:
       cached = expensive_computation()
       self.set_cache("expensive_key", cached)
   ```

5. **Track state in base class**
   ```python
   self.set_state("player_count", count)
   count = self.get_state("player_count", 0)
   ```

## FAQ

**Q: Do I need to refactor existing systems?**
A: No, they work as-is. Refactoring enables better maintenance and faster development for new systems.

**Q: What's the performance overhead?**
A: Negligible (<1%) for inheritance. Caching and event system are optional.

**Q: Can I use multiple mixins?**
A: Yes! `class MySystem(GameSystem, ValidationMixin, CacheMixin, SerializableMixin)`

**Q: How do I handle system dependencies?**
A: Register them with `define_system(..., dependencies=["other_system"])` and the registry handles initialization order.

**Q: Where do I put custom validators?**
A: Either use existing validators or create new ones in a custom module and mix them in.

---

**For complete examples, see:**
- `src/sagacraft/core/system_base.py` - Base classes
- `src/sagacraft/core/system_registry.py` - Registry system
- `src/sagacraft/core/validators.py` - Validation utilities
- `src/sagacraft/core/utilities.py` - Helper utilities
- `tests/test_refactoring_architecture.py` - Example tests
