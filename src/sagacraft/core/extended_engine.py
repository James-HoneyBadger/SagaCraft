#!/usr/bin/env python3
"""SagaCraft - Extended Game Engine

Extended features for rich interactive fiction experiences.
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

from sagacraft.core.adventure_loader import read_adventure_data


# Import core engine types for compatibility
from sagacraft.core.engine import ItemType, MonsterStatus, Item, Monster, Room, Player


class PuzzleType(Enum):
    """Types of puzzles"""

    LOCKED_DOOR = "locked_door"
    COMBINATION = "combination"
    RIDDLE = "riddle"
    HIDDEN_OBJECT = "hidden_object"
    SEQUENCE = "sequence"
    CUSTOM = "custom"


class QuestStatus(Enum):
    """Quest completion status"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class EquipmentSlot(Enum):
    """Equipment slots for items"""

    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    SHIELD = "shield"
    BOOTS = "boots"
    RING = "ring"
    AMULET = "amulet"


@dataclass
class ExtendedItem(Item):
    """Extended item with additional features"""

    # New fields (all optional for backward compatibility)
    durability: int = 100
    max_durability: int = 100
    magical_bonus: int = 0
    special_abilities: List[str] = field(default_factory=list)
    required_level: int = 0
    can_be_equipped: bool = False
    equipment_slot: Optional[str] = None
    is_container: bool = False
    container_capacity: int = 0
    contains_items: List[int] = field(default_factory=list)
    is_key: bool = False
    unlocks_puzzle: Optional[int] = None
    on_use_effect: Optional[str] = None
    is_quest_item: bool = False
    quest_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create ExtendedItem from dict, handling both old and new format"""
        # Handle original Item fields
        item_type = ItemType(data.get("type", "normal"))

        # Create with all fields, using defaults for missing extended fields
        # pylint: disable=unexpected-keyword-arg
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=item_type,
            weight=data.get("weight", 1),
            value=data.get("value", 0),
            is_weapon=data.get("is_weapon", False),
            weapon_type=data.get("weapon_type", 0),
            weapon_dice=data.get("weapon_dice", 1),
            weapon_sides=data.get("weapon_sides", 6),
            is_armor=data.get("is_armor", False),
            armor_value=data.get("armor_value", 0),
            is_takeable=data.get("is_takeable", True),
            is_wearable=data.get("is_wearable", False),
            location=data.get("location", 0),
            # Extended fields (optional)
            durability=data.get("durability", 100),
            max_durability=data.get("max_durability", 100),
            magical_bonus=data.get("magical_bonus", 0),
            special_abilities=data.get("special_abilities", []),
            required_level=data.get("required_level", 0),
            can_be_equipped=data.get(
                "can_be_equipped",
                data.get("is_weapon", False) or data.get("is_armor", False),
            ),
            equipment_slot=data.get("equipment_slot"),
            is_container=data.get("is_container", False),
            container_capacity=data.get("container_capacity", 0),
            contains_items=data.get("contains_items", []),
            is_key=data.get("is_key", False),
            unlocks_puzzle=data.get("unlocks_puzzle"),
            on_use_effect=data.get("on_use_effect"),
            is_quest_item=data.get("is_quest_item", False),
            quest_id=data.get("quest_id"),
        )


@dataclass
class ExtendedMonster(Monster):
    """Extended monster/NPC with additional features"""

    # New fields (all optional)
    dialogue_id: Optional[int] = None
    can_trade: bool = False
    inventory: List[int] = field(default_factory=list)
    gives_quests: List[int] = field(default_factory=list)
    reaction_level: int = 0  # -100 to +100, affects behavior
    special_abilities: List[str] = field(default_factory=list)
    ai_behavior: str = "hostile"  # hostile, defensive, fleeing, stationary, patrol
    respawns: bool = False
    respawn_time: int = 0
    drops_items_on_death: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        """Create ExtendedMonster from dict"""
        friendliness = MonsterStatus(data.get("friendliness", "neutral"))

        # pylint: disable=unexpected-keyword-arg
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            room_id=data["room_id"],
            hardiness=data.get("hardiness", 10),
            agility=data.get("agility", 10),
            friendliness=friendliness,
            courage=data.get("courage", 100),
            weapon_id=data.get("weapon_id"),
            armor_worn=data.get("armor_worn", 0),
            gold=data.get("gold", 0),
            # Extended fields
            dialogue_id=data.get("dialogue_id"),
            can_trade=data.get("can_trade", False),
            inventory=data.get("inventory", []),
            gives_quests=data.get("gives_quests", []),
            reaction_level=data.get("reaction_level", 0),
            special_abilities=data.get("special_abilities", []),
            ai_behavior=data.get(
                "ai_behavior",
                "hostile" if friendliness == MonsterStatus.HOSTILE else "stationary",
            ),
            respawns=data.get("respawns", False),
            respawn_time=data.get("respawn_time", 0),
            drops_items_on_death=data.get("drops_items_on_death", []),
        )


@dataclass
class ExtendedRoom(Room):
    """Extended room with environmental features"""

    # New fields (all optional)
    alternate_description: Optional[str] = None
    condition_for_alternate: Optional[str] = None
    light_level: str = "normal"  # bright, normal, dim, dark
    requires_light_source: bool = False
    has_trap: bool = False
    trap_damage: int = 0
    trap_disarmed: bool = False
    is_safe_zone: bool = False
    environmental_effects: List[str] = field(default_factory=list)
    hidden_items: List[int] = field(default_factory=list)
    items_revealed: bool = False
    ambient_sound: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create ExtendedRoom from dict"""
        # pylint: disable=unexpected-keyword-arg
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            exits=data.get("exits", {}),
            is_dark=data.get("is_dark", False),
            # Extended fields
            alternate_description=data.get("alternate_description"),
            condition_for_alternate=data.get("condition_for_alternate"),
            light_level=data.get(
                "light_level", "dark" if data.get("is_dark", False) else "normal"
            ),
            requires_light_source=data.get(
                "requires_light_source", data.get("is_dark", False)
            ),
            has_trap=data.get("has_trap", False),
            trap_damage=data.get("trap_damage", 0),
            trap_disarmed=data.get("trap_disarmed", False),
            is_safe_zone=data.get("is_safe_zone", False),
            environmental_effects=data.get("environmental_effects", []),
            hidden_items=data.get("hidden_items", []),
            items_revealed=data.get("items_revealed", False),
            ambient_sound=data.get("ambient_sound"),
        )


