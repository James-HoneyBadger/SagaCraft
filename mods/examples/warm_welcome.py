"""
name: Warm Welcome
version: 1.0
author: SagaCraft Team
summary: Adds a friendly greeting when the player enters the starting room.
"""

# pylint: disable=import-error
from sagacraft.tools.modding import CustomCommand, EventType, ScriptHook

if "register_hook" not in globals():  # pragma: no cover

    def register_hook(*_args, **_kwargs):
        """Fallback used when the mod loader does not inject hook helpers."""

        raise RuntimeError("register_hook is only available inside the mod loader")


if "register_command" not in globals():  # pragma: no cover

    def register_command(*_args, **_kwargs):
        """Fallback used when the mod loader does not inject command helpers."""

        raise RuntimeError("register_command is only available inside the mod loader")


hook = ScriptHook(
    event=EventType.ON_ENTER_ROOM,
    script_code="""
if data.get('room_id') == 1:
    echo("A hush falls over the hall as banners unfurl in your honor.")
    echo("🎉 Welcome to your adventure!")
""",
    filter_params={"room_id": 1},
    priority=10,
)
register_hook(hook)

command = CustomCommand(
    verb="wave",
    aliases=["greet"],
    help_text="Greet anyone nearby with a friendly wave.",
    handler_code="""
if room:
    echo(f"You wave cheerfully at everyone in {room.name}.")
else:
    echo("You wave into the void. Hopefully someone noticed.")
""",
)
register_command(command)
