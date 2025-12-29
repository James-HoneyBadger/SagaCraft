"""Advanced Debug & Development Tools - replay, profiling, time travel debugging."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import time
import json


class EventType(Enum):
    """Types of game events to record."""
    COMMAND = "command"
    STATE_CHANGE = "state_change"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    ITEM_PICKUP = "item_pickup"
    LEVEL_UP = "level_up"
    SAVE = "save"
    ERROR = "error"
    CUSTOM = "custom"


@dataclass
class GameEvent:
    """A recorded game event."""
    event_id: str
    timestamp: int
    event_type: EventType
    command: Optional[str] = None
    result: Optional[str] = None
    state_snapshot: Optional[Dict] = None
    player_position: Optional[Tuple[int, int]] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class ReplaySession:
    """A recorded gameplay session for replay."""
    session_id: str
    start_time: int
    end_time: Optional[int] = None
    duration_seconds: int = 0
    events: List[GameEvent] = field(default_factory=list)
    player_name: str = ""
    adventure_name: str = ""
    final_state: Optional[Dict] = None


@dataclass
class PerformanceMetric:
    """Performance metrics for debugging."""
    metric_name: str
    value: float
    unit: str = "ms"
    timestamp: int = 0
    context: Optional[str] = None


@dataclass
class BreakPoint:
    """A debugging breakpoint."""
    breakpoint_id: str
    condition: str  # Python expression to evaluate
    location: str  # Function or location name
    enabled: bool = True
    hit_count: int = 0


@dataclass
class GameState:
    """Snapshot of game state at a moment in time."""
    timestamp: int
    player_level: int
    player_health: int
    player_inventory: List[str] = field(default_factory=list)
    current_room: Optional[str] = None
    status_effects: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)


class ReplaySystem:
    """Records and replays gameplay sessions."""

    def __init__(self):
        self.sessions: Dict[str, ReplaySession] = {}
        self.current_session: Optional[ReplaySession] = None
        self.next_session_id = 0
        self.next_event_id = 0

    def start_replay_recording(
        self,
        player_name: str,
        adventure_name: str
    ) -> ReplaySession:
        """Start recording a new replay session."""
        session_id = f"replay_{self.next_session_id}"
        self.next_session_id += 1

        session = ReplaySession(
            session_id=session_id,
            start_time=int(time.time()),
            player_name=player_name,
            adventure_name=adventure_name
        )

        self.sessions[session_id] = session
        self.current_session = session
        return session

    def record_event(
        self,
        event_type: EventType,
        command: Optional[str] = None,
        result: Optional[str] = None,
        state_snapshot: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> GameEvent:
        """Record a game event."""
        if not self.current_session:
            raise ValueError("No active replay session")

        event_id = f"event_{self.next_event_id}"
        self.next_event_id += 1

        event = GameEvent(
            event_id=event_id,
            timestamp=int(time.time()),
            event_type=event_type,
            command=command,
            result=result,
            state_snapshot=state_snapshot,
            metadata=metadata or {}
        )

        self.current_session.events.append(event)
        return event

    def end_replay_recording(self, final_state: Optional[Dict] = None) -> ReplaySession:
        """End the current replay recording."""
        if not self.current_session:
            raise ValueError("No active replay session")

        session = self.current_session
        session.end_time = int(time.time())
        session.duration_seconds = session.end_time - session.start_time
        session.final_state = final_state

        self.current_session = None
        return session

    def get_replay(self, session_id: str) -> Optional[ReplaySession]:
        """Get a recorded replay session."""
        return self.sessions.get(session_id)

    def list_replays(self) -> List[ReplaySession]:
        """List all recorded replays."""
        return list(self.sessions.values())

    def export_replay(self, session_id: str) -> Optional[str]:
        """Export replay as JSON."""
        session = self.get_replay(session_id)
        if not session:
            return None

        data = {
            "session_id": session.session_id,
            "player_name": session.player_name,
            "adventure_name": session.adventure_name,
            "duration_seconds": session.duration_seconds,
            "events": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp,
                    "type": e.event_type.value,
                    "command": e.command,
                    "result": e.result
                }
                for e in session.events
            ]
        }

        return json.dumps(data, indent=2)


class TimeTravelDebugger:
    """Time-travel debugging - step backward through game state."""

    def __init__(self):
        self.state_snapshots: List[GameState] = []
        self.current_index: int = -1

    def record_state(
        self,
        player_level: int,
        player_health: int,
        current_room: Optional[str] = None,
        inventory: Optional[List[str]] = None,
        status_effects: Optional[List[str]] = None,
        variables: Optional[Dict] = None
    ) -> None:
        """Record a game state snapshot."""
        state = GameState(
            timestamp=int(time.time()),
            player_level=player_level,
            player_health=player_health,
            player_inventory=inventory or [],
            current_room=current_room,
            status_effects=status_effects or [],
            variables=variables or {}
        )

        self.state_snapshots.append(state)
        self.current_index = len(self.state_snapshots) - 1

    def step_backward(self) -> Optional[GameState]:
        """Step backward one state."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.state_snapshots[self.current_index]
        return None

    def step_forward(self) -> Optional[GameState]:
        """Step forward one state."""
        if self.current_index < len(self.state_snapshots) - 1:
            self.current_index += 1
            return self.state_snapshots[self.current_index]
        return None

    def jump_to_time(self, timestamp: int) -> Optional[GameState]:
        """Jump to state at specific time."""
        for i, state in enumerate(self.state_snapshots):
            if state.timestamp >= timestamp:
                self.current_index = i
                return state
        return None

    def get_current_state(self) -> Optional[GameState]:
        """Get current state."""
        if 0 <= self.current_index < len(self.state_snapshots):
            return self.state_snapshots[self.current_index]
        return None

    def compare_states(self, index1: int, index2: int) -> Dict:
        """Compare two states."""
        if not (0 <= index1 < len(self.state_snapshots) and 0 <= index2 < len(self.state_snapshots)):
            return {}

        state1 = self.state_snapshots[index1]
        state2 = self.state_snapshots[index2]

        return {
            "level_change": state2.player_level - state1.player_level,
            "health_change": state2.player_health - state1.player_health,
            "room_changed": state1.current_room != state2.current_room,
            "new_room": state2.current_room,
            "inventory_changes": set(state2.player_inventory) - set(state1.player_inventory),
        }