@dataclass
class Puzzle:
    """Represents a puzzle in the game"""

    id: int
    puzzle_type: PuzzleType
    room_id: int
    description: str
    exit_direction: Optional[str] = None  # For locked doors
    required_item: Optional[int] = None  # For key puzzles
    combination: Optional[str] = None  # For combination locks
    riddle_question: Optional[str] = None  # For riddles
    riddle_answer: Optional[str] = None
    success_message: str = "Success!"
    failure_message: str = "That didn't work."
    is_solved: bool = False
    attempts_allowed: int = -1  # -1 = unlimited
    attempts_made: int = 0

    @classmethod
    def from_dict(cls, data: dict):
        """Create Puzzle from dict"""
        return cls(
            id=data["id"],
            puzzle_type=PuzzleType(data.get("type", "custom")),
            room_id=data["room_id"],
            description=data["description"],
            exit_direction=data.get("exit_direction"),
            required_item=data.get("required_item"),
            combination=data.get("combination"),
            riddle_question=data.get("riddle_question"),
            riddle_answer=data.get("riddle_answer"),
            success_message=data.get("success_message", "Success!"),
            failure_message=data.get("failure_message", "That didn't work."),
            is_solved=data.get("is_solved", False),
            attempts_allowed=data.get("attempts_allowed", -1),
            attempts_made=data.get("attempts_made", 0),
        )


@dataclass
class DialogueTopic:
    """A conversation topic"""

    keyword: str
    response: str
    unlocks_quest: Optional[int] = None
    gives_item: Optional[int] = None
    requires_item: Optional[int] = None
    requires_quest_complete: Optional[int] = None
    changes_reaction: int = 0
    one_time_only: bool = False
    has_been_used: bool = False


