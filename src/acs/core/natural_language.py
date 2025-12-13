#!/usr/bin/env python3
"""SagaCraft - Natural Language Parser
Inspired by Inform 7's natural language understanding capabilities.

This module provides enhanced natural language processing for command
interpretation, similar to Inform 7's approach but adapted for SagaCraft.
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class GrammarPattern(Enum):
    """Command grammar patterns inspired by Inform 7"""

    VERB_NOUN = "verb_noun"  # "take sword"
    VERB_NOUN_PREP_NOUN = "verb_noun_prep_noun"  # "put sword in bag"
    VERB_PREP_NOUN = "verb_prep_noun"  # "look at statue"
    VERB_NOUN_NOUN = "verb_noun_noun"  # "give sword guard"
    VERB_ADJECTIVE_NOUN = "verb_adj_noun"  # "take red key"
    VERB_ALONE = "verb_alone"  # "inventory", "wait"


@dataclass
class ParsedCommand:
    """Represents a parsed natural language command"""

    verb: str
    direct_object: Optional[str] = None
    indirect_object: Optional[str] = None
    preposition: Optional[str] = None
    adjectives: List[str] = None
    pattern: Optional[GrammarPattern] = None
    confidence: float = 1.0  # 0.0 to 1.0
    raw_input: str = ""

    def __post_init__(self):
        if self.adjectives is None:
            self.adjectives = []


class InformStyleParser:
    """
    Natural language parser inspired by Inform 7's understanding system.

    Inform 7 excels at understanding varied phrasings and natural
    language. This parser brings similar capabilities to SagaCraft.
    """

    def __init__(self):
        # Verb synonyms (Inform 7 style "understand")
        self.verb_synonyms = {
            "take": ["get", "grab", "pick", "acquire", "obtain"],
            "drop": ["discard", "throw", "leave", "dump"],
            "examine": ["x", "look", "inspect", "check", "read", "study"],
            "go": ["walk", "run", "move", "travel", "head"],
            "attack": ["hit", "fight", "kill", "strike", "punch", "stab"],
            "talk": ["speak", "chat", "converse", "say", "ask", "tell"],
            "use": ["utilize", "employ", "apply", "wield"],
            "open": ["unlock", "unfasten"],
            "close": ["shut", "lock", "fasten"],
            "give": ["offer", "hand", "present"],
            "pull": ["drag", "tug", "yank"],
            "push": ["press", "shove"],
            "turn": ["rotate", "twist", "spin"],
            "wait": ["z", "rest", "pause"],
            "inventory": ["i", "inv", "items"],
            "save": ["backup", "store"],
            "load": ["restore", "resume"],
            "help": ["?", "info", "instructions"],
            "quit": ["exit", "end", "bye", "goodbye"],
        }

        # Prepositions (Inform 7 recognizes these naturally)
        self.prepositions = {
            "in",
            "into",
            "on",
            "onto",
            "under",
            "behind",
            "with",
            "at",
            "to",
            "from",
            "through",
            "around",
            "about",
            "using",
            "by",
            "via",
            "against",
        }

        # Articles to ignore (like Inform 7)
        self.articles = {"a", "an", "the", "some", "my"}

        # Directional commands
        self.directions = {
            "north": ["n"],
            "south": ["s"],
            "east": ["e"],
            "west": ["w"],
            "northeast": ["ne"],
            "northwest": ["nw"],
            "southeast": ["se"],
            "southwest": ["sw"],
            "up": ["u"],
            "down": ["d"],
            "in": [],
            "out": [],
        }

        # Common adjectives for object disambiguation
        self.common_adjectives = {
            "red",
            "blue",
            "green",
            "yellow",
            "black",
            "white",
            "large",
            "small",
            "big",
            "tiny",
            "huge",
            "old",
            "new",
            "ancient",
            "rusty",
            "shiny",
            "wooden",
            "metal",
            "stone",
            "glass",
            "golden",
            "left",
            "right",
            "upper",
            "lower",
        }

    def normalize_verb(self, verb: str) -> str:
        """Convert synonyms to canonical verb (Inform 7 'understand')"""
        verb = verb.lower()

        # Check if it's already canonical
        if verb in self.verb_synonyms:
            return verb

        # Check synonyms
        for canonical, synonyms in self.verb_synonyms.items():
            if verb in synonyms:
                return canonical

        # Check directions
        for direction, shortcuts in self.directions.items():
            if verb == direction or verb in shortcuts:
                return "go"

        return verb

    def tokenize(self, command: str) -> List[str]:
        """Tokenize command, removing articles"""
        tokens = command.lower().strip().split()
        # Remove articles (like Inform 7)
        return [t for t in tokens if t not in self.articles]

    def extract_adjectives(self, tokens: List[str]) -> Tuple[List[str], List[str]]:
        """Extract adjectives from token list"""
        adjectives = []
        remaining = []

        for token in tokens:
            if token in self.common_adjectives:
                adjectives.append(token)
            else:
                remaining.append(token)

        return adjectives, remaining

    def find_preposition_split(
        self, tokens: List[str]
    ) -> Tuple[Optional[int], Optional[str]]:
        """Find preposition that splits direct and indirect objects"""
        for i, token in enumerate(tokens):
            if token in self.prepositions:
                return i, token
        return None, None

    def parse(self, command: str) -> ParsedCommand:
        """
        Parse natural language command (Inform 7 style).

        Examples:
            "take the red sword" -> verb=take, adj=[red], obj=sword
            "put sword in bag" -> verb=put, obj1=sword, prep=in, obj2=bag
            "examine statue" -> verb=examine, obj=statue
            "go north" -> verb=go, obj=north
        """
        original = command
        tokens = self.tokenize(command)

        if not tokens:
            return ParsedCommand(verb="", raw_input=original, confidence=0.0)

        # Extract verb
        verb = self.normalize_verb(tokens[0])
        remaining = tokens[1:]

        # Handle direction shortcuts (single word)
        if not remaining and verb == "go":
            return ParsedCommand(
                verb="go",
                direct_object=tokens[0],
                pattern=GrammarPattern.VERB_NOUN,
                raw_input=original,
            )

        # Handle verb-only commands
        if not remaining:
            return ParsedCommand(
                verb=verb, pattern=GrammarPattern.VERB_ALONE, raw_input=original
            )

        # Extract adjectives
        adjectives, remaining = self.extract_adjectives(remaining)

        # Find preposition
        prep_index, preposition = self.find_preposition_split(remaining)

        if preposition:
            # Pattern: VERB [ADJ] NOUN PREP [ADJ] NOUN
            direct_obj = " ".join(remaining[:prep_index])
            slice_start = prep_index + 1
            indirect_obj = " ".join(remaining[slice_start:])

            return ParsedCommand(
                verb=verb,
                direct_object=direct_obj,
                indirect_object=indirect_obj,
                preposition=preposition,
                adjectives=adjectives,
                pattern=GrammarPattern.VERB_NOUN_PREP_NOUN,
                raw_input=original,
            )

        elif len(remaining) >= 2:
            # Pattern: VERB NOUN NOUN (like "give guard sword")
            return ParsedCommand(
                verb=verb,
                direct_object=remaining[0],
                indirect_object=" ".join(remaining[1:]),
                adjectives=adjectives,
                pattern=GrammarPattern.VERB_NOUN_NOUN,
                raw_input=original,
            )

        else:
            # Pattern: VERB [ADJ] NOUN
            return ParsedCommand(
                verb=verb,
                direct_object=" ".join(remaining),
                adjectives=adjectives,
                pattern=(
                    GrammarPattern.VERB_NOUN if adjectives else GrammarPattern.VERB_NOUN
                ),
                raw_input=original,
            )

    def understand_as(self, phrase: str, canonical: str):
        """
        Add new understanding (like Inform 7's 'Understand' syntax).

        Example:
            parser.understand_as("steal", "take")
            parser.understand_as("n", "north")
        """
        phrase = phrase.lower()
        canonical = canonical.lower()

        # Find the canonical verb
        for verb, synonyms in self.verb_synonyms.items():
            if canonical == verb or canonical in synonyms:
                if phrase not in synonyms:
                    synonyms.append(phrase)
                return

        # If not found, create new entry
        if canonical in self.verb_synonyms:
            self.verb_synonyms[canonical].append(phrase)
        else:
            self.verb_synonyms[canonical] = [phrase]

    def suggest_corrections(self, command: str, known_verbs: Set[str]) -> List[str]:
        """
        Suggest corrections for unknown commands
        (like Inform 7's error messages).
        """
        tokens = self.tokenize(command)
        if not tokens:
            return []

        verb = tokens[0]
        suggestions = []

        # Find similar verbs using simple edit distance
        for known_verb in known_verbs:
            if self._similarity(verb, known_verb) > 0.6:
                suggestions.append(f"Did you mean '{known_verb}'?")

        return suggestions[:3]  # Top 3 suggestions

    def _similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words (simple method)"""
        if word1 == word2:
            return 1.0

        # Levenshtein-like similarity
        len1, len2 = len(word1), len(word2)
        if max(len1, len2) == 0:
            return 0.0

        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(word1, word2))
        return matches / max(len1, len2)


class InformStyleWorld:
    """
    World model inspired by Inform 7's knowledge representation.

    Inform 7 tracks relationships, properties, and kinds. This class
    provides similar capabilities for SagaCraft.
    """

    def __init__(self):
        self.relations: Dict[str, List[Tuple[str, str]]] = {}
        self.properties: Dict[str, Dict[str, any]] = {}
        self.kinds: Dict[str, str] = {}  # object -> kind

    def relate(self, relation: str, obj1: str, obj2: str):
        """
        Define a relation between objects (Inform 7 style).

        Example:
            world.relate("contains", "box", "key")
            world.relate("supports", "table", "book")
        """
        if relation not in self.relations:
            self.relations[relation] = []
        self.relations[relation].append((obj1, obj2))

    def query_relation(self, relation: str, obj1: str) -> List[str]:
        """Query what objects are related"""
        if relation not in self.relations:
            return []
        return [obj2 for o1, obj2 in self.relations[relation] if o1 == obj1]

    def set_property(self, obj: str, property_name: str, value: any):
        """Set property on object (like Inform 7 properties)"""
        if obj not in self.properties:
            self.properties[obj] = {}
        self.properties[obj][property_name] = value

    def get_property(self, obj: str, property_name: str, default=None) -> any:
        """Get property from object"""
        return self.properties.get(obj, {}).get(property_name, default)

    def has_property(self, obj: str, property_name: str) -> bool:
        """Check if object has property"""
        return obj in self.properties and property_name in self.properties[obj]

    def set_kind(self, obj: str, kind: str):
        """Set the kind of an object (Inform 7 kinds)"""
        self.kinds[obj] = kind

    def get_kind(self, obj: str) -> Optional[str]:
        """Get the kind of an object"""
        return self.kinds.get(obj)

    def is_kind(self, obj: str, kind: str) -> bool:
        """Check if object is of a certain kind"""
        return self.kinds.get(obj) == kind


# Example usage and testing
if __name__ == "__main__":
    parser = InformStyleParser()
    world = InformStyleWorld()

    # Test parsing
    test_commands = [
        "take the red sword",
        "put sword in bag",
        "examine ancient statue",
        "give guard golden key",
        "go north",
        "attack orc with sword",
        "look at mysterious door",
        "inventory",
        "x sword",
    ]

    print("=== Inform 7 Style Natural Language Parser ===\n")

    for cmd in test_commands:
        result = parser.parse(cmd)
        print(f"Input: '{cmd}'")
        print(f"  Verb: {result.verb}")
        if result.direct_object:
            print(f"  Direct Object: {result.direct_object}")
        if result.indirect_object:
            print(f"  Indirect Object: {result.indirect_object}")
        if result.preposition:
            print(f"  Preposition: {result.preposition}")
        if result.adjectives:
            print(f"  Adjectives: {result.adjectives}")
        print(f"  Pattern: {result.pattern}")
        print()

    # Test world model
    print("\n=== Inform 7 Style World Model ===\n")

    world.set_kind("sword", "weapon")
    world.set_kind("key", "item")
    world.set_property("sword", "sharp", True)
    world.set_property("sword", "damage", 10)
    world.relate("carries", "player", "sword")
    world.relate("contains", "chest", "key")

    print(f"Sword is a: {world.get_kind('sword')}")
    print(f"Sword is sharp: {world.get_property('sword', 'sharp')}")
    print(f"Player carries: {world.query_relation('carries', 'player')}")
    print(f"Chest contains: {world.query_relation('contains', 'chest')}")