class PerformanceProfiler:
    """Profiles game performance for optimization."""

    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.active_timers: Dict[str, int] = {}

    def start_timer(self, label: str) -> None:
        """Start timing an operation."""
        self.active_timers[label] = int(time.time() * 1000)  # milliseconds

    def end_timer(self, label: str, context: Optional[str] = None) -> Optional[PerformanceMetric]:
        """End timing an operation."""
        if label not in self.active_timers:
            return None

        start_time = self.active_timers[label]
        end_time = int(time.time() * 1000)
        duration = end_time - start_time

        metric = PerformanceMetric(
            metric_name=label,
            value=float(duration),
            unit="ms",
            timestamp=int(time.time()),
            context=context
        )

        self.metrics.append(metric)
        del self.active_timers[label]
        return metric

    def get_slow_operations(self, threshold_ms: int = 100) -> List[PerformanceMetric]:
        """Get operations slower than threshold."""
        return [m for m in self.metrics if m.value > threshold_ms]

    def get_average_time(self, label: str) -> float:
        """Get average execution time for operation."""
        matching = [m for m in self.metrics if m.metric_name == label]
        if not matching:
            return 0.0
        return sum(m.value for m in matching) / len(matching)

    def generate_performance_report(self) -> Dict:
        """Generate performance analysis report."""
        if not self.metrics:
            return {"status": "No metrics recorded"}

        slow_ops = self.get_slow_operations()
        operation_times = {}

        for metric in self.metrics:
            if metric.metric_name not in operation_times:
                operation_times[metric.metric_name] = []
            operation_times[metric.metric_name].append(metric.value)

        avg_times = {
            op: sum(times) / len(times)
            for op, times in operation_times.items()
        }

        return {
            "total_metrics": len(self.metrics),
            "slow_operations_count": len(slow_ops),
            "slowest_operation": max(self.metrics, key=lambda m: m.value).metric_name if self.metrics else None,
            "slowest_time_ms": max(m.value for m in self.metrics) if self.metrics else 0,
            "average_times": {op: round(t, 2) for op, t in avg_times.items()},
            "slow_operations": [
                {
                    "operation": m.metric_name,
                    "time_ms": round(m.value, 2),
                    "context": m.context
                }
                for m in slow_ops[:10]  # Top 10 slowest
            ]
        }


