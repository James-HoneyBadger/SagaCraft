"""
name: Treasure Cache
version: 1.0
author: SagaCraft Team
summary: Spawns a bonus treasure chest after defeating a hostile monster.
"""

# pylint: disable=import-error
from acs.tools.modding import EventType, ScriptHook

if "register_hook" not in globals():  # pragma: no cover

    def register_hook(*_args, **_kwargs):
        """Fallback used when the mod loader does not inject hook helpers."""

        raise RuntimeError("register_hook is only available inside the mod loader")


hook = ScriptHook(
    event=EventType.ON_KILL,
    script_code="""
if data.get('monster') and data['monster'].friendliness.value == 'hostile':
    echo("A hidden panel slides open, revealing a treasure cache!")
    spawn_item("Gleaming Treasure Chest", room_id=data['monster'].room_id)
""",
    priority=5,
)
register_hook(hook)
