"""
Phase IV: Dialogue Tree System

Implements a branching dialogue tree system with conditional paths, 
dialogue consequences, and NPC memory tracking. Features:

- Node-based dialogue structure
- Conditional dialogue branches
- Player dialogue history
- Consequence system
- Character relationship tracking
- Dialogue flags and state management
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Set
from abc import ABC, abstractmethod


class DialogueConditionType(Enum):
    """Types of conditions that can gate dialogue options."""
    NONE = "none"
    LEVEL_MINIMUM = "level_min"
    LEVEL_MAXIMUM = "level_max"
    ATTRIBUTE = "attribute"
    SKILL_REQUIRED = "skill_required"
    ITEM_REQUIRED = "item_required"
    FLAG = "flag"
    RELATIONSHIP = "relationship"
    PREVIOUSLY_CHOSEN = "previously_chosen"
    STAT_BASED = "stat_based"


class DialogueEventType(Enum):
    """Events that can be triggered by dialogue."""
    NONE = "none"
    QUEST_START = "quest_start"
    QUEST_PROGRESS = "quest_progress"
    QUEST_COMPLETE = "quest_complete"
    RELATIONSHIP_CHANGE = "relationship_change"
    ITEM_GAIN = "item_gain"
    ITEM_LOSS = "item_loss"
    EXPERIENCE_GAIN = "experience_gain"
    FLAG_SET = "flag_set"
    FLAG_UNSET = "flag_unset"
    COMBAT_TRIGGER = "combat_trigger"
    TELEPORT = "teleport"


@dataclass
class DialogueCondition:
    """A condition that must be met for dialogue to appear or be valid."""
    condition_type: DialogueConditionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def is_met(self, player_state: Dict[str, Any], dialogue_state: 'DialogueState') -> bool:
        """Check if this condition is met given the current state."""
        if self.condition_type == DialogueConditionType.NONE:
            return True
        
        elif self.condition_type == DialogueConditionType.LEVEL_MINIMUM:
            min_level = self.parameters.get("level", 1)
            return player_state.get("level", 1) >= min_level
        
        elif self.condition_type == DialogueConditionType.LEVEL_MAXIMUM:
            max_level = self.parameters.get("level", 999)
            return player_state.get("level", 1) <= max_level
        
        elif self.condition_type == DialogueConditionType.ATTRIBUTE:
            attr_name = self.parameters.get("attribute", "")
            attr_value = self.parameters.get("value", 0)
            operator = self.parameters.get("operator", ">=")
            
            player_attr = player_state.get("attributes", {}).get(attr_name, 0)
            if operator == ">=":
                return player_attr >= attr_value
            elif operator == "<=":
                return player_attr <= attr_value
            elif operator == "==":
                return player_attr == attr_value
            elif operator == ">":
                return player_attr > attr_value
            elif operator == "<":
                return player_attr < attr_value
            return False
        
        elif self.condition_type == DialogueConditionType.SKILL_REQUIRED:
            skill_name = self.parameters.get("skill", "")
            return skill_name in player_state.get("skills", set())
        
        elif self.condition_type == DialogueConditionType.ITEM_REQUIRED:
            item_name = self.parameters.get("item", "")
            return item_name in player_state.get("inventory", set())
        
        elif self.condition_type == DialogueConditionType.FLAG:
            flag_name = self.parameters.get("flag", "")
            flag_value = self.parameters.get("value", True)
            return dialogue_state.get_flag(flag_name) == flag_value
        
        elif self.condition_type == DialogueConditionType.RELATIONSHIP:
            npc_name = self.parameters.get("npc", "")
            min_level = self.parameters.get("level", 0)
            return dialogue_state.get_relationship(npc_name) >= min_level
        
        elif self.condition_type == DialogueConditionType.PREVIOUSLY_CHOSEN:
            dialogue_id = self.parameters.get("dialogue_id", "")
            return dialogue_id in dialogue_state.chosen_dialogues
        
        elif self.condition_type == DialogueConditionType.STAT_BASED:
            stat_name = self.parameters.get("stat", "")
            min_value = self.parameters.get("min_value", 0)
            return player_state.get("stats", {}).get(stat_name, 0) >= min_value
        
        return True


@dataclass
class DialogueConsequence:
    """A consequence that occurs when a dialogue option is chosen."""
    consequence_type: DialogueEventType
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def apply(self, player_state: Dict[str, Any], dialogue_state: 'DialogueState') -> None:
        """Apply this consequence to the game state."""
        if self.consequence_type == DialogueEventType.NONE:
            return
        
        elif self.consequence_type == DialogueEventType.QUEST_START:
            quest_id = self.parameters.get("quest_id", "")
            dialogue_state.active_quests.add(quest_id)
        
        elif self.consequence_type == DialogueEventType.QUEST_COMPLETE:
            quest_id = self.parameters.get("quest_id", "")
            dialogue_state.completed_quests.add(quest_id)
            if quest_id in dialogue_state.active_quests:
                dialogue_state.active_quests.remove(quest_id)
        
        elif self.consequence_type == DialogueEventType.RELATIONSHIP_CHANGE:
            npc_name = self.parameters.get("npc", "")
            change = self.parameters.get("change", 0)
            dialogue_state.modify_relationship(npc_name, change)
        
        elif self.consequence_type == DialogueEventType.FLAG_SET:
            flag_name = self.parameters.get("flag", "")
            dialogue_state.set_flag(flag_name, True)
        
        elif self.consequence_type == DialogueEventType.FLAG_UNSET:
            flag_name = self.parameters.get("flag", "")
            dialogue_state.set_flag(flag_name, False)
        
        elif self.consequence_type == DialogueEventType.EXPERIENCE_GAIN:
            xp_amount = self.parameters.get("amount", 0)
            player_state["experience"] = player_state.get("experience", 0) + xp_amount
        
        elif self.consequence_type == DialogueEventType.ITEM_GAIN:
            item_name = self.parameters.get("item", "")
            player_state.setdefault("inventory", set()).add(item_name)
        
        elif self.consequence_type == DialogueEventType.ITEM_LOSS:
            item_name = self.parameters.get("item", "")
            if "inventory" in player_state and item_name in player_state["inventory"]:
                player_state["inventory"].remove(item_name)


@dataclass
class DialogueOption:
    """A dialogue choice presented to the player."""
    option_id: str
    text: str
    next_node_id: Optional[str] = None
    conditions: List[DialogueCondition] = field(default_factory=list)
    consequences: List[DialogueConsequence] = field(default_factory=list)
    
    def is_available(self, player_state: Dict[str, Any], dialogue_state: 'DialogueState') -> bool:
        """Check if this option is available given current conditions."""
        return all(cond.is_met(player_state, dialogue_state) for cond in self.conditions)
    
    def apply_consequences(self, player_state: Dict[str, Any], dialogue_state: 'DialogueState') -> None:
        """Apply all consequences for choosing this option."""
        for consequence in self.consequences:
            consequence.apply(player_state, dialogue_state)
        dialogue_state.record_choice(self.option_id)


@dataclass
class DialogueNode:
    """A node in the dialogue tree representing NPC speech."""
    node_id: str
    speaker: str
    text: str
    options: List[DialogueOption] = field(default_factory=list)
    
    def get_available_options(self, player_state: Dict[str, Any], 
                            dialogue_state: 'DialogueState') -> List[DialogueOption]:
        """Get all available dialogue options for this node."""
        return [opt for opt in self.options if opt.is_available(player_state, dialogue_state)]


@dataclass
class DialogueState:
    """Tracks the current state of a dialogue conversation."""
    dialogue_history: List[str] = field(default_factory=list)
    chosen_dialogues: Set[str] = field(default_factory=set)
    active_quests: Set[str] = field(default_factory=set)
    completed_quests: Set[str] = field(default_factory=set)
    flags: Dict[str, bool] = field(default_factory=dict)
    relationships: Dict[str, int] = field(default_factory=dict)
    
    def record_choice(self, option_id: str) -> None:
        """Record that the player chose this dialogue option."""
        self.chosen_dialogues.add(option_id)
        self.dialogue_history.append(option_id)
    
    def record_dialogue(self, node_id: str) -> None:
        """Record that this dialogue node was visited."""
        self.dialogue_history.append(node_id)
    
    def set_flag(self, flag_name: str, value: bool) -> None:
        """Set a dialogue flag."""
        self.flags[flag_name] = value
    
    def get_flag(self, flag_name: str) -> bool:
        """Get the value of a dialogue flag."""
        return self.flags.get(flag_name, False)
    
    def modify_relationship(self, npc_name: str, change: int) -> None:
        """Modify relationship level with an NPC."""
        current = self.relationships.get(npc_name, 0)
        self.relationships[npc_name] = max(0, min(100, current + change))
    
    def get_relationship(self, npc_name: str) -> int:
        """Get relationship level with an NPC (0-100)."""
        return self.relationships.get(npc_name, 0)
    
    def reset_dialogue(self) -> None:
        """Reset dialogue for a new conversation."""
        self.dialogue_history.clear()


class DialogueTree:
    """A complete dialogue tree with nodes and branching logic."""
    
    def __init__(self, tree_id: str, npc_name: str):
        """Initialize a new dialogue tree."""
        self.tree_id = tree_id
        self.npc_name = npc_name
        self.nodes: Dict[str, DialogueNode] = {}
        self.root_node_id: Optional[str] = None
        self.is_repeatable = True
    
    def add_node(self, node: DialogueNode) -> None:
        """Add a dialogue node to the tree."""
        self.nodes[node.node_id] = node
        if self.root_node_id is None:
            self.root_node_id = node.node_id
    
    def get_node(self, node_id: str) -> Optional[DialogueNode]:
        """Get a dialogue node by ID."""
        return self.nodes.get(node_id)
    
    def get_root_node(self) -> Optional[DialogueNode]:
        """Get the root (starting) node of this tree."""
        if self.root_node_id:
            return self.nodes.get(self.root_node_id)
        return None
    
    def get_next_node(self, current_node_id: str, option_id: str) -> Optional[DialogueNode]:
        """Get the next node after choosing an option."""
        current_node = self.get_node(current_node_id)
        if not current_node:
            return None
        
        for option in current_node.options:
            if option.option_id == option_id and option.next_node_id:
                return self.get_node(option.next_node_id)
        
        return None
    
    def validate(self) -> bool:
        """Validate that all node references are valid."""
        if not self.root_node_id or self.root_node_id not in self.nodes:
            return False
        
        visited = set()
        to_visit = [self.root_node_id]
        
        while to_visit:
            node_id = to_visit.pop(0)
            if node_id in visited:
                continue
            
            visited.add(node_id)
            node = self.nodes.get(node_id)
            if not node:
                return False
            
            for option in node.options:
                if option.next_node_id and option.next_node_id not in self.nodes:
                    return False
                if option.next_node_id:
                    to_visit.append(option.next_node_id)
        
        return True


class DialogueManager:
    """Manages all dialogue trees and active conversations."""
    
    def __init__(self):
        """Initialize the dialogue manager."""
        self.dialogue_trees: Dict[str, DialogueTree] = {}
        self.active_conversations: Dict[str, tuple[DialogueTree, DialogueState]] = {}
    
    def register_tree(self, tree: DialogueTree) -> None:
        """Register a dialogue tree."""
        if tree.validate():
            self.dialogue_trees[tree.tree_id] = tree
    
    def get_tree(self, tree_id: str) -> Optional[DialogueTree]:
        """Get a dialogue tree by ID."""
        return self.dialogue_trees.get(tree_id)
    
    def start_conversation(self, tree_id: str, npc_name: str) -> Optional[DialogueNode]:
        """Start a new conversation with an NPC."""
        tree = self.get_tree(tree_id)
        if not tree:
            return None
        
        state = DialogueState()
        self.active_conversations[npc_name] = (tree, state)
        
        return tree.get_root_node()
    
    def get_current_node(self, npc_name: str) -> Optional[DialogueNode]:
        """Get the current dialogue node for an active conversation."""
        if npc_name not in self.active_conversations:
            return None
        
        tree, state = self.active_conversations[npc_name]
        if not state.dialogue_history:
            return tree.get_root_node()
        
        last_node_id = state.dialogue_history[-1]
        if last_node_id in tree.nodes:
            return tree.get_node(last_node_id)
        
        return tree.get_root_node()
    
    def get_available_options(self, npc_name: str, player_state: Dict[str, Any]) -> List[DialogueOption]:
        """Get available dialogue options for the current conversation."""
        if npc_name not in self.active_conversations:
            return []
        
        tree, state = self.active_conversations[npc_name]
        current_node = self.get_current_node(npc_name)
        
        if not current_node:
            return []
        
        return current_node.get_available_options(player_state, state)
    
    def choose_option(self, npc_name: str, option_id: str, player_state: Dict[str, Any]) -> Optional[DialogueNode]:
        """Choose a dialogue option and move to the next node."""
        if npc_name not in self.active_conversations:
            return None
        
        tree, state = self.active_conversations[npc_name]
        current_node = self.get_current_node(npc_name)
        
        if not current_node:
            return None
        
        # Find and apply the chosen option
        for option in current_node.options:
            if option.option_id == option_id:
                option.apply_consequences(player_state, state)
                
                # Move to next node
                if option.next_node_id:
                    next_node = tree.get_node(option.next_node_id)
                    state.record_dialogue(option.next_node_id)
                    return next_node
                else:
                    # Dialogue ends
                    del self.active_conversations[npc_name]
                    return None
        
        return None
    
    def end_conversation(self, npc_name: str) -> None:
        """End an active conversation."""
        if npc_name in self.active_conversations:
            del self.active_conversations[npc_name]
    
    def get_dialogue_state(self, npc_name: str) -> Optional[DialogueState]:
        """Get the current dialogue state for a conversation."""
        if npc_name in self.active_conversations:
            _, state = self.active_conversations[npc_name]
            return state
        return None
    
    def has_active_conversation(self, npc_name: str) -> bool:
        """Check if there's an active conversation with an NPC."""
        return npc_name in self.active_conversations


