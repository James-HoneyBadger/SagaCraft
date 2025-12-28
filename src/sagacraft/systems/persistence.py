"""
Phase VI: Persistent World & Consequences System

Implements world persistence, NPC memory, and consequence cascading:
- Game world state persistence
- NPC memory and dialogue history
- Permanent world changes
- Relationship persistence
- Consequence cascades
- Multiple endings support
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Tuple, Any
import json
from datetime import datetime


class ConsequenceType(Enum):
    """Types of world consequences."""
    NPC_DEATH = "npc_death"
    NPC_GONE = "npc_gone"
    LOCATION_DESTROYED = "location_destroyed"
    LOCATION_SEALED = "location_sealed"
    ITEM_REMOVED = "item_removed"
    ITEM_AVAILABLE = "item_available"
    QUEST_BLOCKED = "quest_blocked"
    QUEST_ENABLED = "quest_enabled"
    RELATIONSHIP_CHANGED = "relationship_changed"
    FACTION_ATTITUDE = "faction_attitude"
    WORLD_FLAG = "world_flag"
    DIALOGUE_LOCKED = "dialogue_locked"
    DIALOGUE_UNLOCKED = "dialogue_unlocked"
    ENDING_ALTERED = "ending_altered"


@dataclass
class Consequence:
    """A persistent consequence that affects the world."""
    consequence_type: ConsequenceType
    target: str  # NPC name, location, item, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reason: str = ""  # Why this consequence occurred
    
    def apply(self, world_state: 'WorldState') -> None:
        """Apply this consequence to the world state."""
        if self.consequence_type == ConsequenceType.NPC_DEATH:
            world_state.mark_npc_dead(self.target, self.reason)
        
        elif self.consequence_type == ConsequenceType.NPC_GONE:
            world_state.mark_npc_gone(self.target, self.reason)
        
        elif self.consequence_type == ConsequenceType.LOCATION_DESTROYED:
            world_state.destroy_location(self.target)
        
        elif self.consequence_type == ConsequenceType.LOCATION_SEALED:
            world_state.seal_location(self.target)
        
        elif self.consequence_type == ConsequenceType.ITEM_REMOVED:
            world_state.remove_item(self.target)
        
        elif self.consequence_type == ConsequenceType.ITEM_AVAILABLE:
            location = self.parameters.get("location", "")
            world_state.make_item_available(self.target, location)
        
        elif self.consequence_type == ConsequenceType.QUEST_BLOCKED:
            world_state.block_quest(self.target)
        
        elif self.consequence_type == ConsequenceType.QUEST_ENABLED:
            world_state.enable_quest(self.target)
        
        elif self.consequence_type == ConsequenceType.RELATIONSHIP_CHANGED:
            npc = self.target
            change = self.parameters.get("change", 0)
            world_state.modify_npc_relationship(npc, change)
        
        elif self.consequence_type == ConsequenceType.FACTION_ATTITUDE:
            faction = self.target
            attitude = self.parameters.get("attitude", 0)
            world_state.set_faction_attitude(faction, attitude)
        
        elif self.consequence_type == ConsequenceType.WORLD_FLAG:
            flag_name = self.target
            value = self.parameters.get("value", True)
            world_state.set_world_flag(flag_name, value)
        
        elif self.consequence_type == ConsequenceType.DIALOGUE_LOCKED:
            npc = self.parameters.get("npc", "")
            dialogue_id = self.target
            world_state.lock_dialogue(npc, dialogue_id)
        
        elif self.consequence_type == ConsequenceType.DIALOGUE_UNLOCKED:
            npc = self.parameters.get("npc", "")
            dialogue_id = self.target
            world_state.unlock_dialogue(npc, dialogue_id)
        
        elif self.consequence_type == ConsequenceType.ENDING_ALTERED:
            world_state.alter_ending(self.target)
        
        world_state.consequence_history.append(self)


@dataclass
class NPCMemory:
    """NPC memory of interactions and world events."""
    npc_name: str
    dialogue_history: List[str] = field(default_factory=list)
    encountered: bool = False
    last_encounter: Optional[str] = None
    relationship_level: int = 0  # -100 to 100
    quest_offers: Set[str] = field(default_factory=set)
    accepted_quests: Set[str] = field(default_factory=set)
    completed_quests: Set[str] = field(default_factory=set)
    gifts_received: List[str] = field(default_factory=list)
    favors_owed: int = 0
    is_dead: bool = False
    is_gone: bool = False
    notes: List[str] = field(default_factory=list)
    
    def record_dialogue(self, dialogue_id: str) -> None:
        """Record that dialogue was used with this NPC."""
        self.dialogue_history.append(dialogue_id)
        self.last_encounter = datetime.now().isoformat()
        if not self.encountered:
            self.encountered = True
    
    def add_note(self, note: str) -> None:
        """Add a note about this NPC."""
        self.notes.append(f"{datetime.now().isoformat()}: {note}")
    
    def has_dialogue_history(self, dialogue_id: str) -> bool:
        """Check if NPC has used this dialogue before."""
        return dialogue_id in self.dialogue_history
    
    def modify_relationship(self, change: int) -> None:
        """Modify NPC relationship (-100 to 100 clamped)."""
        self.relationship_level = max(-100, min(100, self.relationship_level + change))
    
    def get_relationship_tier(self) -> str:
        """Get relationship tier name."""
        if self.is_dead:
            return "dead"
        elif self.is_gone:
            return "gone"
        elif self.relationship_level <= -75:
            return "hated"
        elif self.relationship_level <= -25:
            return "disliked"
        elif self.relationship_level < 25:
            return "neutral"
        elif self.relationship_level < 75:
            return "liked"
        else:
            return "loved"


@dataclass
class Location:
    """A persistent location in the world."""
    name: str
    description: str
    is_destroyed: bool = False
    is_sealed: bool = False
    seal_reason: str = ""
    npcs_present: Set[str] = field(default_factory=set)
    items_available: Set[str] = field(default_factory=set)
    visited: bool = False
    visit_count: int = 0
    notes: List[str] = field(default_factory=list)
    
    def visit(self) -> None:
        """Record a visit to this location."""
        self.visited = True
        self.visit_count += 1
    
    def add_npc(self, npc_name: str) -> None:
        """Add an NPC to this location."""
        self.npcs_present.add(npc_name)
    
    def remove_npc(self, npc_name: str) -> None:
        """Remove an NPC from this location."""
        self.npcs_present.discard(npc_name)
    
    def has_npc(self, npc_name: str) -> bool:
        """Check if NPC is present."""
        return npc_name in self.npcs_present
    
    def add_item(self, item_name: str) -> None:
        """Add an item to this location."""
        self.items_available.add(item_name)
    
    def remove_item(self, item_name: str) -> None:
        """Remove an item from this location."""
        self.items_available.discard(item_name)
    
    def has_item(self, item_name: str) -> bool:
        """Check if item is available."""
        return item_name in self.items_available
    
    def add_note(self, note: str) -> None:
        """Add a note about this location."""
        self.notes.append(f"{datetime.now().isoformat()}: {note}")


class FactionSystem:
    """Tracks faction relationships and attitudes."""
    
    FACTIONS = [
        "guild",
        "nobles",
        "rebels",
        "merchants",
        "clergy",
        "guards",
        "bandits",
        "druids",
    ]
    
    def __init__(self):
        """Initialize faction attitudes (0 = neutral)."""
        self.attitudes: Dict[str, int] = {faction: 0 for faction in self.FACTIONS}
    
    def set_attitude(self, faction: str, attitude: int) -> None:
        """Set faction attitude (-100 to 100)."""
        if faction in self.attitudes:
            self.attitudes[faction] = max(-100, min(100, attitude))
    
    def modify_attitude(self, faction: str, change: int) -> None:
        """Modify faction attitude."""
        if faction in self.attitudes:
            self.set_attitude(faction, self.attitudes[faction] + change)
    
    def get_attitude(self, faction: str) -> int:
        """Get faction attitude."""
        return self.attitudes.get(faction, 0)
    
    def is_hostile(self, faction: str) -> bool:
        """Check if faction is hostile."""
        return self.get_attitude(faction) < -50
    
    def is_friendly(self, faction: str) -> bool:
        """Check if faction is friendly."""
        return self.get_attitude(faction) > 50
    
    def get_all_attitudes(self) -> Dict[str, int]:
        """Get all faction attitudes."""
        return self.attitudes.copy()


class WorldState:
    """Complete persistent world state."""
    
    def __init__(self, world_name: str):
        """Initialize world state."""
        self.world_name = world_name
        self.created_at = datetime.now().isoformat()
        self.last_saved = self.created_at
        self.playtime_seconds = 0
        self.play_count = 0
        
        # Core state
        self.npc_memories: Dict[str, NPCMemory] = {}
        self.locations: Dict[str, Location] = {}
        self.faction_system = FactionSystem()
        
        # Quest state
        self.active_quests: Set[str] = set()
        self.completed_quests: Set[str] = set()
        self.blocked_quests: Set[str] = set()
        self.quest_progress: Dict[str, int] = {}
        
        # World flags
        self.world_flags: Dict[str, bool] = {}
        self.global_variables: Dict[str, Any] = {}
        
        # Items and inventory
        self.available_items: Dict[str, str] = {}  # item -> location
        self.item_disappearances: Set[str] = set()
        
        # Dialogue state
        self.locked_dialogues: Dict[str, Set[str]] = {}  # npc -> dialogue_ids
        self.unlocked_dialogues: Dict[str, Set[str]] = {}  # npc -> dialogue_ids
        
        # Consequences and history
        self.consequence_history: List[Consequence] = []
        self.ending_flags: Set[str] = set()
        self.current_ending: Optional[str] = None
    
    def create_npc_memory(self, npc_name: str) -> NPCMemory:
        """Create or get NPC memory."""
        if npc_name not in self.npc_memories:
            self.npc_memories[npc_name] = NPCMemory(npc_name)
        return self.npc_memories[npc_name]
    
    def get_npc_memory(self, npc_name: str) -> Optional[NPCMemory]:
        """Get NPC memory if exists."""
        return self.npc_memories.get(npc_name)
    
    def record_npc_dialogue(self, npc_name: str, dialogue_id: str) -> None:
        """Record dialogue interaction with NPC."""
        memory = self.create_npc_memory(npc_name)
        memory.record_dialogue(dialogue_id)
    
    def modify_npc_relationship(self, npc_name: str, change: int) -> None:
        """Modify NPC relationship."""
        memory = self.create_npc_memory(npc_name)
        memory.modify_relationship(change)
    
    def get_npc_relationship(self, npc_name: str) -> int:
        """Get NPC relationship level."""
        memory = self.get_npc_memory(npc_name)
        if memory:
            return memory.relationship_level
        return 0
    
    def mark_npc_dead(self, npc_name: str, reason: str = "") -> None:
        """Mark NPC as dead."""
        memory = self.create_npc_memory(npc_name)
        memory.is_dead = True
        memory.is_gone = False
        if reason:
            memory.add_note(f"Marked as dead: {reason}")
    
    def mark_npc_gone(self, npc_name: str, reason: str = "") -> None:
        """Mark NPC as gone (left world)."""
        memory = self.create_npc_memory(npc_name)
        memory.is_gone = True
        if reason:
            memory.add_note(f"Gone from world: {reason}")
    
    def is_npc_alive(self, npc_name: str) -> bool:
        """Check if NPC is alive and present."""
        memory = self.get_npc_memory(npc_name)
        if not memory:
            return True  # Unknown NPCs are assumed alive
        return not memory.is_dead and not memory.is_gone
    
    def create_location(self, location_name: str, description: str) -> Location:
        """Create or get location."""
        if location_name not in self.locations:
            self.locations[location_name] = Location(location_name, description)
        return self.locations[location_name]
    
    def get_location(self, location_name: str) -> Optional[Location]:
        """Get location if exists."""
        return self.locations.get(location_name)
    
    def destroy_location(self, location_name: str) -> None:
        """Destroy a location."""
        location = self.create_location(location_name, "Destroyed ruins")
        location.is_destroyed = True
        location.add_note("Location destroyed")
    
    def seal_location(self, location_name: str, reason: str = "") -> None:
        """Seal a location."""
        location = self.create_location(location_name, "Sealed location")
        location.is_sealed = True
        location.seal_reason = reason
    
    def is_location_accessible(self, location_name: str) -> bool:
        """Check if location is accessible."""
        location = self.get_location(location_name)
        if not location:
            return True
        return not location.is_destroyed and not location.is_sealed
    
    def make_item_available(self, item_name: str, location_name: str) -> None:
        """Make item available in location."""
        self.available_items[item_name] = location_name
        self.item_disappearances.discard(item_name)
    
    def remove_item(self, item_name: str) -> None:
        """Remove item from world."""
        self.available_items.pop(item_name, None)
        self.item_disappearances.add(item_name)
    
    def is_item_available(self, item_name: str) -> bool:
        """Check if item is available."""
        return item_name in self.available_items
    
    def get_item_location(self, item_name: str) -> Optional[str]:
        """Get location of item."""
        return self.available_items.get(item_name)
    
    def block_quest(self, quest_id: str) -> None:
        """Block a quest from being taken."""
        self.blocked_quests.add(quest_id)
        self.active_quests.discard(quest_id)
    
    def enable_quest(self, quest_id: str) -> None:
        """Enable a quest."""
        self.blocked_quests.discard(quest_id)
    
    def is_quest_blocked(self, quest_id: str) -> bool:
        """Check if quest is blocked."""
        return quest_id in self.blocked_quests
    
    def activate_quest(self, quest_id: str) -> None:
        """Activate a quest."""
        if not self.is_quest_blocked(quest_id):
            self.active_quests.add(quest_id)
    
    def complete_quest(self, quest_id: str) -> None:
        """Complete a quest."""
        self.active_quests.discard(quest_id)
        self.completed_quests.add(quest_id)
    
    def set_world_flag(self, flag_name: str, value: bool) -> None:
        """Set a world flag."""
        self.world_flags[flag_name] = value
    
    def get_world_flag(self, flag_name: str) -> bool:
        """Get a world flag."""
        return self.world_flags.get(flag_name, False)
    
    def set_faction_attitude(self, faction: str, attitude: int) -> None:
        """Set faction attitude."""
        self.faction_system.set_attitude(faction, attitude)
    
    def get_faction_attitude(self, faction: str) -> int:
        """Get faction attitude."""
        return self.faction_system.get_attitude(faction)
    
    def lock_dialogue(self, npc_name: str, dialogue_id: str) -> None:
        """Lock dialogue option."""
        if npc_name not in self.locked_dialogues:
            self.locked_dialogues[npc_name] = set()
        self.locked_dialogues[npc_name].add(dialogue_id)
    
    def unlock_dialogue(self, npc_name: str, dialogue_id: str) -> None:
        """Unlock dialogue option."""
        if npc_name in self.locked_dialogues:
            self.locked_dialogues[npc_name].discard(dialogue_id)
    
    def is_dialogue_locked(self, npc_name: str, dialogue_id: str) -> bool:
        """Check if dialogue is locked."""
        if npc_name in self.locked_dialogues:
            return dialogue_id in self.locked_dialogues[npc_name]
        return False
    
    def alter_ending(self, ending_flag: str) -> None:
        """Add a flag that alters the ending."""
        self.ending_flags.add(ending_flag)
    
    def get_possible_endings(self) -> List[str]:
        """Get possible endings based on current state."""
        endings = []
        
        if len(self.completed_quests) >= 10:
            endings.append("hero")
        
        if self.get_faction_attitude("nobles") > 50:
            endings.append("noble_favor")
        
        if self.get_faction_attitude("rebels") > 50:
            endings.append("rebellion_victory")
        
        if self.get_npc_relationship("merchant") > 80:
            endings.append("merchant_alliance")
        
        if "betrayal" in self.ending_flags:
            endings.append("dark_ending")
        
        if "sacrifice" in self.ending_flags:
            endings.append("heroic_sacrifice")
        
        if not endings:
            endings.append("neutral")
        
        return endings
    
    def choose_ending(self, ending: str) -> None:
        """Choose the ending (locks it in)."""
        self.current_ending = ending
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize world state to dictionary."""
        return {
            "world_name": self.world_name,
            "created_at": self.created_at,
            "last_saved": datetime.now().isoformat(),
            "playtime_seconds": self.playtime_seconds,
            "play_count": self.play_count,
            "npc_count": len(self.npc_memories),
            "location_count": len(self.locations),
            "active_quests": len(self.active_quests),
            "completed_quests": len(self.completed_quests),
            "blocked_quests": len(self.blocked_quests),
            "consequence_count": len(self.consequence_history),
            "current_ending": self.current_ending,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ConsequenceCascade:
    """System for cascading consequences through the world."""
    
    def __init__(self, world_state: WorldState):
        """Initialize cascade system."""
        self.world_state = world_state
    
    def apply_npc_death(self, npc_name: str, reason: str = "") -> List[Consequence]:
        """Apply NPC death and cascade consequences."""
        consequences = []
        
        # Mark NPC as dead
        main = Consequence(
            ConsequenceType.NPC_DEATH,
            npc_name,
            reason=reason
        )
        main.apply(self.world_state)
        consequences.append(main)
        
        # Cascade: related dialogue becomes unavailable
        dialogue_lock = Consequence(
            ConsequenceType.DIALOGUE_LOCKED,
            "all_dialogue",
            {"npc": npc_name},
            reason=f"{npc_name} is no longer alive to talk"
        )
        dialogue_lock.apply(self.world_state)
        consequences.append(dialogue_lock)
        
        # Cascade: related quests block
        for quest_id in self.world_state.active_quests.copy():
            block = Consequence(
                ConsequenceType.QUEST_BLOCKED,
                quest_id,
                reason=f"Related NPC {npc_name} is dead"
            )
            block.apply(self.world_state)
            consequences.append(block)
        
        return consequences
    
    def apply_location_destruction(self, location_name: str, reason: str = "") -> List[Consequence]:
        """Destroy location and cascade consequences."""
        consequences = []
        
        # Destroy location
        main = Consequence(
            ConsequenceType.LOCATION_DESTROYED,
            location_name,
            reason=reason
        )
        main.apply(self.world_state)
        consequences.append(main)
        
        # Cascade: items in location become unavailable
        items_to_remove = [
            item_name for item_name, item_location in self.world_state.available_items.items()
            if item_location == location_name
        ]
        for item_name in items_to_remove:
            item_removal = Consequence(
                ConsequenceType.ITEM_REMOVED,
                item_name,
                reason=f"Location {location_name} was destroyed"
            )
            item_removal.apply(self.world_state)
            consequences.append(item_removal)
        
        # Cascade: NPCs in location must leave or die
        location = self.world_state.get_location(location_name)
        if location:
            for npc_name in location.npcs_present.copy():
                npc_gone = Consequence(
                    ConsequenceType.NPC_GONE,
                    npc_name,
                    reason=f"Location {location_name} was destroyed"
                )
                npc_gone.apply(self.world_state)
                consequences.append(npc_gone)
        
        return consequences
    
    def apply_faction_war(self, faction1: str, faction2: str) -> List[Consequence]:
        """Create faction conflict."""
        consequences = []
        
        # Set hostile attitudes
        att1 = Consequence(
            ConsequenceType.FACTION_ATTITUDE,
            faction1,
            {"attitude": -100},
            reason=f"War declared against {faction2}"
        )
        att1.apply(self.world_state)
        consequences.append(att1)
        
        att2 = Consequence(
            ConsequenceType.FACTION_ATTITUDE,
            faction2,
            {"attitude": -100},
            reason=f"War declared against {faction1}"
        )
        att2.apply(self.world_state)
        consequences.append(att2)
        
        return consequences
