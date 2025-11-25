#!/usr/bin/env python3
"""
Colossal StoryWorks - Modding & Scripting Support
Allow adventure creators to extend functionality with Python scripts
"""

import copy
from typing import Any, Dict, Iterable, List, Optional, Tuple
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from enum import Enum

try:
    from acs.core import engine as core_engine  # type: ignore
except ImportError:  # pragma: no cover - optional dependency for spawning helpers
    core_engine = None


class EventType(Enum):
    """Types of events that can trigger scripts"""

    ON_ENTER_ROOM = "on_enter_room"
    ON_EXIT_ROOM = "on_exit_room"
    ON_TAKE_ITEM = "on_take_item"
    ON_DROP_ITEM = "on_drop_item"
    ON_ATTACK = "on_attack"
    ON_KILL = "on_kill"
    ON_DEATH = "on_death"
    ON_TALK = "on_talk"
    ON_USE_ITEM = "on_use_item"
    ON_EXAMINE = "on_examine"
    ON_COMMAND = "on_command"  # Before any command
    ON_UNKNOWN_COMMAND = "on_unknown_command"
    ON_SAVE = "on_save"
    ON_LOAD = "on_load"


@dataclass
class ScriptHook:
    """A script that runs in response to an event"""

    event: EventType
    script_code: str
    priority: int = 0  # Higher priority runs first
    enabled: bool = True
    filter_params: Dict[str, Any] = field(default_factory=dict)

    def matches_filter(self, event_data: Dict[str, Any]) -> bool:
        """Check if event matches filter parameters"""
        if not self.filter_params:
            return True

        for key, value in self.filter_params.items():
            if key not in event_data:
                return False
            if isinstance(value, list):
                if event_data[key] not in value:
                    return False
            elif event_data[key] != value:
                return False
        return True


@dataclass
class CustomCommand:
    """A custom command added by a mod"""

    verb: str
    aliases: List[str]
    handler_code: str
    help_text: str = ""
    hidden: bool = False


