#!/usr/bin/env python3
"""SagaCraft Player - lightweight play-only client.

A minimal Tk interface focused solely on loading and playing SagaCraft
adventures. Supports theme + font selection and save/load slots.
"""

from __future__ import annotations

import sys
import importlib.util
from functools import partial
from collections.abc import Callable
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Optional, cast
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

from sagacraft.ui.config_io import (
    safe_read_json_mapping,
    update_basic_ui_preferences,
    write_json_mapping,
)
from sagacraft.ui.engine_runner import capture_stdout, run_engine_command
from sagacraft.ui.menu_helpers import (
    add_font_family_commands,
    add_font_size_commands,
    create_styled_menu,
)
from sagacraft.ui.theme import get_default_themes


CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "engine.json"
ENGINE_PATH = Path(__file__).resolve().parents[3] / "sagacraft_engine.py"
ADVENTURES_DIR = Path(__file__).resolve().parents[3] / "adventures"


@dataclass
class UISettings:
    """User-facing UI preferences."""

    theme: str = "Dark"
    font_family: str = "Segoe UI"
    font_size: int = 10


class SagaCraftPlayer:  # pylint: disable=too-many-instance-attributes
    """Lightweight play-only SagaCraft client."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("SagaCraft Player")
        self.root.geometry("960x760")

        # Theme palette (shared with IDE)
        self.themes = get_default_themes()

        self.settings = UISettings()
        self._load_ui_preferences()

        self.current_theme = (
            self.settings.theme if self.settings.theme in self.themes else "Dark"
        )
        self.colors = self.themes[self.current_theme]
        self.current_font_family = self.settings.font_family
        self.current_font_size = self.settings.font_size

        self.game_instance: Any | None = None
        self.game_loaded = False
        self.current_file: Optional[Path] = None

        self.status_var = tk.StringVar(value="Load an adventure to begin.")

        self._setup_styles()
        self._build_menu()
        self._build_layout()
        self._apply_theme()

    # UI setup ---------------------------------------------------------------
    def _setup_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=2)
        style.configure("TMenubutton", padding=4)

    def _build_menu(self) -> None:
        menubar = create_styled_menu(self.root, self.colors)

        file_menu = create_styled_menu(menubar, self.colors, tearoff=0)
        file_menu.add_command(label="Open Adventure...", command=self.open_adventure)
        file_menu.add_separator()
        file_menu.add_command(
            label="Save Game (slot 1)",
            command=cast(Callable[[], Any], partial(self.save_game, 1)),
        )
        file_menu.add_command(
            label="Load Game (slot 1)",
            command=cast(Callable[[], Any], partial(self.load_game, 1)),
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        options_menu = create_styled_menu(menubar, self.colors, tearoff=0)
        theme_menu = create_styled_menu(options_menu, self.colors, tearoff=0)
        for theme_name in self.themes:
            theme_menu.add_command(
                label=theme_name,
                command=cast(Callable[[], Any], partial(self.change_theme, theme_name)),
            )
        options_menu.add_cascade(label="Theme", menu=theme_menu)

        font_menu = create_styled_menu(options_menu, self.colors, tearoff=0)
        add_font_family_commands(font_menu, self.change_font_family)
        font_size_menu = create_styled_menu(font_menu, self.colors, tearoff=0)
        add_font_size_commands(font_size_menu, self.change_font_size)
        font_menu.add_cascade(label="Font Size", menu=font_size_menu)
        options_menu.add_cascade(label="Font", menu=font_menu)

        menubar.add_cascade(label="Options", menu=options_menu)
        self.root.config(menu=menubar)

    def _build_layout(self) -> None:
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=10)

        self.file_label = ttk.Label(top, text="No adventure loaded")
        self.file_label.pack(side=tk.LEFT)

        spacer = ttk.Frame(top)
        spacer.pack(side=tk.LEFT, expand=True, fill=tk.X)

        ttk.Label(top, text="Theme:").pack(side=tk.LEFT, padx=(0, 4))
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_box = ttk.Combobox(
            top,
            textvariable=self.theme_var,
            values=list(self.themes.keys()),
            state="readonly",
            width=12,
        )
        theme_box.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.change_theme(self.theme_var.get()),
        )
        theme_box.pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Font:").pack(side=tk.LEFT, padx=(12, 4))
        self.font_var = tk.StringVar(value=self.current_font_family)
        font_box = ttk.Combobox(
            top,
            textvariable=self.font_var,
            values=["Segoe UI", "Arial", "Helvetica", "Verdana", "Tahoma", "Calibri"],
            state="readonly",
            width=12,
        )
        font_box.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.change_font_family(self.font_var.get()),
        )
        font_box.pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Size:").pack(side=tk.LEFT, padx=(12, 4))
        self.size_var = tk.IntVar(value=self.current_font_size)
        size_spin = ttk.Spinbox(
            top,
            from_=8,
            to=18,
            textvariable=self.size_var,
            width=4,
            command=lambda: self.change_font_size(self.size_var.get()),
        )
        size_spin.pack(side=tk.LEFT)

        action_row = ttk.Frame(self.root)
        action_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(action_row, text="Open Adventure", command=self.open_adventure).pack(
            side=tk.LEFT
        )
        ttk.Button(action_row, text="Save Slot 1", command=lambda: self.save_game(1)).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Button(action_row, text="Load Slot 1", command=lambda: self.load_game(1)).pack(
            side=tk.LEFT, padx=6
        )

        console_frame = ttk.Frame(self.root)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.game_output = scrolledtext.ScrolledText(
            console_frame, wrap=tk.WORD, height=24, state=tk.DISABLED
        )
        self.game_output.pack(fill=tk.BOTH, expand=True)

        entry_row = ttk.Frame(self.root)
        entry_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.command_var = tk.StringVar()
        self.command_entry = ttk.Entry(entry_row, textvariable=self.command_var)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", lambda _e: self.run_command())

        ttk.Button(entry_row, text="Send", command=self.run_command).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Button(
            entry_row,
            text="Look",
            command=lambda: self._process_command("look", echo=True),
        ).pack(side=tk.LEFT)

        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Label(status_bar, textvariable=self.status_var).pack(side=tk.LEFT)

    def _apply_theme(self) -> None:
        self.root.configure(bg=self.colors["bg"])
        for widget in self.root.winfo_children():
            self._style_widget(widget)
        self._apply_fonts()

    def _style_widget(self, widget: tk.Misc) -> None:
        if isinstance(
            widget, (ttk.Frame, ttk.Label, ttk.Button, ttk.Combobox, ttk.Spinbox)
        ):
            for child in widget.winfo_children():
                self._style_widget(child)
        if isinstance(widget, tk.Tk):
            widget.configure(bg=self.colors["bg"])
        if isinstance(widget, scrolledtext.ScrolledText):
            widget.configure(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
                highlightbackground=self.colors["border"],
            )
        # Avoid styling ttk spinbox/combobox/entry with tk options
        if isinstance(widget, tk.Entry) and not isinstance(
            widget, (ttk.Entry, ttk.Combobox, ttk.Spinbox)
        ):
            widget.configure(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
                highlightbackground=self.colors["border"],
            )
        if isinstance(widget, ttk.Button):
            widget.configure()

    def _apply_fonts(self) -> None:
        body_font = (self.current_font_family, self.current_font_size)
        self.game_output.configure(font=body_font)
        self.command_entry.configure(font=body_font)
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.configure(font=body_font)

    # Persistence -----------------------------------------------------------
    def _load_ui_preferences(self) -> None:
        """Load UI preferences from `CONFIG_PATH` if present."""
        if not CONFIG_PATH.exists():
            return
        data = safe_read_json_mapping(CONFIG_PATH)
        ui = data.get("ui", {}) if isinstance(data.get("ui", {}), dict) else {}
        theme = ui.get("theme")
        if isinstance(theme, str):
            # Accept case-insensitive values
            for name in self.themes:
                if name.lower() == theme.lower():
                    self.settings.theme = name
                    break
        font_family = ui.get("font_family")
        if isinstance(font_family, str):
            self.settings.font_family = font_family
        font_size = ui.get("font_size")
        if isinstance(font_size, int) and 6 <= font_size <= 24:
            self.settings.font_size = font_size

    def _save_ui_preferences(self) -> None:
        """Persist current UI preferences to `CONFIG_PATH`."""
        data = safe_read_json_mapping(CONFIG_PATH) if CONFIG_PATH.exists() else {}
        update_basic_ui_preferences(
            data,
            theme=self.current_theme,
            font_family=self.current_font_family,
            font_size=self.current_font_size,
        )
        try:
            write_json_mapping(CONFIG_PATH, data)
        except OSError:
            pass

    # Adventure management --------------------------------------------------
    def open_adventure(self) -> None:
        """Open an adventure JSON file and load it."""
        path = filedialog.askopenfilename(
            parent=self.root,
            initialdir=ADVENTURES_DIR,
            filetypes=[("SagaCraft Adventure", "*.json"), ("All Files", "*.*")],
            title="Open Adventure",
        )
        if not path:
            return
        self._load_adventure(Path(path))

    def _load_adventure(self, path: Path) -> None:
        """Load an adventure via the dynamically loaded engine."""
        self.game_instance = None
        self.game_loaded = False
        self.current_file = path

        engine_module = self._load_engine_module()
        if engine_module is None:
            self._set_status("Unable to load game engine.")
            return

        try:
            game_ctor_obj = getattr(
                engine_module, "ExtendedAdventureGame", None
            ) or getattr(engine_module, "EnhancedAdventureGame", None)
            if game_ctor_obj is None or not callable(game_ctor_obj):
                self._set_status("Engine missing game class.")
                return
            game_ctor: Callable[..., Any] = game_ctor_obj
            instance = game_ctor(str(path))  # pylint: disable=not-callable
            instance.load_adventure()
            self.game_instance = instance
        except (
            OSError,
            RuntimeError,
            ValueError,
            AttributeError,
            TypeError,
        ) as exc:  # pragma: no cover
            self._set_status(f"Failed to load adventure: {exc}")
            return

        self._clear_output()
        self._print_header()
        self._set_status(f"Loaded: {path.name}")
        self.file_label.config(text=f"Adventure: {path.name}")
        self.game_loaded = True
        # Show starting room
        assert self.game_instance is not None
        self._capture_output(self.game_instance.look)

    def _print_header(self) -> None:
        """Print the adventure title + intro block."""
        if not self.game_instance:
            return
        title = getattr(self.game_instance, "adventure_title", "Adventure")
        intro = getattr(self.game_instance, "adventure_intro", "")
        rule = "=" * 58
        self._append(f"={rule}\n  {title.upper()}\n={rule}\n\n{intro}\n\n{rule}")

    def save_game(self, slot: int = 1) -> None:
        """Save the current game state to a slot."""
        if not self.game_loaded or not self.game_instance:
            self._set_status("Load an adventure first.")
            return
        Path("saves").mkdir(parents=True, exist_ok=True)
        result = self._capture_output(self.game_instance.save_game, slot)
        if result:
            self._set_status(f"Saved slot {slot}")
        else:
            self._set_status(f"Save failed (slot {slot})")

    def load_game(self, slot: int = 1) -> None:
        """Load a previously saved game state from a slot."""
        if not self.game_loaded or not self.game_instance:
            self._set_status("Load an adventure first.")
            return
        result = self._capture_output(self.game_instance.load_game, slot)
        if result:
            self._set_status(f"Loaded slot {slot}")
            self._capture_output(self.game_instance.look)
        else:
            self._set_status(f"Load failed (slot {slot})")

    # Command handling ------------------------------------------------------
    def run_command(self) -> None:
        """Send the current command entry to the engine."""
        command = self.command_var.get().strip()
        if not command:
            return
        self.command_var.set("")
        self._process_command(command, echo=True)

    def _process_command(self, command: str, echo: bool = False) -> None:
        """Process a single command via the loaded engine."""
        if not self.game_loaded or not self.game_instance:
            self._set_status("Load an adventure first.")
            return
        if echo:
            self._append(f"> {command}")
        if command.lower() in {"quit", "exit", "q"}:
            self._append("Thanks for playing!")
            self._set_status("Game ended")
            return
        output, error = run_engine_command(self.game_instance, command)
        if error is not None:
            self._append(f"Error: {error}")
            self._set_status("Command error")
            return
        if output:
            self._append(output.rstrip())
        if getattr(self.game_instance, "game_over", False):
            self._append("\nGAME OVER")
            self._set_status("Game over")

    # Helpers ---------------------------------------------------------------
    def _load_engine_module(self):
        """Dynamically load the engine module from `ENGINE_PATH`."""
        spec = importlib.util.spec_from_file_location("sagacraft_engine", ENGINE_PATH)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except (ImportError, OSError, RuntimeError):  # pragma: no cover
            return None
        return module

    def _capture_output(self, func, *args, **kwargs):
        """Run a callable while capturing stdout into the UI output box."""
        result, raw = capture_stdout(func, *args, **kwargs)
        text = raw.strip()
        if text:
            self._append(text)
        return result

    def _append(self, text: str) -> None:
        """Append text to the output console."""
        self.game_output.configure(state=tk.NORMAL)
        self.game_output.insert(tk.END, text + "\n")
        self.game_output.see(tk.END)
        self.game_output.configure(state=tk.DISABLED)

    def _clear_output(self) -> None:
        """Clear the output console."""
        self.game_output.configure(state=tk.NORMAL)
        self.game_output.delete("1.0", tk.END)
        self.game_output.configure(state=tk.DISABLED)

    def _set_status(self, message: str) -> None:
        """Update the status bar."""
        self.status_var.set(message)

    # Theme + font changes --------------------------------------------------
    def change_theme(self, theme_name: str) -> None:
        """Apply a named UI theme."""
        if theme_name not in self.themes:
            return
        self.current_theme = theme_name
        self.colors = self.themes[theme_name]
        self.theme_var.set(theme_name)
        self._apply_theme()
        self._save_ui_preferences()
        self._set_status(f"Theme: {theme_name}")

    def change_font_family(self, family: str) -> None:
        """Set the UI font family."""
        self.current_font_family = family
        self.font_var.set(family)
        self._apply_fonts()
        self._save_ui_preferences()
        self._set_status(f"Font: {family}")

    def change_font_size(self, size: int) -> None:
        """Set the UI font size."""
        try:
            size_int = int(size)
        except (TypeError, ValueError):
            return
        self.current_font_size = max(8, min(24, size_int))
        self.size_var.set(self.current_font_size)
        self._apply_fonts()
        self._save_ui_preferences()
        self._set_status(f"Font size: {self.current_font_size}pt")


# pylint: disable=too-many-locals,too-many-branches,too-many-statements
# pylint: disable=too-many-return-statements,inconsistent-return-statements
def main() -> Optional[SagaCraftPlayer]:
    """Entry point for the player UI (and CLI debug modes)."""
    # Headless check mode: initialize nothing, just verify engine loads
    if "--check" in sys.argv:
        try:
            spec = importlib.util.spec_from_file_location(
                "sagacraft_engine", ENGINE_PATH
            )
            if spec is None or spec.loader is None:
                print("CHECK: engine spec load failed")
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Basic sanity: required class exists
            ok = hasattr(module, "EnhancedAdventureGame") or hasattr(
                module, "ExtendedAdventureGame"
            )
            print("CHECK: engine import OK" if ok else "CHECK: engine missing game class")
        except (ImportError, OSError, RuntimeError) as exc:
            print(f"CHECK: import error: {exc}")
        return None

    # Headless load mode: load an adventure JSON and print intro + first look
    if "--load" in sys.argv:
        try:
            idx = sys.argv.index("--load")
            adventure_path = (
                Path(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else None
            )
        except (ValueError, IndexError):
            adventure_path = None
        if not adventure_path or not Path(adventure_path).exists():
            print("LOAD: missing or invalid path")
            return None
        try:
            spec = importlib.util.spec_from_file_location(
                "sagacraft_engine", ENGINE_PATH
            )
            if spec is None or spec.loader is None:
                print("LOAD: engine spec load failed")
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            game_ctor_obj = getattr(module, "ExtendedAdventureGame", None) or getattr(
                module, "EnhancedAdventureGame", None
            )
            if game_ctor_obj is None or not callable(game_ctor_obj):
                print("LOAD: engine game class missing")
                return None
            # Optional seed for deterministic runs: --seed <int>
            seed = None
            if "--seed" in sys.argv:
                try:
                    sidx = sys.argv.index("--seed")
                    seed_s = sys.argv[sidx + 1] if sidx + 1 < len(sys.argv) else None
                    seed = int(seed_s) if seed_s is not None else None
                except (ValueError, IndexError):
                    seed = None
            game_ctor: Callable[..., Any] = game_ctor_obj
            instance = game_ctor(str(adventure_path), seed=seed)  # pylint: disable=not-callable
            instance.load_adventure()
            title = getattr(instance, "adventure_title", "Adventure")
            intro = getattr(instance, "adventure_intro", "")
            rule = "=" * 58
            header = f"={rule}\n  {title.upper()}\n={rule}\n\n{intro}\n\n{rule}"
            transcript_out = None
            # Optional transcript file: --transcript <file>
            if "--transcript" in sys.argv:
                try:
                    tidx = sys.argv.index("--transcript")
                    transcript_out = (
                        Path(sys.argv[tidx + 1]) if tidx + 1 < len(sys.argv) else None
                    )
                except (ValueError, IndexError):
                    transcript_out = None

            def _print(text: str):
                """Print to stdout (and optional transcript file)."""
                print(text)
                if transcript_out:
                    try:
                        transcript_out.parent.mkdir(parents=True, exist_ok=True)
                        with open(transcript_out, "a", encoding="utf-8") as tf:
                            tf.write(text + "\n")
                    except OSError:
                        pass
            _print(header)
            # Capture first room description
            buf = StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                instance.look()
            finally:
                sys.stdout = old
            _print(buf.getvalue().strip())

            # Optional single command: --cmd "<command>"
            if "--cmd" in sys.argv:
                try:
                    cidx = sys.argv.index("--cmd")
                    cmd = sys.argv[cidx + 1] if cidx + 1 < len(sys.argv) else None
                except (ValueError, IndexError):
                    cmd = None
                if not cmd:
                    print("CMD: missing command string")
                    return None
                buf2 = StringIO()
                old2 = sys.stdout
                sys.stdout = buf2
                try:
                    instance.process_command(cmd)
                finally:
                    sys.stdout = old2
                out = buf2.getvalue().strip()
                _print(out if out else f"CMD: executed '{cmd}' with no output")

            # Optional commands file: --cmds <file>
            if "--cmds" in sys.argv:
                try:
                    fidx = sys.argv.index("--cmds")
                    cmds_path = Path(sys.argv[fidx + 1]) if fidx + 1 < len(sys.argv) else None
                except (ValueError, IndexError):
                    cmds_path = None
                if not cmds_path or not cmds_path.exists():
                    print("CMDS: missing or invalid file path")
                    return None
                try:
                    with open(cmds_path, "r", encoding="utf-8") as fh:
                        lines = [
                            ln.strip()
                            for ln in fh
                            if ln.strip() and not ln.strip().startswith("#")
                        ]
                except OSError as exc:
                    print(f"CMDS: read error: {exc}")
                    return None
                _print(
                    "CMDS: running "
                    + str(len(lines))
                    + " commands from "
                    + str(cmds_path)
                )
                for line in lines:
                    _print("> " + line)
                    buf3 = StringIO()
                    old3 = sys.stdout
                    sys.stdout = buf3
                    try:
                        instance.process_command(line)
                    finally:
                        sys.stdout = old3
                    out3 = buf3.getvalue().strip()
                    if out3:
                        _print(out3)

            # Optional save slot: --save <slot>
            if "--save" in sys.argv:
                try:
                    sidx = sys.argv.index("--save")
                    slot_s = sys.argv[sidx + 1] if sidx + 1 < len(sys.argv) else None
                    slot = int(slot_s) if slot_s is not None else 1
                except (ValueError, IndexError):
                    slot = 1
                buf4 = StringIO()
                old4 = sys.stdout
                sys.stdout = buf4
                try:
                    instance.save_game(slot)
                finally:
                    sys.stdout = old4
                out4 = buf4.getvalue().strip()
                _print(out4 if out4 else f"SAVE: slot {slot}")

            # Optional load saved slot: --load-slot <slot>
            if "--load-slot" in sys.argv:
                try:
                    lsidx = sys.argv.index("--load-slot")
                    slot_s = sys.argv[lsidx + 1] if lsidx + 1 < len(sys.argv) else None
                    slot = int(slot_s) if slot_s is not None else 1
                except (ValueError, IndexError):
                    slot = 1
                buf5 = StringIO()
                old5 = sys.stdout
                sys.stdout = buf5
                try:
                    instance.load_game(slot)
                    instance.look()
                finally:
                    sys.stdout = old5
                out5 = buf5.getvalue().strip()
                _print(out5 if out5 else f"LOAD-SLOT: {slot}")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"LOAD: error: {exc}")
        return None

    # Normal GUI run
    root = tk.Tk()
    app = SagaCraftPlayer(root)
    root.mainloop()
    return app


if __name__ == "__main__":
    main()
