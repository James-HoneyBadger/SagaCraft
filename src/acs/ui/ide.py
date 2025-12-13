#!/usr/bin/env python3
"""SagaCraft - Graphical Adventure Editor

A complete IDE for creating, editing, and playing text adventures.
"""

# pylint: disable=too-many-lines

import ast
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import difflib
import json
import os
import sys
import importlib.util
from pathlib import Path
from io import StringIO

from acs.tools.modding import ModdingSystem


class AdventureIDE:
    """Main IDE window for SagaCraft"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎮 SagaCraft - IDE")
        self.root.geometry("1400x900")

        # Theme definitions
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

        # Current theme and font settings
        self.current_theme = "Dark"
        self.colors = self.themes[self.current_theme]
        self.current_font_family = "Segoe UI"
        self.current_font_size = 10
        self.editor_font_family = "Consolas"
        self.editor_font_size = 11

        # Configure dark theme
        self.setup_styles()

        # Current adventure data
        self.adventure = {
            "title": "New Adventure",
            "author": "",
            "intro": "",
            "start_room": 1,
            "rooms": [],
            "items": [],
            "monsters": [],
            "effects": [],
            "mode": "text",
            "scenes": [],
        }

        self.current_file = None
        self.modified = False

        # Recent files and quick status state
        self.recent_files = self._load_recent_files()
        self.recent_list_container = None
        self.validation_badge_var = tk.StringVar(value="Validation: —")
        self.test_badge_var = tk.StringVar(value="Play: Idle")
        self.demo_scripts = self._default_demo_scripts()
        self.demo_script_var = tk.StringVar()
        self.game_instance = None
        self.game_running = False
        self.point_and_click = None
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

        # Widget references populated during UI construction
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
        self.scenes_listbox = None
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

        self._ensure_mod_root()
        self._load_mod_state()
        self.setup_ui()
        self.new_adventure()

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
        # Menu bar with dark theme
        menubar = tk.Menu(
            self.root,
            bg=self.colors["sidebar"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(
            label="🆕 New Adventure", command=self.new_adventure, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="📂 Open...", command=self.open_adventure, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="💾 Save", command=self.save_adventure, accelerator="Ctrl+S"
        )
        file_menu.add_command(label="💾 Save As...", command=self.save_adventure_as)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.quit_ide)

        # Tools menu
        tools_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="🛠️ Tools", menu=tools_menu)
        tools_menu.add_command(
            label="▶️ Test Adventure", command=self.test_adventure, accelerator="F5"
        )
        tools_menu.add_command(
            label="✓ Validate Adventure", command=self.validate_adventure
        )
        # DSK import functionality removed

        # View menu
        view_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="👁️ View", menu=view_menu)

        # Theme submenu
        theme_menu = tk.Menu(
            view_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        view_menu.add_cascade(label="🎨 Theme", menu=theme_menu)
        for theme_name in self.themes:
            theme_menu.add_command(
                label=theme_name, command=lambda t=theme_name: self.change_theme(t)
            )

        # Font submenu
        font_menu = tk.Menu(
            view_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        view_menu.add_cascade(label="🔤 Font", menu=font_menu)

        # Font family submenu
        font_family_menu = tk.Menu(
            font_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        font_menu.add_cascade(label="Font Family", menu=font_family_menu)
        for family in [
            "Segoe UI",
            "Arial",
            "Helvetica",
            "Verdana",
            "Tahoma",
            "Calibri",
        ]:
            font_family_menu.add_command(
                label=family, command=lambda f=family: self.change_font_family(f)
            )

        # Font size submenu
        font_size_menu = tk.Menu(
            font_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        font_menu.add_cascade(label="Font Size", menu=font_size_menu)
        for size in [8, 9, 10, 11, 12, 14, 16]:
            font_size_menu.add_command(
                label=f"{size}pt", command=lambda s=size: self.change_font_size(s)
            )

        # Editor font submenu
        editor_font_menu = tk.Menu(
            font_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
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
                label=family, command=lambda f=family: self.change_editor_font(f)
            )

        view_menu.add_separator()
        view_menu.add_command(
            label="↺ Reset to Defaults", command=self.reset_view_settings
        )

        # Help menu
        help_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="📖 Quick Start Guide", command=self.show_help)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.new_adventure())
        self.root.bind("<Control-o>", lambda e: self.open_adventure())
        self.root.bind("<Control-s>", lambda e: self.save_adventure())
        self.root.bind("<F5>", lambda e: self.test_adventure())

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create tabs - Play tab first for easy access
        self.create_play_tab()
        self.create_info_tab()
        self.create_rooms_tab()
        self.create_items_tab()
        self.create_monsters_tab()
        self.create_modding_tab()
        self.create_preview_tab()

        # Status bar with color
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
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

        # Experience mode toggle
        row += 2
        ttk.Label(
            form_frame,
            text="🕹️ Experience Mode:",
            style="Subtitle.TLabel",
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.game_mode_var = tk.StringVar(value="text")
        mode_frame = ttk.Frame(form_frame)
        mode_frame.grid(row=row + 1, column=0, sticky=tk.W, pady=(0, 15))
        ttk.Radiobutton(
            mode_frame,
            text="Text Adventure (classic parser)",
            value="text",
            variable=self.game_mode_var,
        ).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(
            mode_frame,
            text="Point & Click Visual",
            value="visual",
            variable=self.game_mode_var,
        ).pack(side=tk.LEFT)
        self.game_mode_var.trace_add("write", lambda *_: self._on_mode_changed())

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
        self.intro_text.pack(fill=tk.BOTH, expand=True)

        # Save button - styled
        row += 2
        save_btn = ttk.Button(
            form_frame,
            text="💾 Update Adventure Info",
            command=self.update_info,
            style="Success.TButton",
        )
        save_btn.grid(row=row, column=0, sticky=tk.E, pady=(10, 0))

        # Recent adventures panel
        recent_panel = ttk.Frame(frame, style="Panel.TFrame", padding="15")
        recent_panel.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        ttk.Label(
            recent_panel,
            text="Recent Adventures",
            style="Subtitle.TLabel",
        ).pack(anchor=tk.W, pady=(0, 10))

        self.recent_list_container = ttk.Frame(recent_panel, style="TFrame")
        self.recent_list_container.pack(fill=tk.X)
        self.refresh_recent_files_ui()

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

    def create_items_tab(self):
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

    def create_monsters_tab(self):
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

    def create_visual_tab(self):
        """Visual Builder has been removed; SagaCraft is text-only."""
        pass

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

    def create_play_tab(self):
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
        self.command_entry.bind("<Return>", lambda e: self.send_command())

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

    def _load_adventure_file(
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
        self.adventure.setdefault("mode", "text")
        scenes = self.adventure.setdefault("scenes", [])
        for scene in scenes:
            scene.setdefault("hotspots", [])
            scene["grid_visible"] = bool(scene.get("grid_visible", False))
            try:
                size_value = int(scene.get("grid_size", 64))
            except (TypeError, ValueError):
                size_value = 64
            scene["grid_size"] = max(16, min(256, size_value))
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

        # Visual scenes
        self.refresh_scenes_list()

        # Preview
        self.update_preview()

    def collect_adventure_data(self):
        """Collect data from UI into adventure dict"""
        self.adventure["title"] = self.title_var.get()
        self.adventure["author"] = self.author_var.get()
        self.adventure["start_room"] = self.start_room_var.get()
        self.adventure["intro"] = self.intro_text.get("1.0", tk.END).strip()
        if self.game_mode_var:
            self.adventure["mode"] = self.game_mode_var.get() or "text"
        self.adventure.setdefault("scenes", [])
        for scene in self.adventure["scenes"]:
            scene.setdefault("hotspots", [])
            scene["grid_visible"] = bool(scene.get("grid_visible", False))
            try:
                size_value = int(scene.get("grid_size", 64))
            except (TypeError, ValueError):
                size_value = 64
            scene["grid_size"] = max(16, min(256, size_value))

    # Room methods
    def refresh_rooms_list(self):
        """Refresh the rooms listbox"""
        self.rooms_listbox.delete(0, tk.END)
        for room in self.adventure["rooms"]:
            self.rooms_listbox.insert(tk.END, f"#{room['id']}: {room['name']}")

    def add_room(self):
        """Add a new room"""
        new_id = max([r["id"] for r in self.adventure["rooms"]], default=0) + 1
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

    def _on_mode_changed(self):
        """Flag the document dirty when switching between text and visual modes."""
        if not self.game_mode_var:
            return
        if self._suppress_mode_change:
            return
        self.modified = True
        selected = self.game_mode_var.get()
        label = "Visual" if selected == "visual" else "Text"
        self.update_status(f"Experience mode set to {label}")

    # Visual scene methods - removed (SagaCraft is text-only)
    def refresh_scenes_list(self):
        """Removed - SagaCraft is text-only."""
        pass

    def add_scene(self):
        """Removed - SagaCraft is text-only."""
        pass

    def delete_scene(self):
        """Removed - SagaCraft is text-only."""
        pass

    def select_scene(self, _event):
        """Removed - SagaCraft is text-only."""
        pass

    def clear_scene_editor(self):
        """Removed - SagaCraft is text-only."""
        pass

    def update_scene(self):
        """Removed - SagaCraft is text-only."""
        pass

    def browse_scene_background(self):
        """Removed - SagaCraft is text-only."""
        pass

    def refresh_hotspots_list(self, scene=None, *, clear_only: bool = False):
        """Removed - SagaCraft is text-only."""
        pass

    def add_hotspot(self):
        """Removed - SagaCraft is text-only."""
        pass

    def delete_hotspot(self):
        """Removed - SagaCraft is text-only."""
        pass

    def select_hotspot(self, _event):
        """Removed - SagaCraft is text-only."""
        pass

    def clear_hotspot_editor(self):
        """Removed - SagaCraft is text-only."""
        pass

    def update_hotspot(self):
        """Removed - SagaCraft is text-only."""
        pass

    # Item methods
    def refresh_items_list(self):
        """Refresh items listbox"""
        self.items_listbox.delete(0, tk.END)
        for item in self.adventure["items"]:
            self.items_listbox.insert(tk.END, f"#{item['id']}: {item['name']}")

    def add_item(self):
        """Add a new item"""
        new_id = max([i["id"] for i in self.adventure["items"]], default=0) + 1
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
        new_id = max([m["id"] for m in self.adventure["monsters"]], default=0) + 1
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

    def validate_adventure(self, silent: bool = False):
        """Validate adventure data and update the status badge."""
        self.collect_adventure_data()
        errors = []

        if not self.adventure["title"]:
            errors.append("Adventure must have a title")

        if not self.adventure["rooms"]:
            errors.append("Adventure must have at least one room")

        # Check start room exists
        start_room = self.adventure["start_room"]
        if not any(r["id"] == start_room for r in self.adventure["rooms"]):
            errors.append(f"Start room {start_room} does not exist")

        # Check room exits
        room_ids = {r["id"] for r in self.adventure["rooms"]}
        for room in self.adventure["rooms"]:
            for _, target in room["exits"].items():
                if target not in room_ids and target != 0:
                    errors.append(
                        f"Room {room['id']} has exit to non-existent room {target}"
                    )

        mode = self.adventure.get("mode", "text")
        if mode == "visual":
            scenes = self.adventure.get("scenes", []) or []
            if not scenes:
                errors.append("Visual adventures require at least one scene defined")
            for scene in scenes:
                scene_id = scene.get("id") or scene.get("name", "(unnamed)")
                if not scene.get("background"):
                    errors.append(
                        f"Scene {scene_id} is missing a background image path"
                    )
                for hotspot in scene.get("hotspots", []) or []:
                    if hotspot.get("action", "command").startswith(
                        "command"
                    ) and not hotspot.get("value"):
                        errors.append(
                            f"Scene {scene_id} has a hotspot without a command value"
                        )

        if errors:
            self.validation_badge_var.set(f"Validation: ⚠ {len(errors)} issue(s)")
            if not silent:
                messagebox.showwarning("Validation Issues", "\n".join(errors))
        else:
            self.validation_badge_var.set("Validation: ✅ Clean")
            if not silent:
                messagebox.showinfo("Validation", "Adventure is valid!")

        return errors

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
            "• Visual room editor\n"
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

    def start_game(self):
        """Start playing the loaded adventure"""
        # Save current adventure to temp file
        temp_file = "adventures/_temp_play.json"
        self.collect_adventure_data()

        validation_errors = self.validate_adventure(silent=True)
        if validation_errors:
            self.validation_badge_var.set(
                f"Validation: ⚠ {len(validation_errors)} issue(s)"
            )
        else:
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
            Path(__file__).parent.parent.parent.parent / "acs_engine_enhanced.py"
        )
        spec = importlib.util.spec_from_file_location(
            "acs_engine_enhanced", engine_path
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
            self.game_instance = acs_module.EnhancedAdventureGame(temp_file)
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

        if (
            self.adventure.get("mode") == "visual"
            and self.adventure.get("scenes")
            and self.game_instance is not None
        ):
            try:
                self._open_visual_window()
            except (
                tk.TclError,
                RuntimeError,
            ) as exc:  # pragma: no cover - UI safeguard
                self.print_game(f"[Visual] Unable to open point-and-click view: {exc}")

        if self.command_entry is not None:
            self.command_entry.focus()
        self.update_status("Game started - enter commands below")
        self.test_badge_var.set("Play: Running")

    def restart_game(self):
        """Restart the current game"""
        if self.game_running:
            self.test_badge_var.set("Play: Restarting")
            self.start_game()
        else:
            messagebox.showinfo("No Game", "Please start a game first")

    def send_command(self):
        """Send command to game engine"""
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
        old_stdout = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer
        try:
            result = func(*args, **kwargs)
        finally:
            sys.stdout = old_stdout

        output = buffer.getvalue().strip()
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

        old_stdout = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer
        error: Exception | None = None

        try:
            self.game_instance.process_command(command)
        except (RuntimeError, ValueError, AttributeError, OSError) as exc:
            error = exc
        finally:
            output = buffer.getvalue()
            sys.stdout = old_stdout

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

    def change_theme(self, theme_name):
        """Change the color theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.colors = self.themes[theme_name]
            self.setup_styles()
            self.refresh_all_widgets()
            self.update_status(f"Theme changed to: {theme_name}")

    def _open_visual_window(self):
        """Visual builder removed; no-op."""
        self.update_status("Visual builder is no longer available.")

    def _run_visual_command(self, commands):
        """Visual builder removed; no-op."""
        return

    def _on_visual_closed(self):
        """Visual builder removed; no-op."""
        return

    def change_font_family(self, font_family):
        """Change the UI font family"""
        self.current_font_family = font_family
        self.setup_styles()
        self.refresh_all_widgets()
        self.update_status(f"Font changed to: {font_family}")

    def change_font_size(self, font_size):
        """Change the UI font size"""
        self.current_font_size = font_size
        self.setup_styles()
        self.refresh_all_widgets()
        self.update_status(f"Font size changed to: {font_size}pt")

    def change_editor_font(self, font_family):
        """Change the editor font family"""
        self.editor_font_family = font_family
        self.apply_editor_fonts()
        self.update_status(f"Editor font changed to: {font_family}")

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

    def quit_ide(self):
        """Quit the IDE"""
        if self.modified and not messagebox.askyesno(
            "Unsaved Changes", "You have unsaved changes. Quit anyway?"
        ):
            return

        self.root.quit()


def main():
    """Main entry point"""
    root = tk.Tk()
    AdventureIDE(root)
    root.mainloop()


if __name__ == "__main__":
    main()