class ScriptContext:
    """Safe execution context for mod scripts"""

    def __init__(self, engine=None):
        self.engine = engine
        self.output_buffer = []
        self._allowed_modules = {
            "math",
            "random",
            "re",
            "json",
            "datetime",
            "collections",
        }

    def print(self, *args, sep: str = " ", end: str = ""):
        """Capture print output with limited formatting support."""
        message = sep.join(str(arg) for arg in args) + end
        self.output_buffer.append(message)

    def echo(self, message: str):
        """Echo message to player"""
        self.output_buffer.append(message)

    def get_player(self):
        """Get player object"""
        if self.engine:
            return self.engine.player
        return None

    @property
    def allowed_modules(self) -> Iterable[str]:
        """Safe iterable of modules scripts may import."""
        return tuple(self._allowed_modules)

    def get_room(self, room_id: Optional[int] = None):
        """Get room object"""
        if not self.engine:
            return None
        if room_id is None:
            if hasattr(self.engine, "get_current_room"):
                return self.engine.get_current_room()
            return None
        return self.engine.rooms.get(room_id)

    def get_npc(self, name: str):
        """Get NPC by name"""
        if not self.engine:
            return None
        room = self.get_room()
        if not room:
            return None
        lookup_name = name.lower()
        for npc in self.engine.get_monsters_in_room(room.id):
            if npc.name.lower() == lookup_name:
                return npc
        return None

    def get_item(self, name: str):
        """Get item by name from room or inventory"""
        if not self.engine:
            return None

        lookup_name = name.lower()

        # Check player inventory for accessible items
        for item_id in getattr(self.engine.player, "inventory", []):
            item_obj = self.engine.items.get(item_id)
            if item_obj and lookup_name in item_obj.name.lower():
                return item_obj

        # Check the active room for loose items
        room = self.get_room()
        if room:
            for item_obj in self.engine.get_items_in_room(room.id):
                if lookup_name in item_obj.name.lower():
                    return item_obj
        return None

    @staticmethod
    def _instantiate_dataclass(dataclass_cls, overrides: Dict[str, Any], template=None):
        """Create a dataclass instance using template defaults and overrides."""
        if template is not None:
            instance = copy.deepcopy(template)
            for key, value in overrides.items():
                setattr(instance, key, value)
            return instance

        if not dataclass_cls or not is_dataclass(dataclass_cls):
            return None

        init_kwargs: Dict[str, Any] = {}
        for field_def in fields(dataclass_cls):
            if not field_def.init:
                continue
            if field_def.name in overrides:
                init_kwargs[field_def.name] = overrides[field_def.name]
            elif field_def.default is not MISSING:
                init_kwargs[field_def.name] = field_def.default
            elif field_def.default_factory is not MISSING:  # type: ignore[attr-defined]
                init_kwargs[field_def.name] = field_def.default_factory()
            else:
                init_kwargs[field_def.name] = None
        return dataclass_cls(**init_kwargs)

    def _resolve_npc_room_id(
        self, room_id: Optional[int], npc_name: str
    ) -> Optional[int]:
        """Pick a valid room for spawning; echo errors when unavailable."""
        if not self.engine:
            return None

        target_room_id = room_id
        if target_room_id is None:
            target_room_id = getattr(self.engine.player, "current_room", None)

        if target_room_id is None or target_room_id not in self.engine.rooms:
            self.echo(
                f"[Cannot spawn NPC {npc_name}: room {target_room_id} not available]"
            )
            return None

        return target_room_id

    def _next_monster_id(self) -> int:
        """Get the next available monster id."""
        monsters = getattr(self.engine, "monsters", {})
        if not monsters:
            return 1

        next_id = max(monsters.keys()) + 1
        while next_id in monsters:
            next_id += 1
        return next_id

    def _get_monster_template(self):
        """Return a template NPC from the engine, if any."""
        if not self.engine or not getattr(self.engine, "monsters", None):
            return None
        return next(iter(self.engine.monsters.values()), None)

    def _resolve_npc_type(self, template_npc) -> Tuple[Optional[type], Any]:
        """Determine class and friendliness defaults for a new NPC."""

        npc_cls = template_npc.__class__ if template_npc else None
        friendliness_value: Any = getattr(template_npc, "friendliness", None)

        if npc_cls is None and core_engine is not None:
            npc_cls = getattr(core_engine, "Monster", None)

        if friendliness_value is None and core_engine is not None:
            status_enum = getattr(core_engine, "MonsterStatus", None)
            if status_enum is not None:
                try:
                    friendliness_value = status_enum("neutral")
                except ValueError:
                    friendliness_value = None

        if friendliness_value is None:
            friendliness_value = "neutral"

        return npc_cls, friendliness_value

    def _build_npc_overrides(
        self,
        metadata: Dict[str, Any],
        template_npc,
        friendliness_value: Any,
    ) -> Dict[str, Any]:
        """Compose override values used when instantiating a new NPC."""

        def inherit(attr: str, default: Any) -> Any:
            if template_npc is None:
                return default
            return getattr(template_npc, attr, default)

        npc_id = metadata["id"]
        npc_name = metadata["name"]
        room_id = metadata["room_id"]

        return {
            "id": npc_id,
            "name": npc_name,
            "description": f"{npc_name} looks ready for adventure.",
            "room_id": room_id,
            "hardiness": inherit("hardiness", 10),
            "agility": inherit("agility", 10),
            "friendliness": friendliness_value,
            "courage": inherit("courage", 100),
            "weapon_id": None,
            "armor_worn": inherit("armor_worn", 0),
            "gold": inherit("gold", 0),
            "is_dead": False,
        }

    @staticmethod
    def _apply_npc_overrides(new_npc, overrides: Dict[str, Any]):
        """Apply overrides and core defaults to a new NPC instance."""
        for key, value in overrides.items():
            setattr(new_npc, key, value)

        new_npc.current_health = getattr(new_npc, "hardiness", 10)

    def _resolve_item_location(
        self, room_id: Optional[int], item_name: str
    ) -> Optional[int]:
        """Determine where an item should spawn; handle validation messaging."""
        if not self.engine:
            return None

        target_room_id = room_id
        if target_room_id is None:
            target_room_id = getattr(self.engine.player, "current_room", None)

        if target_room_id is None:
            self.echo(f"[Cannot spawn {item_name}: no target room]")
            return None

        if target_room_id != 0 and target_room_id not in self.engine.rooms:
            self.echo(f"[Cannot spawn {item_name}: room {target_room_id} not found]")
            return None

        return target_room_id

    def _next_item_id(self) -> int:
        """Get the next available item id."""
        items = getattr(self.engine, "items", {})
        if not items:
            return 1

        next_id = max(items.keys()) + 1
        while next_id in items:
            next_id += 1
        return next_id

    def _get_item_template(self):
        """Return a template item from the engine, if available."""
        if not self.engine or not getattr(self.engine, "items", None):
            return None
        return next(iter(self.engine.items.values()), None)

    def _resolve_item_type(self, template_item) -> Tuple[Optional[type], Any]:
        """Determine class and item type defaults for new items."""

        item_cls = template_item.__class__ if template_item else None
        item_type_value: Any = getattr(template_item, "item_type", None)

        if item_cls is None and core_engine is not None:
            item_cls = getattr(core_engine, "Item", None)

        if item_type_value is None and core_engine is not None:
            item_type_enum = getattr(core_engine, "ItemType", None)
            if item_type_enum is not None:
                try:
                    item_type_value = item_type_enum("normal")
                except ValueError:
                    item_type_value = None

        if item_type_value is None:
            item_type_value = "normal"

        return item_cls, item_type_value

    def _build_item_overrides(
        self,
        metadata: Dict[str, Any],
        template_item,
        item_type_value: Any,
    ) -> Dict[str, Any]:
        """Compose override values for item instantiation."""

        def inherit(attr: str, default: Any) -> Any:
            if template_item is None:
                return default
            return getattr(template_item, attr, default)

        item_id = metadata["id"]
        item_name = metadata["name"]
        room_id = metadata["room_id"]
        location = 0 if room_id == 0 else room_id

        return {
            "id": item_id,
            "name": item_name,
            "description": f"A newly conjured {item_name}.",
            "item_type": item_type_value,
            "weight": inherit("weight", 1),
            "value": inherit("value", 0),
            "is_weapon": inherit("is_weapon", False),
            "weapon_type": inherit("weapon_type", 0),
            "weapon_dice": inherit("weapon_dice", 1),
            "weapon_sides": inherit("weapon_sides", 6),
            "is_armor": inherit("is_armor", False),
            "armor_value": inherit("armor_value", 0),
            "is_takeable": inherit("is_takeable", True),
            "is_wearable": inherit("is_wearable", False),
            "location": location,
        }

    @staticmethod
    def _apply_item_overrides(new_item, overrides: Dict[str, Any]):
        """Apply item overrides to a freshly created item."""
        for key, value in overrides.items():
            setattr(new_item, key, value)

    def _finalize_item_spawn(self, new_item):
        """Persist the spawned item and emit appropriate feedback."""
        self.engine.items[new_item.id] = new_item

        if new_item.location == 0 and hasattr(self.engine.player, "inventory"):
            inventory = self.engine.player.inventory
            if isinstance(inventory, list) and new_item.id not in inventory:
                inventory.append(new_item.id)
            self.echo(f"[Added {new_item.name} to inventory]")
        else:
            room = self.engine.rooms.get(new_item.location)
            room_name = room.name if room else str(new_item.location)
            self.echo(f"[Spawned {new_item.name} in {room_name}]")

    def spawn_item(self, item_name: str, room_id: Optional[int] = None):
        """Spawn a new item"""
        if not self.engine:
            return None

        target_room_id = self._resolve_item_location(room_id, item_name)
        if target_room_id is None:
            return None

        next_id = self._next_item_id()
        template_item = self._get_item_template()
        item_cls, item_type_value = self._resolve_item_type(template_item)

        overrides = self._build_item_overrides(
            {"id": next_id, "name": item_name, "room_id": target_room_id},
            template_item,
            item_type_value,
        )

        new_item = self._instantiate_dataclass(item_cls, overrides, template_item)
        if new_item is None:
            self.echo(f"[Cannot spawn {item_name}: item template unavailable]")
            return None

        self._apply_item_overrides(new_item, overrides)
        self._finalize_item_spawn(new_item)

        return new_item

    def spawn_npc(self, npc_name: str, room_id: Optional[int] = None):
        """Spawn a new NPC"""
        if not self.engine:
            return None

        target_room_id = self._resolve_npc_room_id(room_id, npc_name)
        if target_room_id is None:
            return None

        next_id = self._next_monster_id()
        template_npc = self._get_monster_template()
        npc_cls, friendliness_value = self._resolve_npc_type(template_npc)

        overrides = self._build_npc_overrides(
            {"id": next_id, "name": npc_name, "room_id": target_room_id},
            template_npc,
            friendliness_value,
        )

        new_npc = self._instantiate_dataclass(npc_cls, overrides, template_npc)
        if new_npc is None:
            self.echo(f"[Cannot spawn NPC {npc_name}: template unavailable]")
            return None

        self._apply_npc_overrides(new_npc, overrides)

        self.engine.monsters[new_npc.id] = new_npc
        room = self.engine.rooms.get(target_room_id)
        room_name = room.name if room else str(target_room_id)
        self.echo(f"[Spawned NPC {npc_name} in {room_name}]")

        return new_npc

    def set_flag(self, flag_name: str, value: Any = True):
        """Set a global flag"""
        if self.engine:
            if not hasattr(self.engine, "script_flags"):
                self.engine.script_flags = {}
            self.engine.script_flags[flag_name] = value

    def get_flag(self, flag_name: str, default: Any = None):
        """Get a global flag"""
        if self.engine and hasattr(self.engine, "script_flags"):
            return self.engine.script_flags.get(flag_name, default)
        return default

    def has_flag(self, flag_name: str) -> bool:
        """Check if flag exists and is truthy"""
        return bool(self.get_flag(flag_name))


