#!/usr/bin/env python3
"""SagaCraft - Inform 7 Integration

Integrates Inform 7-style natural language understanding into the SagaCraft engine.
"""

from typing import List, Optional, Tuple
from acs.core.natural_language import (
    InformStyleParser,
    InformStyleWorld,
    ParsedCommand,
)


class InformEnhancedEngine:
    """
    Mixin class that adds Inform 7 capabilities to SagaCraft engine.

    This provides:
    - Natural language command understanding
    - Flexible verb synonyms
    - Rich world model with relations
    - Object properties and kinds
    """

    def __init__(self):
        """Initialize Inform 7 integration"""
        self.inform_parser = InformStyleParser()
        self.inform_world = InformStyleWorld()
        self._setup_world_model()

    def _setup_world_model(self):
        """
        Initialize world model with Inform 7 style definitions.
        This is called during engine initialization.
        """
        # Define object kinds (like Inform 7 "kind" declarations)
        # These will be populated as objects are loaded

        # Define common relations
        # "carrying" relation (player -> items)
        # "contains" relation (containers -> items)
        # "supports" relation (surfaces -> items)

        pass  # Will be filled in during game load

    def parse_inform_command(self, command: str) -> ParsedCommand:
        """
        Parse command using Inform 7 style natural language.

        Returns ParsedCommand with verb, objects, and grammatical info.
        """
        return self.inform_parser.parse(command)

    def teach_command(self, phrase: str, canonical: str):
        """
        Teach the parser a new command synonym.

        Example:
            engine.teach_command("steal", "take")
            engine.teach_command("smash", "attack")

        This is like Inform 7's "Understand" declarations.
        """
        self.inform_parser.understand_as(phrase, canonical)

    def relate_objects(self, relation: str, obj1: str, obj2: str):
        """
        Create a relation between two objects.

        Examples:
            relate_objects("contains", "chest", "key")
            relate_objects("wears", "guard", "helmet")
        """
        self.inform_world.relate(relation, obj1, obj2)

    def query_related(self, relation: str, obj: str) -> List[str]:
        """
        Query what objects are related.

        Example:
            keys_in_chest = query_related("contains", "chest")
        """
        return self.inform_world.query_relation(relation, obj)

    def set_object_property(self, obj: str, prop: str, value):
        """
        Set a property on an object (Inform 7 style).

        Examples:
            set_object_property("door", "locked", True)
            set_object_property("lamp", "lit", False)
        """
        self.inform_world.set_property(obj, prop, value)

    def get_object_property(self, obj: str, prop: str, default=None):
        """Get a property from an object"""
        return self.inform_world.get_property(obj, prop, default)

    def object_has_property(self, obj: str, prop: str) -> bool:
        """Check if object has a property"""
        return self.inform_world.has_property(obj, prop)

    def set_object_kind(self, obj: str, kind: str):
        """
        Set the kind of an object.

        Examples:
            set_object_kind("sword", "weapon")
            set_object_kind("chest", "container")
        """
        self.inform_world.set_kind(obj, kind)

    def is_object_kind(self, obj: str, kind: str) -> bool:
        """Check if object is of a certain kind"""
        return self.inform_world.is_kind(obj, kind)

    def process_natural_command(
        self, command: str
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Process natural language command and return
        (verb, direct_object, indirect_object).

        This bridges the Inform 7 parser to the existing SagaCraft command
        system.
        """
        parsed = self.parse_inform_command(command)

        # Handle failed parse
        if not parsed.verb or parsed.confidence < 0.5:
            return ("unknown", None, None)

        # Convert parsed command to SagaCraft format
        verb = parsed.verb
        direct_obj = parsed.direct_object
        indirect_obj = parsed.indirect_object

        # Handle adjective disambiguation
        if parsed.adjectives and direct_obj:
            # Try to find object matching adjectives
            direct_obj = self._disambiguate_with_adjectives(
                direct_obj, parsed.adjectives
            )

        return (verb, direct_obj, indirect_obj)

    def _disambiguate_with_adjectives(self, noun: str, adjectives: List[str]) -> str:
        """
        Use adjectives to disambiguate objects.

        If there are multiple "keys", and user says "red key",
        try to find the one with adjective "red".
        """
        # Combine adjectives and noun
        if adjectives:
            return " ".join(adjectives + [noun])
        return noun

    def describe_understand(self) -> str:
        """
        Return a string describing what commands are understood.
        Like Inform 7's ACTIONS command.
        """
        descriptions = ["I understand the following commands:\n"]

        for verb, synonyms in self.inform_parser.verb_synonyms.items():
            syn_str = ", ".join(synonyms[:3])  # Show first 3 synonyms
            if len(synonyms) > 3:
                syn_str += f", ... ({len(synonyms)} more)"
            descriptions.append(f"  {verb.upper()}: {syn_str}")

        return "\n".join(descriptions)

    def suggest_command_corrections(self, command: str, known_verbs: set) -> List[str]:
        """Get suggestions for mistyped commands"""
        return self.inform_parser.suggest_corrections(command, known_verbs)


def create_inform_enhanced_engine(base_engine_class):
    """
    Factory function to create an Inform 7 enhanced engine class.

    Usage:
        from acs.core.engine import GameEngine
        EnhancedEngine = create_inform_enhanced_engine(GameEngine)
        game = EnhancedEngine()
    """

    class InformEnhancedGameEngine(InformEnhancedEngine, base_engine_class):
        """GameEngine with Inform 7 natural language capabilities"""

        def __init__(self, *args, **kwargs):
            # Initialize both parent classes
            InformEnhancedEngine.__init__(self)
            base_engine_class.__init__(self, *args, **kwargs)

        def process_command(self, command: str):
            """
            Override command processing to use Inform 7 style parsing.
            Falls back to original parsing if Inform parsing fails.
            """
            # Try Inform 7 style parsing first
            verb, obj1, obj2 = self.process_natural_command(command)

            if verb != "unknown":
                # Successfully parsed with Inform style
                # Route to appropriate handler
                return self._route_command(verb, obj1, obj2)
            else:
                # Fall back to original parser
                return base_engine_class.process_command(self, command)

        def _route_command(self, verb: str, obj1: Optional[str], obj2: Optional[str]):
            """Route parsed command to appropriate handler"""
            # Map to existing engine methods
            handlers = {
                "take": lambda: self._handle_take(obj1),
                "drop": lambda: self._handle_drop(obj1),
                "examine": lambda: self._handle_examine(obj1),
                "go": lambda: self._handle_go(obj1),
                "attack": lambda: self._handle_attack(obj1),
                "inventory": lambda: self._handle_inventory(),
                "help": lambda: self._handle_help(),
                "quit": lambda: self._handle_quit(),
            }

            handler = handlers.get(verb)
            if handler:
                return handler()
            else:
                return f"I don't know how to {verb}."

        def _handle_take(self, obj):
            """Handle take command"""
            if not obj:
                return "Take what?"
            # Implementation would call engine's take logic
            return f"You take the {obj}."

        def _handle_drop(self, obj):
            """Handle drop command"""
            if not obj:
                return "Drop what?"
            return f"You drop the {obj}."

        def _handle_examine(self, obj):
            """Handle examine command"""
            if not obj:
                return "Examine what?"
            return f"You examine the {obj}."

        def _handle_go(self, direction):
            """Handle movement command"""
            if not direction:
                return "Go where?"
            return f"You go {direction}."

        def _handle_attack(self, target):
            """Handle attack command"""
            if not target:
                return "Attack what?"
            return f"You attack the {target}."

        def _handle_inventory(self):
            """Show inventory"""
            return "Inventory: (items here)"

        def _handle_help(self):
            """Show help"""
            return self.describe_understand()

        def _handle_quit(self):
            """Quit game"""
            return "Thanks for playing!"

    return InformEnhancedGameEngine


# Convenience function for quick testing
def demo_inform_integration():
    """Demonstrate Inform 7 integration"""
    print("=== SagaCraft + Inform 7 Integration ===\n")

    # Create enhanced engine (would use real GameEngine in production)
    class DummyEngine:
        def __init__(self):
            pass

        def process_command(self, cmd):
            return f"Base engine: {cmd}"

    EnhancedEngine = create_inform_enhanced_engine(DummyEngine)
    game = EnhancedEngine()

    # Teach some custom commands
    game.teach_command("steal", "take")
    game.teach_command("smash", "attack")

    # Set up world model
    game.set_object_kind("sword", "weapon")
    game.set_object_kind("key", "item")
    game.set_object_property("sword", "sharp", True)
    game.set_object_property("door", "locked", True)
    game.relate_objects("contains", "chest", "key")

    # Test commands
    test_commands = [
        "take red sword",
        "steal the golden key",
        "examine ancient door",
        "smash orc",
        "inventory",
        "go north",
    ]

    print("Testing natural language commands:\n")
    for cmd in test_commands:
        result = game.process_command(cmd)
        print(f"> {cmd}")
        print(f"  {result}\n")

    # Show understood commands
    print("\n" + game.describe_understand())


if __name__ == "__main__":
    demo_inform_integration()
