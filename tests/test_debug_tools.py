"""Tests for Debug & Development Tools."""

import unittest
import time
from sagacraft.systems.debug_tools import (
    DebugToolkit,
    ReplaySystem,
    TimeTravelDebugger,
    PerformanceProfiler,
    AdventureValidator,
    EventType,
)


class TestReplaySystem(unittest.TestCase):
    """Test replay recording system."""

    def setUp(self):
        """Set up test fixtures."""
        self.replay = ReplaySystem()

    def test_start_recording(self):
        """Test starting replay recording."""
        session = self.replay.start_replay_recording("TestPlayer", "TestAdventure")

        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.player_name, "TestPlayer")
        self.assertEqual(session.adventure_name, "TestAdventure")

    def test_record_event(self):
        """Test recording events."""
        self.replay.start_replay_recording("Player", "Adventure")

        event = self.replay.record_event(
            EventType.COMMAND,
            command="look",
            result="You see a room"
        )

        self.assertEqual(event.event_type, EventType.COMMAND)
        self.assertEqual(event.command, "look")
        self.assertEqual(len(self.replay.current_session.events), 1)

    def test_end_recording(self):
        """Test ending replay recording."""
        self.replay.start_replay_recording("Player", "Adventure")
        self.replay.record_event(EventType.COMMAND, command="north")

        time.sleep(1.1)
        session = self.replay.end_replay_recording()

        self.assertIsNotNone(session.end_time)
        self.assertGreaterEqual(session.duration_seconds, 1)
        self.assertIsNone(self.replay.current_session)

    def test_export_replay(self):
        """Test exporting replay as JSON."""
        self.replay.start_replay_recording("Player", "Adventure")
        self.replay.record_event(EventType.COMMAND, command="look")
        session = self.replay.end_replay_recording()

        exported = self.replay.export_replay(session.session_id)

        self.assertIsNotNone(exported)
        self.assertIn("Player", exported)
        self.assertIn("Adventure", exported)


class TestTimeTravelDebugger(unittest.TestCase):
    """Test time-travel debugging."""

    def setUp(self):
        """Set up test fixtures."""
        self.debugger = TimeTravelDebugger()

    def test_record_state(self):
        """Test state recording."""
        self.debugger.record_state(
            player_level=1,
            player_health=100,
            current_room="start"
        )

        self.assertEqual(len(self.debugger.state_snapshots), 1)
        self.assertEqual(self.debugger.current_index, 0)

    def test_step_backward(self):
        """Test stepping backward in time."""
        self.debugger.record_state(player_level=1, player_health=100)
        self.debugger.record_state(player_level=2, player_health=80)

        state = self.debugger.step_backward()

        self.assertIsNotNone(state)
        self.assertEqual(state.player_level, 1)
        self.assertEqual(state.player_health, 100)

    def test_step_forward(self):
        """Test stepping forward in time."""
        self.debugger.record_state(player_level=1, player_health=100)
        self.debugger.record_state(player_level=2, player_health=80)

        self.debugger.step_backward()
        state = self.debugger.step_forward()

        self.assertIsNotNone(state)
        self.assertEqual(state.player_level, 2)

    def test_get_current_state(self):
        """Test getting current state."""
        self.debugger.record_state(player_level=5, player_health=75)

        state = self.debugger.get_current_state()

        self.assertIsNotNone(state)
        self.assertEqual(state.player_level, 5)

    def test_compare_states(self):
        """Test comparing two states."""
        self.debugger.record_state(
            player_level=1,
            player_health=100,
            inventory=["sword"]
        )
        self.debugger.record_state(
            player_level=2,
            player_health=85,
            inventory=["sword", "shield"]
        )

        comparison = self.debugger.compare_states(0, 1)

        self.assertEqual(comparison["level_change"], 1)
        self.assertEqual(comparison["health_change"], -15)
        self.assertIn("shield", comparison["inventory_changes"])


