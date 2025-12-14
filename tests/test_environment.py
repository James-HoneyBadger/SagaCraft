import json
import pytest

from sagacraft.core.engine import AdventureGame


def env_adventure():
    return {
        "title": "Env Adventure",
        "intro": "Env tests.",
        "start_room": 1,
        "rooms": [
            {"id": 1, "name": "Glade", "description": "A quiet glade.", "exits": {"east": 2}},
            {"id": 2, "name": "Brook", "description": "A running brook.", "exits": {"west": 1}},
        ],
        "items": [],
        "monsters": [],
    }


@pytest.fixture()
def env_engine(tmp_path):
    path = tmp_path / "env.json"
    path.write_text(json.dumps(env_adventure()), encoding="utf-8")
    eng = AdventureGame(str(path))
    eng.load_adventure()
    return eng


def test_look_and_environment_no_crash(env_engine, capsys):
    env_engine.look()
    out = capsys.readouterr().out
    # Basic room text appears; environmental lines may or may not be present.
    assert "glade" in out.lower()
    env_engine.move("east")
    env_engine.look()
    out = capsys.readouterr().out
    assert "brook" in out.lower()