@dataclass
class Dialogue:
    """NPC dialogue system"""

    npc_id: int
    greeting: str
    topics: List[DialogueTopic]
    farewell: str = "Goodbye."

    @classmethod
    def from_dict(cls, data: dict):
        """Create Dialogue from dict"""
        topics = [
            DialogueTopic(
                keyword=t["keyword"],
                response=t["response"],
                unlocks_quest=t.get("unlocks_quest"),
                gives_item=t.get("gives_item"),
                requires_item=t.get("requires_item"),
                requires_quest_complete=t.get("requires_quest_complete"),
                changes_reaction=t.get("changes_reaction", 0),
                one_time_only=t.get("one_time_only", False),
                has_been_used=t.get("has_been_used", False),
            )
            for t in data.get("topics", [])
        ]

        return cls(
            npc_id=data["npc_id"],
            greeting=data.get("greeting", "Hello, traveler."),
            topics=topics,
            farewell=data.get("farewell", "Goodbye."),
        )


@dataclass
class QuestObjective:
    """A single quest objective"""

    type: str  # collect_item, kill_monster, reach_room, talk_to_npc, etc.
    target_id: Optional[int] = None
    target_name: Optional[str] = None
    quantity: int = 1
    current_progress: int = 0
    description: str = ""

    def is_complete(self) -> bool:
        """Return True when the objective progress meets the requirement."""
        return self.current_progress >= self.quantity


@dataclass
class Quest:
    """Represents a quest"""

    id: int
    title: str
    description: str
    giver_npc: Optional[int]
    objectives: List[QuestObjective]
    rewards_gold: int = 0
    rewards_experience: int = 0
    rewards_items: List[int] = field(default_factory=list)
    status: QuestStatus = QuestStatus.NOT_STARTED

    @classmethod
    def from_dict(cls, data: dict):
        """Create Quest from dict"""
        objectives = [
            QuestObjective(
                type=obj["type"],
                target_id=obj.get("target_id"),
                target_name=obj.get("target_name"),
                quantity=obj.get("quantity", 1),
                current_progress=obj.get("current_progress", 0),
                description=obj.get("description", ""),
            )
            for obj in data.get("objectives", [])
        ]

        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            giver_npc=data.get("giver_npc"),
            objectives=objectives,
            rewards_gold=data.get("rewards_gold", 0),
            rewards_experience=data.get("rewards_experience", 0),
            rewards_items=data.get("rewards_items", []),
            status=QuestStatus(data.get("status", "not_started")),
        )

    def is_complete(self) -> bool:
        """Check if all objectives are complete"""
        return all(obj.is_complete() for obj in self.objectives)


@dataclass
class ExtendedPlayer(Player):
    """Extended player with progression system"""
    max_hardiness: int = 0

    experience: int = 0
    level: int = 1
    experience_to_next_level: int = 100
    equipped_items: Dict[str, Optional[int]] = field(default_factory=dict)
    known_spells: List[str] = field(default_factory=list)
    active_quests: List[int] = field(default_factory=list)
    completed_quests: List[int] = field(default_factory=list)
    discovered_rooms: List[int] = field(default_factory=list)
    flags: Dict[str, bool] = field(default_factory=dict)  # For conditional events

    def __post_init__(self):
        super().__post_init__()
        if self.max_hardiness <= 0:
            self.max_hardiness = self.hardiness

    def add_experience(self, amount: int):
        """Add experience and handle leveling up"""
        self.experience += amount
        while self.experience >= self.experience_to_next_level:
            self.level_up()

    def level_up(self):
        """Level up the player"""
        self.experience -= self.experience_to_next_level
        self.level += 1
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)

        # Increase stats
        self.hardiness += 5
        self.max_hardiness += 5
        self.agility += 2


@dataclass
class _ExtendedWorld:
    rooms: Dict[int, "ExtendedRoom"] = field(default_factory=dict)
    items: Dict[int, "ExtendedItem"] = field(default_factory=dict)
    monsters: Dict[int, "ExtendedMonster"] = field(default_factory=dict)
    puzzles: Dict[int, "Puzzle"] = field(default_factory=dict)
    dialogues: Dict[int, "Dialogue"] = field(default_factory=dict)
    quests: Dict[int, "Quest"] = field(default_factory=dict)