class TestPerformanceProfiler(unittest.TestCase):
    """Test performance profiler."""

    def setUp(self):
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler()

    def test_timer_operations(self):
        """Test timing operations."""
        self.profiler.start_timer("test_op")
        time.sleep(0.01)  # 10ms
        metric = self.profiler.end_timer("test_op")

        self.assertIsNotNone(metric)
        self.assertEqual(metric.metric_name, "test_op")
        self.assertGreater(metric.value, 0)

    def test_get_slow_operations(self):
        """Test finding slow operations."""
        self.profiler.start_timer("slow")
        time.sleep(0.15)  # 150ms
        self.profiler.end_timer("slow")

        self.profiler.start_timer("fast")
        self.profiler.end_timer("fast")

        slow = self.profiler.get_slow_operations(threshold_ms=100)

        self.assertEqual(len(slow), 1)
        self.assertEqual(slow[0].metric_name, "slow")

    def test_average_time(self):
        """Test average time calculation."""
        for _ in range(3):
            self.profiler.start_timer("operation")
            time.sleep(0.01)
            self.profiler.end_timer("operation")

        avg = self.profiler.get_average_time("operation")

        self.assertGreater(avg, 0)

    def test_performance_report(self):
        """Test performance report generation."""
        self.profiler.start_timer("op1")
        time.sleep(0.01)
        self.profiler.end_timer("op1")

        report = self.profiler.generate_performance_report()

        self.assertIn("total_metrics", report)
        self.assertIn("average_times", report)
        self.assertEqual(report["total_metrics"], 1)


class TestAdventureValidator(unittest.TestCase):
    """Test adventure validation."""

    def test_valid_adventure(self):
        """Test validating a valid adventure."""
        adventure = {
            "intro": "Welcome",
            "rooms": {
                "room1": {
                    "description": "A room",
                    "exits": {"north": "room2"}
                },
                "room2": {
                    "description": "Another room",
                    "exits": {"south": "room1"}
                }
            }
        }

        valid, issues = AdventureValidator.validate_adventure(adventure)

        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)

    def test_missing_intro(self):
        """Test detecting missing intro."""
        adventure = {
            "rooms": {}
        }

        valid, issues = AdventureValidator.validate_adventure(adventure)

        self.assertFalse(valid)
        self.assertTrue(any("intro" in issue for issue in issues))

    def test_no_rooms(self):
        """Test detecting no rooms."""
        adventure = {
            "intro": "Welcome",
            "rooms": {}
        }

        valid, issues = AdventureValidator.validate_adventure(adventure)

        self.assertFalse(valid)
        self.assertTrue(any("no rooms" in issue for issue in issues))

    def test_broken_exit(self):
        """Test detecting broken room exits."""
        adventure = {
            "intro": "Welcome",
            "rooms": {
                "room1": {
                    "description": "A room",
                    "exits": {"north": "nonexistent"}
                }
            }
        }

        valid, issues = AdventureValidator.validate_adventure(adventure)

        self.assertFalse(valid)
        self.assertTrue(any("non-existent" in issue for issue in issues))

    def test_isolated_rooms(self):
        """Test detecting isolated rooms."""
        adventure = {
            "intro": "Welcome",
            "rooms": {
                "room1": {
                    "description": "Room 1",
                    "exits": {}
                },
                "room2": {
                    "description": "Room 2",
                    "exits": {}
                }
            }
        }

        valid, issues = AdventureValidator.validate_adventure(adventure)

        self.assertFalse(valid)
        self.assertTrue(any("Isolated" in issue for issue in issues))


class TestDebugToolkit(unittest.TestCase):
    """Test the debug toolkit."""

    def setUp(self):
        """Set up test fixtures."""
        self.toolkit = DebugToolkit()

    def test_add_breakpoint(self):
        """Test adding a breakpoint."""
        bp = self.toolkit.add_breakpoint("player.health < 50", "combat_system")

        self.assertIsNotNone(bp.breakpoint_id)
        self.assertEqual(bp.condition, "player.health < 50")
        self.assertTrue(bp.enabled)

    def test_remove_breakpoint(self):
        """Test removing a breakpoint."""
        bp = self.toolkit.add_breakpoint("test", "location")
        success, msg = self.toolkit.remove_breakpoint(bp.breakpoint_id)

        self.assertTrue(success)
        self.assertNotIn(bp.breakpoint_id, self.toolkit.breakpoints)

    def test_toggle_breakpoint(self):
        """Test toggling breakpoint."""
        bp = self.toolkit.add_breakpoint("test", "location")
        original_state = bp.enabled

        success, msg = self.toolkit.toggle_breakpoint(bp.breakpoint_id)

        self.assertTrue(success)
        self.assertNotEqual(bp.enabled, original_state)

    def test_diagnostics_summary(self):
        """Test getting diagnostics summary."""
        summary = self.toolkit.get_diagnostics_summary()

        self.assertIn("replay_sessions", summary)
        self.assertIn("state_snapshots", summary)
        self.assertIn("performance_metrics", summary)
        self.assertIn("active_breakpoints", summary)


if __name__ == "__main__":
    unittest.main()
