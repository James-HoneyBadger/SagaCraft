#!/usr/bin/env python3
"""
Demonstration of the new modular architecture

This script shows:
- Engine initialization
- Plugin registration
- Event-driven communication
- Service usage
- State management
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(name)-20s %(levelname)-8s %(message)s"
)

# Import core components
from core import Engine, PluginMetadata, PluginPriority, BasePlugin, Event  # noqa: E402
from utils import ConfigService, IOService, DataService  # noqa: E402


# Example Plugin 1: Simple Counter
class CounterPlugin(BasePlugin):
    """Counts game events"""

    def __init__(self):
        metadata = PluginMetadata(
            name="counter",
            version="1.0",
            description="Counts various game events",
            priority=PluginPriority.LOW,
        )
        super().__init__(metadata)
        self.move_count = 0
        self.command_count = 0

    def initialize(self, state, event_bus, services):
        super().initialize(state, event_bus, services)
        print(f"✓ {self.metadata.name} initialized")

    def get_event_subscriptions(self):
        return {
            "game.move": self.on_move,
            "command.input": self.on_command,
        }

    def on_move(self, event: Event):
        self.move_count += 1
        print(f"  [Counter] Moves: {self.move_count}")

    def on_command(self, event: Event):
        self.command_count += 1
        command = event.data.get("command", "")
        print(f"  [Counter] Commands: {self.command_count} (last: '{command}')")

    def get_stats(self):
        return {"moves": self.move_count, "commands": self.command_count}


# Example Plugin 2: Achievement System (Simplified)
class SimpleAchievementPlugin(BasePlugin):
    """Simple achievement tracker"""

    def __init__(self):
        metadata = PluginMetadata(
            name="achievements",
            version="1.0",
            description="Tracks player achievements",
            priority=PluginPriority.NORMAL,
        )
        super().__init__(metadata)
        self.achievements = {
            "first_move": {"unlocked": False, "name": "First Steps"},
            "explorer": {"unlocked": False, "name": "Explorer"},
        }

    def initialize(self, state, event_bus, services):
        super().initialize(state, event_bus, services)
        print(f"✓ {self.metadata.name} initialized")

    def get_event_subscriptions(self):
        return {
            "game.move": self.check_achievements,
        }

    def check_achievements(self, event: Event):
        # Check first move
        if not self.achievements["first_move"]["unlocked"]:
            self.unlock("first_move")

    def unlock(self, achievement_id):
        if achievement_id in self.achievements:
            ach = self.achievements[achievement_id]
            if not ach["unlocked"]:
                ach["unlocked"] = True
                print(f"  🏆 Achievement Unlocked: {ach['name']}!")
                self.event_bus.publish(
                    "achievement.unlocked",
                    {"achievement": achievement_id, "name": ach["name"]},
                )


# Example Plugin 3: Logger
class EventLoggerPlugin(BasePlugin):
    """Logs all events for debugging"""

    def __init__(self):
        metadata = PluginMetadata(
            name="event_logger",
            version="1.0",
            description="Logs all game events",
            priority=PluginPriority.LOW,
            enabled=True,  # Can be disabled via config
        )
        super().__init__(metadata)

    def initialize(self, state, event_bus, services):
        super().initialize(state, event_bus, services)
        print(f"✓ {self.metadata.name} initialized")

    def get_event_subscriptions(self):
        # Subscribe to ALL events with wildcard
        return {
            "*": self.log_event,
        }

    def log_event(self, event: Event):
        # Don't log our own stats updates to avoid spam
        if event.name not in ["stats.updated"]:
            print(f"  [EventLog] {event.name} from {event.source}")


def demo_basic_engine():
    """Demonstrate basic engine functionality"""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Engine with Plugins")
    print("=" * 60 + "\n")

    # Create engine
    engine = Engine(enable_event_history=True)

    # Register services
    config_service = ConfigService()
    config_service.initialize({})
    engine.services.register("config", config_service)

    io_service = IOService()
    io_service.initialize({})
    engine.services.register("io", io_service)

    data_service = DataService()
    data_service.initialize({})
    engine.services.register("data", data_service)

    print("Services registered:")
    for service in engine.services.list_services():
        print(f"  - {service}")
    print()

    # Register plugins
    counter = CounterPlugin()
    achievements = SimpleAchievementPlugin()
    logger = EventLoggerPlugin()

    engine.register_plugin(counter)
    engine.register_plugin(achievements)
    engine.register_plugin(logger)

    print("\nPlugins registered:")
    for plugin_name in engine.list_plugins():
        print(f"  - {plugin_name}")
    print()

    # Initialize engine
    print("Initializing engine...\n")
    engine.initialize()

    print("\n" + "-" * 60)
    print("Simulating game events...")
    print("-" * 60 + "\n")

    # Simulate some game events
    engine.event_bus.publish("game.start", source="demo")

    engine.event_bus.publish("command.input", {"command": "look"}, source="player")

    engine.event_bus.publish(
        "game.move", {"from_room": 1, "to_room": 2}, source="engine"
    )

    engine.event_bus.publish("command.input", {"command": "go north"}, source="player")

    engine.event_bus.publish(
        "game.move", {"from_room": 2, "to_room": 3}, source="engine"
    )

    # Get stats from counter plugin
    print("\n" + "-" * 60)
    print("Final Statistics:")
    print("-" * 60)
    stats = counter.get_stats()
    print(f"Total moves: {stats['moves']}")
    print(f"Total commands: {stats['commands']}")

    # Check event history
    print(f"\nTotal events published: {len(engine.event_bus._event_history)}")

    # Shutdown
    print("\nShutting down engine...")
    engine.shutdown()
    print("✓ Engine shut down cleanly\n")


def demo_plugin_enable_disable():
    """Demonstrate plugin enable/disable"""
    print("\n" + "=" * 60)
    print("DEMO 2: Plugin Enable/Disable")
    print("=" * 60 + "\n")

    engine = Engine()

    counter = CounterPlugin()
    engine.register_plugin(counter)
    engine.initialize()

    # Fire event with plugin enabled
    print("Plugin enabled:")
    engine.event_bus.publish("game.move", {"to_room": 2})

    # Disable plugin
    print("\nDisabling plugin...")
    counter.disable()

    print("\nPlugin disabled:")
    engine.event_bus.publish("game.move", {"to_room": 3})
    print("  (no output from plugin)")

    # Re-enable
    print("\nRe-enabling plugin...")
    counter.enable()

    print("\nPlugin re-enabled:")
    engine.event_bus.publish("game.move", {"to_room": 4})

    engine.shutdown()
    print()


def demo_event_cancellation():
    """Demonstrate event cancellation"""
    print("\n" + "=" * 60)
    print("DEMO 3: Event Cancellation")
    print("=" * 60 + "\n")

    class GuardPlugin(BasePlugin):
        """Prevents movement to room 666"""

        def __init__(self):
            metadata = PluginMetadata(
                name="guard",
                version="1.0",
                priority=PluginPriority.HIGH,  # Run before other plugins
            )
            super().__init__(metadata)

        def initialize(self, state, event_bus, services):
            super().initialize(state, event_bus, services)

        def get_event_subscriptions(self):
            return {"game.move": self.check_movement}

        def check_movement(self, event: Event):
            to_room = event.data.get("to_room")
            if to_room == 666:
                print("  [Guard] BLOCKED: You cannot enter room 666!")
                event.cancel()

    engine = Engine()

    guard = GuardPlugin()
    counter = CounterPlugin()

    engine.register_plugin(guard)
    engine.register_plugin(counter)
    engine.initialize()

    # Try allowed movement
    print("Moving to room 2:")
    event = engine.event_bus.publish("game.move", {"to_room": 2}, cancellable=True)
    print(f"  Event cancelled: {event.is_cancelled()}\n")

    # Try forbidden movement
    print("Moving to room 666:")
    event = engine.event_bus.publish("game.move", {"to_room": 666}, cancellable=True)
    print(f"  Event cancelled: {event.is_cancelled()}\n")

    engine.shutdown()


def demo_state_management():
    """Demonstrate state management"""
    print("\n" + "=" * 60)
    print("DEMO 4: State Management")
    print("=" * 60 + "\n")

    engine = Engine()
    engine.initialize()

    # Access game state
    print("Initial player state:")
    print(f"  Name: {engine.state.player.name}")
    print(f"  Gold: {engine.state.player.gold}")
    print(f"  Room: {engine.state.player.current_room}")

    # Modify state
    print("\nModifying state...")
    engine.state.player.gold += 50
    engine.state.player.current_room = 5

    print("\nUpdated player state:")
    print(f"  Gold: {engine.state.player.gold}")
    print(f"  Room: {engine.state.player.current_room}")

    # Plugin data
    print("\nPlugin-specific data:")
    engine.state.set_plugin_data("my_plugin", "counter", 42)
    engine.state.set_plugin_data("my_plugin", "name", "Test")

    value = engine.state.get_plugin_data("my_plugin", "counter")
    name = engine.state.get_plugin_data("my_plugin", "name")
    print(f"  Counter: {value}")
    print(f"  Name: {name}")

    # Global flags
    print("\nGlobal flags:")
    engine.state.set_flag("dragon_defeated", True)
    engine.state.set_flag("has_key", False)

    print(f"  dragon_defeated: {engine.state.get_flag('dragon_defeated')}")
    print(f"  has_key: {engine.state.get_flag('has_key')}")
    print(f"  unknown_flag: {engine.state.get_flag('unknown', 'default')}")

    # Serialization
    print("\nSerializing state...")
    state_dict = engine.state.to_dict()
    print(f"  State keys: {list(state_dict.keys())}")

    engine.shutdown()
    print()


def main():
    """Run all demos"""
    print("\n" + "🎮 " * 30)
    print("SagaCraft - Modular Architecture Demo")
    print("🎮 " * 30)

    try:
        demo_basic_engine()
        demo_plugin_enable_disable()
        demo_event_cancellation()
        demo_state_management()

        print("\n" + "=" * 60)
        print("All demos completed successfully! ✓")
        print("=" * 60 + "\n")

        print("Key Takeaways:")
        print("  1. Plugins are self-contained and independent")
        print("  2. Events enable loose coupling between systems")
        print("  3. Services provide shared functionality")
        print("  4. State is centralized and easy to serialize")
        print("  5. System is modular, testable, and extensible")
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