@dataclass
class _ExtendedAdventureMeta:
    title: str = ""
    intro: str = ""


@dataclass
class _ExtendedAdventureRuntime:
    turn_count: int = 0
    game_over: bool = False
    last_loaded_state: Any | None = None


@dataclass
class _ExtendedAdventureFeatures:
    allow_save: bool = True
    has_puzzles: bool = False
    has_quests: bool = False
    has_dialogues: bool = False


class ExtendedAdventureGame:
    """Game engine with extended features"""

    def __init__(self, adventure_file: str):
        self.adventure_file = adventure_file
        self.world = _ExtendedWorld()
        self.player: ExtendedPlayer = ExtendedPlayer()
        self.meta = _ExtendedAdventureMeta()
        self.runtime = _ExtendedAdventureRuntime()
        self.features = _ExtendedAdventureFeatures()

    # Compatibility properties: preserve the old public attribute API while
    # keeping actual state grouped under a few objects.
    # pylint: disable=missing-function-docstring
    @property
    def rooms(self) -> Dict[int, ExtendedRoom]:
        return self.world.rooms

    @rooms.setter
    def rooms(self, value: Dict[int, ExtendedRoom]) -> None:
        self.world.rooms = value

    @property
    def items(self) -> Dict[int, ExtendedItem]:
        return self.world.items

    @items.setter
    def items(self, value: Dict[int, ExtendedItem]) -> None:
        self.world.items = value

    @property
    def monsters(self) -> Dict[int, ExtendedMonster]:
        return self.world.monsters

    @monsters.setter
    def monsters(self, value: Dict[int, ExtendedMonster]) -> None:
        self.world.monsters = value

    @property
    def puzzles(self) -> Dict[int, Puzzle]:
        return self.world.puzzles

    @puzzles.setter
    def puzzles(self, value: Dict[int, Puzzle]) -> None:
        self.world.puzzles = value

    @property
    def dialogues(self) -> Dict[int, Dialogue]:
        return self.world.dialogues

    @dialogues.setter
    def dialogues(self, value: Dict[int, Dialogue]) -> None:
        self.world.dialogues = value

    @property
    def quests(self) -> Dict[int, Quest]:
        return self.world.quests

    @quests.setter
    def quests(self, value: Dict[int, Quest]) -> None:
        self.world.quests = value

    @property
    def adventure_title(self) -> str:
        return self.meta.title

    @adventure_title.setter
    def adventure_title(self, value: str) -> None:
        self.meta.title = value

    @property
    def adventure_intro(self) -> str:
        return self.meta.intro

    @adventure_intro.setter
    def adventure_intro(self, value: str) -> None:
        self.meta.intro = value

    @property
    def turn_count(self) -> int:
        return self.runtime.turn_count

    @turn_count.setter
    def turn_count(self, value: int) -> None:
        self.runtime.turn_count = value

    @property
    def game_over(self) -> bool:
        return self.runtime.game_over

    @game_over.setter
    def game_over(self, value: bool) -> None:
        self.runtime.game_over = value

    @property
    def _last_loaded_state(self) -> Any | None:
        return self.runtime.last_loaded_state

    @_last_loaded_state.setter
    def _last_loaded_state(self, value: Any | None) -> None:
        self.runtime.last_loaded_state = value

    @property
    def allow_save(self) -> bool:
        return self.features.allow_save

    @allow_save.setter
    def allow_save(self, value: bool) -> None:
        self.features.allow_save = value

    @property
    def has_puzzles(self) -> bool:
        return self.features.has_puzzles

    @has_puzzles.setter
    def has_puzzles(self, value: bool) -> None:
        self.features.has_puzzles = value

    @property
    def has_quests(self) -> bool:
        return self.features.has_quests

    @has_quests.setter
    def has_quests(self, value: bool) -> None:
        self.features.has_quests = value

    @property
    def has_dialogues(self) -> bool:
        return self.features.has_dialogues

    @has_dialogues.setter
    def has_dialogues(self, value: bool) -> None:
        self.features.has_dialogues = value

    # pylint: enable=missing-function-docstring

    def load_adventure(self):
        """Load adventure with additional features"""
        try:
            data = read_adventure_data(self.adventure_file)

            self.meta.title = data.get("title", "Untitled Adventure")
            self.meta.intro = data.get("intro", "")

            # Load extended settings if present
            settings = data.get("settings", {})
            self.features.allow_save = settings.get("allow_save", True)

            # Load rooms (extended or original)
            for room_data in data.get("rooms", []):
                room = ExtendedRoom.from_dict(room_data)
                self.world.rooms[room.id] = room

            # Load items (extended or original)
            for item_data in data.get("items", []):
                item = ExtendedItem.from_dict(item_data)
                self.world.items[item.id] = item

            # Load monsters (extended or original)
            for mon_data in data.get("monsters", []):
                monster = ExtendedMonster.from_dict(mon_data)
                self.world.monsters[monster.id] = monster

            # Load puzzles if present
            if "puzzles" in data:
                self.features.has_puzzles = True
                for puzzle_data in data["puzzles"]:
                    puzzle = Puzzle.from_dict(puzzle_data)
                    self.world.puzzles[puzzle.id] = puzzle

            # Load dialogues if present
            if "dialogues" in data:
                self.features.has_dialogues = True
                for dialogue_data in data["dialogues"]:
                    dialogue = Dialogue.from_dict(dialogue_data)
                    self.world.dialogues[dialogue.npc_id] = dialogue

            # Load quests if present
            if "quests" in data:
                self.features.has_quests = True
                for quest_data in data["quests"]:
                    quest = Quest.from_dict(quest_data)
                    self.world.quests[quest.id] = quest

            # Set player starting position
            self.player.current_room = data.get("start_room", 1)

            return True

        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"Error loading adventure: {exc}")
            return False

    def save_game(self, slot: int = 1) -> bool:
        """Save current game state"""
        if not self.allow_save:
            print("Saving is not allowed in this adventure.")
            return False

        save_data = {
            "adventure_file": self.adventure_file,
            "player": asdict(self.player),
            "items": {id: asdict(item) for id, item in self.items.items()},
            "monsters": {id: asdict(monster) for id, monster in self.monsters.items()},
            "puzzles": {id: asdict(puzzle) for id, puzzle in self.puzzles.items()},
            "quests": {id: asdict(quest) for id, quest in self.quests.items()},
            "rooms": {id: asdict(room) for id, room in self.rooms.items()},
            "turn_count": self.turn_count,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            save_file = f"saves/save_slot_{slot}.json"
            with open(save_file, "w", encoding="utf-8") as handle:
                json.dump(save_data, handle, indent=2)
            print(f"\n✓ Game saved to slot {slot}")
            return True
        except (OSError, TypeError, ValueError) as exc:
            print(f"\n✗ Error saving game: {exc}")
            return False

    def load_game(self, slot: int = 1) -> bool:
        """Load saved game state"""
        try:
            save_file = f"saves/save_slot_{slot}.json"
            with open(save_file, "r", encoding="utf-8") as handle:
                save_data = json.load(handle)

                # Restore game state
                # (Implementation would restore all objects)
                self.runtime.last_loaded_state = save_data
            print(f"\n✓ Game loaded from slot {slot}")
            return True
        except FileNotFoundError:
            print(f"\n✗ No save file found in slot {slot}")
            return False
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"\n✗ Error loading game: {exc}")
            return False

    # Additional extended methods would go here
    # These would extend the original game engine methods
    # while maintaining backward compatibility


# Export extended classes for use in other modules
__all__ = [
    "ExtendedAdventureGame",
    "ExtendedItem",
    "ExtendedMonster",
    "ExtendedRoom",
    "ExtendedPlayer",
    "Puzzle",
    "Dialogue",
    "Quest",
    "PuzzleType",
    "QuestStatus",
    "EquipmentSlot",
]
