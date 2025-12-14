#!/usr/bin/env python3
# pyright: reportGeneralTypeIssues=false, reportMissingImports=false
"""SagaCraft - Game Engine

A Python implementation of classic text adventure game mechanics for creating and
playing interactive fiction adventures.
"""

# pylint: disable=too-many-lines

import json
import random
from typing import Any, Dict, List, Optional, Set, cast
from dataclasses import dataclass, field
from enum import Enum

# Import natural language parser if available
try:
    from sagacraft.core import parser as parser_module
    from sagacraft.systems import npc_context as npc_context_module
    from sagacraft.systems import environment as environment_module
    from sagacraft.tools import commands as commands_module
    from sagacraft.systems import achievements as achievements_module
    from sagacraft.systems import journal as journal_module
    from sagacraft.systems import tutorial as tutorial_module
    from sagacraft.ui import accessibility as accessibility_module

    NaturalLanguageParser = parser_module.NaturalLanguageParser
    Companion = parser_module.Companion
    CompanionStance = getattr(parser_module, "CompanionStance", None)
    NPCContextManager = npc_context_module.NPCContextManager
    EnvironmentalSystem = environment_module.EnvironmentalSystem
    SmartCommandSystem = commands_module.SmartCommandSystem
    AchievementSystem = achievements_module.AchievementSystem
    AdventureJournal = journal_module.AdventureJournal
    ContextualHintSystem = tutorial_module.ContextualHintSystem
    AccessibilitySystem = accessibility_module.AccessibilitySystem
    # Defer modding import to avoid circular dependency
    ModdingSystem = None
    EventType = None

    ENHANCED_PARSER_AVAILABLE = True
except ImportError:
    ENHANCED_PARSER_AVAILABLE = False
    NaturalLanguageParser = cast(Any, None)
    Companion = cast(Any, None)
    CompanionStance = None
    NPCContextManager = cast(Any, None)
    EnvironmentalSystem = cast(Any, None)
    SmartCommandSystem = cast(Any, None)
    AchievementSystem = cast(Any, None)
    AdventureJournal = cast(Any, None)
    ContextualHintSystem = cast(Any, None)
    ModdingSystem = cast(Any, None)
    EventType = cast(Any, None)
    AccessibilitySystem = cast(Any, None)


class ItemType(Enum):
    """Item categories represented in the engine."""

    WEAPON = "weapon"
    ARMOR = "armor"
    TREASURE = "treasure"
    READABLE = "readable"
    EDIBLE = "edible"
    DRINKABLE = "drinkable"
    CONTAINER = "container"
    NORMAL = "normal"


class MonsterStatus(Enum):
    """Disposition states used for creature behavior."""

    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"


@dataclass
class Item:
    """Represents an item in the game world"""

    id: int
    name: str
    description: str
    item_type: ItemType
    weight: int
    value: int
    is_weapon: bool = False
    weapon_type: int = 0  # 1=axe, 2=bow, 3=club, 4=spear, 5=sword
    weapon_dice: int = 1
    weapon_sides: int = 6
    is_armor: bool = False
    armor_value: int = 0
    is_takeable: bool = True
    is_wearable: bool = False
    location: int = 0  # 0=inventory, -1=worn, room_id or monster_id

    def get_damage(self) -> int:
        """Calculate weapon damage"""
        if not self.is_weapon:
            return 0
        return sum(
            random.randint(1, self.weapon_sides) for _ in range(self.weapon_dice)
        )


@dataclass
class Monster:
    """Represents a monster or NPC"""

    id: int
    name: str
    description: str
    room_id: int
    hardiness: int
    agility: int
    friendliness: MonsterStatus
    courage: int
    weapon_id: Optional[int] = None
    armor_worn: int = 0
    gold: int = 0
    is_dead: bool = False
    current_health: Optional[int] = None

    def __post_init__(self):
        if self.current_health is None:
            self.current_health = self.hardiness


@dataclass
class Room:
    """Represents a room/location"""

    id: int
    name: str
    description: str
    exits: Dict[str, int] = field(default_factory=dict)  # direction: room_id
    is_dark: bool = False

    def get_exit(self, direction: str) -> Optional[int]:
        """Get room ID for a given direction"""
        return self.exits.get(direction.lower())


@dataclass
class Player:
    """Player character stats"""

    name: str = "Adventurer"
    hardiness: int = 12
    agility: int = 12
    charisma: int = 12
    weapon_ability: Dict[int, int] = field(
        default_factory=lambda: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5}
    )
    armor_expertise: int = 0
    gold: int = 200
    current_room: int = 1
    current_health: Optional[int] = None
    inventory: List[Any] = field(default_factory=list)  # item IDs or objects from mods
    equipped_weapon: Optional[int] = None
    equipped_armor: Optional[int] = None

    def __post_init__(self):
        if self.current_health is None:
            self.current_health = self.hardiness