class ScriptExecutionError(RuntimeError):
    """Generic script execution failure."""


class ModdingSystem:
    """System for loading and executing mod scripts"""

    def __init__(self, engine=None):
        self.engine = engine
        self.hooks: Dict[EventType, List[ScriptHook]] = {
            event: [] for event in EventType
        }
        self.custom_commands: Dict[str, CustomCommand] = {}
        self.script_context = ScriptContext(engine)

    def register_hook(self, hook: ScriptHook):
        """Register an event hook"""
        if hook.event not in self.hooks:
            self.hooks[hook.event] = []
        self.hooks[hook.event].append(hook)
        # Sort by priority (highest first)
        self.hooks[hook.event].sort(key=lambda h: h.priority, reverse=True)

    def register_command(self, command: CustomCommand):
        """Register a custom command"""
        self.custom_commands[command.verb] = command
        for alias in command.aliases:
            self.custom_commands[alias] = command

    def trigger_event(self, event: EventType, event_data: Dict[str, Any]) -> List[str]:
        """Trigger an event and run associated hooks"""
        output = []

        if event not in self.hooks:
            return output

        for hook in self.hooks[event]:
            if not hook.enabled:
                continue
            if not hook.matches_filter(event_data):
                continue

            try:
                result = self._execute_script(hook.script_code, event_data)
                if result:
                    output.extend(result)
            except ScriptExecutionError as error:
                output.append(f"[Script Error: {error}]")

        return output

    def execute_custom_command(self, verb: str, args: str) -> Optional[List[str]]:
        """Execute a custom command if registered"""
        if verb not in self.custom_commands:
            return None

        command = self.custom_commands[verb]
        event_data = {"verb": verb, "args": args, "command": f"{verb} {args}"}

        try:
            return self._execute_script(command.handler_code, event_data)
        except ScriptExecutionError as error:
            return [f"[Command Error: {error}]"]

    @staticmethod
    def _safe_exec(code: str, namespace: Dict[str, Any]) -> None:
        """Execute script code and normalize raised exceptions."""
        try:
            exec(code, namespace)  # pylint: disable=exec-used
        except (
            SyntaxError,
            NameError,
            RuntimeError,
            TypeError,
            ValueError,
            AttributeError,
        ) as exc:
            raise ScriptExecutionError(f"{type(exc).__name__}: {exc}") from exc
        except Exception as exc:  # pylint: disable=broad-exception-caught
            raise ScriptExecutionError(str(exc)) from exc

    def _execute_script(self, code: str, event_data: Dict[str, Any]) -> List[str]:
        """Execute script code in safe context"""
        # Reset output buffer
        self.script_context.output_buffer = []

        # Create execution namespace
        namespace = {
            "ctx": self.script_context,
            "data": event_data,
            "print": self.script_context.print,
            "echo": self.script_context.echo,
            "player": self.script_context.get_player(),
            "room": self.script_context.get_room(),
            # Utility functions
            "get_npc": self.script_context.get_npc,
            "get_item": self.script_context.get_item,
            "spawn_item": self.script_context.spawn_item,
            "spawn_npc": self.script_context.spawn_npc,
            "set_flag": self.script_context.set_flag,
            "get_flag": self.script_context.get_flag,
            "has_flag": self.script_context.has_flag,
        }

        # Import allowed modules
        for module in self.script_context.allowed_modules:
            try:
                namespace[module] = __import__(module)
            except ImportError:
                pass

        # Execute code
        try:
            self._safe_exec(code, namespace)
        except ScriptExecutionError as error:
            return [f"[Script Error: {error}]"]

        return self.script_context.output_buffer

    def load_mod_file(self, filepath: str) -> bool:
        """Load a mod from a Python file"""
        try:
            with open(filepath, "r", encoding="utf-8") as handle:
                code = handle.read()
        except OSError as exc:
            print(f"Error loading mod {filepath}: {exc}")
            return False

        namespace = {
            "register_hook": self.register_hook,
            "register_command": self.register_command,
            "ScriptHook": ScriptHook,
            "CustomCommand": CustomCommand,
            "EventType": EventType,
        }

        try:
            self._safe_exec(code, namespace)
        except ScriptExecutionError as exc:
            print(f"Error loading mod {filepath}: {exc}")
            return False

        return True

    def get_custom_command_help(self) -> List[str]:
        """Get help text for custom commands"""
        help_lines = []

        seen = set()
        for command in self.custom_commands.values():
            if command.verb in seen or command.hidden:
                continue
            seen.add(command.verb)

            aliases = ", ".join(command.aliases) if command.aliases else ""
            help_text = command.help_text or "Custom command"

            if aliases:
                help_lines.append(f"  {command.verb} ({aliases}) - {help_text}")
            else:
                help_lines.append(f"  {command.verb} - {help_text}")

        return help_lines

    def to_dict(self) -> Dict:
        """Serialize mod state"""
        return {
            "script_flags": getattr(self.engine, "script_flags", {}),
            "enabled_hooks": [
                {"event": hook.event.value, "enabled": hook.enabled}
                for hooks in self.hooks.values()
                for hook in hooks
            ],
        }

    def from_dict(self, data: Dict):
        """Restore mod state"""
        if "script_flags" in data and self.engine:
            self.engine.script_flags = data["script_flags"]

        if "enabled_hooks" in data:
            for hook_data in data["enabled_hooks"]:
                event = EventType(hook_data["event"])
                # Find matching hook and set enabled state
                for hook in self.hooks[event]:
                    # Would need better hook identification
                    hook.enabled = hook_data["enabled"]


# Example mod file format:
# example_mod.py - Example mod for Colossal StoryWorks
#
# hook = ScriptHook(
#     event=EventType.ON_ENTER_ROOM,
#     script_code='''
# if room.id == 5:
#     echo("You feel a strange presence in this room...")
#     set_flag("visited_haunted_room", True)
# ''',
#     filter_params={'room_id': 5}
# )
# register_hook(hook)
#
# command = CustomCommand(
#     verb="dance",
#     aliases=["boogie"],
#     help_text="Dance around like nobody's watching",
#     handler_code='''
# echo("You dance awkwardly. Everyone stares.")
# if has_flag("dance_master"):
#     echo("Actually, you're quite good at this!")
# else:
#     echo("Maybe practice more...")
# '''
# )
# register_command(command)
