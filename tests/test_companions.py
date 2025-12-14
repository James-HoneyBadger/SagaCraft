import json
import pytest

from sagacraft.core.engine import AdventureGame


def comp_adventure():
    return {
        "title": "Companions Adventure",
        "intro": "Companion tests.",
        "start_room": 1,
        "rooms": [
            {"id": 1, "name": "Camp", "description": "A safe spot.", "exits": {"north": 2}},
            {"id": 2, "name": "Trail", "description": "A narrow trail.", "exits": {"south": 1}},
        ],
        "items": [],
        "monsters": [
            {"id": 1, "name": "Lyra", "description": "Friendly scout.", "room_id": 1, "hardiness": 8, "agility": 10, "friendliness": "friendly", "courage": 10}
        ],
    }


@pytest.fixture()
def comp_engine(tmp_path):
    path = tmp_path / "comp.json"
    path.write_text(json.dumps(comp_adventure()), encoding="utf-8")
    eng = AdventureGame(str(path))
    eng.load_adventure()
    return eng


@pytest.mark.skipif(not getattr(AdventureGame, "use_enhanced_parser", False) and True, reason="Enhanced systems not available")
def test_recruit_and_party_commands(comp_engine, capsys):
    # Attempt recruit when optional systems present; otherwise skipped.
    comp_engine.recruit_companion("Lyra")
    if comp_engine.companions:
        comp_engine.party_command(comp_engine.companions[0].name, "follow")
        out = capsys.readouterr().out
        assert "resumes following" in out.lower() or "nods" in out.lower()