class AdventureGame:
    """Main game engine for text adventures"""

    def __init__(self, adventure_file: str):
        self.adventure_file = adventure_file
        self.rooms: Dict[int, Room] = {}
        self.items: Dict[int, Item] = {}
        self.monsters: Dict[int, Monster] = {}
        self.player: Player = Player()
        self.companions: List = []  # Party members
        self.turn_count = 0
        self.game_over = False
        self.adventure_title = ""
        self.adventure_intro = ""

        # Optional subsystems initialized below
        self.parser: Optional[Any] = None
        self.npc_context_manager: Optional[Any] = None
        self.environment: Optional[Any] = None
        self.command_system: Optional[Any] = None
        self.achievements: Optional[Any] = None
        self.journal: Optional[Any] = None
        self.tutorial: Optional[Any] = None
        self.modding: Optional[Any] = None
        self.accessibility: Optional[Any] = None

        # Initialize natural language parser if available
        if ENHANCED_PARSER_AVAILABLE:
            self.parser = NaturalLanguageParser()
            self.npc_context_manager = NPCContextManager()
            self.environment = EnvironmentalSystem()
            self.command_system = SmartCommandSystem()
            self.achievements = AchievementSystem()
            self.journal = AdventureJournal()
            self.tutorial = ContextualHintSystem()
            # Lazy load ModdingSystem to avoid circular import
            self._init_modding()
            self.accessibility = AccessibilitySystem()
            self.use_enhanced_parser = True
        else:
            self.use_enhanced_parser = False

        self.effects: List[Dict[str, Any]] = []
        self.equipped_items: Set[Any] = set()
        self._mod_last_room_id: Optional[int] = None

    def _init_modding(self):
        """Lazy load ModdingSystem and EventType to break circular import."""
        try:
            import sys
            from sagacraft.tools.modding import (
                EventType as _EventType,
                ModdingSystem as _ModdingSystem,
            )

            # Update both module-level and instance-level EventType
            globals()["EventType"] = _EventType
            sys.modules[__name__].EventType = _EventType
            self.modding = _ModdingSystem(engine=self)
        except ImportError:
            self.modding = None

    @staticmethod
    def _safe_int(value: Any, default: int) -> int:
        """Convert value to int, returning default on failure."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _iter_inventory_items(self):
        """Yield Item objects from inventory entries (ids or objects)."""
        for entry in list(self.player.inventory):
            if isinstance(entry, int):
                item_obj = self.items.get(entry)
            else:
                item_obj = entry if isinstance(entry, Item) else None
            if item_obj:
                yield item_obj

    def _find_inventory_item(self, name: str) -> Optional[Item]:
        target_lower = name.lower()
        for item_obj in self._iter_inventory_items():
            if target_lower in item_obj.name.lower():
                return item_obj
        return None

    def _add_inventory_item(self, item: Item):
        if item.id not in self.player.inventory and item not in self.player.inventory:
            self.player.inventory.append(item.id)

    def _remove_inventory_item(self, item: Item):
        if item.id in self.player.inventory:
            self.player.inventory.remove(item.id)
        elif item in self.player.inventory:
            self.player.inventory.remove(item)

    def _fire_mod_event(
        self,
        event,
        payload: Optional[Dict[str, Any]] = None,
        *,
        echo: bool = True,
    ) -> tuple[Dict[str, Any], List[str]]:
        """Trigger a mod event and optionally echo resulting output."""
        if payload is None:
            payload = {}

        if not self.modding or EventType is None or event is None:
            return payload, []

        if not isinstance(event, EventType):
            try:
                event = EventType(event)
            except ValueError:
                return payload, []

        outputs = self.modding.trigger_event(event, payload) or []
        if echo:
            for line in outputs:
                print(line)
        return payload, outputs

    def notify_room_entry(
        self, room: Optional["Room"], previous_room: Optional["Room"] = None
    ):
        """Inform mods that the player has entered a room."""
        if not room:
            return

        payload = {
            "player": self.player,
            "room": room,
            "room_id": getattr(room, "id", None),
            "previous_room": previous_room,
            "previous_room_id": getattr(previous_room, "id", None),
        }
        self._fire_mod_event(EventType.ON_ENTER_ROOM, payload)
        self._mod_last_room_id = getattr(room, "id", None)

    def _notify_room_exit(
        self, room: Optional["Room"], direction: str
    ) -> Dict[str, Any]:
        """Fire the exit-room event and allow scripts to cancel movement."""
        payload = {
            "player": self.player,
            "room": room,
            "room_id": getattr(room, "id", None),
            "direction": direction,
            "cancel": False,
        }
        payload, _ = self._fire_mod_event(EventType.ON_EXIT_ROOM, payload)
        return payload

    def on_mods_loaded(self):
        """Called after external systems finish loading mods for this engine."""
        if not self.modding or EventType is None:
            return

        payload = {"player": self.player, "adventure": self}
        self._fire_mod_event(EventType.ON_LOAD, payload)
        self.notify_room_entry(self.get_current_room(), previous_room=None)

    def load_adventure(self):
        """Load adventure data from JSON file"""
        try:
            with open(self.adventure_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)

            self.adventure_title = data.get("title", "Untitled Adventure")
            self.adventure_intro = data.get("intro", "")

            # Load rooms
            for room_data in data.get("rooms", []):
                room = Room(
                    id=room_data["id"],
                    name=room_data["name"],
                    description=room_data["description"],
                    exits=room_data.get("exits", {}),
                    is_dark=room_data.get("is_dark", False),
                )
                self.rooms[room.id] = room

            # Load items
            for item_data in data.get("items", []):
                item = Item(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    item_type=ItemType(item_data.get("type", "normal")),
                    weight=item_data.get("weight", 1),
                    value=item_data.get("value", 0),
                    is_weapon=item_data.get("is_weapon", False),
                    weapon_type=item_data.get("weapon_type", 0),
                    weapon_dice=item_data.get("weapon_dice", 1),
                    weapon_sides=item_data.get("weapon_sides", 6),
                    is_armor=item_data.get("is_armor", False),
                    armor_value=item_data.get("armor_value", 0),
                    is_takeable=item_data.get("is_takeable", True),
                    location=item_data.get("location", 0),
                )
                self.items[item.id] = item

            # Load monsters
            for mon_data in data.get("monsters", []):
                monster = Monster(
                    id=mon_data["id"],
                    name=mon_data["name"],
                    description=mon_data["description"],
                    room_id=mon_data.get("room_id", 1),
                    hardiness=mon_data.get("hardiness", 10),
                    agility=mon_data.get("agility", 10),
                    friendliness=MonsterStatus(mon_data.get("friendliness", "neutral")),
                    courage=mon_data.get("courage", 100),
                    weapon_id=mon_data.get("weapon_id"),
                    armor_worn=mon_data.get("armor_worn", 0),
                    gold=mon_data.get("gold", 0),
                )
                self.monsters[monster.id] = monster

            # Load effects (special events)
            self.effects = data.get("effects", [])

            # Set player starting position
            self.player.current_room = data.get("start_room", 1)

            print(f"\n{'=' * 60}")
            print(f"{self.adventure_title:^60}")
            print(f"{'=' * 60}\n")
            if self.adventure_intro:
                print(self.adventure_intro)
                print()

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Adventure file '{self.adventure_file}' not found"
            ) from exc
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in adventure file '{self.adventure_file}': {exc}"
            ) from exc

    def get_current_room(self) -> Optional[Room]:
        """Get the room the player is currently in"""
        return self.rooms.get(self.player.current_room)

    def get_items_in_room(self, room_id: int) -> List[Item]:
        """Get all items in a specific room"""
        return [item for item in self.items.values() if item.location == room_id]

    def get_monsters_in_room(self, room_id: int) -> List[Monster]:
        """Get all living monsters in a specific room"""
        return [
            m for m in self.monsters.values() if m.room_id == room_id and not m.is_dead
        ]

    def look(self):
        """Display current room description"""
        room = self.get_current_room()
        if not room:
            print("You are in a void.")
            return
        print(f"\n{room.name}")
        print("-" * len(room.name))
        print(room.description)

        # Show exits
        if room.exits:
            exits = ", ".join(room.exits.keys())
            print(f"\nObvious exits: {exits}")
        else:
            print("\nNo obvious exits.")

        # Environmental details (time/weather)
        if self.environment:
            self.environment.advance_time()
            room_state = self.environment.get_or_create_room_state(room.id)
            room_state.increment_visit()

            # Show environmental atmosphere occasionally
            if room_state.visited_count == 1:
                print(f"\n{self.environment.get_time_description()}")
                print(self.environment.get_weather_description())

            # Show ambient message occasionally
            ambient = self.environment.get_ambient_message(room.id)
            if ambient:
                print(f"\n{ambient}")

            # Show inspectable objects
            objects = self.environment.get_room_objects(room.id)
            if objects:
                print("\nYou notice:")
                for obj in objects:
                    print(f"  - {obj.short_desc}")

        # Show items
        items = self.get_items_in_room(room.id)
        if items:
            print("\nYou see:")
            for item in items:
                print(f"  - {item.name}")

        # Show monsters
        monsters = self.get_monsters_in_room(room.id)
        if monsters:
            print("\nPresent:")
            for monster in monsters:
                status = (
                    "friendly"
                    if monster.friendliness == MonsterStatus.FRIENDLY
                    else (
                        "hostile"
                        if monster.friendliness == MonsterStatus.HOSTILE
                        else ""
                    )
                )
                print(f"  - {monster.name} {f'({status})' if status else ''}")

    def move(self, direction: str):
        """Move player in a direction"""
        room = self.get_current_room()
        if not room:
            print("You feel disoriented and cannot move.")
            return

        normalized_direction = direction.lower()
        exit_payload = self._notify_room_exit(room, normalized_direction)
        if exit_payload.get("cancel"):
            if exit_payload.get("message"):
                print(exit_payload["message"])
            return

        next_room_id = room.get_exit(normalized_direction)

        if next_room_id is None:
            print("You can't go that way.")
            return

        previous_room = room
        self.player.current_room = next_room_id
        self.turn_count += 1

        # Track stats and achievements
        if self.achievements:
            self.achievements.statistics.increment("steps_taken")
            self.achievements.statistics.increment("rooms_visited")
            self.achievements.check_achievements()

        # Log to journal
        new_room = self.rooms[next_room_id]

        if self.journal and self.journal.auto_log_enabled:
            self.journal.log_event(
                title="Room Entered",
                content=f"Entered {new_room.name}",
                room_id=next_room_id,
            )

        # Progress environment time
        if self.environment:
            self.environment.advance_time()

        self.notify_room_entry(new_room, previous_room=previous_room)

        self.look()

        # Show tutorial hint
        if self.tutorial:
            stats = self.achievements.statistics.to_dict() if self.achievements else {}
            hint = self.tutorial.check_and_show_hint("moved", stats)
            if hint:
                print(self.tutorial.format_tutorial(hint))

    def get_item(self, item_name: str):
        """Pick up an item"""
        room = self.get_current_room()
        if not room:
            print("There's nothing to pick up here.")
            return
        items = self.get_items_in_room(room.id)

        # Find matching item
        item = None
        search = item_name.lower()
        for i in items:
            if search in i.name.lower():
                item = i
                break

        if item is None:
            print(f"You don't see a {item_name} here.")
            return

        if not item.is_takeable:
            print(f"You can't take the {item.name}.")
            return

        take_payload = {
            "player": self.player,
            "room": room,
            "room_id": room.id,
            "item": item,
            "item_id": item.id,
            "item_name": item.name,
            "cancel": False,
        }
        take_payload, _ = self._fire_mod_event(EventType.ON_TAKE_ITEM, take_payload)
        if take_payload.get("cancel"):
            message = take_payload.get("message")
            if message:
                print(message)
            return

        payload_item = take_payload.get("item", item)
        if isinstance(payload_item, Item):
            item = payload_item
        item.location = 0  # Move to inventory
        self._add_inventory_item(item)
        print(f"You take the {item.name}.")

    def drop_item(self, item_name: str):
        """Drop an item"""
        room = self.get_current_room()
        if not room:
            print("You are nowhere. You can't drop anything.")
            return

        item = self._find_inventory_item(item_name)

        if item is None:
            print(f"You don't have a {item_name}.")
            return

        drop_payload = {
            "player": self.player,
            "room": room,
            "room_id": self.player.current_room,
            "item": item,
            "item_id": item.id,
            "item_name": item.name,
            "cancel": False,
        }
        drop_payload, _ = self._fire_mod_event(EventType.ON_DROP_ITEM, drop_payload)
        if drop_payload.get("cancel"):
            message = drop_payload.get("message")
            if message:
                print(message)
            return

        room_id = self._safe_int(
            drop_payload.get("room_id", self.player.current_room),
            self.player.current_room,
        )
        payload_item = drop_payload.get("item", item)
        if isinstance(payload_item, Item):
            item = payload_item
        item.location = room_id
        self._remove_inventory_item(item)
        print(f"You drop the {item.name}.")

    def show_inventory(self):
        """Display player inventory"""
        if not self.player.inventory:
            print("\nYou are empty-handed.")
            return

        print("\nYou are carrying:")
        total_weight = 0
        for item_id in self.player.inventory:
            item = self.items[item_id]
            equipped = ""
            if item.id == self.player.equipped_weapon:
                equipped = " (weapon)"
            elif item.id == self.player.equipped_armor:
                equipped = " (armor)"
            print(f"  - {item.name}{equipped}")
            total_weight += item.weight

        print(f"\nTotal weight: {total_weight}")
        print(f"Gold: {self.player.gold}")

    def show_status(self):
        """Display player status"""
        print(f"\n{self.player.name}")
        print("-" * 40)
        print(f"Health: {self.player.current_health}/{self.player.hardiness}")
        print(f"Hardiness: {self.player.hardiness}")
        print(f"Agility: {self.player.agility}")
        print(f"Charisma: {self.player.charisma}")
        print(f"Gold: {self.player.gold}")

        if self.player.equipped_weapon:
            weapon = self.items[self.player.equipped_weapon]
            print(f"Weapon: {weapon.name}")
        if self.player.equipped_armor:
            armor = self.items[self.player.equipped_armor]
            print(f"Armor: {armor.name}")

    def attack(self, target_name: str):
        """Attack a monster"""
        room = self.get_current_room()
        if not room:
            print("There's nothing to attack here.")
            return
        monsters = self.get_monsters_in_room(room.id)

        target = None
        for m in monsters:
            if target_name.lower() in m.name.lower():
                target = m
                break

        if target is None:
            print(f"You don't see a {target_name} here.")
            return

        # Make target hostile
        target.friendliness = MonsterStatus.HOSTILE

        # Player attacks
        weapon = None
        if self.player.equipped_weapon:
            weapon = self.items.get(self.player.equipped_weapon)

        base_damage = weapon.get_damage() if weapon else random.randint(1, 3)
        attack_payload = {
            "player": self.player,
            "room": room,
            "weapon": weapon,
            "target": target,
            "damage": base_damage,
            "cancel": False,
        }
        attack_payload, _ = self._fire_mod_event(EventType.ON_ATTACK, attack_payload)
        if attack_payload.get("cancel"):
            message = attack_payload.get("message")
            if message:
                print(message)
            return

        raw_damage = attack_payload.get("damage", base_damage)
        damage = self._safe_int(raw_damage, base_damage)
        payload_target = attack_payload.get("target", target)
        if isinstance(payload_target, Monster):
            target = payload_target
        if target is None:
            print("Your attack fizzles before it lands.")
            return

        if target.current_health is None:
            target.current_health = target.hardiness

        print(f"\nYou attack the {target.name}!")
        target.current_health -= damage
        print(f"You hit for {damage} damage!")

        if target.current_health <= 0:
            target.is_dead = True
            print(f"The {target.name} is dead!")
            kill_payload = {
                "player": self.player,
                "room": room,
                "monster": target,
                "weapon": weapon,
                "damage": damage,
            }
            self._fire_mod_event(EventType.ON_KILL, kill_payload)
            if target.gold > 0:
                self.player.gold += target.gold
                print(f"You found {target.gold} gold pieces!")
            return

        # Monster counter-attacks
        mon_damage = random.randint(1, 6)
        if self.player.current_health is None:
            self.player.current_health = self.player.hardiness
        self.player.current_health -= mon_damage
        print(f"The {target.name} hits you for {mon_damage} damage!")

        if self.player.current_health <= 0:
            print("\nYou have died!")
            death_payload = {
                "player": self.player,
                "room": room,
                "killer": target,
            }
            self._fire_mod_event(EventType.ON_DEATH, death_payload)
            self.game_over = True

    # NPC Interaction & Context Methods
    def talk_to_npc(self, npc_name: str, topic: Optional[str] = None):
        """Enhanced NPC interaction with memory and emotions"""
        room = self.get_current_room()
        if not room:
            print("No one is here to talk to.")
            return
        monsters = self.get_monsters_in_room(room.id)

        # Find the NPC
        npc = None
        for m in monsters:
            if npc_name.lower() in m.name.lower():
                npc = m
                break

        if npc is None:
            print(f"You don't see {npc_name} here.")
            return

        talk_payload = {
            "player": self.player,
            "room": room,
            "npc": npc,
            "topic": topic,
            "cancel": False,
        }
        talk_payload, _ = self._fire_mod_event(EventType.ON_TALK, talk_payload)
        if talk_payload.get("cancel"):
            message = talk_payload.get("message")
            if message:
                print(message)
            return

        payload_npc = talk_payload.get("npc", npc)
        if isinstance(payload_npc, Monster):
            npc = payload_npc
        topic_val = talk_payload.get("topic", topic)
        if isinstance(topic_val, str):
            topic = topic_val

        if npc is None:
            print("There is no one left to talk to.")
            return

        # Get or create NPC context
        if self.npc_context_manager:
            context = self.npc_context_manager.get_or_create_context(npc.id, npc.name)

            # Show greeting based on relationship
            print(f"\n{context.get_greeting()}")

            # Record the conversation
            if topic:
                context.memory.add_topic(topic)
                print(f'You ask about "{topic}".')

                # Check if topic has been discussed before
                if context.memory.has_discussed(topic):
                    print(
                        f"{npc.name} says {context.get_dialogue_modifier()}, "
                        f'"We\'ve discussed this before..."'
                    )
                else:
                    print(f"{npc.name} responds {context.get_dialogue_modifier()}.")

            context.memory.increment_conversation()

            # Show relationship status for trusted+ NPCs
            if context.relationship.value >= 2:
                print(
                    f"[{npc.name} considers you a "
                    f"{context.relationship.name.lower()}]"
                )
        else:
            # Fallback for simple interaction
            print(f"You talk to {npc.name}.")
            if npc.friendliness == MonsterStatus.FRIENDLY:
                print(f"{npc.name} seems friendly.")
            elif npc.friendliness == MonsterStatus.HOSTILE:
                print(f"{npc.name} looks angry!")

    def examine_npc(self, npc_name: str):
        """Examine an NPC to learn about them"""
        room = self.get_current_room()
        if not room:
            print("No one is here to examine.")
            return
        monsters = self.get_monsters_in_room(room.id)

        npc = None
        for m in monsters:
            if npc_name.lower() in m.name.lower():
                npc = m
                break

        if npc is None:
            print(f"You don't see {npc_name} here.")
            return

        examine_payload = {
            "player": self.player,
            "room": room,
            "npc": npc,
            "target_type": "npc",
            "target_name": npc_name,
            "cancel": False,
        }
        examine_payload, _ = self._fire_mod_event(EventType.ON_EXAMINE, examine_payload)
        if examine_payload.get("cancel"):
            message = examine_payload.get("message")
            if message:
                print(message)
            return
        if examine_payload.get("handled"):
            return

        payload_npc = examine_payload.get("npc", npc)
        if isinstance(payload_npc, Monster):
            npc = payload_npc
        if npc is None:
            return

        print(f"\n{npc.description}")

        # Show context-aware details
        if self.npc_context_manager:
            context = self.npc_context_manager.get_context(npc.id)
            if context:
                print(f"{npc.name} appears {context.current_mood}.")

                # Show personality if familiar
                if context.memory.times_talked >= 3:
                    if context.personality_traits:
                        traits = ", ".join(context.personality_traits)
                        print(f"They seem {traits}.")

    def examine_object(self, object_name: str):
        """Examine an environmental object"""
        if not self.environment:
            print(f"You examine the {object_name} closely...")
            return

        room = self.get_current_room()
        if not room:
            print("You are nowhere. There's nothing to examine.")
            return
        obj = self.environment.find_object_by_keyword(room.id, object_name)

        examine_payload = {
            "player": self.player,
            "room": room,
            "object": obj,
            "object_name": object_name,
            "target_type": "object",
            "cancel": False,
        }
        examine_payload, _ = self._fire_mod_event(EventType.ON_EXAMINE, examine_payload)
        if examine_payload.get("cancel"):
            message = examine_payload.get("message")
            if message:
                print(message)
            return
        if examine_payload.get("handled"):
            return

        payload_object = examine_payload.get("object", obj)
        if payload_object is not None:
            obj = payload_object

        if obj:
            print(f"\n{obj.long_desc}")

            # Reveal item if object contains one
            if obj.contains_item_id:
                item = self.items.get(obj.contains_item_id)
                if item:
                    print(f"\nYou found: {item.name}!")
                    item.location = room.id
        else:
            print(f"You don't see anything special about {object_name}.")

    def search_area(self):
        """Search current area for hidden objects"""
        if not self.environment:
            print("You search the area carefully...")
            return

        room = self.get_current_room()
        if not room:
            print("You are nowhere. There's nothing to search.")
            return
        found = self.environment.search_room(room.id)

        if found:
            print("\nYour careful search reveals:")
            for obj in found:
                print(f"  - {obj.short_desc}")
        else:
            print("You search carefully but find nothing hidden.")

    # Party/Companion Management Methods
    def recruit_companion(self, npc_name: str):
        """Recruit an NPC as a companion"""
        if not ENHANCED_PARSER_AVAILABLE:
            print("Companion system not available.")
            return

        room = self.get_current_room()
        if not room:
            print("No one is here to recruit.")
            return
        monsters = self.get_monsters_in_room(room.id)

        # Find NPC
        npc = None
        for m in monsters:
            if npc_name.lower() in m.name.lower():
                npc = m
                break

        if not npc:
            print(f"You don't see {npc_name} here.")
            return

        # Check if NPC is friendly
        if npc.friendliness != MonsterStatus.FRIENDLY:
            print(f"{npc.name} doesn't seem interested in joining you.")
            return

        # Check party size
        if len(self.companions) >= 3:
            print("Your party is full! (Maximum 3 companions)")
            return

        # Determine role
        role = "fighter"
        if npc.agility > npc.hardiness:
            role = "rogue"

        # Create companion
        companion = Companion(npc.id, npc.name, role)
        companion.current_health = npc.current_health or npc.hardiness
        companion.max_health = npc.hardiness

        self.companions.append(companion)
        print(f"\n{npc.name} joins your party as a {role}!")
        npc.room_id = -999

    def show_party(self):
        """Display party status"""
        if not self.companions:
            print("\nYou are traveling alone.")
            return

        print("\n" + "=" * 50)
        print("YOUR PARTY")
        print("=" * 50)
        for companion in self.companions:
            alive = "ALIVE" if companion.is_alive() else "DEAD"
            status_info = ""
            if hasattr(companion, "is_waiting") and companion.is_waiting:
                status_info = " (WAITING)"
            print(f"\n{companion.name} - {companion.role} " f"({alive}){status_info}")
            print(f"  HP: {companion.current_health}/{companion.max_health}")
            print(f"  Loyalty: {companion.loyalty}/100")
            if hasattr(companion, "stance"):
                print(f"  Stance: {companion.stance.value}")
        print("=" * 50)

    def party_command(self, companion_name: str, order: str):
        """Give orders to a specific companion"""
        if not ENHANCED_PARSER_AVAILABLE:
            print("Party commands not available.")
            return

        # Find companion
        companion = None
        for c in self.companions:
            if companion_name.lower() in c.name.lower():
                companion = c
                break

        if not companion:
            print(f"{companion_name} is not in your party.")
            return

        order = order.lower().strip()

        # Handle different orders
        if "wait" in order or "stay" in order:
            companion.tell_to_wait(self.player.current_room)
            print(f"{companion.name} will wait here.")
        elif "follow" in order or "come" in order:
            companion.tell_to_follow()
            print(f"{companion.name} resumes following you.")
        elif CompanionStance is not None and ("aggressive" in order or "attack" in order):
            companion.set_stance(CompanionStance.AGGRESSIVE)
            print(f"{companion.name} will fight aggressively.")
        elif CompanionStance is not None and ("defensive" in order or "defend" in order):
            companion.set_stance(CompanionStance.DEFENSIVE)
            print(f"{companion.name} will focus on defense.")
        elif CompanionStance is not None and ("support" in order or "help" in order):
            companion.set_stance(CompanionStance.SUPPORT)
            print(f"{companion.name} will support the party.")
        elif CompanionStance is not None and ("passive" in order or "rest" in order):
            companion.set_stance(CompanionStance.PASSIVE)
            print(f"{companion.name} will avoid combat.")
        else:
            print(f"You tell {companion.name}: {order}")
            print(f"{companion.name} nods in understanding.")

    def gather_party(self):
        """Bring all waiting companions to current location"""
        if not ENHANCED_PARSER_AVAILABLE:
            return

        gathered = []
        for companion in self.companions:
            if hasattr(companion, "is_waiting") and companion.is_waiting:
                companion.tell_to_follow()
                gathered.append(companion.name)

        if gathered:
            names = ", ".join(gathered)
            print(f"{names} rejoin(s) your party.")
        else:
            print("All companions are already following you.")

    def process_command(self, command: str):
        """Process a player command"""
        # Process with smart command system if available
        if self.command_system:
            # Fix typos and process
            command = self.command_system.process_input(command)
            # Add to history
            self.command_system.add_to_history(command)

        room = self.get_current_room()
        verb_initial, _, args_initial = command.partition(" ")
        command_payload: Dict[str, Any] = {
            "player": self.player,
            "room": room,
            "command": command,
            "verb": verb_initial,
            "args": args_initial.strip(),
            "handled": False,
            "cancel": False,
        }
        command_payload, _ = self._fire_mod_event(EventType.ON_COMMAND, command_payload)
        if command_payload.get("cancel"):
            message = command_payload.get("message")
            if message:
                print(message)
            return
        if command_payload.get("handled"):
            return

        command = str(command_payload.get("command", command) or "")
        verb = str(command_payload.get("verb", verb_initial) or "")
        args_text = str(command_payload.get("args", args_initial.strip()) or "")

        if not verb and command:
            verb, _, remainder = command.partition(" ")
            args_text = remainder.strip()

        if self.modding and not command_payload.get("skip_custom") and command.strip():
            verb_candidates = []
            if verb:
                verb_candidates.append(verb)
                verb_lower = verb.lower()
                if verb_lower != verb:
                    verb_candidates.append(verb_lower)

            for candidate in verb_candidates:
                custom_output = self.modding.execute_custom_command(
                    candidate,
                    args_text or "",
                )
                if custom_output is not None:
                    for line in custom_output:
                        print(line)
                    return

        # Try natural language parser first
        if self.use_enhanced_parser and self.parser:
            parsed = self.parser.parse_command(command)
            action = parsed.get("action")

            if action == "quit":
                print("\nThanks for playing!")
                self.game_over = True
                return
            elif action == "help":
                self.show_help()
                return
            elif action == "move":
                self.move(parsed.get("direction", ""))
                return
            elif action == "look":
                if parsed.get("target"):
                    print(f"You examine the {parsed['target']}...")
                    # Could add detailed examine here
                else:
                    self.look()
                return
            elif action == "get":
                target = parsed.get("target", parsed.get("object", ""))
                if target:
                    self.get_item(target)
                else:
                    print("Get what?")
                return
            elif action == "drop":
                target = parsed.get("target", parsed.get("object", ""))
                if target:
                    self.drop_item(target)
                else:
                    print("Drop what?")
                return
            elif action == "attack":
                target = parsed.get("target", "")
                if target:
                    self.attack(target)
                else:
                    print("Attack what?")
                return
            elif action == "inventory":
                self.show_inventory()
                return
            elif action == "status":
                self.show_status()
                return
            elif action == "party":
                self.show_party()
                return
            elif action == "recruit":
                target = parsed.get("target", "")
                if target:
                    self.recruit_companion(target)
                else:
                    print("Recruit who?")
                return
            elif action == "party_order":
                companion = parsed.get("companion", "")
                order = parsed.get("order", "")
                if companion and order:
                    self.party_command(companion, order)
                else:
                    print("Tell who to do what?")
                return
            elif action == "gather":
                self.gather_party()
                return
            elif action == "eat" or action == "drink":
                target = parsed.get("target", "")
                if target:
                    item = self._find_inventory_item(target)

                    if item:
                        # Check if it's consumable
                        consumable = hasattr(item, "consumable") and item.consumable
                        if consumable:
                            print(f"You {action} the {item.name}.")
                            # Apply any effects (healing, etc)
                            if hasattr(item, "heal_amount") and item.heal_amount > 0:
                                old_health = getattr(
                                    self.player, "current_health", self.player.hardiness
                                )
                                max_health = getattr(
                                    self.player, "hardiness", old_health
                                )
                                new_health = min(
                                    max_health, old_health + item.heal_amount
                                )
                                self.player.current_health = new_health
                                heal_msg = (
                                    f"You feel refreshed! "
                                    f"Health restored by "
                                    f"{item.heal_amount}."
                                )
                                print(heal_msg)
                            self._remove_inventory_item(item)
                        else:
                            print(f"You can't {action} that.")
                    else:
                        print(f"You don't have any {target}.")
                else:
                    print(f"{action.capitalize()} what?")
                return
            elif action == "trade":
                target = parsed.get("target", "")
                if target:
                    # Find NPC to trade with
                    room = self.get_current_room()
                    if not room:
                        print("You are nowhere. Trading is impossible.")
                        return
                    monsters = self.get_monsters_in_room(room.id)
                    npc = None
                    for m in monsters:
                        if target.lower() in m.name.lower():
                            npc = m
                            break

                    if npc:
                        # Check if NPC is a merchant
                        is_merchant = hasattr(npc, "is_merchant") and npc.is_merchant
                        if is_merchant:
                            print(f"You begin trading with {npc.name}.")
                            # Show merchant inventory if available
                            if hasattr(npc, "inventory") and npc.inventory:
                                print("\nAvailable items:")
                                for inv_item in npc.inventory:
                                    if not isinstance(inv_item, Item):
                                        continue
                                    price = inv_item.value if hasattr(inv_item, "value") else 10
                                    print(f"  - {inv_item.name} ({price} gold)")
                                print("\nUse 'buy [item]' or 'sell [item]'")
                            else:
                                print(f"{npc.name} has nothing to trade.")
                        else:
                            print(f"{npc.name} doesn't want to trade.")
                    else:
                        print(f"You don't see any {target} here.")
                else:
                    print("Trade with whom?")
                return
            elif action == "buy":
                target = parsed.get("target", "")
                if target:
                    # Find merchant NPC in current room
                    room = self.get_current_room()
                    if not room:
                        print("There's no one here to buy from.")
                        return
                    monsters = self.get_monsters_in_room(room.id)
                    merchant = None
                    for m in monsters:
                        is_merch = hasattr(m, "is_merchant") and m.is_merchant
                        if is_merch:
                            merchant = m
                            break

                    if merchant:
                        # Find item in merchant's inventory
                        item = None
                        if hasattr(merchant, "inventory"):
                            for inv_entry in merchant.inventory:
                                if not isinstance(inv_entry, Item):
                                    continue
                                if target.lower() in inv_entry.name.lower():
                                    item = inv_entry
                                    break

                        if item:
                            price = item.value if hasattr(item, "value") else 10
                            player_gold = (
                                self.player.gold if hasattr(self.player, "gold") else 0
                            )
                            if player_gold >= price:
                                self.player.gold -= price
                                self._add_inventory_item(item)
                                if hasattr(merchant, "inventory"):
                                    try:
                                        merchant.inventory.remove(item)
                                    except ValueError:
                                        pass
                                print(f"You bought {item.name} for " f"{price} gold.")
                            else:
                                print(f"You need {price} gold to buy that.")
                        else:
                            print(f"The merchant doesn't have any {target}.")
                    else:
                        print("There's no merchant here.")
                else:
                    print("Buy what?")
                return
            elif action == "sell":
                target = parsed.get("target", "")
                if target:
                    # Find merchant NPC in current room
                    room = self.get_current_room()
                    if not room:
                        print("There's no one here to sell to.")
                        return
                    monsters = self.get_monsters_in_room(room.id)
                    merchant = None
                    for m in monsters:
                        is_merch = hasattr(m, "is_merchant") and m.is_merchant
                        if is_merch:
                            merchant = m
                            break

                    if merchant:
                        # Find item in player's inventory
                        item = self._find_inventory_item(target)

                        if item:
                            price = item.value if hasattr(item, "value") else 5
                            sell_price = price // 2
                            if not hasattr(self.player, "gold"):
                                self.player.gold = 0
                            self.player.gold += sell_price
                            self._remove_inventory_item(item)
                            if hasattr(merchant, "inventory"):
                                merchant.inventory.append(item)
                            print(f"You sold {item.name} for " f"{sell_price} gold.")
                        else:
                            print(f"You don't have any {target}.")
                    else:
                        print("There's no merchant here.")
                else:
                    print("Sell what?")
                return
            elif action == "use":
                target = parsed.get("target", "")
                if target:
                    # Find item in inventory
                    item = self._find_inventory_item(target)

                    if item:
                        use_payload = {
                            "player": self.player,
                            "room": self.get_current_room(),
                            "item": item,
                            "item_name": item.name,
                            "cancel": False,
                        }
                        use_payload, _ = self._fire_mod_event(
                            EventType.ON_USE_ITEM, use_payload
                        )
                        if use_payload.get("cancel"):
                            message = use_payload.get("message")
                            if message:
                                print(message)
                            return
                        if use_payload.get("handled"):
                            return

                        payload_item = use_payload.get("item", item)
                        if isinstance(payload_item, Item):
                            item = payload_item

                        # Check for usable attribute
                        if hasattr(item, "usable") and getattr(item, "usable"):
                            print(f"You use the {item.name}.")
                            # Apply effects if any
                            if hasattr(item, "on_use"):
                                item.on_use(self.player, self)
                        else:
                            print(f"You can't use the {item.name}.")
                    else:
                        print(f"You don't have any {target}.")
                else:
                    print("Use what?")
                return
            elif action == "open" or action == "close":
                target = parsed.get("target", "")
                if target:
                    room = self.get_current_room()
                    if not room:
                        print("You are nowhere. There is nothing to interact with.")
                        return
                    # Check if target is in room
                    found = False
                    if hasattr(room, "features"):
                        for feature in room.features:
                            if target.lower() in feature.lower():
                                found = True
                                print(f"You {action} the {target}.")
                                # Could store state changes here
                                break

                    if not found:
                        print(f"You don't see any {target} to {action}.")
                else:
                    print(f"{action.capitalize()} what?")
                return
            elif action == "equip" or action == "unequip":
                target = parsed.get("target", "")
                if target:
                    item = None
                    if action == "equip":
                        # Find in inventory
                        item = self._find_inventory_item(target)

                        if item:
                            equippable = hasattr(item, "equippable") and item.equippable
                            if equippable:
                                # Track equipped items locally
                                self.equipped_items.add(item)
                                print(f"You equip the {item.name}.")
                            else:
                                print(f"You can't equip the {item.name}.")
                        else:
                            print(f"You don't have any {target}.")
                    else:  # unequip
                        if self.equipped_items:
                            for equipped_item in list(self.equipped_items):
                                if target.lower() in equipped_item.name.lower():
                                    item = equipped_item
                                    break

                            if item:
                                self.equipped_items.discard(item)
                                print(f"You unequip the {item.name}.")
                            else:
                                print(f"You don't have {target} equipped.")
                        else:
                            print("You don't have anything equipped.")
                else:
                    print(f"{action.capitalize()} what?")
                return
            elif action == "flee":
                # Try to escape from combat or dangerous situation
                combat_system = getattr(self, "combat", None)
                if combat_system and getattr(combat_system, "in_combat", False):
                    print("You attempt to flee from combat!")
                    # Simple flee logic
                    if random.random() > 0.5:
                        combat_system.in_combat = False
                        print("You successfully escaped!")
                    else:
                        print("You couldn't get away!")
                else:
                    # Not in combat, just move to random exit
                    room = self.get_current_room()
                    if room and room.exits:
                        direction = random.choice(list(room.exits.keys()))
                        print(f"You flee {direction}!")
                        self.move(direction)
                    else:
                        print("There's nowhere to flee!")
                return
            elif action == "give":
                target = parsed.get("target", "")
                recipient = parsed.get("recipient", "")
                if target and recipient:
                    # Find item in inventory
                    item = self._find_inventory_item(target)

                    if item:
                        # Find NPC
                        room = self.get_current_room()
                        if not room:
                            print("You are nowhere. There's no one to give items to.")
                            return
                        monsters = self.get_monsters_in_room(room.id)
                        npc = None
                        for m in monsters:
                            if recipient.lower() in m.name.lower():
                                npc = m
                                break

                        if npc:
                            self._remove_inventory_item(item)
                            if hasattr(npc, "inventory"):
                                npc.inventory.append(item)
                            print(f"You give the {item.name} to {npc.name}.")
                        else:
                            print(f"You don't see any {recipient} here.")
                    else:
                        print(f"You don't have any {target}.")
                else:
                    print("Give what to whom?")
                return
            elif action == "quests":
                # Show active quests
                quests = list(getattr(self.player, "quests", []) or [])
                if quests:
                    print("\n=== Active Quests ===")
                    for quest in quests:
                        status = "Complete" if quest.completed else "Active"
                        print(f"[{status}] {quest.name}")
                        print(f"  {quest.description}")
                else:
                    print("You have no active quests.")
                return
            elif action == "dismiss":
                target = parsed.get("target", "")
                if target:
                    if hasattr(self.player, "party"):
                        companion = None
                        for c in self.player.party:
                            if target.lower() in c.name.lower():
                                companion = c
                                break

                        if companion:
                            self.player.party.remove(companion)
                            print(f"{companion.name} has left your party.")
                        else:
                            print(f"{target} is not in your party.")
                    else:
                        print("You don't have any companions.")
                else:
                    print("Dismiss whom?")
                return
            elif action == "examine":
                target = parsed.get("target", "")
                if target:
                    # Check if examining an NPC
                    room = self.get_current_room()
                    if not room:
                        print("You are nowhere. There's nothing to examine.")
                        return
                    monsters = self.get_monsters_in_room(room.id)
                    is_npc = any(target.lower() in m.name.lower() for m in monsters)
                    if is_npc:
                        self.examine_npc(target)
                    else:
                        # Examine environmental object or item
                        self.examine_object(target)
                else:
                    print("Examine what?")
                return
            elif action == "search":
                self.search_area()
                return
            elif action == "talk":
                target = parsed.get("target", "")
                topic = parsed.get("topic", "")
                if target:
                    self.talk_to_npc(target, topic)
                else:
                    print("Talk to whom?")
                return
            elif action == "question":
                # Handle questions naturally
                q_text = parsed.get("text", "")
                if "where" in q_text.lower():
                    self.look()
                elif "what" in q_text.lower() and "carry" in q_text.lower():
                    self.show_inventory()
                elif "who" in q_text.lower():
                    monsters = self.get_monsters_in_room(self.player.current_room)
                    if monsters:
                        print("You see:")
                        for m in monsters:
                            print(f"  - {m.name}")
                    else:
                        print("No one else is here.")
                else:
                    print("I'm not sure how to answer that.")
                return

        # Fall back to simple parser
        parts = command.lower().strip().split()
        if not parts:
            return

        cmd = parts[0]
        args = " ".join(parts[1:]) if len(parts) > 1 else ""

        # Movement commands
        if cmd in ["n", "north"]:
            self.move("north")
        elif cmd in ["s", "south"]:
            self.move("south")
        elif cmd in ["e", "east"]:
            self.move("east")
        elif cmd in ["w", "west"]:
            self.move("west")
        elif cmd in ["u", "up"]:
            self.move("up")
        elif cmd in ["d", "down"]:
            self.move("down")

        # Action commands
        elif cmd in ["l", "look"]:
            self.look()
        elif cmd in ["i", "inventory"]:
            self.show_inventory()
        elif cmd in ["status", "stats"]:
            self.show_status()
        elif cmd in ["party"]:
            self.show_party()
        elif cmd in ["recruit", "invite"]:
            if args:
                self.recruit_companion(args)
            else:
                print("Recruit who?")
        elif cmd in ["get", "take"]:
            if args:
                self.get_item(args)
            else:
                print("Get what?")
        elif cmd in ["drop"]:
            if args:
                self.drop_item(args)
            else:
                print("Drop what?")
        elif cmd in ["attack", "kill", "fight"]:
            if args:
                self.attack(args)
            else:
                print("Attack what?")
        elif cmd in ["quit", "exit", "q"]:
            print("\nThanks for playing!")
            self.game_over = True
        elif cmd in ["help", "h", "?"]:
            self.show_help()
        elif cmd in ["achievements"]:
            if self.achievements:
                print("\n" + self.achievements.get_progress_summary())
            else:
                print("Achievements not available.")
        elif cmd in ["journal", "notes"]:
            if self.journal:
                entries = self.journal.get_recent_entries(10)
                print("\n=== Recent Journal Entries ===")
                for entry in entries:
                    print(f"\n[{entry.timestamp}] {entry.title}")
                    print(f"  {entry.content}")
            else:
                print("Journal not available.")
        elif cmd in ["settings"]:
            if self.accessibility:
                print("\n=== Game Settings ===")
                print(f"Difficulty: {self.accessibility.difficulty.level.value}")
                print(f"Text Size: {self.accessibility.display.text_size.value}")
                print(
                    f"Colors: {'Enabled' if self.accessibility.display.use_colors else 'Disabled'}"
                )
            else:
                print("Settings not available.")
        else:
            unknown_payload = {
                "player": self.player,
                "room": self.get_current_room(),
                "command": command,
                "verb": cmd,
                "args": args,
                "handled": False,
            }
            unknown_payload, _ = self._fire_mod_event(
                EventType.ON_UNKNOWN_COMMAND, unknown_payload
            )
            if unknown_payload.get("handled"):
                return

            message = unknown_payload.get("message")
            if message:
                print(message)
            else:
                print(f"I don't understand '{command}'. Type 'help' for commands.")

    def show_help(self):
        """Display help text"""
        if self.use_enhanced_parser and self.parser:
            print(self.parser.get_help_text())
        else:
            print("\n" + "=" * 60)
            print("ADVENTURE COMMANDS")
            print("=" * 60)
            print("\nMovement:")
            print("  n, north, s, south, e, east, w, west, u, up, d, down")
            print("\nActions:")
            print("  look (l)        - Look around")
            print("  get/take <item> - Pick up an item")
            print("  drop <item>     - Drop an item")
            print("  attack <target> - Attack a monster")
            print("\nParty:")
            print("  party           - View your companions")
            print("  recruit <npc>   - Invite NPC to join party")
            print("\nInfo:")
            print("  inventory (i)   - Show what you're carrying")
            print("  status          - Show your character stats")
            print("  help (h, ?)     - Show this help")
            print("\nOther:")
            print("  quit (q)        - Exit the game")
            print("=" * 60 + "\n")

    def run(self):
        """Main game loop"""
        self.load_adventure()
        self.look()

        while not self.game_over:
            try:
                command = input("\n> ").strip()
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                print("\n\nThanks for playing!")
                break
            except EOFError:
                break


if __name__ == "__main__":
    raise SystemExit(
        "The command-line engine has been retired. Launch the IDE with "
        "`python -m src.sagacraft.ui.ide`."
    )
