#!/usr/bin/env python3
"""SagaCraft - Graphical Adventure Editor

A complete IDE for creating, editing, and playing text adventures.
"""

# pylint: disable=too-many-lines,too-many-instance-attributes,too-many-public-methods
# pylint: disable=attribute-defined-outside-init

import ast
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import difflib
import json
import os
import random
import sys
import importlib.util
from functools import partial
from collections import deque
from pathlib import Path
from io import StringIO
import traceback
from typing import Any, Callable, cast

from sagacraft.ui.config_io import (
    safe_read_json_mapping,
    update_ui_preferences,
    write_json_mapping,
)
from sagacraft.ui.engine_runner import capture_stdout, run_engine_command
from sagacraft.ui.menu_helpers import (
    add_font_family_commands,
    add_font_size_commands,
    create_styled_menu,
)
from sagacraft.ui.theme import get_default_themes


class AdventureIDE:
    """Main IDE window for SagaCraft"""

    def quit_ide(self):
        """Exit the IDE application."""
        if getattr(self, "modified", False) and not messagebox.askyesno(
            "Unsaved Changes", "You have unsaved changes. Quit anyway?"
        ):
            return
        self.root.quit()

    def __init__(self, root):
        self.root = root
        self.root.title("🎮 SagaCraft - IDE")
        self.root.geometry("1400x900")

        # Theme definitions
        self.themes = get_default_themes()

        self._init_default_theme_and_fonts()
        self._load_ui_preferences()
        self.setup_styles()

        self._init_empty_adventure()
        self._init_file_state()
        self._init_recent_and_play_state()
        self._init_modding_state()
        self._init_widget_refs()

        self._ensure_mod_root()
        self._load_mod_state()
        self.setup_ui()
        self.new_adventure()

    def _init_default_theme_and_fonts(self):
        self.current_theme = "Dark"
        self.colors = self.themes[self.current_theme]
        self.current_font_family = "Segoe UI"
        self.current_font_size = 10
        self.editor_font_family = "Consolas"
        self.editor_font_size = 11

    def _init_empty_adventure(self):
        self.adventure = {
            "title": "New Adventure",
            "author": "",
            "intro": "",
            "start_room": 1,
            "rooms": [],
            "items": [],
            "monsters": [],
            "effects": [],
        }

    def _init_file_state(self):
        self.current_file = None
        self.modified = False

    def _init_recent_and_play_state(self):
        self.recent_files = self._load_recent_files()
        self.recent_list_container = None
        self.validation_badge_var = tk.StringVar(value="Validation: —")
        self.test_badge_var = tk.StringVar(value="Play: Idle")
        self.demo_scripts = self._default_demo_scripts()
        self.demo_script_var = tk.StringVar()
        self.game_instance = None
        self.game_running = False
        self.point_and_click = None

    def _init_modding_state(self):
        self.mod_root = Path("mods")
        self.mod_state_path = Path("config/modding_state.json")
        self.mod_catalog = []
        self.enabled_mods = set()
        self.mod_cache = {}
        self.mod_tree = None
        self.mod_detail_text = None
        self.mod_console = None
        self.mod_output_history = []
        self.mod_toggle_button = None
        self.mod_view_button = None

    def _init_widget_refs(self):  # pylint: disable=too-many-statements
        self.notebook = None
        self.status_bar = None
        self.game_output = None
        self.command_entry = None
        self.play_tab = None
        self.preview_text = None
        self.title_var = None
        self.author_var = None
        self.start_room_var = None
        self.intro_text = None
        self.rooms_listbox = None
        self.room_id_var = None
        self.room_name_var = None
        self.room_desc = None
        self.exit_vars = {}
        self.items_listbox = None
        self.item_id_var = None
        self.item_name_var = None
        self.item_desc = None
        self.item_weight_var = None
        self.item_value_var = None
        self.item_location_var = None
        self.item_is_weapon_var = None
        self.item_is_takeable_var = None
        self.monsters_listbox = None
        self.monster_id_var = None
        self.monster_name_var = None
        self.monster_desc = None
        self.monster_room_var = None
        self.monster_hardiness_var = None
        self.monster_agility_var = None
        self.monster_friendliness_var = None
        self.monster_gold_var = None
        self.game_mode_var = None
        self.scene_id_var = None
        self.scene_name_var = None
        self.scene_room_var = None
        self.scene_background_var = None
        self.scene_music_var = None
        self.scene_grid_visible_var = None
        self.scene_grid_size_var = None
        self.scene_narration_text = None
        self.hotspots_listbox = None
        self.hotspot_id_var = None
        self.hotspot_label_var = None
        self.hotspot_shape_var = None
        self.hotspot_x_var = None
        self.hotspot_y_var = None
        self.hotspot_width_var = None
        self.hotspot_height_var = None
        self.hotspot_action_var = None
        self.hotspot_value_var = None
        self.hotspot_tooltip_var = None
        self._suppress_mode_change = False

    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use("clam")  # Use clam as base for customization

        # Configure colors
        self.root.configure(bg=self.colors["bg"])

        # Notebook (tabs)
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=self.colors["sidebar"],
            foreground=self.colors["fg"],
            padding=[20, 10],
            font=(self.current_font_family, self.current_font_size, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.colors["accent"])],
            foreground=[("selected", "#ffffff")],
        )

        # Frames
        style.configure("TFrame", background=self.colors["bg"])
        style.configure(
            "Panel.TFrame",
            background=self.colors["panel"],
            relief="flat",
            borderwidth=1,
        )

        # Labels
        style.configure(
            "TLabel",
            background=self.colors["bg"],
            foreground=self.colors["fg"],
            font=(self.current_font_family, self.current_font_size),
        )
        style.configure(
            "Title.TLabel",
            font=(self.current_font_family, self.current_font_size + 4, "bold"),
            foreground=self.colors["accent"],
        )
        style.configure(
            "Subtitle.TLabel",
            font=(self.current_font_family, self.current_font_size + 1, "bold"),
            foreground=self.colors["fg"],
        )

        # Buttons
        style.configure(
            "TButton",
            background=self.colors["button"],
            foreground="#ffffff",
            borderwidth=0,
            padding=[15, 8],
            font=(self.current_font_family, self.current_font_size, "bold"),
        )
        style.map(
            "TButton",
            background=[
                ("active", self.colors["button_hover"]),
                ("pressed", self.colors["accent_dark"]),
            ],
        )

        # Success button
        style.configure(
            "Success.TButton", background=self.colors["success"], foreground="#ffffff"
        )
        style.map("Success.TButton", background=[("active", "#4cae4c")])

        # Warning button
        style.configure(
            "Warning.TButton", background=self.colors["warning"], foreground="#ffffff"
        )

        # Danger button
        style.configure(
            "Danger.TButton", background=self.colors["danger"], foreground="#ffffff"
        )

        # Entry widgets
        style.configure(
            "TEntry",
            fieldbackground=self.colors["text_bg"],
            foreground=self.colors["fg"],
            borderwidth=1,
            relief="flat",
        )

        # Spinbox
        style.configure(
            "TSpinbox",
            fieldbackground=self.colors["text_bg"],
            foreground=self.colors["fg"],
            arrowcolor=self.colors["fg"],
        )

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=self.colors["text_bg"],
            foreground=self.colors["fg"],
            arrowcolor=self.colors["fg"],
        )

    def setup_ui(self):
        """Create the main UI"""
        menubar = self._create_menubar()
        self._add_file_menu(menubar)
        self._add_tools_menu(menubar)
        self._add_view_menu(menubar)
        self._add_help_menu(menubar)
        self._bind_ide_shortcuts()

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(
            row=0, column=0, sticky="nsew", pady=(0, 10)
        )
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create tabs - Play tab first for easy access
        # Ensure self.notebook is initialized before creating tabs
        self.create_play_tab()
        self.create_info_tab()
        self.create_rooms_tab()
        self.create_items_tab()
        self.create_monsters_tab()
        self.create_modding_tab()
        self.create_preview_tab()

        # Status bar with color
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, sticky="we")
        self.status_bar = tk.Label(
            status_frame,
            text="✓ Ready",
            relief=tk.FLAT,
            bg=self.colors["sidebar"],
            fg=self.colors["success"],
            font=("Segoe UI", 10),
            anchor=tk.W,
            padx=10,
            pady=5,
        )
        self.status_bar.pack(fill=tk.BOTH, expand=True)

    def _create_menubar(self) -> tk.Menu:
        menubar = tk.Menu(
            self.root,
            bg=self.colors["sidebar"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        self.root.config(menu=menubar)
        return menubar

    def _add_file_menu(self, menubar: tk.Menu):
        file_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(
            label="🆕 New Adventure",
            command=self.new_adventure,
            accelerator="Ctrl+N",
        )
        file_menu.add_command(
            label="📂 Open...",
            command=self.open_adventure,
            accelerator="Ctrl+O",
        )
        file_menu.add_command(
            label="💾 Save",
            command=self.save_adventure,
            accelerator="Ctrl+S",
        )
        file_menu.add_command(label="💾 Save As...", command=self.save_adventure_as)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.quit_ide)

    def _add_tools_menu(self, menubar: tk.Menu):
        tools_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="🛠️ Tools", menu=tools_menu)
        tools_menu.add_command(
            label="▶️ Test Adventure",
            command=self.test_adventure,
            accelerator="F5",
        )
        tools_menu.add_command(label="✓ Validate Adventure", command=self.validate_adventure)
        tools_menu.add_command(label="🔎 Verify Game (Detailed)", command=self.verify_game)
        tools_menu.add_command(label="🖥️ Play in IDE", command=self.play_in_ide_console)
        tools_menu.add_command(
            label="🧭 Command Palette…",
            command=self.open_command_palette,
            accelerator="Ctrl+Shift+P",
        )
        tools_menu.add_command(label="🔧 Auto-Fix Common Issues", command=self.auto_fix_game)
        tools_menu.add_separator()
        tools_menu.add_command(
            label="📋 Strict Schema Validation",
            command=self.strict_schema_validation,
        )
        tools_menu.add_separator()
        tools_menu.add_command(label="📊 Graph Analytics", command=self.show_graph_analytics)
        tools_menu.add_command(label="🖼️ Asset Browser", command=self.show_asset_browser)
        tools_menu.add_command(label="📦 Mod Sandbox", command=self.show_mod_sandbox)
        tools_menu.add_command(label="📝 Snippets & Templates", command=self.show_snippets_menu)

    def _add_view_menu(self, menubar: tk.Menu):
        view_menu = create_styled_menu(menubar, self.colors, tearoff=0)
        menubar.add_cascade(label="👁️ View", menu=view_menu)

        theme_menu = create_styled_menu(view_menu, self.colors, tearoff=0)
        view_menu.add_cascade(label="🎨 Theme", menu=theme_menu)
        for theme_name in self.themes:
            theme_menu.add_command(
                label=theme_name,
                command=cast(
                    Callable[[], Any],
                    partial(self.change_theme, theme_name),
                ),
            )

        font_menu = create_styled_menu(view_menu, self.colors, tearoff=0)
        view_menu.add_cascade(label="🔤 Font", menu=font_menu)

        self._add_font_family_menu(font_menu)
        self._add_font_size_menu(font_menu)
        self._add_editor_font_menu(font_menu)

        view_menu.add_separator()
        view_menu.add_command(label="↺ Reset to Defaults", command=self.reset_view_settings)

    def _add_font_family_menu(self, font_menu: tk.Menu):
        font_family_menu = create_styled_menu(font_menu, self.colors, tearoff=0)
        font_menu.add_cascade(label="Font Family", menu=font_family_menu)
        add_font_family_commands(font_family_menu, self.change_font_family)

    def _add_font_size_menu(self, font_menu: tk.Menu):
        font_size_menu = create_styled_menu(font_menu, self.colors, tearoff=0)
        font_menu.add_cascade(label="Font Size", menu=font_size_menu)
        add_font_size_commands(
            font_size_menu,
            self.change_font_size,
            sizes=[8, 9, 10, 11, 12, 14, 16],
        )

    def _add_editor_font_menu(self, font_menu: tk.Menu):
        editor_font_menu = create_styled_menu(font_menu, self.colors, tearoff=0)
        font_menu.add_cascade(label="Editor Font", menu=editor_font_menu)
        for family in [
            "Consolas",
            "Courier New",
            "Monaco",
            "Menlo",
            "Source Code Pro",
            "Fira Code",
        ]:
            editor_font_menu.add_command(
                label=family,
                command=cast(
                    Callable[[], Any],
                    partial(self.change_editor_font, family),
                ),
            )

    def _add_help_menu(self, menubar: tk.Menu):
        help_menu = create_styled_menu(menubar, self.colors, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="📖 Quick Start Guide", command=self.show_help)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)

    def _bind_ide_shortcuts(self):
        def _on_palette(_e: Any) -> None:
            self.open_command_palette()

        def _on_test(_e: Any) -> None:
            self.test_adventure()

        def _on_verify(_e: Any) -> None:
            self.verify_game()

        def _on_autofix(_e: Any) -> None:
            self.auto_fix_game()

        def _on_strict_validate(_e: Any) -> None:
            self.strict_schema_validation()

        def _on_new(_e: Any) -> None:
            self.new_adventure()

        def _on_open(_e: Any) -> None:
            self.open_adventure()

        def _on_save(_e: Any) -> None:
            self.save_adventure()

        self.root.bind_all("<Control-Shift-Key-P>", _on_palette)
        self.root.bind_all("<F5>", _on_test)
        self.root.bind_all("<Control-Shift-Key-V>", _on_verify)
        self.root.bind_all("<Control-Shift-Key-F>", _on_autofix)
        self.root.bind_all("<Control-Shift-Key-S>", _on_strict_validate)

        self.root.bind("<Control-n>", _on_new)
        self.root.bind("<Control-o>", _on_open)
        self.root.bind("<Control-s>", _on_save)
        self.root.bind("<F5>", _on_test)

    def create_info_tab(self):
        """Adventure info tab with modern design"""
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="📋 Info")

        # Header
        header = ttk.Label(frame, text="Adventure Information", style="Title.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        # Create a styled container for form fields
        form_frame = ttk.Frame(frame, style="Panel.TFrame", padding="20")
        form_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # Title with icon
        row = 0
        ttk.Label(form_frame, text="🎮 Adventure Title:", style="Subtitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(
            form_frame, textvariable=self.title_var, width=60, font=("Segoe UI", 11)
        )
        title_entry.grid(row=row + 1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Author
        row += 2
        ttk.Label(form_frame, text="👤 Author:", style="Subtitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.author_var = tk.StringVar()
        author_entry = ttk.Entry(
            form_frame, textvariable=self.author_var, width=60, font=("Segoe UI", 11)
        )
        author_entry.grid(row=row + 1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Start room
        row += 2
        ttk.Label(form_frame, text="🚪 Starting Room:", style="Subtitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.start_room_var = tk.IntVar(value=1)
        room_spin = ttk.Spinbox(
            form_frame,
            from_=1,
            to=999,
            textvariable=self.start_room_var,
            width=15,
            font=("Segoe UI", 11),
        )
        room_spin.grid(row=row + 1, column=0, sticky=tk.W, pady=(0, 15))

        # Experience mode (SagaCraft is text-only)
        row += 2
        ttk.Label(
            form_frame,
            text="🕹️ Experience Mode:",
            style="Subtitle.TLabel",
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(
            form_frame,
            text="Text adventure (parser-driven)",
            style="Body.TLabel",
        ).grid(row=row + 1, column=0, sticky=tk.W, pady=(0, 15))
        self.game_mode_var = None

        # Introduction
        row += 2
        ttk.Label(
            form_frame, text="📖 Introduction Text:", style="Subtitle.TLabel"
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))

        # Styled text widget
        text_frame = tk.Frame(
            form_frame, bg=self.colors["text_bg"], relief=tk.FLAT, bd=1
        )
        text_frame.grid(
            row=row + 1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20)
        )
        form_frame.rowconfigure(row + 1, weight=1)
        self.intro_text = scrolledtext.ScrolledText(
            text_frame,
            width=70,
            height=12,
            wrap=tk.WORD,
            bg=self.colors["text_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            font=("Consolas", 10),
            relief=tk.FLAT,
            bd=5,
        )
        self.intro_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_rooms_tab(self):
        """Rooms editor tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🏠 Rooms")

        # Left panel - room list
        left_panel = ttk.Frame(frame)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=5)

        ttk.Label(left_panel, text="Rooms:").pack()

        self.rooms_listbox = tk.Listbox(left_panel, width=30, height=25)
        self.rooms_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.rooms_listbox.bind("<<ListboxSelect>>", self.select_room)

        scrollbar = ttk.Scrollbar(
            left_panel, orient=tk.VERTICAL, command=self.rooms_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rooms_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Room", command=self.add_room).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Delete", command=self.delete_room).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Map", command=self.show_reachability_map).pack(
            side=tk.LEFT, padx=2
        )

        # Right panel - room editor
        right_panel = ttk.Frame(frame)
        right_panel.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        frame.columnconfigure(1, weight=1)

        # Room ID
        ttk.Label(right_panel, text="Room ID:").grid(row=0, column=0, sticky=tk.W)
        self.room_id_var = tk.IntVar()
        ttk.Label(right_panel, textvariable=self.room_id_var).grid(
            row=0, column=1, sticky=tk.W
        )

        # Room name
        ttk.Label(right_panel, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.room_name_var = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.room_name_var, width=40).grid(
            row=1, column=1, pady=5
        )

        # Description
        ttk.Label(right_panel, text="Description:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.room_desc = scrolledtext.ScrolledText(
            right_panel, width=50, height=8, wrap=tk.WORD
        )
        self.room_desc.grid(row=3, column=0, columnspan=2, pady=5)

        # Exits
        ttk.Label(right_panel, text="Exits:").grid(row=4, column=0, sticky=tk.W, pady=5)

        exits_frame = ttk.Frame(right_panel)
        exits_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W)

        self.exit_vars = {}
        directions = [
            ("North", "north"),
            ("South", "south"),
            ("East", "east"),
            ("West", "west"),
            ("Up", "up"),
            ("Down", "down"),
        ]

        for i, (label, key) in enumerate(directions):
            row = i // 3
            col = (i % 3) * 2
            ttk.Label(exits_frame, text=f"{label}:").grid(
                row=row, column=col, sticky=tk.W, padx=5
            )
            var = tk.IntVar(value=0)
            ttk.Spinbox(exits_frame, from_=0, to=999, textvariable=var, width=8).grid(
                row=row, column=col + 1, padx=5
            )
            self.exit_vars[key] = var

        # Update button
        ttk.Button(right_panel, text="Update Room", command=self.update_room).grid(
            row=6, column=1, sticky=tk.E, pady=10
        )

    def create_items_tab(self):  # pylint: disable=too-many-statements
        """Items editor tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="⚔️ Items")

        # Left panel - item list
        left_panel = ttk.Frame(frame)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=5)

        ttk.Label(left_panel, text="Items:").pack()

        self.items_listbox = tk.Listbox(left_panel, width=30, height=25)
        self.items_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.items_listbox.bind("<<ListboxSelect>>", self.select_item)

        scrollbar = ttk.Scrollbar(
            left_panel, orient=tk.VERTICAL, command=self.items_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.items_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Item", command=self.add_item).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Delete", command=self.delete_item).pack(
            side=tk.LEFT, padx=2
        )

        # Right panel - item editor
        right_panel = ttk.Frame(frame)
        right_panel.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        frame.columnconfigure(1, weight=1)

        # Item properties
        row = 0
        ttk.Label(right_panel, text="Item ID:").grid(row=row, column=0, sticky=tk.W)
        self.item_id_var = tk.IntVar()
        ttk.Label(right_panel, textvariable=self.item_id_var).grid(
            row=row, column=1, sticky=tk.W
        )

        row += 1
        ttk.Label(right_panel, text="Name:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_name_var = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.item_name_var, width=40).grid(
            row=row, column=1, pady=3
        )

        row += 1
        ttk.Label(right_panel, text="Description:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_desc = scrolledtext.ScrolledText(
            right_panel, width=40, height=4, wrap=tk.WORD
        )
        self.item_desc.grid(row=row + 1, column=0, columnspan=2, pady=3)

        row += 2
        ttk.Label(right_panel, text="Weight:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_weight_var = tk.IntVar(value=1)
        ttk.Spinbox(
            right_panel, from_=0, to=1000, textvariable=self.item_weight_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Value:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_value_var = tk.IntVar(value=0)
        ttk.Spinbox(
            right_panel, from_=0, to=10000, textvariable=self.item_value_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Location (Room):").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_location_var = tk.IntVar(value=1)
        ttk.Spinbox(
            right_panel, from_=0, to=999, textvariable=self.item_location_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        self.item_is_weapon_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            right_panel, text="Is Weapon", variable=self.item_is_weapon_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=3)

        row += 1
        self.item_is_takeable_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            right_panel, text="Can Be Taken", variable=self.item_is_takeable_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=3)

        row += 1
        ttk.Button(right_panel, text="Update Item", command=self.update_item).grid(
            row=row, column=1, sticky=tk.E, pady=10
        )

    def create_monsters_tab(self):  # pylint: disable=too-many-statements
        """Monsters editor tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="👾 Monsters")

        # Left panel - monster list
        left_panel = ttk.Frame(frame)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=5)

        ttk.Label(left_panel, text="Monsters/NPCs:").pack()

        self.monsters_listbox = tk.Listbox(left_panel, width=30, height=25)
        self.monsters_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.monsters_listbox.bind("<<ListboxSelect>>", self.select_monster)

        scrollbar = ttk.Scrollbar(
            left_panel, orient=tk.VERTICAL, command=self.monsters_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.monsters_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Monster", command=self.add_monster).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Delete", command=self.delete_monster).pack(
            side=tk.LEFT, padx=2
        )

        # Right panel - monster editor
        right_panel = ttk.Frame(frame)
        right_panel.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        frame.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(right_panel, text="Monster ID:").grid(row=row, column=0, sticky=tk.W)
        self.monster_id_var = tk.IntVar()
        ttk.Label(right_panel, textvariable=self.monster_id_var).grid(
            row=row, column=1, sticky=tk.W
        )

        row += 1
        ttk.Label(right_panel, text="Name:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_name_var = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.monster_name_var, width=40).grid(
            row=row, column=1, pady=3
        )

        row += 1
        ttk.Label(right_panel, text="Description:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_desc = scrolledtext.ScrolledText(
            right_panel, width=40, height=4, wrap=tk.WORD
        )
        self.monster_desc.grid(row=row + 1, column=0, columnspan=2, pady=3)

        row += 2
        ttk.Label(right_panel, text="Room:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_room_var = tk.IntVar(value=1)
        ttk.Spinbox(
            right_panel, from_=1, to=999, textvariable=self.monster_room_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Hardiness (HP):").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_hardiness_var = tk.IntVar(value=10)
        ttk.Spinbox(
            right_panel,
            from_=1,
            to=100,
            textvariable=self.monster_hardiness_var,
            width=10,
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Agility:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_agility_var = tk.IntVar(value=10)
        ttk.Spinbox(
            right_panel, from_=1, to=30, textvariable=self.monster_agility_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Friendliness:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_friendliness_var = tk.StringVar(value="hostile")
        ttk.Combobox(
            right_panel,
            textvariable=self.monster_friendliness_var,
            values=["friendly", "neutral", "hostile"],
            width=15,
            state="readonly",
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Gold:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_gold_var = tk.IntVar(value=0)
        ttk.Spinbox(
            right_panel, from_=0, to=1000, textvariable=self.monster_gold_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Button(
            right_panel, text="Update Monster", command=self.update_monster
        ).grid(row=row, column=1, sticky=tk.E, pady=10)

    def create_modding_tab(self):
        """Modding management tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🧩 Mods")

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        header = ttk.Label(frame, text="Mod Browser", style="Title.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        description = ttk.Label(
            frame,
            text=(
                "Enable and inspect gameplay mods without leaving the IDE. "
                "Mods are loaded when you start a play session."
            ),
        )
        description.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Mod list
        list_frame = ttk.Frame(frame, style="Panel.TFrame", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.N, tk.S), padx=(0, 10))
        list_frame.rowconfigure(1, weight=1)

        ttk.Label(list_frame, text="Available Mods", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W
        )

        tree_container = ttk.Frame(list_frame)
        tree_container.grid(row=1, column=0, sticky=(tk.N, tk.S))

        columns = ("status", "name", "version")
        self.mod_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=20,
            selectmode="browse",
        )
        self.mod_tree.heading("status", text="Status")
        self.mod_tree.heading("name", text="Mod")
        self.mod_tree.heading("version", text="Version")
        self.mod_tree.column("status", width=90, anchor=tk.W)
        self.mod_tree.column("name", width=220, anchor=tk.W)
        self.mod_tree.column("version", width=80, anchor=tk.W)
        self.mod_tree.bind("<<TreeviewSelect>>", self._on_mod_select)
        self.mod_tree.grid(row=0, column=0, sticky=(tk.N, tk.S))

        scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL, command=self.mod_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.mod_tree.configure(yscrollcommand=scrollbar.set)

        button_bar = ttk.Frame(list_frame)
        button_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        self.mod_toggle_button = ttk.Button(
            button_bar, text="Enable Mod", command=self._toggle_selected_mod
        )
        self.mod_toggle_button.grid(row=0, column=0, sticky=tk.W, padx=(0, 6))
        self.mod_view_button = ttk.Button(
            button_bar, text="View Script", command=self._view_selected_mod
        )
        self.mod_view_button.grid(row=0, column=1, sticky=tk.W, padx=(0, 6))
        ttk.Button(
            button_bar,
            text="Reload List",
            command=self.refresh_mod_catalog_ui,
        ).grid(row=0, column=2, sticky=tk.W)

        # Details panel
        detail_frame = ttk.Frame(frame, style="Panel.TFrame", padding="10")
        detail_frame.grid(row=2, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(1, weight=1)
        detail_frame.rowconfigure(3, weight=1)

        ttk.Label(detail_frame, text="Mod Details", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W
        )

        self.mod_detail_text = scrolledtext.ScrolledText(
            detail_frame,
            height=12,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.colors["text_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief=tk.FLAT,
            bd=5,
        )
        self.mod_detail_text.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        ttk.Label(
            detail_frame, text="Recent Mod Activity", style="Subtitle.TLabel"
        ).grid(row=2, column=0, sticky=tk.W, pady=(10, 0))

        self.mod_console = scrolledtext.ScrolledText(
            detail_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.colors["text_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief=tk.FLAT,
            bd=5,
        )
        self.mod_console.grid(row=3, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.refresh_mod_catalog_ui()
        self._populate_mod_console()
        self._update_mod_action_state()

    def refresh_mod_catalog_ui(self):
        """Refresh the UI list of discovered mods."""
        self.mod_catalog = self._discover_mods()

        if not self.mod_tree:
            return

        current_selection = None
        if self.mod_tree.selection():
            current_selection = self.mod_tree.selection()[0]

        for item in self.mod_tree.get_children():
            self.mod_tree.delete(item)

        self.mod_tree.tag_configure("enabled", foreground=self.colors["success"])
        self.mod_tree.tag_configure("disabled", foreground=self.colors["fg"])

        for mod in self.mod_catalog:
            status = "Enabled" if mod["enabled"] else "Disabled"
            version = mod.get("version", "—") or "—"
            tag = "enabled" if mod["enabled"] else "disabled"
            self.mod_tree.insert(
                "",
                tk.END,
                iid=mod["relative"],
                values=(status, mod["name"], version),
                tags=(tag,),
            )

        selection_target = None
        if current_selection and self.mod_tree.exists(current_selection):
            selection_target = current_selection
        elif self.mod_catalog:
            enabled_mod = next((m for m in self.mod_catalog if m["enabled"]), None)
            selection_target = (
                enabled_mod["relative"]
                if enabled_mod
                else self.mod_catalog[0]["relative"]
            )

        if selection_target:
            self.mod_tree.selection_set(selection_target)
            self.mod_tree.focus(selection_target)
            self._display_mod_details(selection_target)
        else:
            self._clear_mod_detail()

        self._update_mod_action_state()

    def _populate_mod_console(self):
        if not self.mod_console:
            return
        self.mod_console.config(state=tk.NORMAL)
        self.mod_console.delete("1.0", tk.END)
        for line in self.mod_output_history:
            self.mod_console.insert(tk.END, line + "\n")
        self.mod_console.config(state=tk.DISABLED)

    def _update_mod_action_state(self):
        has_selection = bool(self.mod_tree and self.mod_tree.selection())
        state = tk.NORMAL if has_selection else tk.DISABLED
        if self.mod_toggle_button:
            self.mod_toggle_button.config(state=state)
        if self.mod_view_button:
            self.mod_view_button.config(state=state)

        if has_selection:
            mod = self._get_selected_mod()
            if mod:
                label = "Disable Mod" if mod["enabled"] else "Enable Mod"
                self.mod_toggle_button.config(text=label)

    def _on_mod_select(self, _event=None):
        if not self.mod_tree or not self.mod_tree.selection():
            self._clear_mod_detail()
            self._update_mod_action_state()
            return
        mod_id = self.mod_tree.selection()[0]
        self._display_mod_details(mod_id)
        self._update_mod_action_state()

    def _toggle_selected_mod(self):
        mod = self._get_selected_mod()
        if not mod:
            return
        self._set_mod_enabled(mod["relative"], not mod["enabled"])
        self.refresh_mod_catalog_ui()

    def _view_selected_mod(self):
        mod = self._get_selected_mod()
        if not mod:
            return

        try:
            content = Path(mod["absolute"]).read_text(encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("View Script", f"Unable to read mod:\n{exc}")
            return

        preview = tk.Toplevel(self.root)
        preview.title(f"Mod Preview - {mod['name']}")
        preview.geometry("800x600")

        text_widget = scrolledtext.ScrolledText(
            preview,
            wrap=tk.NONE,
            bg=self.colors["text_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            font=(self.editor_font_family, self.editor_font_size),
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

    def _get_selected_mod(self):
        if not self.mod_tree or not self.mod_tree.selection():
            return None
        mod_id = self.mod_tree.selection()[0]
        return self._find_mod(mod_id)

    def _find_mod(self, mod_id):
        for mod in self.mod_catalog:
            if mod["relative"] == mod_id:
                return mod
        return None

    def _clear_mod_detail(self):
        if not self.mod_detail_text:
            return
        self.mod_detail_text.config(state=tk.NORMAL)
        self.mod_detail_text.delete("1.0", tk.END)
        self.mod_detail_text.insert(
            tk.END,
            "No mods discovered in the 'mods' folder yet. Add .py files to see them here.",
        )
        self.mod_detail_text.config(state=tk.DISABLED)

    def _display_mod_details(self, mod_id):
        mod = self._find_mod(mod_id)
        if not mod or not self.mod_detail_text:
            self._clear_mod_detail()
            return

        summary = self._get_mod_summary(mod)

        lines = [
            f"Name: {mod['name']}",
            f"Version: {mod.get('version', '—') or '—'}",
            f"Author: {mod.get('author', 'Unknown')}",
            f"Location: {mod['relative']}",
            f"Status: {'Enabled' if mod['enabled'] else 'Disabled'}",
            "",
        ]

        if mod.get("summary"):
            lines.append(mod["summary"])
            lines.append("")

        if summary.get("error"):
            lines.append(f"⚠ Unable to load mod for inspection: {summary['error']}")
        else:
            if summary.get("hooks"):
                lines.append("Registered Hooks:")
                for hook in summary["hooks"]:
                    filter_desc = ", ".join(
                        f"{key}={value}" for key, value in hook["filters"].items()
                    )
                    if filter_desc:
                        filter_desc = f" [{filter_desc}]"
                    lines.append(
                        f"  • {hook['event']} (priority {hook['priority']}){filter_desc}"
                    )
            if summary.get("commands"):
                if summary.get("hooks"):
                    lines.append("")
                lines.append("Custom Commands:")
                for command in summary["commands"]:
                    alias_text = (
                        f" (aliases: {', '.join(command['aliases'])})"
                        if command["aliases"]
                        else ""
                    )
                    help_text = command["help_text"] or "No description provided."
                    lines.append(f"  • {command['verb']}{alias_text}: {help_text}")

        detail_text = "\n".join(lines)
        self.mod_detail_text.config(state=tk.NORMAL)
        self.mod_detail_text.delete("1.0", tk.END)
        self.mod_detail_text.insert(tk.END, detail_text)
        self.mod_detail_text.config(state=tk.DISABLED)

    def _get_mod_summary(self, mod):
        cache_entry = self.mod_cache.get(mod["relative"])
        if cache_entry and cache_entry["mtime"] == mod["mtime"]:
            return cache_entry["data"]

        from sagacraft.tools.modding import ModdingSystem  # pylint: disable=import-outside-toplevel
        summary = {"hooks": [], "commands": [], "error": None}
        sandbox = ModdingSystem()
        try:
            success = sandbox.load_mod_file(str(mod["absolute"]))
        except OSError as exc:
            summary["error"] = str(exc)
        else:
            if not success:
                summary["error"] = "Failed to execute mod script."
            else:
                for event, hooks in sandbox.hooks.items():
                    for hook in hooks:
                        summary["hooks"].append(
                            {
                                "event": event.value,
                                "priority": hook.priority,
                                "filters": hook.filter_params or {},
                            }
                        )
                seen_verbs = set()
                for command in sandbox.custom_commands.values():
                    if command.verb in seen_verbs:
                        continue
                    seen_verbs.add(command.verb)
                    summary["commands"].append(
                        {
                            "verb": command.verb,
                            "aliases": list(command.aliases),
                            "help_text": command.help_text,
                        }
                    )

        self.mod_cache[mod["relative"]] = {
            "mtime": mod["mtime"],
            "data": summary,
        }
        return summary

    def _discover_mods(self):
        mods = []
        if not self.mod_root.exists():
            return mods

        for path in sorted(self.mod_root.rglob("*.py")):
            if path.name.startswith("__"):
                continue
            metadata = self._parse_mod_metadata(path)
            relative_path = path.relative_to(self.mod_root).as_posix()
            metadata.update(
                {
                    "absolute": path,
                    "relative": relative_path,
                    "enabled": relative_path in self.enabled_mods,
                    "mtime": path.stat().st_mtime,
                }
            )
            mods.append(metadata)

        return mods

    def _parse_mod_metadata(self, path: Path):
        metadata = {
            "name": path.stem.replace("_", " ").title(),
            "version": "1.0",
            "author": "Unknown",
            "summary": "No summary provided.",
            "docstring": "",
        }

        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            metadata["summary"] = "Unable to read mod file."
            return metadata

        try:
            module = ast.parse(source)
        except SyntaxError as exc:
            metadata["summary"] = f"Syntax error: {exc}".strip()
            return metadata

        docstring = ast.get_docstring(module) or ""
        metadata["docstring"] = docstring

        for line in docstring.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key == "name" and value:
                metadata["name"] = value
            elif key == "version" and value:
                metadata["version"] = value
            elif key in {"summary", "description"} and value:
                metadata["summary"] = value
            elif key == "author" and value:
                metadata["author"] = value

        return metadata

    def _set_mod_enabled(self, relative_path: str, enabled: bool):
        if enabled:
            self.enabled_mods.add(relative_path)
        else:
            self.enabled_mods.discard(relative_path)
        self._save_mod_state()

    def _ensure_mod_root(self):
        self.mod_root.mkdir(parents=True, exist_ok=True)

    def _load_mod_state(self):
        self.enabled_mods = set()
        self.mod_state_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.mod_state_path.exists():
            self._save_mod_state()
            return

        try:
            with open(self.mod_state_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            data = {}

        enabled = data.get("enabled_mods", []) or []
        self.enabled_mods = {entry for entry in enabled if isinstance(entry, str)}

    def _save_mod_state(self):
        self.mod_state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"enabled_mods": sorted(self.enabled_mods)}
        try:
            with open(self.mod_state_path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
        except OSError:
            messagebox.showwarning(
                "Mod State",
                "Unable to persist mod selection. Changes will apply for this session only.",
            )

    def _clear_mod_console(self):
        self.mod_output_history.clear()
        if not self.mod_console:
            return
        self.mod_console.config(state=tk.NORMAL)
        self.mod_console.delete("1.0", tk.END)
        self.mod_console.config(state=tk.DISABLED)

    def _log_mod_console(self, message: str):
        timestamped = message
        self.mod_output_history.append(timestamped)
        if len(self.mod_output_history) > 200:
            self.mod_output_history = self.mod_output_history[-200:]
        if self.mod_console:
            self.mod_console.config(state=tk.NORMAL)
            self.mod_console.insert(tk.END, timestamped + "\n")
            self.mod_console.see(tk.END)
            self.mod_console.config(state=tk.DISABLED)

    def _apply_active_mods_to_game(self):
        messages = []
        if not self.game_instance or not hasattr(self.game_instance, "modding"):
            messages.append("Modding system not available for this adventure.")
            return messages

        from sagacraft.tools.modding import ModdingSystem  # pylint: disable=import-outside-toplevel
        self.game_instance.modding = ModdingSystem(engine=self.game_instance)

        for relative_path in sorted(self.enabled_mods):
            mod_path = self.mod_root / relative_path
            if not mod_path.exists():
                messages.append(f"⚠ Missing mod: {relative_path}")
                continue
            success = self.game_instance.modding.load_mod_file(str(mod_path))
            if success:
                messages.append(f"✅ Loaded {relative_path}")
            else:
                messages.append(f"⚠ Failed to load {relative_path}")

        return messages

    def create_preview_tab(self):
        """JSON preview tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="📄 JSON")

        ttk.Label(frame, text="Adventure JSON:").pack(anchor=tk.W)

        self.preview_text = scrolledtext.ScrolledText(
            frame, width=80, height=35, wrap=tk.WORD
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh Preview", command=self.update_preview).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_preview).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            btn_frame,
            text="Show Diff vs Saved",
            command=self.show_json_diff,
        ).pack(side=tk.LEFT, padx=5)

    def create_play_tab(self):  # pylint: disable=too-many-statements,too-many-locals
        """Interactive play tab with modern design"""
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="▶️ Play")
        self.play_tab = frame

        # Header
        header = ttk.Label(frame, text="Adventure Playthrough", style="Title.TLabel")
        header.pack(anchor=tk.W, pady=(0, 15))

        # Game output area with modern styling
        output_frame = tk.Frame(frame, bg=self.colors["text_bg"], relief=tk.FLAT, bd=2)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.game_output = scrolledtext.ScrolledText(
            output_frame,
            width=90,
            height=28,
            wrap=tk.WORD,
            bg="#0d1117",
            fg="#c9d1d9",
            font=("Consolas", 10),
            insertbackground="#58a6ff",
            relief=tk.FLAT,
            bd=10,
        )
        self.game_output.pack(fill=tk.BOTH, expand=True)
        self.game_output.config(state=tk.DISABLED)

        # Configure text tags for colored output
        self.game_output.tag_config("success", foreground="#3fb950")
        self.game_output.tag_config("warning", foreground="#d29922")
        self.game_output.tag_config("error", foreground="#f85149")
        self.game_output.tag_config("info", foreground="#58a6ff")

        # Command input area with modern styling
        cmd_container = tk.Frame(frame, bg=self.colors["panel"], relief=tk.FLAT, bd=1)
        cmd_container.pack(fill=tk.X, pady=(0, 15))

        cmd_frame = tk.Frame(cmd_container, bg=self.colors["panel"])
        cmd_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(cmd_frame, text="💬", font=("Segoe UI", 14)).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        self.command_entry = tk.Entry(
            cmd_frame,
            font=("Consolas", 11),
            bg=self.colors["text_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["accent"],
            relief=tk.FLAT,
            bd=5,
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        def _on_command_enter(_event):
            self.send_command()

        self.command_entry.bind("<Return>", _on_command_enter)

        send_btn = ttk.Button(
            cmd_frame, text="➤ Send", command=self.send_command, style="Success.TButton"
        )
        send_btn.pack(side=tk.LEFT)

        # Status badges
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(
            status_frame,
            textvariable=self.validation_badge_var,
            style="Subtitle.TLabel",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(
            status_frame,
            textvariable=self.test_badge_var,
            style="Subtitle.TLabel",
        ).pack(side=tk.LEFT, padx=5)

        # Control buttons with colors
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X)

        ttk.Button(
            control_frame,
            text="📂 Load Adventure",
            command=self.load_for_play,
            width=18,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame,
            text="▶️ Start Game",
            command=self.start_game,
            width=15,
            style="Success.TButton",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame,
            text="⟳ Restart",
            command=self.restart_game,
            width=15,
            style="Warning.TButton",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame,
            text="🗑️ Clear Output",
            command=self.clear_game_output,
            width=15,
        ).pack(side=tk.LEFT, padx=5)

        # Quick save/load controls
        quick_frame = ttk.Frame(frame)
        quick_frame.pack(fill=tk.X, pady=(10, 5))
        ttk.Label(quick_frame, text="Quick Save Slots", style="Subtitle.TLabel").pack(
            anchor=tk.W, padx=5
        )
        slot_container = ttk.Frame(quick_frame)
        slot_container.pack(anchor=tk.W, padx=5)
        for slot in (1, 2, 3):
            slot_frame = ttk.Frame(slot_container)
            slot_frame.pack(side=tk.LEFT, padx=5)
            ttk.Button(
                slot_frame,
                text=f"Save {slot}",
                command=lambda s=slot: self.quick_save(s),
                width=12,
                style="Success.TButton",
            ).pack(pady=2)
            ttk.Button(
                slot_frame,
                text=f"Load {slot}",
                command=lambda s=slot: self.quick_load(s),
                width=12,
            ).pack(pady=2)

        # Demo command helpers
        demo_frame = ttk.Frame(frame)
        demo_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(demo_frame, text="Demo Commands", style="Subtitle.TLabel").pack(
            side=tk.LEFT, padx=5
        )

        demo_values = list(self.demo_scripts.keys())
        demo_selector = ttk.Combobox(
            demo_frame,
            textvariable=self.demo_script_var,
            values=demo_values,
            state="readonly",
            width=30,
        )
        demo_selector.pack(side=tk.LEFT, padx=5)
        if demo_values and not self.demo_script_var.get():
            self.demo_script_var.set(demo_values[0])

        ttk.Button(demo_frame, text="Run Demo", command=self.run_demo_script).pack(
            side=tk.LEFT, padx=5
        )

    # Adventure management methods
    def new_adventure(self):
        """Create a new adventure"""
        if self.modified and not messagebox.askyesno(
            "Unsaved Changes", "You have unsaved changes. Continue anyway?"
        ):
            return

        # Provide a usable default adventure so Play works immediately
        self.adventure = {
            "title": "New Adventure",
            "author": "",
            "intro": "Welcome to your new SagaCraft adventure!",
            "start_room": 1,
            "rooms": [
                {
                    "id": 1,
                    "name": "Start",
                    "description": "You are at the start.",
                    "exits": {},
                    "is_dark": False,
                }
            ],
            "items": [],
            "monsters": [],
            "effects": [],
        }

        self.current_file = None
        self.modified = False
        self.load_adventure_to_ui()
        self.update_status("New adventure created")

    def open_adventure(self):
        """Open an existing adventure"""
        filename = filedialog.askopenfilename(
            title="Open Adventure",
            initialdir="adventures",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if not filename:
            return

        self._load_adventure_file(filename)

    def save_adventure(self):
        """Save the current adventure"""
        if not self.current_file:
            return self.save_adventure_as()

        success = self._write_adventure_to_file(self.current_file)
        if success:
            self._remember_recent_file(self.current_file)
        return success

    def save_adventure_as(self):
        """Save adventure with a new name"""
        filename = filedialog.asksaveasfilename(
            title="Save Adventure As",
            initialdir="adventures",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if not filename:
            return False

        self.current_file = filename
        return self.save_adventure()

    def _load_adventure_file(  # pylint: disable=too-many-arguments
        self,
        filename: str,
        *,
        set_current: bool = True,
        refresh_ui: bool = True,
        update_recent: bool = True,
        show_status: bool = True,
        show_errors: bool = True,
    ) -> bool:
        """Load adventure data from disk and optionally refresh the UI."""
        try:
            with open(filename, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            if show_errors:
                messagebox.showerror("Error", f"Failed to load file:\n{exc}")
            else:
                self.update_status(f"Load failed: {exc}")
            return False

        self.adventure = data
        if set_current:
            self.current_file = filename
        self.modified = False
        if refresh_ui:
            self.load_adventure_to_ui()
        if update_recent:
            self._remember_recent_file(filename)
        if show_status:
            self.update_status(f"Opened: {os.path.basename(filename)}")
        return True

    def _write_adventure_to_file(self, filename: str) -> bool:
        """Persist the current adventure to disk."""
        try:
            self.collect_adventure_data()
            with open(filename, "w", encoding="utf-8") as handle:
                json.dump(self.adventure, handle, indent=2)
        except (OSError, TypeError) as exc:
            messagebox.showerror("Error", f"Failed to save file:\n{exc}")
            return False

        self.modified = False
        self.update_status(f"Saved: {os.path.basename(filename)}")
        return True

    def load_adventure_to_ui(self):
        """Load adventure data into UI"""
        # Info tab
        self.title_var.set(self.adventure.get("title", ""))
        self.author_var.set(self.adventure.get("author", ""))
        self.start_room_var.set(self.adventure.get("start_room", 1))
        self.intro_text.delete("1.0", tk.END)
        self.intro_text.insert("1.0", self.adventure.get("intro", ""))

        if self.game_mode_var:
            self._suppress_mode_change = True
            self.game_mode_var.set(self.adventure.get("mode", "text"))
            self._suppress_mode_change = False

        # Rooms
        self.refresh_rooms_list()

        # Items
        self.refresh_items_list()

        # Monsters
        self.refresh_monsters_list()

        # Preview
        self.update_preview()

    def collect_adventure_data(self):
        """Collect data from UI into adventure dict"""
        self.adventure["title"] = self.title_var.get()
        self.adventure["author"] = self.author_var.get()
        self.adventure["start_room"] = self.start_room_var.get()
        self.adventure["intro"] = self.intro_text.get("1.0", tk.END).strip()

    # Room methods
    def refresh_rooms_list(self):
        """Refresh the rooms listbox"""
        self.rooms_listbox.delete(0, tk.END)
        for room in self.adventure["rooms"]:
            badge = self._get_room_validation_badge(room)
            self.rooms_listbox.insert(tk.END, f"#{room['id']}: {room['name']} {badge}")

    def _get_room_validation_badge(self, room: dict) -> str:
        """Return status badge for a room (error/warning/ok)."""
        errors = []
        warnings = []

        # Check required fields
        if not room.get("name", "").strip():
            errors.append("missing_name")
        if not room.get("description", "").strip():
            warnings.append("missing_desc")

        # Check exits point to valid rooms
        room_ids = {r.get("id") for r in self.adventure.get("rooms", [])}
        exits = room.get("exits", {})
        if isinstance(exits, dict):
            for direction, target in exits.items():
                if isinstance(target, int) and target not in room_ids:
                    errors.append(f"bad_exit_{direction}")

        # Check for missing reverse exits
        for direction, target in exits.items():
            if not isinstance(target, int) or target not in room_ids:
                continue
            rev = self._reverse_direction(direction)
            if rev:
                target_room = next(
                    (r for r in self.adventure.get("rooms", [])
                     if r.get("id") == target),
                    None
                )
                if target_room and rev not in target_room.get("exits", {}):
                    warnings.append(f"no_reverse_{direction}")

        if errors:
            return "❌"
        if warnings:
            return "⚠️"
        return "✅"

    def add_room(self):
        """Add a new room"""
        new_id = max((r["id"] for r in self.adventure["rooms"]), default=0) + 1
        room = {
            "id": new_id,
            "name": f"Room {new_id}",
            "description": "A new room.",
            "exits": {},
            "is_dark": False,
        }
        self.adventure["rooms"].append(room)
        self.refresh_rooms_list()
        self.rooms_listbox.selection_set(tk.END)
        self.select_room(None)
        self.modified = True

    def delete_room(self):
        """Delete selected room"""
        selection = self.rooms_listbox.curselection()
        if not selection:
            return

        if messagebox.askyesno("Confirm", "Delete this room?"):
            idx = selection[0]
            del self.adventure["rooms"][idx]
            self.refresh_rooms_list()
            self.modified = True

    def select_room(self, _event):
        """Load selected room into editor"""
        selection = self.rooms_listbox.curselection()
        if not selection:
            return

        room = self.adventure["rooms"][selection[0]]
        self.room_id_var.set(room["id"])
        self.room_name_var.set(room["name"])
        self.room_desc.delete("1.0", tk.END)
        self.room_desc.insert("1.0", room["description"])

        for direction, var in self.exit_vars.items():
            var.set(room["exits"].get(direction, 0))

    def update_room(self):
        """Update current room from editor"""
        selection = self.rooms_listbox.curselection()
        if not selection:
            return

        room = self.adventure["rooms"][selection[0]]
        room["name"] = self.room_name_var.get()
        room["description"] = self.room_desc.get("1.0", tk.END).strip()

        room["exits"] = {}
        for direction, var in self.exit_vars.items():
            if var.get() > 0:
                room["exits"][direction] = var.get()

        self.refresh_rooms_list()
        self.rooms_listbox.selection_set(selection[0])
        self.modified = True
        self.update_status("Room updated")

    def update_info(self):
        """Update adventure info"""
        self.collect_adventure_data()
        self.modified = True
        self.update_status("Adventure info updated")

    def browse_scene_background(self):
        """Removed - SagaCraft is text-only."""

    def refresh_hotspots_list(self, scene=None, *, clear_only: bool = False):
        """Removed - SagaCraft is text-only."""

    def add_hotspot(self):
        """Removed - SagaCraft is text-only."""

    def delete_hotspot(self):
        """Removed - SagaCraft is text-only."""

    def select_hotspot(self, _event):
        """Removed - SagaCraft is text-only."""

    def clear_hotspot_editor(self):
        """Removed - SagaCraft is text-only."""

    def update_hotspot(self):
        """Removed - SagaCraft is text-only."""

    # Item methods
    def refresh_items_list(self):
        """Refresh items listbox"""
        self.items_listbox.delete(0, tk.END)
        for item in self.adventure["items"]:
            self.items_listbox.insert(tk.END, f"#{item['id']}: {item['name']}")

    def add_item(self):
        """Add a new item"""
        new_id = max((i["id"] for i in self.adventure["items"]), default=0) + 1
        item = {
            "id": new_id,
            "name": f"Item {new_id}",
            "description": "A new item.",
            "type": "normal",
            "weight": 1,
            "value": 0,
            "is_weapon": False,
            "is_takeable": True,
            "location": 1,
        }
        self.adventure["items"].append(item)
        self.refresh_items_list()
        self.items_listbox.selection_set(tk.END)
        self.select_item(None)
        self.modified = True

    def delete_item(self):
        """Delete selected item"""
        selection = self.items_listbox.curselection()
        if not selection:
            return

        if messagebox.askyesno("Confirm", "Delete this item?"):
            idx = selection[0]
            del self.adventure["items"][idx]
            self.refresh_items_list()
            self.modified = True

    def select_item(self, _event):
        """Load selected item into editor"""
        selection = self.items_listbox.curselection()
        if not selection:
            return

        item = self.adventure["items"][selection[0]]
        self.item_id_var.set(item["id"])
        self.item_name_var.set(item["name"])
        self.item_desc.delete("1.0", tk.END)
        self.item_desc.insert("1.0", item["description"])
        self.item_weight_var.set(item.get("weight", 1))
        self.item_value_var.set(item.get("value", 0))
        self.item_location_var.set(item.get("location", 1))
        self.item_is_weapon_var.set(item.get("is_weapon", False))
        self.item_is_takeable_var.set(item.get("is_takeable", True))

    def update_item(self):
        """Update current item"""
        selection = self.items_listbox.curselection()
        if not selection:
            return

        item = self.adventure["items"][selection[0]]
        item["name"] = self.item_name_var.get()
        item["description"] = self.item_desc.get("1.0", tk.END).strip()
        item["weight"] = self.item_weight_var.get()
        item["value"] = self.item_value_var.get()
        item["location"] = self.item_location_var.get()
        item["is_weapon"] = self.item_is_weapon_var.get()
        item["is_takeable"] = self.item_is_takeable_var.get()

        self.refresh_items_list()
        self.items_listbox.selection_set(selection[0])
        self.modified = True
        self.update_status("Item updated")

    # Monster methods
    def refresh_monsters_list(self):
        """Refresh monsters listbox"""
        self.monsters_listbox.delete(0, tk.END)
        for monster in self.adventure["monsters"]:
            self.monsters_listbox.insert(tk.END, f"#{monster['id']}: {monster['name']}")

    def add_monster(self):
        """Add a new monster"""
        new_id = max((m["id"] for m in self.adventure["monsters"]), default=0) + 1
        monster = {
            "id": new_id,
            "name": f"Monster {new_id}",
            "description": "A new creature.",
            "room_id": 1,
            "hardiness": 10,
            "agility": 10,
            "friendliness": "hostile",
            "courage": 100,
            "gold": 0,
        }
        self.adventure["monsters"].append(monster)
        self.refresh_monsters_list()
        self.monsters_listbox.selection_set(tk.END)
        self.select_monster(None)
        self.modified = True

    def delete_monster(self):
        """Delete selected monster"""
        selection = self.monsters_listbox.curselection()
        if not selection:
            return

        if messagebox.askyesno("Confirm", "Delete this monster?"):
            idx = selection[0]
            del self.adventure["monsters"][idx]
            self.refresh_monsters_list()
            self.modified = True

    def select_monster(self, _event):
        """Load selected monster into editor"""
        selection = self.monsters_listbox.curselection()
        if not selection:
            return

        monster = self.adventure["monsters"][selection[0]]
        self.monster_id_var.set(monster["id"])
        self.monster_name_var.set(monster["name"])
        self.monster_desc.delete("1.0", tk.END)
        self.monster_desc.insert("1.0", monster["description"])
        self.monster_room_var.set(monster.get("room_id", 1))
        self.monster_hardiness_var.set(monster.get("hardiness", 10))
        self.monster_agility_var.set(monster.get("agility", 10))
        self.monster_friendliness_var.set(monster.get("friendliness", "hostile"))
        self.monster_gold_var.set(monster.get("gold", 0))

    def update_monster(self):
        """Update current monster"""
        selection = self.monsters_listbox.curselection()
        if not selection:
            return

        monster = self.adventure["monsters"][selection[0]]
        monster["name"] = self.monster_name_var.get()
        monster["description"] = self.monster_desc.get("1.0", tk.END).strip()
        monster["room_id"] = self.monster_room_var.get()
        monster["hardiness"] = self.monster_hardiness_var.get()
        monster["agility"] = self.monster_agility_var.get()
        monster["friendliness"] = self.monster_friendliness_var.get()
        monster["gold"] = self.monster_gold_var.get()

        self.refresh_monsters_list()
        self.monsters_listbox.selection_set(selection[0])
        self.modified = True
        self.update_status("Monster updated")

    # Preview methods
    def update_preview(self):
        """Update JSON preview"""
        self.collect_adventure_data()
        json_text = json.dumps(self.adventure, indent=2)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", json_text)

    def copy_preview(self):
        """Copy preview to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.preview_text.get("1.0", tk.END))
        self.update_status("JSON copied to clipboard")

    def show_json_diff(self):
        """Display differences between the current state and last saved file."""
        if not self.current_file or not Path(self.current_file).exists():
            messagebox.showinfo(
                "Diff Unavailable", "Save the adventure to enable diff view."
            )
            return

        self.collect_adventure_data()

        try:
            with open(self.current_file, "r", encoding="utf-8") as handle:
                saved_data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Diff Error", f"Unable to read saved file:\n{exc}")
            return

        current_lines = json.dumps(self.adventure, indent=2).splitlines()
        saved_lines = json.dumps(saved_data, indent=2).splitlines()
        diff_lines = list(
            difflib.unified_diff(
                saved_lines,
                current_lines,
                fromfile="saved",
                tofile="current",
                lineterm="",
            )
        )

        diff_window = tk.Toplevel(self.root)
        diff_window.title("Adventure JSON Diff")
        diff_window.geometry("960x720")

        text_widget = scrolledtext.ScrolledText(
            diff_window,
            wrap=tk.NONE,
            font=("Consolas", 10),
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        if diff_lines:
            text_widget.insert("1.0", "\n".join(diff_lines))
        else:
            text_widget.insert("1.0", "No differences detected.")

        text_widget.config(state=tk.DISABLED)

    # Tool methods
    def test_adventure(self):
        """Test the adventure directly in the IDE play tab"""
        self.collect_adventure_data()

        if hasattr(self, "play_tab"):
            self.notebook.select(self.play_tab)

        self.test_badge_var.set("Play: Testing")
        self.start_game()
        if self.game_running:
            self.update_status("Testing adventure in IDE play tab")

    def play_in_ide_console(self):  # pylint: disable=too-many-statements,too-many-locals
        """Play adventure in a dedicated console window with command input."""
        self.collect_adventure_data()

        console = tk.Toplevel(self.root)
        console.title("Play in IDE - Console")
        console.geometry("700x600")
        console.configure(bg=self.colors.get("panel", "#222"))

        # Top frame with options
        options_frame = ttk.Frame(console)
        options_frame.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(options_frame, text="RNG Seed:").pack(side=tk.LEFT, padx=5)
        seed_var = tk.IntVar(value=42)
        seed_spin = ttk.Spinbox(options_frame, from_=0, to=999999, textvariable=seed_var, width=8)
        seed_spin.pack(side=tk.LEFT, padx=5)

        deterministic_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Deterministic playthrough",
            variable=deterministic_var
        ).pack(side=tk.LEFT, padx=5)

        # Output area
        output_frame = ttk.Frame(console)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        output = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            bg=self.colors.get("text_bg", "#1a1a1a"),
            fg=self.colors.get("fg", "#eee"),
            height=20
        )
        output.pack(fill=tk.BOTH, expand=True)

        # Input area
        input_frame = ttk.Frame(console)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="Command:").pack(side=tk.LEFT, padx=5)
        cmd_var = tk.StringVar()
        cmd_entry = ttk.Entry(input_frame, textvariable=cmd_var, width=50)
        cmd_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Game instance holder
        game_state = {"game": None, "output_capture": None}

        def start_game() -> None:
            """Initialize the game in the console."""
            try:
                output.delete(1.0, tk.END)

                # Write temp adventure
                adv_path = Path("adventures")
                adv_path.mkdir(parents=True, exist_ok=True)
                tmp = adv_path / "_console_play.json"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(self.adventure, f, indent=2)

                # Load engine
                engine_path = (
                    Path(__file__).parent.parent.parent.parent / "sagacraft_engine.py"
                )
                spec = importlib.util.spec_from_file_location("engine", engine_path)
                if spec is None or spec.loader is None:
                    output.insert(tk.END, "❌ Could not load engine.\n")
                    return

                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    output.insert(tk.END, f"❌ Engine import error: {e}\n")
                    return

                # Get game class
                game_cls = (
                    getattr(mod, "ExtendedAdventureGame", None)
                    or getattr(mod, "EnhancedAdventureGame", None)
                    or getattr(mod, "AdventureGame", None)
                )
                if game_cls is None or not callable(game_cls):
                    output.insert(tk.END, "❌ Engine missing game class.\n")
                    return

                # Create game instance with seeded RNG if requested
                if deterministic_var.get():
                    random.seed(seed_var.get())

                game_ctor: Callable[[str], Any] = cast(Callable[[str], Any], game_cls)
                game = game_ctor(str(tmp))  # pylint: disable=not-callable
                game.load_adventure()
                game_state["game"] = game

                title = self.adventure.get("title", "Untitled")
                output.insert(tk.END, f"🎮 Adventure loaded: {title}\n")
                seed_str = f"{seed_var.get()} (deterministic={deterministic_var.get()})"
                output.insert(tk.END, f"RNG Seed: {seed_str}\n")
                output.insert(tk.END, "=" * 60 + "\n\n")

                # Run initial look
                output.insert(tk.END, "[Initial state]\n")
                game.state.current_room = game.adventure.get("start_room", 1)
                look_out = game.look()
                output.insert(tk.END, look_out + "\n\n")

            except Exception as e:  # pylint: disable=broad-exception-caught
                output.insert(tk.END, f"❌ Error starting game: {e}\n")

        def send_command() -> None:
            """Send a command to the game."""
            cmd = cmd_var.get().strip()
            if not cmd or not game_state["game"]:
                return

            try:
                output.insert(tk.END, f"> {cmd}\n")
                result = game_state["game"].handle_input(cmd)
                output.insert(tk.END, result + "\n\n")
                output.see(tk.END)
                cmd_var.set("")
            except Exception as e:  # pylint: disable=broad-exception-caught
                output.insert(tk.END, f"❌ Error: {e}\n")

        # Start button
        start_btn = ttk.Button(options_frame, text="Start Game", command=start_game)
        start_btn.pack(side=tk.RIGHT, padx=5)

        # Bind enter key to send command

        def _on_console_enter(_event):
            send_command()

        cmd_entry.bind("<Return>", _on_console_enter)
        send_btn = ttk.Button(input_frame, text="Send", command=send_command)
        send_btn.pack(side=tk.LEFT, padx=5)

        output.insert(tk.END, "Click 'Start Game' to begin. Then type commands below.\n")
        help_text = (
            "Commands: look, go <direction>, take <item>, "
            "drop <item>, examine <thing>, etc.\n\n"
        )
        output.insert(tk.END, help_text)
        output.configure(state=tk.DISABLED)

    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    def validate_adventure(self, silent: bool = False):
        """Validate adventure data and update the status badge.

        Returns a list of error strings. When silent=False, also shows a dialog.
        """
        self.collect_adventure_data()
        errors: list[str] = []

        # Title and minimal structure
        if not self.adventure.get("title"):
            errors.append("Adventure must have a title")

        rooms = list(self.adventure.get("rooms", []))
        if not rooms:
            errors.append("Adventure must have at least one room")

        # Room ID integrity
        room_ids = [r.get("id") for r in rooms]
        if any(rid is None for rid in room_ids):
            errors.append("Every room must have an 'id'")
        # Duplicate room ids
        seen: set[int] = set()
        dupes: set[int] = set()
        for rid in room_ids:
            if not isinstance(rid, int):
                continue
            if rid in seen:
                dupes.add(rid)
            else:
                seen.add(rid)
        if dupes:
            errors.append(f"Duplicate room id(s): {sorted(dupes)}")

        room_id_set = {rid for rid in room_ids if rid is not None}

        # Start room exists
        start_room = self.adventure.get("start_room")
        if start_room not in room_id_set:
            errors.append(f"Start room {start_room} does not exist")

        # Check room exits refer to valid rooms (allow 0 for 'nowhere')
        for room in rooms:
            exits = dict(room.get("exits", {}))
            for direction, target in exits.items():
                if target not in room_id_set and target != 0:
                    room_id = room.get("id")
                    error_msg = (
                        f"Room {room_id} has exit '{direction}' "
                        f"to non-existent room {target}"
                    )
                    errors.append(error_msg)

        # Items located in valid rooms, if any
        for item in self.adventure.get("items", []):
            loc = item.get("location")
            if isinstance(loc, int) and loc not in room_id_set:
                item_name = item.get("id", item.get("name", "unknown"))
                error_msg = f"Item {item_name} references missing room {loc}"
                errors.append(error_msg)

        # Monsters placed in valid rooms, if any
        for mon in self.adventure.get("monsters", []):
            mroom = mon.get("room")
            if isinstance(mroom, int) and mroom not in room_id_set:
                mon_name = mon.get("id", mon.get("name", "unknown"))
                error_msg = f"Monster {mon_name} references missing room {mroom}"
                errors.append(error_msg)

        # Update UI badges and optionally show dialog
        if errors:
            self.validation_badge_var.set(f"Validation: ⚠ {len(errors)} issue(s)")
            if not silent:
                messagebox.showwarning("Validation Issues", "\n".join(errors))
        else:
            self.validation_badge_var.set("Validation: ✅ Clean")
            if not silent:
                messagebox.showinfo("Validation", "Adventure is valid!")

        return errors

    # --- Detailed Game Verification ---
    def verify_game(self):
        """Run a comprehensive verification and show a detailed report."""
        report = self._analyze_adventure()
        # Add simulated playthrough section
        play = self._simulate_playthrough(max_steps=200)
        report["playthrough"] = play

        # Check if mods are active and analyze impact
        active_mods = self._get_active_mods()
        if active_mods:
            report["mods_active"] = active_mods
            # Optionally add mod analysis to suggestions
            suggestions = report.get("suggestions", [])
            mod_str = ", ".join(active_mods)
            mod_msg = (
                f"Mods active: {mod_str} - "
                "verify game behavior with all mods enabled"
            )
            suggestions.append(mod_msg)
            report["suggestions"] = suggestions

        errors = report.get("errors", [])
        warnings = report.get("warnings", [])

        # Update badges to reflect verification results
        if errors:
            err_count = len(errors)
            warn_count = len(warnings)
            status = f"Validation: ⚠ {err_count} error(s), {warn_count} warning(s)"
            self.validation_badge_var.set(status)
        elif warnings:
            warn_count = len(warnings)
            self.validation_badge_var.set(f"Validation: ⚠ {warn_count} warning(s)")
        else:
            self.validation_badge_var.set("Validation: ✅ Clean")

        # Show report window
        text = self._format_verification_report(report)
        self._show_text_report("Game Verification Report", text)

    def open_command_palette(self):
        """Quick action launcher for common IDE tasks."""
        palette = tk.Toplevel(self.root)
        palette.title("Command Palette")
        palette.geometry("420x320")
        palette.configure(bg=self.colors.get("panel", "#222"))

        label_text = "Type to filter commands:"
        tk.Label(
            palette,
            text=label_text,
            bg=self.colors.get("panel", "#222"),
            fg=self.colors.get("fg", "#eee"),
        ).pack(pady=6)
        query = tk.StringVar()
        entry = ttk.Entry(palette, textvariable=query)
        entry.pack(fill=tk.X, padx=10)

        commands = [
            ("Verify Game (Detailed)", self.verify_game),
            ("Validate Adventure", self.validate_adventure),
            ("Auto-Fix Common Issues", self.auto_fix_game),
            ("Strict Schema Validation", self.strict_schema_validation),
            ("Play Adventure", self.test_adventure),
        ]

        frame = tk.Frame(palette, bg=self.colors.get("panel", "#222"))
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        listbox = tk.Listbox(frame)
        listbox.pack(fill=tk.BOTH, expand=True)

        def refresh():
            term = query.get().lower().strip()
            listbox.delete(0, tk.END)
            for label, _ in commands:
                if not term or term in label.lower():
                    listbox.insert(tk.END, label)

        def run_selected(_event=None):
            sel = listbox.curselection()
            if not sel:
                return
            label = listbox.get(sel[0])
            for cmd_label, fn in commands:
                if cmd_label == label:
                    try:
                        fn()
                    finally:
                        palette.destroy()
                    break

        entry.bind("<KeyRelease>", lambda _e: refresh())
        listbox.bind("<Double-Button-1>", run_selected)
        listbox.bind("<Return>", run_selected)
        refresh()
        entry.focus_set()

        ttk.Button(palette, text="Run", command=run_selected).pack(pady=6)

    def auto_fix_game(self):
        """Apply automatic fixes and report what changed."""
        self.collect_adventure_data()

        fixes = []

        # 1. Add reverse exits
        rev_count = self._add_reverse_exits()
        if rev_count > 0:
            fixes.append(f"Added {rev_count} reverse exit(s)")

        # 2. Normalize direction aliases
        norm_count = self._normalize_directions()
        if norm_count > 0:
            fixes.append(f"Normalized {norm_count} direction alias(es)")

        # 3. Fill missing names/descriptions
        fill_count = self._fill_placeholders()
        if fill_count > 0:
            fixes.append(f"Filled {fill_count} missing name(s)/description(s)")

        if fixes:
            self.modified = True
            self.load_adventure_to_ui()
            messagebox.showinfo("Auto-Fix Complete", "\n".join(fixes))
        else:
            messagebox.showinfo("Auto-Fix", "No fixes needed!")

    def _add_reverse_exits(self) -> int:
        """Add missing reverse exits for reciprocity. Returns count of added exits."""
        count = 0
        rooms = self.adventure.get("rooms", [])
        room_map = {r.get("id"): r for r in rooms if isinstance(r, dict)}

        for r in rooms:
            if not isinstance(r, dict):
                continue
            rid = r.get("id")
            exits = r.get("exits", {})
            if not isinstance(exits, dict):
                continue
            for direction, target in list(exits.items()):
                if not isinstance(target, int) or target not in room_map:
                    continue
                rev = self._reverse_direction(direction)
                if not rev:
                    continue
                target_room = room_map[target]
                target_exits = target_room.get("exits", {})
                if not isinstance(target_exits, dict):
                    target_room["exits"] = {}
                    target_exits = target_room["exits"]
                if target_exits.get(rev) != rid:
                    target_exits[rev] = rid
                    count += 1
        return count

    def _normalize_directions(self) -> int:
        """Convert direction aliases to full names. Returns count."""
        aliases = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
            "u": "up", "d": "down"
        }
        count = 0
        for r in self.adventure.get("rooms", []):
            if not isinstance(r, dict):
                continue
            exits = r.get("exits", {})
            if not isinstance(exits, dict):
                continue
            for old_key in list(exits.keys()):
                if old_key.lower() in aliases:
                    new_key = aliases[old_key.lower()]
                    if new_key not in exits:
                        exits[new_key] = exits.pop(old_key)
                        count += 1
        return count

    def _fill_placeholders(self) -> int:
        """Fill missing names/descriptions with placeholders. Returns count."""
        count = 0
        for r in self.adventure.get("rooms", []):
            if not isinstance(r, dict):
                continue
            if not (r.get("name") or "").strip():
                r["name"] = f"Room {r.get('id', '?')}"
                count += 1
            if not (r.get("description") or "").strip():
                r["description"] = "A mysterious place."
                count += 1
        for it in self.adventure.get("items", []):
            if not isinstance(it, dict):
                continue
            if not (it.get("name") or "").strip():
                it["name"] = f"Item {it.get('id', '?')}"
                count += 1
            if not (it.get("description") or "").strip():
                it["description"] = "An interesting object."
                count += 1
        for mon in self.adventure.get("monsters", []):
            if not isinstance(mon, dict):
                continue
            if not (mon.get("name") or "").strip():
                mon["name"] = f"Creature {mon.get('id', '?')}"
                count += 1
            if not (mon.get("description") or "").strip():
                mon["description"] = "A mysterious being."
                count += 1
        return count

    def strict_schema_validation(self):
        """Run strict JSON schema validation and show detailed field-path errors."""
        self.collect_adventure_data()
        errors = self._strict_schema_check()

        if errors:
            text = "Strict Schema Validation Errors\n" + "=" * 60 + "\n\n"
            for e in errors:
                text += f"- {e}\n"
            self._show_text_report("Strict Schema Validation", text)
        else:
            messagebox.showinfo("Strict Validation", "Adventure passes strict schema validation!")

    def _strict_schema_check(self) -> list[str]:  # pylint: disable=too-many-branches
        """Enforce strict schema rules with field paths."""
        errors = []
        adv = self.adventure

        # Top level required fields
        if "title" not in adv or not isinstance(adv.get("title"), str):
            errors.append("Root: 'title' must be a non-empty string")
        if "start_room" not in adv or not isinstance(adv.get("start_room"), int):
            errors.append("Root: 'start_room' must be an integer")
        if "rooms" not in adv or not isinstance(adv.get("rooms"), list):
            errors.append("Root: 'rooms' must be a list")
        else:
            for i, r in enumerate(adv["rooms"]):
                if not isinstance(r, dict):
                    errors.append(f"rooms[{i}]: must be an object")
                    continue
                if "id" not in r or not isinstance(r.get("id"), int):
                    errors.append(f"rooms[{i}]: 'id' must be an integer")
                if "name" not in r or not isinstance(r.get("name"), str):
                    errors.append(f"rooms[{i}]: 'name' must be a string")
                if "description" not in r or not isinstance(r.get("description"), str):
                    errors.append(f"rooms[{i}]: 'description' must be a string")
                if "exits" not in r or not isinstance(r.get("exits"), dict):
                    errors.append(f"rooms[{i}]: 'exits' must be an object/dict")
                else:
                    for k, v in r["exits"].items():
                        if not isinstance(k, str):
                            errors.append(f"rooms[{i}].exits: key '{k}' must be a string")
                        if not isinstance(v, int):
                            errors.append(f"rooms[{i}].exits.{k}: must be an integer room ID")

        if "items" in adv:
            if not isinstance(adv["items"], list):
                errors.append("Root: 'items' must be a list")
            else:
                for i, it in enumerate(adv["items"]):
                    if not isinstance(it, dict):
                        errors.append(f"items[{i}]: must be an object")
                        continue
                    if "name" not in it or not isinstance(it.get("name"), str):
                        errors.append(f"items[{i}]: 'name' must be a string")

        if "monsters" in adv:
            if not isinstance(adv["monsters"], list):
                errors.append("Root: 'monsters' must be a list")
            else:
                for i, mon in enumerate(adv["monsters"]):
                    if not isinstance(mon, dict):
                        errors.append(f"monsters[{i}]: must be an object")
                        continue
                    if "name" not in mon or not isinstance(mon.get("name"), str):
                        errors.append(f"monsters[{i}]: 'name' must be a string")

        return errors

    def _reverse_direction(self, d: str) -> str | None:
        mapping = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east",
            "northeast": "southwest",
            "southwest": "northeast",
            "northwest": "southeast",
            "southeast": "northwest",
            "up": "down",
            "down": "up",
            "in": "out",
            "out": "in",
        }
        return mapping.get(d.lower())

    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    def _analyze_adventure(self) -> dict:
        """Compute stats, errors, and warnings for the current adventure."""
        self.collect_adventure_data()

        adv = self.adventure
        rooms = list(adv.get("rooms", []))
        items = list(adv.get("items", []))
        monsters = list(adv.get("monsters", []))
        start_room = adv.get("start_room")

        errors: list[str] = []
        warnings: list[str] = []
        suggestions: list[str] = []

        # --- Top-level schema/type checks ---
        if not isinstance(rooms, list):
            errors.append("'rooms' must be a list")
            rooms = []
        if not isinstance(items, list):
            errors.append("'items' must be a list")
            items = []
        if not isinstance(monsters, list):
            errors.append("'monsters' must be a list")
            monsters = []
        if not (isinstance(start_room, int) or start_room is None):
            warnings.append("'start_room' should be an integer room id")

        # Basic structure
        title = adv.get("title") or ""
        if not title.strip():
            errors.append("Missing adventure title")

        if not rooms:
            errors.append("Adventure has no rooms")

        # Room id integrity and duplicates
        room_ids = []
        for r in rooms:
            if not isinstance(r, dict):
                errors.append("Encountered non-object in rooms list")
                continue
            rid = r.get("id")
            if rid is None:
                errors.append("A room is missing an 'id'")
            elif not isinstance(rid, int):
                errors.append("Room 'id' must be an integer")
            else:
                room_ids.append(rid)
        seen: set[int] = set()
        dupes_set: set[int] = set()
        for rid in room_ids:
            if rid in seen:
                dupes_set.add(rid)
            else:
                seen.add(rid)
        dupes = sorted(dupes_set)
        if dupes:
            errors.append(f"Duplicate room id(s): {dupes}")

        room_id_set = set(room_ids)

        # Start room validity
        if start_room not in room_id_set:
            errors.append(f"Start room {start_room} does not exist")

        # Exit targets and reciprocity
        total_exits = 0
        missing_reverse = 0
        unknown_directions = 0
        for r in rooms:
            rid = r.get("id")
            exits = r.get("exits", {})
            # Type sanity
            if not isinstance(exits, dict):
                errors.append(f"Room {rid} has invalid 'exits' (must be object/dict)")
                continue
            for direction, target in exits.items():
                total_exits += 1
                if not isinstance(direction, str):
                    warnings.append(f"Room {rid} has a non-string exit key: {direction}")
                    continue
                if target not in room_id_set and target != 0:
                    errors.append(
                        f"Room {rid} has exit '{direction}' to non-existent room {target}"
                    )
                # Reciprocity check (warning-level)
                rev = self._reverse_direction(direction)
                if rev is None:
                    unknown_directions += 1
                    warnings.append(f"Room {rid} has exit with unknown direction '{direction}'")
                if rev and target in room_id_set:
                    # Find target room
                    tr = next((x for x in rooms if x.get("id") == target), None)
                    if tr is not None:
                        trexits = tr.get("exits", {})
                        if not isinstance(trexits, dict):
                            msg = (
                                f"Room {target} exits not a dict; "
                                "skipping reciprocity check"
                            )
                            warnings.append(msg)
                            continue
                        if trexits.get(rev) != rid:
                            missing_reverse += 1
                            error_msg = (
                                f"Exit {rid}.{direction} -> {target} "
                                f"has no reverse {target}.{rev} -> {rid}"
                            )
                            warnings.append(error_msg)

        # Reachability from start_room (if valid)
        reachable = set()
        if start_room in room_id_set:
            # BFS
            q = deque([start_room])
            reachable.add(start_room)
            exits_map = {r.get("id"): dict(r.get("exits", {})) for r in rooms}
            while q:
                cur = q.popleft()
                for tgt in exits_map.get(cur, {}).values():
                    if isinstance(tgt, int) and tgt in room_id_set and tgt not in reachable:
                        reachable.add(tgt)
                        q.append(tgt)

        unreachable = sorted(list(room_id_set - reachable)) if room_id_set else []
        if unreachable:
            warnings.append(f"Unreachable rooms from start: {unreachable}")
            msg = (
                "Ensure main story areas are reachable from the start "
                "room or provide guidance."
            )
            suggestions.append(msg)

        # Room content quality
        for r in rooms:
            rid = r.get("id")
            name = (r.get("name") or "").strip()
            desc = (r.get("description") or "").strip()
            if not name:
                warnings.append(f"Room {rid} is missing a name")
            if not desc:
                warnings.append(f"Room {rid} is missing a description")
            # Dead-ends and isolation
            exits = r.get("exits", {})
            if isinstance(exits, dict):
                degree = len([t for t in exits.values() if isinstance(t, int) and t in room_id_set])
                if degree == 0:
                    warnings.append(f"Room {rid} is isolated (no exits)")
                elif degree == 1 and rid != start_room:
                    msg = (
                        f"Room {rid} is a dead-end; consider adding "
                        "a branch or a clue"
                    )
                    suggestions.append(msg)

        # Item placement sanity
        item_ids = []
        for it in items:
            if not isinstance(it, dict):
                errors.append("Encountered non-object in items list")
                continue
            loc = it.get("location")
            label = it.get("id", it.get("name", "<unnamed item>"))
            iid = it.get("id")
            if iid is not None:
                item_ids.append(iid)
            nm = (it.get("name") or "").strip()
            if not nm:
                warnings.append(f"Item {label} is missing a name")
            desc = (it.get("description") or "").strip()
            if not desc:
                warnings.append(f"Item {label} is missing a description")
            if isinstance(loc, int) and loc not in room_id_set:
                errors.append(f"Item {label} references missing room {loc}")
        # Duplicate item ids (only check when ids present and hashable)
        seen_i: set[Any] = set()
        dupe_items_set: set[Any] = set()
        for x in item_ids:
            try:
                if x in seen_i:
                    dupe_items_set.add(x)
                else:
                    seen_i.add(x)
            except TypeError:
                continue
        dupe_items = sorted(dupe_items_set)
        if dupe_items:
            errors.append(f"Duplicate item id(s): {dupe_items}")

        # Monster placement sanity
        monster_ids = []
        for mon in monsters:
            if not isinstance(mon, dict):
                errors.append("Encountered non-object in monsters list")
                continue
            mroom = mon.get("room")
            label = mon.get("id", mon.get("name", "<unnamed monster>"))
            mid = mon.get("id")
            if mid is not None:
                monster_ids.append(mid)
            nm = (mon.get("name") or "").strip()
            if not nm:
                warnings.append(f"Monster {label} is missing a name")
            desc = (mon.get("description") or "").strip()
            if not desc:
                warnings.append(f"Monster {label} is missing a description")
            if isinstance(mroom, int) and mroom not in room_id_set:
                errors.append(f"Monster {label} references missing room {mroom}")
        # Duplicate monster ids (only check when ids present and hashable)
        seen_m: set[Any] = set()
        dupe_mon_set: set[Any] = set()
        for x in monster_ids:
            try:
                if x in seen_m:
                    dupe_mon_set.add(x)
                else:
                    seen_m.add(x)
            except TypeError:
                continue
        dupe_mon = sorted(dupe_mon_set)
        if dupe_mon:
            errors.append(f"Duplicate monster id(s): {dupe_mon}")

        # Duplicate names (soft uniqueness suggestion)
        room_names = [(r.get("id"), (r.get("name") or "").strip()) for r in rooms]
        name_counts: dict[str, int] = {}
        for _, nm in room_names:
            if nm:
                name_counts[nm] = name_counts.get(nm, 0) + 1
        dup_name_list = sorted([nm for nm, cnt in name_counts.items() if cnt > 1])
        if dup_name_list:
            suggestions.append(f"Duplicate room names found: {dup_name_list}")

        # Path hints for unreachable rooms (BFS from start_room)
        path_hints = {}
        if start_room in room_id_set and unreachable:
            # Find shortest paths to each room from start
            dist = {start_room: 0}
            parent = {start_room: None}
            q = deque([start_room])
            exits_map = {r.get("id"): dict(r.get("exits", {})) for r in rooms}
            while q:
                cur = q.popleft()
                for tgt in exits_map.get(cur, {}).values():
                    if isinstance(tgt, int) and tgt in room_id_set and tgt not in dist:
                        dist[tgt] = dist[cur] + 1
                        parent[tgt] = cur
                        q.append(tgt)
            # For unreachable rooms, find closest reachable room
            for urid in unreachable:
                # Check all reachable rooms for exits pointing to unreachable area
                for rrid in reachable:
                    rexits = exits_map.get(rrid, {})
                    for tgt in rexits.values():
                        if isinstance(tgt, int) and tgt == urid:
                            path_hints[urid] = f"Add reverse exit from {urid} back to {rrid}"
                            break
                    if urid in path_hints:
                        break
                if urid not in path_hints:
                    msg = "No direct link found; consider adding an exit from a reachable room"
                    path_hints[urid] = msg

        # Pacing analysis: rooms with many vs. sparse exits
        branch_rooms = []
        sparse_rooms = []
        for r in rooms:
            rid = r.get("id")
            exits = r.get("exits", {})
            if isinstance(exits, dict):
                degree = len([t for t in exits.values() if isinstance(t, int) and t in room_id_set])
                if degree >= 4:
                    branch_rooms.append((rid, degree))
                elif degree <= 1 and rid != start_room:
                    sparse_rooms.append((rid, degree))

        if branch_rooms:
            branch_info = list(branch_rooms)
            suggestions.append(f"High-branch rooms (4+ exits): {branch_info}")
        if len(sparse_rooms) > len(rooms) * 0.3:
            sparse_count = len(sparse_rooms)
            msg = "Many sparse rooms; consider adding more connections"
            suggestions.append(f"{msg} ({sparse_count})")

        # Stats
        stats = {
            "rooms": len(rooms),
            "items": len(items),
            "monsters": len(monsters),
            "exits": total_exits,
            "reachable_rooms": len(reachable),
            "unreachable_rooms": len(unreachable),
            "missing_reverse_links": missing_reverse,
            "unknown_direction_exits": unknown_directions,
        }

        # Engine dry-run to catch runtime loader issues
        engine_errors, engine_info = self._engine_dry_run()
        errors.extend(engine_errors)

        return {
            "title": title or "(untitled)",
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "stats": stats,
            "engine_info": engine_info,
            "path_hints": path_hints,
        }

    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    def _format_verification_report(self, report: dict) -> str:
        lines: list[str] = []
        title = report.get("title", "(untitled)")
        stats = report.get("stats", {})
        errors = report.get("errors", [])
        warnings = report.get("warnings", [])
        suggestions = report.get("suggestions", [])

        lines.append("=" * 60)
        lines.append(f"GAME VERIFICATION: {title}")
        lines.append("=" * 60)
        lines.append("")
        # Engine dry-run details
        engine_info = report.get("engine_info", {})
        if engine_info:
            lines.append("Engine Dry-Run")
            lines.append("-" * 60)
            path = engine_info.get("engine_path")
            lines.append(f"Engine path: {path}")
            status = engine_info.get("status")
            lines.append(f"Status: {status}")
            if engine_info.get("details"):
                lines.append(f"Details: {engine_info.get('details')}")
            lines.append("")

        # Simulated playthrough details
        play = report.get("playthrough", {})
        if play:
            lines.append("Playthrough Simulation")
            lines.append("-" * 60)
            lines.append(f"Status: {play.get('status')}")
            visited = play.get("visited", [])
            if visited:
                lines.append(f"Visited rooms (order): {visited}")
            steps = play.get("steps", [])
            show = steps[:30]  # limit to first 30 actions for readability
            for i, st in enumerate(show, 1):
                act = st.get("action")
                frm = st.get("from")
                to = st.get("to")
                err = st.get("error")
                lines.append(f"{i:02d}. action='{act}' from={frm} to={to}")
                if err:
                    lines.append(f"    error: {err}")
                out = (st.get("output") or "").strip()
                if out:
                    snippet = out.splitlines()
                    snippet = snippet[:8]  # show up to 8 lines
                    for ln in snippet:
                        lines.append(f"    {ln}")
            if len(steps) > len(show):
                lines.append(f"    ... ({len(steps) - len(show)} more actions)")
            errs = play.get("errors", [])
            if errs:
                lines.append("")
                lines.append("Playthrough Errors")
                lines.append("-" * 60)
                for e in errs:
                    lines.append(f"- {e}")

            # Coverage metrics from playthrough
            total_rooms = stats.get('rooms', 0)
            if total_rooms > 0 and visited:
                visited_unique = len(set(visited))
                coverage = (visited_unique / total_rooms) * 100
                lines.append("")
                lines.append("Coverage Metrics")
                lines.append("-" * 60)
                lines.append(f"Rooms visited: {visited_unique}/{total_rooms} ({coverage:.1f}%)")
                lines.append(f"Max path depth: {len(visited)}")
                # Branch factor from steps (transitions between rooms)
                transitions = [st for st in steps if st.get('to') is not None]
                if transitions:
                    lines.append(f"Total transitions: {len(transitions)}")
            lines.append("")

        # Path hints section
        path_hints = report.get("path_hints", {})
        if path_hints:
            lines.append("Path Hints for Unreachable Rooms")
            lines.append("-" * 60)
            for room_id, hint in path_hints.items():
                lines.append(f"Room {room_id}: {hint}")
            lines.append("")

        lines.append("Summary")
        lines.append("-" * 60)
        rooms_count = stats.get('rooms', 0)
        exits_count = stats.get('exits', 0)
        items_count = stats.get('items', 0)
        monsters_count = stats.get('monsters', 0)
        summary_line = f"Rooms: {rooms_count} | Exits: {exits_count}"
        summary_line += f" | Items: {items_count} | Monsters: {monsters_count}"
        lines.append(summary_line)
        reachable = stats.get('reachable_rooms', 0)
        unreachable = stats.get('unreachable_rooms', 0)
        missing_links = stats.get('missing_reverse_links', 0)
        lines.append(
            f"Reach: {reachable} | Unreach: {unreachable} | Missing: {missing_links}"
        )
        lines.append("")

        if errors:
            lines.append("Errors")
            lines.append("-" * 60)
            for e in errors:
                lines.append(f"- {e}")
            lines.append("")

        if warnings:
            lines.append("Warnings")
            lines.append("-" * 60)
            for w in warnings:
                lines.append(f"- {w}")
            lines.append("")

        if suggestions:
            lines.append("Suggestions")
            lines.append("-" * 60)
            for s in suggestions:
                lines.append(f"- {s}")
            lines.append("")

        if not errors and not warnings and not suggestions:
            lines.append("No issues found. Your game looks great!")

        lines.append("")
        return "\n".join(lines)

    def _show_text_report(self, title: str, text: str):
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry("900x600")
        txt = scrolledtext.ScrolledText(top, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, text)
        txt.configure(state=tk.DISABLED)
        btn = ttk.Button(top, text="Close", command=top.destroy)
        btn.pack(pady=6)

    def _engine_dry_run(self) -> tuple[list[str], dict]:
        """Attempt to load current adventure via the actual engine to catch runtime issues.

        Returns (errors, info dict) where info contains engine path and status.
        """
        errors: list[str] = []
        info: dict = {}
        try:
            # Prepare temp adventure file
            adv_path = Path("adventures")
            adv_path.mkdir(parents=True, exist_ok=True)
            tmp = adv_path / "_verify_temp.json"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.adventure, f, indent=2)

            # Load engine
            engine_path = (
                Path(__file__).parent.parent.parent.parent / "sagacraft_engine.py"
            )
            info["engine_path"] = str(engine_path)
            spec = importlib.util.spec_from_file_location("sagacraft_engine", engine_path)
            if spec is None or spec.loader is None:
                errors.append("Engine load failed: could not create import spec")
                info["status"] = "spec failure"
                return errors, info

            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
            except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                errors.append(f"Engine import error: {exc}")
                info["status"] = "import error"
                info["details"] = str(exc)
                return errors, info

            # Instantiate and load
            game_cls = (
                getattr(mod, "ExtendedAdventureGame", None) or
                getattr(mod, "EnhancedAdventureGame", None) or
                getattr(mod, "AdventureGame", None)
            )
            if game_cls is None or not callable(game_cls):
                errors.append(
                    "Engine missing game class "
                    "(Extended/Enhanced/AdventureGame)"
                )
                info["status"] = "missing class"
                return errors, info

            try:
                game_ctor: Callable[[str], Any] = cast(Callable[[str], Any], game_cls)
                game = game_ctor(str(tmp))  # pylint: disable=not-callable
                game.load_adventure()
                info["status"] = "ok"
            except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                errors.append(f"Engine load_adventure failed: {exc}")
                info["status"] = "load error"
                info["details"] = str(exc)
        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            errors.append(f"Verification dry-run error: {exc}")
            info["status"] = "exception"
            info["details"] = str(exc)
        return errors, info

    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    def _simulate_playthrough(self, max_steps: int = 100) -> dict:
        """Run a bounded, deterministic playthrough: look, traverse exits, collect outputs.

        Uses the real engine with the current adventure; walks the graph from start_room
        using a stable direction order. Captures printed output for each action.
        """
        result: dict[str, Any] = {
            "status": "idle",
            "steps": [],
            "visited": [],
            "errors": [],
        }
        try:
            # Write temp adventure
            adv_path = Path("adventures")
            adv_path.mkdir(parents=True, exist_ok=True)
            tmp = adv_path / "_verify_play.json"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.adventure, f, indent=2)

            # Load engine
            engine_path = (
                Path(__file__).parent.parent.parent.parent / "sagacraft_engine.py"
            )
            spec = importlib.util.spec_from_file_location("sagacraft_engine", engine_path)
            if spec is None or spec.loader is None:
                result["status"] = "engine-spec-fail"
                result["errors"].append("Could not create engine spec")
                return result
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
            except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                result["status"] = "engine-import-fail"
                result["errors"].append(f"Engine import error: {exc}")
                return result

            game_cls = (
                getattr(mod, "ExtendedAdventureGame", None) or
                getattr(mod, "EnhancedAdventureGame", None) or
                getattr(mod, "AdventureGame", None)
            )
            if game_cls is None or not callable(game_cls):
                result["status"] = "no-game-class"
                result["errors"].append("Engine missing game class")
                return result

            game_ctor: Callable[[str], Any] = cast(Callable[[str], Any], game_cls)
            game = game_ctor(str(tmp))  # pylint: disable=not-callable
            game.load_adventure()
            result["status"] = "running"

            # Helper to capture one engine call
            def capture(callable_, *args, **kwargs):
                old = sys.stdout
                buf = StringIO()
                sys.stdout = buf
                err = None
                try:
                    callable_(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                    err = exc
                finally:
                    out = buf.getvalue()
                    sys.stdout = old
                return out, err

            # Step 0: look at start
            out, err = capture(game.look)
            err_str = str(err) if err else None
            step_data = {"action": "look", "output": out.strip(), "error": err_str}
            result["steps"].append(step_data)
            if err:
                result["status"] = "error"
                result["errors"].append(f"look failed: {err}")
                return result

            # Traverse rooms breadth-first via exits in stable direction order
            order = [
                "north",
                "south",
                "east",
                "west",
                "up",
                "down",
                "in",
                "out",
                "northeast",
                "northwest",
                "southeast",
                "southwest",
            ]
            visited = set()
            cur = getattr(game.player, "current_room", None)
            start_id = getattr(cur, "id", None)
            if start_id is None:
                result["status"] = "error"
                result["errors"].append("Start room not set")
                return result
            visited.add(start_id)
            q = deque([start_id])
            result["visited"].append(start_id)

            # Map id -> exits from current adventure
            rooms = self.adventure.get("rooms", [])
            exits_map = {r.get("id"): dict(r.get("exits", {})) for r in rooms}
            steps = 0

            while q and steps < max_steps:
                rid = q.popleft()
                exits = exits_map.get(rid, {})
                # Try exits in stable order first, then any others
                stable_dirs = [d for d in order if d in exits]
                other_dirs = [d for d in exits.keys() if d not in order]
                dirs = stable_dirs + other_dirs
                for d in dirs:
                    tgt = exits.get(d)
                    if not isinstance(tgt, int):
                        continue
                    # Issue move command
                    cmd = d
                    out, err = capture(game.process_command, cmd)
                    step = {"action": cmd, "from": rid, "to": tgt, "output": out.strip()}
                    step["error"] = str(err) if err else None
                    result["steps"].append(step)
                    steps += 1
                    if err:
                        result["status"] = "error"
                        result["errors"].append(
                            f"move '{cmd}' failed from {rid} to {tgt}: {err}"
                        )
                        if steps >= max_steps:
                            break
                        continue
                    # Track visited and enqueue
                    cur = getattr(game.player, "current_room", None)
                    cur_id = getattr(cur, "id", None)
                    if cur_id is not None and cur_id not in visited:
                        visited.add(cur_id)
                        result["visited"].append(cur_id)
                        q.append(cur_id)
                if steps >= max_steps:
                    break

            # Final look
            out, err = capture(game.look)
            err_str = str(err) if err else None
            final_step = {"action": "look", "output": out.strip(), "error": err_str}
            result["steps"].append(final_step)
            result["status"] = "ok" if not result["errors"] else "error"
        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            result["status"] = "exception"
            result["errors"].append(str(exc))
        return result

    # DSK import functionality removed

    def show_help(self):
        """Show help dialog"""
        help_text = """SagaCraft - Quick Start

Creating Adventures:
1. Fill in Adventure Info (title, author, intro)
2. Add Rooms (locations in your adventure)
3. Add Items (treasures, weapons, objects)
4. Add Monsters (enemies and NPCs)
5. Test your adventure (F5)
6. Save when done (Ctrl+S)

Tips:
- Room 0 exits = no exit
- Set start room to first room ID
- Use Preview tab to see JSON
- Test frequently while building
- Use Validate to check for errors

Keyboard Shortcuts:
Ctrl+N - New Adventure
Ctrl+O - Open Adventure
Ctrl+S - Save Adventure
F5 - Test Adventure
"""
        messagebox.showinfo("Quick Start Guide", help_text)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "🎮 SagaCraft v3.0.0\n\n"
            "A complete IDE for creating text adventures\n\n"
            "Features:\n"
            "• Item and NPC management\n"
            "• Adventure testing\n"
            "• 5 beautiful themes (Dark, Light, Dracula, Nord, Monokai)\n"
            "• Customizable fonts\n"
            "• 30 natural language commands\n\n"
            "Version 3.0.0",
        )

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)

    # Game play methods
    def print_game(self, text):
        """Print text to game output"""
        self.game_output.config(state=tk.NORMAL)
        self.game_output.insert(tk.END, text + "\n")
        self.game_output.see(tk.END)
        self.game_output.config(state=tk.DISABLED)

    def clear_game_output(self):
        """Clear the game output"""
        self.game_output.config(state=tk.NORMAL)
        self.game_output.delete("1.0", tk.END)
        self.game_output.config(state=tk.DISABLED)

    def _fail_play(self, message: str):
        """Display a play-tab error and reset transient state."""
        messagebox.showerror("Play Error", message)
        self.game_running = False
        self.test_badge_var.set("Play: Error")
        self.update_status("Play error")
        if self.point_and_click is not None:
            self.point_and_click.destroy()
            self.point_and_click = None

    def load_for_play(self):
        """Load an adventure file to play"""
        try:
            filename = filedialog.askopenfilename(
                title="Load Adventure to Play",
                initialdir="adventures",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if not filename:
                return

            loaded = self._load_adventure_file(filename)
            if not loaded:
                return

            self.clear_game_output()
            self.print_game("=" * 60)
            self.print_game(f"  LOADED: {self.adventure.get('title', 'Untitled')}")
            self.print_game("=" * 60)
            self.print_game("")
            self.print_game("Click '▶ Start Game' to begin playing!")
            self.print_game("")
            self.test_badge_var.set("Play: Adventure Loaded")
            self.validation_badge_var.set("Validation: —")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"ERROR in load_for_play: {exc}")
            traceback.print_exc()
            messagebox.showerror("Load Error", f"Failed to load adventure:\n{exc}")

    def start_game(self):  # pylint: disable=too-many-statements
        """Start playing the loaded adventure"""
        try:
            # Immediate UI feedback that the button was clicked
            self.print_game("\n[Play] Start button clicked. Preparing game...")
            # Save current adventure to temp file
            temp_file = "adventures/_temp_play.json"
            self.collect_adventure_data()

            validation_errors = self.validate_adventure(silent=True)
            if validation_errors:
                self.validation_badge_var.set(
                    f"Validation: ⚠ {len(validation_errors)} issue(s)"
                )
                # Stop if invalid to prevent confusing failures later
                messagebox.showwarning(
                    "Validation Issues",
                    "Cannot start game until validation issues are fixed."
                )
                self.test_badge_var.set("Play: Error")
                return
            self.validation_badge_var.set("Validation: ✅ Clean")

            Path("adventures").mkdir(parents=True, exist_ok=True)
            self.test_badge_var.set("Play: Starting...")
            self.game_instance = None
            self.game_running = False
            if self.point_and_click is not None:
                self.point_and_click.destroy()
                self.point_and_click = None

            try:
                with open(temp_file, "w", encoding="utf-8") as handle:
                    json.dump(self.adventure, handle, indent=2)
            except (OSError, TypeError) as exc:
                self._fail_play(f"Failed to prepare adventure file:\n{exc}")
                return

            engine_path = (
                Path(__file__).parent.parent.parent.parent / "sagacraft_engine.py"
            )
            spec = importlib.util.spec_from_file_location(
                "sagacraft_engine", engine_path
            )
            if spec is None or spec.loader is None:
                self._fail_play("Unable to load the enhanced game engine module.")
                return

            acs_module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(acs_module)
            except (FileNotFoundError, ImportError) as exc:
                self._fail_play(f"Failed to load game engine:\n{exc}")
                return

            self.clear_game_output()
            try:
                self.game_instance = acs_module.ExtendedAdventureGame(temp_file)
                self.game_instance.load_adventure()
            except (json.JSONDecodeError, OSError, AttributeError, RuntimeError) as exc:
                self.game_instance = None
                self._fail_play(f"Failed to initialize game:\n{exc}")
                return

            self._clear_mod_console()
            mod_messages = self._apply_active_mods_to_game()
            for message in mod_messages:
                self._log_mod_console(message)
                self.print_game(f"[Mods] {message}")

            self.game_running = True

            # Print introduction
            self.print_game("=" * 60)
            title = self.game_instance.adventure_title.upper()
            self.print_game(f"  {title}")
            self.print_game("=" * 60)
            self.print_game("")
            self.print_game(self.game_instance.adventure_intro)
            self.print_game("")
            self.print_game("=" * 60)
            self.print_game("")

            # Show starting room - capture output
            old_stdout = sys.stdout
            buffer = StringIO()
            sys.stdout = buffer
            try:
                self.game_instance.look()
            except (AttributeError, RuntimeError) as exc:
                sys.stdout = old_stdout
                self._fail_play(f"Failed to render starting room:\n{exc}")
                return

            output = buffer.getvalue()
            sys.stdout = old_stdout

            if output:
                self.print_game(output.rstrip())

            if self.command_entry is not None:
                self.command_entry.focus()
            self.update_status("Game started - enter commands below")
            self.test_badge_var.set("Play: Running")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"UNHANDLED ERROR in start_game: {exc}")
            traceback.print_exc()
            self._fail_play(f"Unexpected error:\n{exc}")

    def restart_game(self):
        """Restart the current game"""
        if self.game_running:
            self.test_badge_var.set("Play: Restarting")
            self.start_game()
        else:
            messagebox.showinfo("No Game", "Please start a game first")

    def send_command(self):
        """Send command to game engine"""
        try:
            if not self.game_running:
                messagebox.showinfo(
                    "No Game", "Please start the game first using '▶ Start Game'"
                )
                return

            command = self.command_entry.get().strip()
            if not command:
                return

            self.command_entry.delete(0, tk.END)
            self._process_game_command(command, echo=True)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"ERROR in send_command: {exc}")
            traceback.print_exc()
            messagebox.showerror("Command Error", f"Failed to process command:\n{exc}")

    def quick_save(self, slot: int):
        """Save the active session to a numbered slot."""
        if not self.game_running or not hasattr(self.game_instance, "save_game"):
            messagebox.showinfo("No Active Game", "Start the game before saving.")
            return

        Path("saves").mkdir(parents=True, exist_ok=True)
        result = self._capture_engine_output(self.game_instance.save_game, slot)
        if result:
            self.test_badge_var.set(f"Play: Saved slot {slot}")
        else:
            self.test_badge_var.set(f"Play: Save failed (slot {slot})")

    def quick_load(self, slot: int):
        """Load a numbered save slot into the active session."""
        if not self.game_running or not hasattr(self.game_instance, "load_game"):
            messagebox.showinfo("No Active Game", "Start the game before loading.")
            return

        result = self._capture_engine_output(self.game_instance.load_game, slot)
        if result:
            self.test_badge_var.set(f"Play: Loaded slot {slot}")
            # Automatically show the current room state after loading
            self._process_game_command("look", echo=True)
        else:
            self.test_badge_var.set(f"Play: Load failed (slot {slot})")

    def run_demo_script(self):
        """Execute a predefined sequence of commands."""
        if not self.game_running:
            messagebox.showinfo("No Game", "Start the game before running a demo.")
            return

        script_name = self.demo_script_var.get()
        commands = self.demo_scripts.get(script_name, [])
        if not commands:
            messagebox.showinfo("Demo", "Select a demo script to run.")
            return

        self.print_game(f"\n[Demo] Running '{script_name}'...")
        for cmd in commands:
            self._process_game_command(cmd, echo=True)

    def _capture_engine_output(self, func, *args, **kwargs):
        """Capture engine output so it appears in the play console."""
        result, raw = capture_stdout(func, *args, **kwargs)
        output = raw.strip()
        if output:
            self.print_game(output)
        return result

    def _process_game_command(self, command: str, echo: bool = False):
        """Process a command through the engine with captured output."""
        if echo:
            self.print_game(f"\n> {command}")

        lowered = command.lower()
        if lowered in ["quit", "q", "exit"]:
            self.print_game("\nThanks for playing!")
            self.print_game("=" * 60)
            self.game_running = False
            self.update_status("Game ended")
            self.test_badge_var.set("Play: Ended")
            return

        output, error = run_engine_command(self.game_instance, command)

        if error is not None:
            self.print_game(f"\nError: {error}")
            self.test_badge_var.set("Play: Error")
            return

        if output:
            self.print_game(output.rstrip())

        if getattr(self.game_instance, "game_over", False):
            self.print_game("\n" + "=" * 60)
            self.print_game("GAME OVER")
            self.print_game("=" * 60)
            self.game_running = False
            self.update_status("Game ended")
            self.test_badge_var.set("Play: Ended")

        if self.point_and_click is not None:
            if self.game_running and self.game_instance is not None:
                current_room = getattr(self.game_instance.player, "current_room", 0)
                self.point_and_click.set_current_room(current_room)
            else:
                self.point_and_click.destroy()
                self.point_and_click = None

    def _load_ui_preferences(self):
        """Load UI theme and font settings from config/engine.json."""
        config_path = Path(__file__).resolve().parents[3] / "config" / "engine.json"
        if not config_path.exists():
            return
        data = safe_read_json_mapping(config_path)
        ui_cfg = data.get("ui", {}) if isinstance(data.get("ui", {}), dict) else {}

        theme_name = ui_cfg.get("theme")
        if isinstance(theme_name, str):
            for candidate, colors in self.themes.items():
                if candidate.lower() == theme_name.lower():
                    self.current_theme = candidate
                    self.colors = colors
                    break

        font_family = ui_cfg.get("font_family")
        if isinstance(font_family, str):
            self.current_font_family = font_family

        font_size = ui_cfg.get("font_size")
        if isinstance(font_size, int) and 6 <= font_size <= 48:
            self.current_font_size = font_size

        editor_font = ui_cfg.get("editor_font_family")
        if isinstance(editor_font, str):
            self.editor_font_family = editor_font

        editor_size = ui_cfg.get("editor_font_size")
        if isinstance(editor_size, int) and 6 <= editor_size <= 48:
            self.editor_font_size = editor_size

    def _save_ui_preferences(self):
        """Persist UI theme and font selections to config/engine.json."""
        config_path = Path(__file__).resolve().parents[3] / "config" / "engine.json"
        data = safe_read_json_mapping(config_path) if config_path.exists() else {}

        update_ui_preferences(
            data,
            theme=self.current_theme,
            font_family=self.current_font_family,
            font_size=self.current_font_size,
            extra={
                "editor_font_family": self.editor_font_family,
                "editor_font_size": self.editor_font_size,
            },
        )

        try:
            write_json_mapping(config_path, data)
        except OSError:
            pass

    def change_theme(self, theme_name):
        """Change the color theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.colors = self.themes[theme_name]
            self.setup_styles()
            self.refresh_all_widgets()
            self.update_status(f"Theme changed to: {theme_name}")
            self._save_ui_preferences()

    def change_font_family(self, font_family):
        """Change the UI font family"""
        self.current_font_family = font_family
        self.setup_styles()
        self.refresh_all_widgets()
        self.update_status(f"Font changed to: {font_family}")
        self._save_ui_preferences()

    def change_font_size(self, font_size):
        """Change the UI font size"""
        self.current_font_size = font_size
        self.setup_styles()
        self.refresh_all_widgets()
        self.update_status(f"Font size changed to: {font_size}pt")
        self._save_ui_preferences()

    def change_editor_font(self, font_family):
        """Change the editor font family"""
        self.editor_font_family = font_family
        self.apply_editor_fonts()
        self.update_status(f"Editor font changed to: {font_family}")
        self._save_ui_preferences()

    def apply_editor_fonts(self):
        """Apply editor font to all text widgets"""
        editor_font = (self.editor_font_family, self.editor_font_size)

        # Update intro text
        if hasattr(self, "intro_text"):
            self.intro_text.config(font=editor_font)

        # Update description text
        if hasattr(self, "description_text"):
            self.description_text.config(font=editor_font)

        # Update game output
        if hasattr(self, "game_output"):
            self.game_output.config(font=editor_font)

        if self.scene_narration_text is not None:
            self.scene_narration_text.config(font=editor_font)

    def refresh_all_widgets(self):
        """Refresh all widgets to apply new theme"""
        # Re-setup the UI with new colors
        self.root.configure(bg=self.colors["bg"])

        # Update status bar
        if hasattr(self, "status_bar"):
            self.status_bar.config(bg=self.colors["panel"], fg=self.colors["fg"])

        # Update all text widgets with new colors
        if hasattr(self, "intro_text"):
            self.intro_text.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

        if hasattr(self, "description_text"):
            self.description_text.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

        if hasattr(self, "game_output"):
            self.game_output.config(bg=self.colors["text_bg"], fg=self.colors["fg"])

        if hasattr(self, "game_input"):
            self.game_input.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

        if self.scene_narration_text is not None:
            self.scene_narration_text.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

        if self.mod_detail_text is not None:
            self.mod_detail_text.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

        if self.mod_console is not None:
            self.mod_console.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

        if self.mod_tree is not None:
            self.refresh_mod_catalog_ui()

    # ------------------------------------------------------------------
    # Recent files and demo support
    # ------------------------------------------------------------------

    def _recent_files_path(self) -> Path:
        """Return the path containing the recent adventure list."""
        return Path("config") / "recent_adventures.json"

    def _load_recent_files(self):
        """Load a small recent-file list from disk."""
        path = self._recent_files_path()
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

        if isinstance(data, list):
            cleaned = []
            for entry in data:
                if isinstance(entry, str) and Path(entry).exists():
                    cleaned.append(entry)
            return cleaned[:5]
        return []

    def _save_recent_files(self):
        """Persist the current recent file list."""
        path = self._recent_files_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(self.recent_files[:5], handle, indent=2)

    def _remember_recent_file(self, filepath: str):
        """Insert a file into the MRU list and refresh the display."""
        if not filepath:
            return

        resolved = str(Path(filepath).resolve())
        if resolved in self.recent_files:
            self.recent_files.remove(resolved)
        self.recent_files.insert(0, resolved)
        self.recent_files = self.recent_files[:5]
        self._save_recent_files()
        self.refresh_recent_files_ui()

    def refresh_recent_files_ui(self):
        """Update the recent file buttons in the info tab."""
        if not self.recent_list_container:
            return

        for child in self.recent_list_container.winfo_children():
            child.destroy()

        if not self.recent_files:
            ttk.Label(
                self.recent_list_container,
                text="No recent adventures yet. Open or save a project to populate this list.",
                style="TLabel",
            ).pack(anchor=tk.W)
            return

        for filepath in self.recent_files:
            display = os.path.basename(filepath)
            ttk.Button(
                self.recent_list_container,
                text=display,
                command=lambda p=filepath: self.open_recent_file(p),
                width=40,
            ).pack(anchor=tk.W, pady=2)

    def open_recent_file(self, filepath: str):
        """Open a recently-used adventure file."""
        path = Path(filepath)
        if not path.exists():
            messagebox.showwarning("Missing File", f"Cannot find {filepath}.")
            if filepath in self.recent_files:
                self.recent_files.remove(filepath)
                self._save_recent_files()
                self.refresh_recent_files_ui()
            return

        self._load_adventure_file(str(path.resolve()))

    def _default_demo_scripts(self):
        """Provide canned demo command sequences for quick showcasing."""
        return {
            "Quest Overview": ["look", "quests"],
            "Meet Quartermaster": ["east", "talk dex", "trade dex"],
            "Explore Atrium": ["look", "north", "look"],
        }

    def reset_view_settings(self):
        """Reset theme and font to defaults"""
        self.current_theme = "Dark"
        self.colors = self.themes[self.current_theme]
        self.current_font_family = "Segoe UI"
        self.current_font_size = 10
        self.editor_font_family = "Consolas"
        self.editor_font_size = 11
        self.setup_styles()
        self.refresh_all_widgets()
        self.apply_editor_fonts()
        self.update_status("View settings reset to defaults")

    def _get_active_mods(self) -> list[str]:
        """Detect which mods are currently active/enabled in the adventure."""
        if not isinstance(self.adventure, dict):
            return []
        mods = self.adventure.get("mods", [])
        if not isinstance(mods, list):
            return []
        active: list[str] = []
        for m in mods:
            if isinstance(m, dict) and m.get("enabled", False):
                active.append(m.get("name", "unknown"))
        return active

    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    def show_reachability_map(self):
        """Display a simple text-based reachability map showing room connectivity."""
        win = tk.Toplevel(self.root)
        win.title("Reachability Map")
        win.geometry("500x600")

        bg_color = self.colors.get("panel", "#222")
        fg_color = self.colors.get("fg", "#eee")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, bg=bg_color, fg=fg_color)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Compute reachability from start room
        rooms = self.adventure.get("rooms", [])
        room_ids = {r.get("id") for r in rooms}
        start_room = self.adventure.get("start_room", 1)

        visited = set()
        q = deque([start_room])
        visited.add(start_room)

        while q:
            cur = q.popleft()
            cur_room = next((r for r in rooms if r.get("id") == cur), None)
            if not cur_room:
                continue
            exits = cur_room.get("exits", {})
            if isinstance(exits, dict):
                for direction, target in exits.items():
                    if isinstance(target, int) and target in room_ids and target not in visited:
                        visited.add(target)
                        q.append(target)

        unreachable = room_ids - visited

        # Format output
        lines = ["REACHABILITY MAP", "=" * 50, ""]
        lines.append(f"Start room: {start_room}")
        lines.append(f"Total rooms: {len(rooms)}")
        lines.append(f"Reachable: {len(visited)} | Unreachable: {len(unreachable)}")
        lines.append("")

        lines.append("REACHABLE ROOMS:")
        lines.append("-" * 50)
        for room in sorted(rooms, key=lambda r: r.get("id", 0)):
            rid = room.get("id")
            if rid in visited:
                name = room.get("name", "?")
                exits = room.get("exits", {})
                exit_str = ", ".join(exits.keys()) if isinstance(exits, dict) else ""
                lines.append(f"  #{rid}: {name} [exits: {exit_str}]")

        if unreachable:
            lines.append("")
            lines.append("UNREACHABLE ROOMS (⚠️  Need connections):")
            lines.append("-" * 50)
            for room in sorted(rooms, key=lambda r: r.get("id", 0)):
                rid = room.get("id")
                if rid in unreachable:
                    name = room.get("name", "?")
                    lines.append(f"  #{rid}: {name} ⚠️")

        lines.append("")
        lines.append("MISSING REVERSE EXITS:")
        lines.append("-" * 50)
        missing = 0
        for room in rooms:
            rid = room.get("id")
            exits = room.get("exits", {})
            if not isinstance(exits, dict):
                continue
            for direction, target in exits.items():
                if not isinstance(target, int) or target not in room_ids:
                    continue
                rev = self._reverse_direction(direction)
                if rev:
                    target_room = next((r for r in rooms if r.get("id") == target), None)
                    if target_room and rev not in target_room.get("exits", {}):
                        lines.append(f"  #{rid} →{direction}→ #{target} (missing ←{rev}←)")
                        missing += 1
        if missing == 0:
            lines.append("  ✅ All reciprocal exits present!")

        text.insert(tk.END, "\n".join(lines))
        text.configure(state=tk.DISABLED)

    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    def show_graph_analytics(self):
        """Display graph analytics: branching factor heatmap, articulation points, dead ends."""
        win = tk.Toplevel(self.root)
        win.title("Graph Analytics")
        win.geometry("600x700")

        text = scrolledtext.ScrolledText(
            win,
            wrap=tk.WORD,
            bg=self.colors.get("panel", "#222"),
            fg=self.colors.get("fg", "#eee"),
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        rooms = self.adventure.get("rooms", [])
        room_ids = {r.get("id") for r in rooms}
        start_room = self.adventure.get("start_room", 1)

        lines = ["GRAPH ANALYTICS", "=" * 60, ""]

        # Compute branching factor (out-degree)
        branch_factor = {}
        in_degree = {}
        for room in rooms:
            rid = room.get("id")
            exits = room.get("exits", {})
            if isinstance(exits, dict):
                degree = sum(
                    1
                    for t in exits.values()
                    if isinstance(t, int) and t in room_ids
                )
            else:
                degree = 0
            branch_factor[rid] = degree
            if rid not in in_degree:
                in_degree[rid] = 0

        # Count in-degrees (reverse paths)
        for room in rooms:
            rid = room.get("id")
            exits = room.get("exits", {})
            if isinstance(exits, dict):
                for _direction, target in exits.items():
                    if isinstance(target, int) and target in room_ids:
                        in_degree[target] = in_degree.get(target, 0) + 1

        # Find articulation points via cutset analysis
        articulation = []
        for test_room in rooms:
            test_rid = test_room.get("id")
            if test_rid == start_room:
                continue
            # Simple check: if removing this room disconnects any other reachable rooms
            visited = set()
            q = deque([start_room])
            visited.add(start_room)
            while q:
                cur = q.popleft()
                if cur == test_rid:
                    continue
                cur_room = next((r for r in rooms if r.get("id") == cur), None)
                if not cur_room:
                    continue
                exits = cur_room.get("exits", {})
                if isinstance(exits, dict):
                    for target in exits.values():
                        if (
                            isinstance(target, int)
                            and target in room_ids
                            and target not in visited
                            and target != test_rid
                        ):
                            visited.add(target)
                            q.append(target)
            # If removing test_room isolates any other rooms, it's an articulation point
            full_reachable = set()
            q = deque([start_room])
            full_reachable.add(start_room)
            while q:
                cur = q.popleft()
                cur_room = next((r for r in rooms if r.get("id") == cur), None)
                if not cur_room:
                    continue
                exits = cur_room.get("exits", {})
                if isinstance(exits, dict):
                    for target in exits.values():
                        if (
                            isinstance(target, int)
                            and target in room_ids
                            and target not in full_reachable
                        ):
                            full_reachable.add(target)
                            q.append(target)

            if len(visited) < len(full_reachable):
                articulation.append((test_rid, test_room.get("name", "?")))

        # Branching heatmap
        lines.append("BRANCHING FACTOR HEATMAP (out-degree):")
        lines.append("-" * 60)
        high_branch = [(rid, deg) for rid, deg in branch_factor.items() if deg >= 4]
        medium_branch = [(rid, deg) for rid, deg in branch_factor.items() if 2 <= deg < 4]
        low_branch = [(rid, deg) for rid, deg in branch_factor.items() if 0 < deg < 2]
        dead_ends = [(rid, deg) for rid, deg in branch_factor.items() if deg == 0]

        if high_branch:
            lines.append("  🔴 HIGH BRANCHING (4+ exits) - Choice hubs:")
            for rid, deg in sorted(high_branch):
                room_name = next(
                    (r.get("name", "?") for r in rooms if r.get("id") == rid),
                    "?",
                )
                lines.append(f"    #{rid}: {room_name} ({deg} exits)")

        if medium_branch:
            lines.append("  🟡 MEDIUM BRANCHING (2-3 exits) - Normal exploration:")
            for rid, deg in sorted(medium_branch):
                room_name = next(
                    (r.get("name", "?") for r in rooms if r.get("id") == rid),
                    "?",
                )
                lines.append(f"    #{rid}: {room_name} ({deg} exits)")

        if low_branch:
            lines.append("  🟢 LOW BRANCHING (1 exit) - Linear sections:")
            for rid, deg in sorted(low_branch):
                room_name = next((r.get("name", "?") for r in rooms if r.get("id") == rid), "?")
                lines.append(f"    #{rid}: {room_name} ({deg} exit)")

        if dead_ends:
            lines.append("  ⚫ DEAD ENDS (0 exits) - Terminal rooms:")
            for rid, deg in sorted(dead_ends):
                room_name = next((r.get("name", "?") for r in rooms if r.get("id") == rid), "?")
                lines.append(f"    #{rid}: {room_name}")

        # Articulation points
        lines.append("")
        lines.append("ARTICULATION POINTS (critical for connectivity):")
        lines.append("-" * 60)
        if articulation:
            for rid, name in articulation:
                in_deg = in_degree.get(rid, 0)
                out_deg = branch_factor.get(rid, 0)
                lines.append(f"  ⚠️  #{rid}: {name} (in={in_deg}, out={out_deg})")
            lines.append("  → Removing any of these isolates other rooms!")
        else:
            lines.append("  ✅ No critical articulation points found.")

        # Summary and suggestions
        lines.append("")
        lines.append("SUMMARY & SUGGESTIONS:")
        lines.append("-" * 60)
        avg_branch = sum(branch_factor.values()) / len(branch_factor) if branch_factor else 0
        lines.append(f"  Total rooms: {len(rooms)}")
        lines.append(f"  Average branching factor: {avg_branch:.2f}")
        lines.append(f"  Dead ends: {len(dead_ends)}")

        if len(dead_ends) > len(rooms) * 0.4:
            lines.append("  💡 Many dead ends—consider adding more exits for exploration.")

        if avg_branch < 1.5 and len(rooms) > 5:
            lines.append(
                "  💡 Low branching suggests linear gameplay—add shortcuts for replayability."
            )

        if len(high_branch) > len(rooms) * 0.3:
            lines.append(
                "  💡 Many high-branch rooms—may be overwhelming; simplify key choice points."
            )

        if articulation:
            lines.append("  💡 Critical bottlenecks exist—consider alternate paths for robustness.")

        text.insert(tk.END, "\n".join(lines))
        text.configure(state=tk.DISABLED)

    def show_asset_browser(self):  # pylint: disable=too-many-statements
        """Browse and preview visual assets from assets/visual."""

        win = tk.Toplevel(self.root)
        win.title("Asset Browser")
        win.geometry("800x600")

        assets_dir = Path("assets/visual")
        if not assets_dir.exists():
            assets_dir.mkdir(parents=True, exist_ok=True)

        # Left panel: file list
        left_frame = ttk.Frame(win)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(left_frame, text="Assets:").pack(anchor=tk.W)

        asset_listbox = tk.Listbox(left_frame, height=20, width=30)
        asset_listbox.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=asset_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        asset_listbox.config(yscrollcommand=scrollbar.set)

        # Right panel: preview
        right_frame = ttk.Frame(win)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Preview:").pack(anchor=tk.W)

        preview_text = scrolledtext.ScrolledText(
            right_frame,
            height=20,
            width=40,
            wrap=tk.WORD,
            bg=self.colors.get("text_bg", "#1a1a1a"),
            fg=self.colors.get("fg", "#eee"),
        )
        preview_text.pack(fill=tk.BOTH, expand=True)

        def load_assets():
            """Populate asset list."""
            asset_listbox.delete(0, tk.END)
            if not assets_dir.exists():
                asset_listbox.insert(tk.END, "(no assets/visual directory)")
                return

            assets = sorted(assets_dir.glob("*"))
            for asset in assets:
                if asset.is_file():
                    size_kb = asset.stat().st_size / 1024
                    asset_listbox.insert(tk.END, f"{asset.name} ({size_kb:.1f}KB)")

        def preview_asset(_event=None):
            """Preview selected asset."""
            sel = asset_listbox.curselection()
            if not sel:
                return

            asset_name = asset_listbox.get(sel[0]).split()[0]
            asset_path = assets_dir / asset_name

            preview_text.configure(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)

            try:
                if asset_path.suffix.lower() in [".ppm", ".txt"]:
                    with open(asset_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(1000)
                    header = (
                        f"File: {asset_name}\n"
                        f"Size: {asset_path.stat().st_size} bytes\n"
                        f"Type: {asset_path.suffix}\n\n"
                    )
                    preview_text.insert(tk.END, header)
                    preview_text.insert(
                        tk.END,
                        "Content (first 1000 chars):\n" + "=" * 40 + "\n\n" + content,
                    )
                else:
                    preview_text.insert(
                        tk.END,
                        (
                            f"File: {asset_name}\n"
                            f"Size: {asset_path.stat().st_size} bytes\n"
                            f"Type: {asset_path.suffix}\n\n"
                            "Binary file (preview not available)"
                        ),
                    )
            except Exception as e:  # pylint: disable=broad-exception-caught
                preview_text.insert(tk.END, f"Error reading asset: {e}")

            preview_text.configure(state=tk.DISABLED)

        asset_listbox.bind("<<ListboxSelect>>", preview_asset)

        # Bottom buttons
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Refresh", command=load_assets).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame,
            text="Open Folder",
            command=lambda: __import__("webbrowser").open(str(assets_dir)),
        ).pack(side=tk.LEFT, padx=5)

        load_assets()

    def show_mod_sandbox(self):  # pylint: disable=too-many-statements
        """Load mods and show delta changes to the game state."""
        win = tk.Toplevel(self.root)
        win.title("Mod Sandbox")
        win.geometry("700x600")

        # Top section: mod selection
        top_frame = ttk.Frame(win)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(top_frame, text="Mods:").pack(anchor=tk.W)

        mods_dir = Path("mods/examples")
        available_mods = []
        if mods_dir.exists():
            available_mods = [
                f.stem
                for f in mods_dir.glob("*.py")
                if f.name not in ["__init__.py", "README.md"]
            ]

        # Current mods in adventure
        current_mods = self.adventure.get("mods", [])
        enabled_mod_names = {
            m.get("name")
            for m in current_mods
            if isinstance(m, dict) and m.get("enabled")
        }

        mod_vars = {}
        for mod_name in available_mods:
            var = tk.BooleanVar(value=mod_name in enabled_mod_names)
            mod_vars[mod_name] = var
            ttk.Checkbutton(top_frame, text=mod_name, variable=var).pack(anchor=tk.W, pady=2)

        # Output area
        output_frame = ttk.Frame(win)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        output = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            bg=self.colors.get("text_bg", "#1a1a1a"),
            fg=self.colors.get("fg", "#eee"),
        )
        output.pack(fill=tk.BOTH, expand=True)

        def analyze_mods():  # pylint: disable=too-many-statements,too-many-locals,too-many-branches
            """Load selected mods and show deltas."""
            output.configure(state=tk.NORMAL)
            output.delete(1.0, tk.END)

            selected = [name for name, var in mod_vars.items() if var.get()]

            if not selected:
                output.insert(tk.END, "No mods selected.")
                output.configure(state=tk.DISABLED)
                return

            lines = ["MOD SANDBOX ANALYSIS", "=" * 60, ""]

            # Get baseline stats
            baseline_rooms = len(self.adventure.get("rooms", []))
            baseline_items = len(self.adventure.get("items", []))
            baseline_monsters = len(self.adventure.get("monsters", []))

            lines.append("BASELINE (no mods):")
            lines.append(f"  Rooms: {baseline_rooms}")
            lines.append(f"  Items: {baseline_items}")
            lines.append(f"  Monsters: {baseline_monsters}")
            lines.append("")

            # Try to load and analyze each mod
            lines.append("MODS TO LOAD:")
            lines.append("-" * 60)

            for mod_name in selected:
                mod_path = mods_dir / f"{mod_name}.py"
                if not mod_path.exists():
                    lines.append(f"  ❌ {mod_name}: file not found")
                    continue

                lines.append(f"  📦 {mod_name}")

                try:
                    spec = importlib.util.spec_from_file_location(mod_name, mod_path)
                    if spec is None or spec.loader is None:
                        lines.append("     ⚠️  Could not load module spec")
                        continue

                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)

                    # Check for apply_mod or modify_game function
                    if hasattr(mod, "apply_mod"):
                        lines.append("     ✓ apply_mod() found")
                    elif hasattr(mod, "modify_game"):
                        lines.append("     ✓ modify_game() found")
                    else:
                        lines.append("     ⚠️  No apply_mod() or modify_game() function")

                    # Check for events hook
                    if hasattr(mod, "on_event"):
                        lines.append("     ✓ Event handlers registered")

                    # List any new commands or items
                    if hasattr(mod, "__doc__") and mod.__doc__:
                        doc_lines = mod.__doc__.split("\n")
                        for doc_line in doc_lines[:3]:
                            if doc_line.strip():
                                lines.append(f"     {doc_line.strip()}")

                except Exception as e:  # pylint: disable=broad-exception-caught
                    lines.append(f"     ❌ Error loading: {e}")

            lines.append("")
            lines.append("DELTA IMPACT:")
            lines.append("-" * 60)
            lines.append("  ⚠️  Run 'Play in IDE' to test mods with actual gameplay")
            lines.append(f"  💡 Load order: {', '.join(selected)}")
            lines.append("  💡 Monitor console for mod events and conflicts")

            output.insert(tk.END, "\n".join(lines))
            output.configure(state=tk.DISABLED)

        # Bottom buttons
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Analyze", command=analyze_mods).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame,
            text="Play with Mods",
            command=lambda: (analyze_mods(), self.play_in_ide_console()),
        ).pack(side=tk.LEFT, padx=5)

        analyze_mods()

    def show_snippets_menu(self):
        """Show snippet insertion menu with templates."""
        snippets_win = tk.Toplevel(self.root)
        snippets_win.title("Snippets & Templates")
        snippets_win.geometry("500x400")

        ttk.Label(snippets_win, text="Quick Snippets:").pack(anchor=tk.W, padx=10, pady=10)

        # Available templates
        templates = {
            "Simple Room": {
                "id": 1,
                "name": "Room Name",
                "description": "A simple room.",
                "exits": {},
                "is_dark": False,
            },
            "Dark Room": {
                "id": 1,
                "name": "Dark Chamber",
                "description": "It is pitch black. You can't see anything.",
                "exits": {},
                "is_dark": True,
            },
            "Hub Room (4 exits)": {
                "id": 1,
                "name": "Central Hub",
                "description": "A central hub with exits in all directions.",
                "exits": {"north": 2, "south": 3, "east": 4, "west": 5},
                "is_dark": False,
            },
            "Dead End": {
                "id": 1,
                "name": "Dead End",
                "description": "You've reached a dead end.",
                "exits": {},
                "is_dark": False,
            },
        }

        item_templates = {
            "Key": {
                "id": "key",
                "name": "Key",
                "description": "A brass key.",
                "location": 1,
                "takeable": True,
            },
            "Treasure": {
                "id": "treasure",
                "name": "Treasure Chest",
                "description": "A chest filled with gold.",
                "location": 1,
                "takeable": False,
            },
            "Sword": {
                "id": "sword",
                "name": "Sword",
                "description": "A sharp iron sword.",
                "location": 1,
                "takeable": True,
            },
        }

        frame = ttk.Frame(snippets_win)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Rooms:").pack(anchor=tk.W, pady=5)

        def make_insert_room(template: dict):
            def insert_room():
                new_id = (
                    max(
                        (r.get("id", 0) for r in self.adventure.get("rooms", [])),
                        default=0,
                    )
                    + 1
                )
                data_copy = dict(template)
                data_copy["id"] = new_id
                self.adventure["rooms"].append(data_copy)
                self.modified = True
                self.refresh_rooms_list()
                self.update_status(f"Inserted room: {template.get('name', '')}")
                snippets_win.destroy()

            return insert_room

        for template_name, template_data in templates.items():
            ttk.Button(
                frame,
                text=f"  → {template_name}",
                command=make_insert_room(template_data),
            ).pack(anchor=tk.W, pady=2)

        ttk.Label(frame, text="Items:").pack(anchor=tk.W, pady=5)

        def make_insert_item(template: dict):
            def insert_item():
                new_id = (
                    f"{template.get('id', 'item')}_"
                    f"{len(self.adventure.get('items', []))}"
                )
                data_copy = dict(template)
                data_copy["id"] = new_id
                self.adventure["items"].append(data_copy)
                self.modified = True
                self.refresh_items_list()
                self.update_status(f"Inserted item: {template.get('name', '')}")
                snippets_win.destroy()

            return insert_item

        for template_name, template_data in item_templates.items():
            ttk.Button(
                frame,
                text=f"  → {template_name}",
                command=make_insert_item(template_data),
            ).pack(anchor=tk.W, pady=2)

        ttk.Label(frame, text="Starter Layouts:").pack(anchor=tk.W, pady=5)

        def use_hub_spoke():
            """Create a hub-and-spoke adventure layout."""
            if len(self.adventure.get("rooms", [])) > 1:
                if not messagebox.askyesno(
                    "Overwrite", "This will replace current rooms. Continue?"
                ):
                    return
            self.adventure["rooms"] = [
                {
                    "id": 1,
                    "name": "Hub",
                    "description": "Central hub.",
                    "exits": {"north": 2, "east": 3, "south": 4, "west": 5},
                    "is_dark": False,
                },
                {
                    "id": 2,
                    "name": "North Wing",
                    "description": "Northern area.",
                    "exits": {"south": 1},
                    "is_dark": False,
                },
                {
                    "id": 3,
                    "name": "East Wing",
                    "description": "Eastern area.",
                    "exits": {"west": 1},
                    "is_dark": False,
                },
                {
                    "id": 4,
                    "name": "South Wing",
                    "description": "Southern area.",
                    "exits": {"north": 1},
                    "is_dark": False,
                },
                {
                    "id": 5,
                    "name": "West Wing",
                    "description": "Western area.",
                    "exits": {"east": 1},
                    "is_dark": False,
                },
            ]
            self.adventure["start_room"] = 1
            self.modified = True
            self.refresh_rooms_list()
            self.update_status("Created hub-and-spoke layout")
            snippets_win.destroy()

        ttk.Button(frame, text="  → Hub & Spoke (5 rooms)", command=use_hub_spoke).pack(
            anchor=tk.W, pady=2
        )


def main():
    """Main entry point"""
    root = tk.Tk()
    AdventureIDE(root)
    root.mainloop()


if __name__ == "__main__":
    main()
