import json
import pytest

from sagacraft.core.engine import AdventureGame, Item


def trading_adventure():
    return {
        "title": "Trading Adventure",
        "intro": "Trading test.",
        "start_room": 1,
        "rooms": [
            {"id": 1, "name": "Market", "description": "A busy market.", "exits": {"north": 2}},
            {"id": 2, "name": "Lane", "description": "A quiet lane.", "exits": {"south": 1}},
        ],
        "items": [
            {"id": 1, "name": "potion", "description": "Healing potion.", "type": "drinkable", "weight": 1, "value": 10, "location": 1},
            {"id": 2, "name": "trinket", "description": "A small trinket.", "type": "normal", "weight": 1, "value": 6, "location": 0},
        ],
        "monsters": [
            {"id": 1, "name": "Dex", "description": "A cheerful merchant.", "room_id": 1, "hardiness": 10, "agility": 10, "friendliness": "friendly", "courage": 10}
        ],
    }


@pytest.fixture()
def trade_engine(tmp_path):
    path = tmp_path / "trade.json"
    path.write_text(json.dumps(trading_adventure()), encoding="utf-8")
    eng = AdventureGame(str(path))
    eng.load_adventure()
    # Inject a minimal parser to enable buy/sell command actions
    class _StubParser:
        def parse_command(self, cmd: str):
            parts = cmd.strip().split()
            verb = parts[0].lower() if parts else ""
            target = " ".join(parts[1:]) if len(parts) > 1 else ""
            if verb in {"buy", "sell", "trade", "move", "get", "look", "status", "inventory"}:
                action = verb if verb != "move" else "move"
                payload = {"action": action}
                if verb in {"buy", "sell", "get", "trade"}:
                    payload["target"] = target
                if verb == "move":
                    payload["direction"] = target
                return payload
            return {"action": None}

    eng.parser = _StubParser()
    eng.use_enhanced_parser = True
    # Set merchant flags and inventory after load
    merchant = eng.monsters[1]
    setattr(merchant, "is_merchant", True)
    # Give merchant Item object inventory
    merchant.inventory = [eng.items[1]]
    # Give player the trinket item object in inventory
    # Move trinket to inventory properly
    trinket = eng.items[2]
    trinket.location = 0
    eng.player.inventory.append(trinket.id)
    return eng


def test_trade_listing_and_buy(trade_engine, capsys):
    # List merchant inventory via trade
    trade_engine.process_command("trade dex")
    out = capsys.readouterr().out
    assert "available items" in out.lower()
    assert "potion" in out.lower()

    # Buy potion
    start_gold = trade_engine.player.gold
    trade_engine.process_command("buy potion")
    out = capsys.readouterr().out
    assert "bought" in out.lower()
    assert 1 in trade_engine.player.inventory
    assert trade_engine.player.gold < start_gold


def test_sell_item_to_merchant(trade_engine, capsys):
    # Ensure player has trinket
    assert 2 in trade_engine.player.inventory
    trade_engine.process_command("sell trinket")
    out = capsys.readouterr().out
    assert "sold" in out.lower()
    assert 2 not in trade_engine.player.inventory
    assert any(getattr(i, "name", "").lower() == "trinket" for i in getattr(trade_engine.monsters[1], "inventory", []))