class DialogueBuilder:
    """Builder pattern for constructing dialogue trees fluently."""
    
    def __init__(self, tree_id: str, npc_name: str):
        """Initialize the builder."""
        self.tree = DialogueTree(tree_id, npc_name)
        self.current_node_id: Optional[str] = None
    
    def add_node(self, node_id: str, speaker: str, text: str) -> 'DialogueBuilder':
        """Add a node to the dialogue tree."""
        node = DialogueNode(node_id, speaker, text)
        self.tree.add_node(node)
        self.current_node_id = node_id
        return self
    
    def add_option(self, option_id: str, text: str, next_node_id: Optional[str] = None) -> 'DialogueBuilder':
        """Add an option to the current node."""
        if self.current_node_id:
            node = self.tree.get_node(self.current_node_id)
            if node:
                option = DialogueOption(option_id, text, next_node_id)
                node.options.append(option)
        return self
    
    def add_condition_to_option(self, option_id: str, condition: DialogueCondition) -> 'DialogueBuilder':
        """Add a condition to an option in the current node."""
        if self.current_node_id:
            node = self.tree.get_node(self.current_node_id)
            if node:
                for option in node.options:
                    if option.option_id == option_id:
                        option.conditions.append(condition)
                        break
        return self
    
    def add_consequence_to_option(self, option_id: str, consequence: DialogueConsequence) -> 'DialogueBuilder':
        """Add a consequence to an option in the current node."""
        if self.current_node_id:
            node = self.tree.get_node(self.current_node_id)
            if node:
                for option in node.options:
                    if option.option_id == option_id:
                        option.consequences.append(consequence)
                        break
        return self
    
    def build(self) -> DialogueTree:
        """Build and return the dialogue tree."""
        return self.tree
