import json
import pytest

from sagacraft.core.engine import AdventureGame


def parser_adventure():
    return {
        "title": "Parser Adventure",
        "intro": "Parser testing.",
        "start_room": 1,
        "rooms": [
            {"id": 1, "name": "Alpha", "description": "Alpha room.", "exits": {"north": 2}},
            {"id": 2, "name": "Beta", "description": "Beta room.", "exits": {"south": 1}},
        ],
        "items": [
            {"id": 1, "name": "bread", "description": "Bread loaf.", "type": "edible", "weight": 1, "value": 1, "location": 1},
        ],
        "monsters": [],
    }


@pytest.fixture()
def parser_engine(tmp_path):
    path = tmp_path / "parser_adventure.json"
    path.write_text(json.dumps(parser_adventure()), encoding="utf-8")
    eng = AdventureGame(str(path))
    eng.load_adventure()
    return eng


@pytest.mark.skipif(not getattr(AdventureGame, "use_enhanced_parser", False) and not getattr(parser_engine, "use_enhanced_parser", False), reason="Enhanced parser not available")
def test_nlp_paths_move_and_get(parser_engine):
    # These rely on parser being active; otherwise the mark skips.
    parser_engine.use_enhanced_parser = True if parser_engine.parser else parser_engine.use_enhanced_parser
    parser_engine.process_command("move north")
    assert parser_engine.player.current_room == 2
    parser_engine.process_command("get bread")
    assert 1 in parser_engine.player.inventory


@pytest.mark.skipif(not getattr(AdventureGame, "use_enhanced_parser", False) and not getattr(parser_engine, "use_enhanced_parser", False), reason="Enhanced parser not available")
def test_nlp_paths_status_and_inventory(parser_engine):
    parser_engine.use_enhanced_parser = True if parser_engine.parser else parser_engine.use_enhanced_parser
    parser_engine.process_command("status")
    parser_engine.process_command("inventory")
