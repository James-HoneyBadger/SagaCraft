#!/usr/bin/env python3
"""SagaCraft Player - lightweight play-only client.

A minimal Tk interface focused solely on loading and playing SagaCraft
adventures. Supports theme + font selection and save/load slots.
"""

from __future__ import annotations

import json
import sys
import importlib.util
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "engine.json"
ENGINE_PATH = Path(__file__).resolve().parents[3] / "sagacraft_engine.py"
ADVENTURES_DIR = Path(__file__).resolve().parents[3] / "adventures"


@dataclass
class UISettings:
    """User-facing UI preferences."""

    theme: str = "Dark"
    font_family: str = "Segoe UI"
    font_size: int = 10


class SagaCraftPlayer:
    """Lightweight play-only SagaCraft client."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("SagaCraft Player")
        self.root.geometry("960x760")

        # Theme palette (shared with IDE)
        self.themes = {
            "Dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "accent": "#4a90e2",
                "accent_dark": "#357abd",
                "success": "#5cb85c",
                "warning": "#f0ad4e",
                "danger": "#d9534f",
                "sidebar": "#3c3c3c",
                "panel": "#353535",
                "border": "#4a4a4a",
                "text_bg": "#252525",
                "button": "#4a90e2",
                "button_hover": "#357abd",
            },
            "Light": {
                "bg": "#f5f5f5",
                "fg": "#333333",
                "accent": "#4a90e2",
                "accent_dark": "#357abd",
                "success": "#5cb85c",
                "warning": "#f0ad4e",
                "danger": "#d9534f",
                "sidebar": "#e0e0e0",
                "panel": "#ffffff",
                "border": "#cccccc",
                "text_bg": "#ffffff",
                "button": "#4a90e2",
                "button_hover": "#357abd",
            },
            "Dracula": {
                "bg": "#282a36",
                "fg": "#f8f8f2",
                "accent": "#bd93f9",
                "accent_dark": "#9d73d9",
                "success": "#50fa7b",
                "warning": "#f1fa8c",
                "danger": "#ff5555",
                "sidebar": "#1e1f28",
                "panel": "#44475a",
                "border": "#6272a4",
                "text_bg": "#1e1f28",
                "button": "#bd93f9",
                "button_hover": "#9d73d9",
            },
            "Nord": {
                "bg": "#2e3440",
                "fg": "#eceff4",
                "accent": "#88c0d0",
                "accent_dark": "#5e81ac",
                "success": "#a3be8c",
                "warning": "#ebcb8b",
                "danger": "#bf616a",
                "sidebar": "#3b4252",
                "panel": "#434c5e",
                "border": "#4c566a",
                "text_bg": "#2e3440",
                "button": "#88c0d0",
                "button_hover": "#5e81ac",
            },
            "Monokai": {
                "bg": "#272822",
                "fg": "#f8f8f2",
                "accent": "#66d9ef",
                "accent_dark": "#46b9cf",
                "success": "#a6e22e",
                "warning": "#e6db74",
                "danger": "#f92672",
                "sidebar": "#1e1f1c",
                "panel": "#3e3d32",
                "border": "#75715e",
                "text_bg": "#1e1f1c",
                "button": "#66d9ef",
                "button_hover": "#46b9cf",
            },
        }

        self.settings = UISettings()
        self._load_ui_preferences()

        self.current_theme = self.settings.theme if self.settings.theme in self.themes else "Dark"
        self.colors = self.themes[self.current_theme]
        self.current_font_family = self.settings.font_family
        self.current_font_size = self.settings.font_size

        self.game_instance = None
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
        menubar = tk.Menu(self.root, bg=self.colors["panel"], fg=self.colors["fg"], activebackground=self.colors["accent"])

        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["panel"], fg=self.colors["fg"], activebackground=self.colors["accent"])
        file_menu.add_command(label="Open Adventure...", command=self.open_adventure)
        file_menu.add_separator()
        file_menu.add_command(label="Save Game (slot 1)", command=lambda: self.save_game(1))
        file_menu.add_command(label="Load Game (slot 1)", command=lambda: self.load_game(1))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        options_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["panel"], fg=self.colors["fg"], activebackground=self.colors["accent"])
        theme_menu = tk.Menu(options_menu, tearoff=0, bg=self.colors["panel"], fg=self.colors["fg"], activebackground=self.colors["accent"])
        for theme_name in self.themes:
            theme_menu.add_command(label=theme_name, command=lambda t=theme_name: self.change_theme(t))
        options_menu.add_cascade(label="Theme", menu=theme_menu)

        font_menu = tk.Menu(options_menu, tearoff=0, bg=self.colors["panel"], fg=self.colors["fg"], activebackground=self.colors["accent"])
        for family in ["Segoe UI", "Arial", "Helvetica", "Verdana", "Tahoma", "Calibri"]:
            font_menu.add_command(label=family, command=lambda f=family: self.change_font_family(f))
        font_size_menu = tk.Menu(font_menu, tearoff=0, bg=self.colors["panel"], fg=self.colors["fg"], activebackground=self.colors["accent"])
        for size in [9, 10, 11, 12, 14, 16]:
            font_size_menu.add_command(label=f"{size}pt", command=lambda s=size: self.change_font_size(s))
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
        theme_box = ttk.Combobox(top, textvariable=self.theme_var, values=list(self.themes.keys()), state="readonly", width=12)
        theme_box.bind("<<ComboboxSelected>>", lambda _e: self.change_theme(self.theme_var.get()))
        theme_box.pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Font:").pack(side=tk.LEFT, padx=(12, 4))
        self.font_var = tk.StringVar(value=self.current_font_family)
        font_box = ttk.Combobox(top, textvariable=self.font_var, values=["Segoe UI", "Arial", "Helvetica", "Verdana", "Tahoma", "Calibri"], state="readonly", width=12)
        font_box.bind("<<ComboboxSelected>>", lambda _e: self.change_font_family(self.font_var.get()))
        font_box.pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Size:").pack(side=tk.LEFT, padx=(12, 4))
        self.size_var = tk.IntVar(value=self.current_font_size)
        size_spin = ttk.Spinbox(top, from_=8, to=18, textvariable=self.size_var, width=4, command=lambda: self.change_font_size(self.size_var.get()))
        size_spin.pack(side=tk.LEFT)

        action_row = ttk.Frame(self.root)
        action_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(action_row, text="Open Adventure", command=self.open_adventure).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Save Slot 1", command=lambda: self.save_game(1)).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_row, text="Load Slot 1", command=lambda: self.load_game(1)).pack(side=tk.LEFT, padx=6)

        console_frame = ttk.Frame(self.root)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.game_output = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=24, state=tk.DISABLED)
        self.game_output.pack(fill=tk.BOTH, expand=True)

        entry_row = ttk.Frame(self.root)
        entry_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.command_var = tk.StringVar()
        self.command_entry = ttk.Entry(entry_row, textvariable=self.command_var)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", lambda _e: self.run_command())

        ttk.Button(entry_row, text="Send", command=self.run_command).pack(side=tk.LEFT, padx=6)
        ttk.Button(entry_row, text="Look", command=lambda: self._process_command("look", echo=True)).pack(side=tk.LEFT)

        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Label(status_bar, textvariable=self.status_var).pack(side=tk.LEFT)

    def _apply_theme(self) -> None:
        self.root.configure(bg=self.colors["bg"])
        for widget in self.root.winfo_children():
            self._style_widget(widget)
        self._apply_fonts()

    def _style_widget(self, widget: tk.Widget) -> None:
        if isinstance(widget, (ttk.Frame, ttk.Label, ttk.Button, ttk.Combobox, ttk.Spinbox)):
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
        if not CONFIG_PATH.exists():
            return
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            ui = data.get("ui", {})
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
        except (OSError, json.JSONDecodeError):
            return

    def _save_ui_preferences(self) -> None:
        data = {}
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
            except (OSError, json.JSONDecodeError):
                data = {}
        data.setdefault("ui", {})
        data["ui"].update(
            {
                "theme": self.current_theme,
                "font_family": self.current_font_family,
                "font_size": self.current_font_size,
            }
        )
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
        except OSError:
            return

    # Adventure management --------------------------------------------------
    def open_adventure(self) -> None:
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
        self.game_instance = None
        self.game_loaded = False
        self.current_file = path

        engine_module = self._load_engine_module()
        if engine_module is None:
            self._set_status("Unable to load game engine.")
            return

        try:
            instance = engine_module.EnhancedAdventureGame(str(path))
            instance.load_adventure()
            self.game_instance = instance
        except Exception as exc:  # pragma: no cover - UI feedback
            self._set_status(f"Failed to load adventure: {exc}")
            return

        self._clear_output()
        self._print_header()
        self._set_status(f"Loaded: {path.name}")
        self.file_label.config(text=f"Adventure: {path.name}")
        self.game_loaded = True
        # Show starting room
        self._capture_output(self.game_instance.look)

    def _print_header(self) -> None:
        if not self.game_instance:
            return
        title = getattr(self.game_instance, "adventure_title", "Adventure")
        intro = getattr(self.game_instance, "adventure_intro", "")
        self._append(f"={'='*58}\n  {title.upper()}\n={'='*58}\n\n{intro}\n\n{'='*58}")

    def save_game(self, slot: int = 1) -> None:
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
        command = self.command_var.get().strip()
        if not command:
            return
        self.command_var.set("")
        self._process_command(command, echo=True)

    def _process_command(self, command: str, echo: bool = False) -> None:
        if not self.game_loaded or not self.game_instance:
            self._set_status("Load an adventure first.")
            return
        if echo:
            self._append(f"> {command}")
        if command.lower() in {"quit", "exit", "q"}:
            self._append("Thanks for playing!")
            self._set_status("Game ended")
            return
        error: Optional[Exception] = None
        output = ""
        old_stdout = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer
        try:
            self.game_instance.process_command(command)
        except (RuntimeError, ValueError, AttributeError, OSError) as exc:
            error = exc
        finally:
            output = buffer.getvalue()
            sys.stdout = old_stdout
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
        spec = importlib.util.spec_from_file_location("sagacraft_engine", ENGINE_PATH)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:  # pragma: no cover - UI feedback path
            return None
        return module

    def _capture_output(self, func, *args, **kwargs):
        old_stdout = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer
        try:
            result = func(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
        text = buffer.getvalue().strip()
        if text:
            self._append(text)
        return result

    def _append(self, text: str) -> None:
        self.game_output.configure(state=tk.NORMAL)
        self.game_output.insert(tk.END, text + "\n")
        self.game_output.see(tk.END)
        self.game_output.configure(state=tk.DISABLED)

    def _clear_output(self) -> None:
        self.game_output.configure(state=tk.NORMAL)
        self.game_output.delete("1.0", tk.END)
        self.game_output.configure(state=tk.DISABLED)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    # Theme + font changes --------------------------------------------------
    def change_theme(self, theme_name: str) -> None:
        if theme_name not in self.themes:
            return
        self.current_theme = theme_name
        self.colors = self.themes[theme_name]
        self.theme_var.set(theme_name)
        self._apply_theme()
        self._save_ui_preferences()
        self._set_status(f"Theme: {theme_name}")

    def change_font_family(self, family: str) -> None:
        self.current_font_family = family
        self.font_var.set(family)
        self._apply_fonts()
        self._save_ui_preferences()
        self._set_status(f"Font: {family}")

    def change_font_size(self, size: int) -> None:
        try:
            size_int = int(size)
        except (TypeError, ValueError):
            return
        self.current_font_size = max(8, min(24, size_int))
        self.size_var.set(self.current_font_size)
        self._apply_fonts()
        self._save_ui_preferences()
        self._set_status(f"Font size: {self.current_font_size}pt")


def main() -> None:
    # Headless check mode: initialize nothing, just verify engine loads
    if "--check" in sys.argv:
        try:
            spec = importlib.util.spec_from_file_location("sagacraft_engine", ENGINE_PATH)
            if spec is None or spec.loader is None:
                print("CHECK: engine spec load failed")
                return
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Basic sanity: required class exists
            ok = hasattr(module, "EnhancedAdventureGame") or hasattr(module, "ExtendedAdventureGame")
            print("CHECK: engine import OK" if ok else "CHECK: engine missing game class")
        except Exception as exc:
            print(f"CHECK: import error: {exc}")
        return

    # Headless load mode: load an adventure JSON and print intro + first look
    if "--load" in sys.argv:
        try:
            idx = sys.argv.index("--load")
            adventure_path = Path(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else None
        except (ValueError, IndexError):
            adventure_path = None
        if not adventure_path or not Path(adventure_path).exists():
            print("LOAD: missing or invalid path")
            return
        try:
            spec = importlib.util.spec_from_file_location("sagacraft_engine", ENGINE_PATH)
            if spec is None or spec.loader is None:
                print("LOAD: engine spec load failed")
                return
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            game_cls = getattr(module, "ExtendedAdventureGame", None) or getattr(module, "EnhancedAdventureGame", None)
            if game_cls is None:
                print("LOAD: engine game class missing")
                return
            # Optional seed for deterministic runs: --seed <int>
            seed = None
            if "--seed" in sys.argv:
                try:
                    sidx = sys.argv.index("--seed")
                    seed_s = sys.argv[sidx + 1] if sidx + 1 < len(sys.argv) else None
                    seed = int(seed_s) if seed_s is not None else None
                except (ValueError, IndexError):
                    seed = None
            instance = game_cls(str(adventure_path), seed=seed)
            instance.load_adventure()
            title = getattr(instance, "adventure_title", "Adventure")
            intro = getattr(instance, "adventure_intro", "")
            header = f"={'='*58}\n  {title.upper()}\n={'='*58}\n\n{intro}\n\n{'='*58}"
            transcript_out = None
            # Optional transcript file: --transcript <file>
            if "--transcript" in sys.argv:
                try:
                    tidx = sys.argv.index("--transcript")
                    transcript_out = Path(sys.argv[tidx + 1]) if tidx + 1 < len(sys.argv) else None
                except (ValueError, IndexError):
                    transcript_out = None
            def _print(text: str):
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
                    return
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
                    return
                try:
                    with open(cmds_path, "r", encoding="utf-8") as fh:
                        lines = [ln.strip() for ln in fh if ln.strip() and not ln.strip().startswith("#")]
                except OSError as exc:
                    print(f"CMDS: read error: {exc}")
                    return
                _print("CMDS: running " + str(len(lines)) + " commands from " + str(cmds_path))
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
        except Exception as exc:
            print(f"LOAD: error: {exc}")
        return

    # Normal GUI run
    root = tk.Tk()
    app = SagaCraftPlayer(root)
    root.mainloop()
    return app


if __name__ == "__main__":
    main()