class AdventureValidator:
    """Validates adventure design patterns."""

    @staticmethod
    def validate_adventure(adventure_data: Dict) -> Tuple[bool, List[str]]:
        """Validate adventure structure and design."""
        issues = []

        # Check required fields
        if "intro" not in adventure_data:
            issues.append("Missing adventure intro")

        if "rooms" not in adventure_data or not adventure_data["rooms"]:
            issues.append("Adventure has no rooms")

        # Check room connectivity
        rooms = adventure_data.get("rooms", {})
        all_room_ids = set(rooms.keys())

        for room_id, room in rooms.items():
            exits = room.get("exits", {})
            for exit_id in exits.values():
                if exit_id not in all_room_ids:
                    issues.append(f"Room {room_id} exits to non-existent room {exit_id}")

        # Check for isolated rooms
        visited = set()

        def visit_rooms(room_id: str) -> None:
            if room_id in visited or room_id not in all_room_ids:
                return
            visited.add(room_id)
            for exit_id in rooms[room_id].get("exits", {}).values():
                visit_rooms(exit_id)

        start_room = list(rooms.keys())[0] if rooms else None
        if start_room:
            visit_rooms(start_room)

        isolated = all_room_ids - visited
        if isolated:
            issues.append(f"Isolated rooms: {isolated}")

        # Check for items without locations
        if "items" in adventure_data:
            item_locations = set()
            for room in rooms.values():
                item_locations.update(room.get("items", []))

            all_items = set(adventure_data["items"].keys())
            missing_location = all_items - item_locations
            if missing_location:
                issues.append(f"Items with no location: {missing_location}")

        return len(issues) == 0, issues


class DebugToolkit:
    """Central toolkit for all debugging and development tools."""

    def __init__(self):
        self.replay_system = ReplaySystem()
        self.debugger = TimeTravelDebugger()
        self.profiler = PerformanceProfiler()
        self.breakpoints: Dict[str, BreakPoint] = {}
        self.next_bp_id = 0

    def add_breakpoint(self, condition: str, location: str) -> BreakPoint:
        """Add a debug breakpoint."""
        bp_id = f"bp_{self.next_bp_id}"
        self.next_bp_id += 1

        bp = BreakPoint(
            breakpoint_id=bp_id,
            condition=condition,
            location=location
        )

        self.breakpoints[bp_id] = bp
        return bp

    def remove_breakpoint(self, breakpoint_id: str) -> Tuple[bool, str]:
        """Remove a breakpoint."""
        if breakpoint_id in self.breakpoints:
            del self.breakpoints[breakpoint_id]
            return True, f"Removed breakpoint {breakpoint_id}"
        return False, "Breakpoint not found"

    def toggle_breakpoint(self, breakpoint_id: str) -> Tuple[bool, str]:
        """Toggle a breakpoint on/off."""
        if breakpoint_id not in self.breakpoints:
            return False, "Breakpoint not found"

        bp = self.breakpoints[breakpoint_id]
        bp.enabled = not bp.enabled
        return True, f"Breakpoint {breakpoint_id} now {'enabled' if bp.enabled else 'disabled'}"

    def get_diagnostics_summary(self) -> Dict:
        """Get overall diagnostics summary."""
        return {
            "replay_sessions": len(self.replay_system.sessions),
            "state_snapshots": len(self.debugger.state_snapshots),
            "performance_metrics": len(self.profiler.metrics),
            "active_breakpoints": len([b for b in self.breakpoints.values() if b.enabled]),
            "performance_report": self.profiler.generate_performance_report()
        }
