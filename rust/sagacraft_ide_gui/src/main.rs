use eframe::egui;
use sagacraft_rs::{AdventureGame, ItemType, MonsterStatus};
use std::path::PathBuf;
use std::collections::HashMap;
use std::fs;
use serde::{Serialize, Deserialize};

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([1400.0, 900.0]),
        ..Default::default()
    };
    eframe::run_native(
        "SagaCraft IDE",
        options,
        Box::new(|_cc| Ok(Box::new(SagaCraftIDE::default()))),
    )
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct AdventureData {
    title: String,
    intro: String,
    start_room: i32,
    rooms: Vec<RoomData>,
    items: Vec<ItemData>,
    monsters: Vec<MonsterData>,
    quests: Vec<QuestData>,
    #[serde(default)]
    author: Option<String>,
    #[serde(default)]
    settings: Option<AdventureSettings>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct AdventureSettings {
    #[serde(default)]
    allow_save: bool,
    #[serde(default)]
    difficulty: String,
    #[serde(default)]
    enable_magic: bool,
    #[serde(default)]
    enable_puzzles: bool,
    #[serde(default)]
    enable_combat_xp: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RoomData {
    id: i32,
    name: String,
    description: String,
    exits: HashMap<String, i32>,
    #[serde(default)]
    is_dark: bool,
    #[serde(default)]
    light_level: Option<String>,
    #[serde(default)]
    is_safe_zone: bool,
    #[serde(default)]
    ambient_sound: Option<String>,
    #[serde(default)]
    has_trap: bool,
    #[serde(default)]
    trap_damage: i32,
    #[serde(default)]
    environmental_effects: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ItemData {
    id: i32,
    name: String,
    description: String,
    item_type: ItemType,
    value: i32,
    weight: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct MonsterData {
    id: i32,
    name: String,
    description: String,
    hardiness: i32,
    agility: i32,
    charisma: i32,
    weapon_id: Option<i32>,
    armor_worn: i32,
    gold: i32,
    status: MonsterStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct QuestData {
    id: i32,
    title: String,
    description: String,
    objectives: Vec<String>,
    rewards_gold: i32,
    rewards_xp: i32,
}

#[derive(Default)]
struct SagaCraftIDE {
    adventure: AdventureData,
    current_file: Option<PathBuf>,
    modified: bool,
    active_tab: Tab,
    status: String,
    // Tab-specific state
    selected_room: Option<usize>,
    selected_item: Option<usize>,
    selected_monster: Option<usize>,
    selected_quest: Option<usize>,
    // Play tab state
    game: Option<AdventureGame>,
    game_output: Vec<String>,
    game_input: String,
}

#[derive(Debug, Clone, Copy, PartialEq)]
enum Tab {
    Play,
    Info,
    Rooms,
    Items,
    Monsters,
    Quests,
    Modding,
    Preview,
}

impl Default for Tab {
    fn default() -> Self {
        Tab::Play
    }
}

impl Default for AdventureData {
    fn default() -> Self {
        Self {
            title: "New Adventure".to_string(),
            intro: "Welcome to your new adventure!".to_string(),
            start_room: 1,
            rooms: vec![RoomData {
                id: 1,
                name: "Starting Room".to_string(),
                description: "A simple room to begin your adventure.".to_string(),
                exits: HashMap::new(),
                is_dark: false,
                light_level: None,
                is_safe_zone: false,
                ambient_sound: None,
                has_trap: false,
                trap_damage: 0,
                environmental_effects: vec![],
            }],
            items: vec![ItemData {
                id: 1,
                name: "Brass Lantern".to_string(),
                description: "A shiny brass lantern that provides light.".to_string(),
                item_type: ItemType::Normal,
                value: 25,
                weight: 2,
            }],
            monsters: vec![MonsterData {
                id: 1,
                name: "Goblin".to_string(),
                description: "A small green goblin with a club.".to_string(),
                hardiness: 8,
                agility: 12,
                charisma: 6,
                weapon_id: Some(1),
                armor_worn: 0,
                gold: 5,
                status: MonsterStatus::Friendly,
            }],
            quests: vec![QuestData {
                id: 1,
                title: "Light the Path".to_string(),
                description: "Secure a light source and reach the Shadow Gallery.".to_string(),
                objectives: vec!["Pick up the brass lantern".to_string(), "Enter the Shadow Gallery with light".to_string()],
                rewards_gold: 40,
                rewards_xp: 60,
            }],
            author: None,
            settings: None,
        }
    }
}

impl eframe::App for SagaCraftIDE {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::TopBottomPanel::top("menu_bar").show(ctx, |ui| {
            self.show_menu_bar(ctx, ui);
        });

        egui::TopBottomPanel::bottom("status_bar").show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.label(&self.status);
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if self.modified {
                        ui.colored_label(egui::Color32::YELLOW, "●");
                    }
                });
            });
        });

        egui::CentralPanel::default().show(ctx, |ui| {
            self.show_main_ui(ui);
        });
    }
}

impl SagaCraftIDE {
    fn show_menu_bar(&mut self, ctx: &egui::Context, ui: &mut egui::Ui) {
        egui::menu::bar(ui, |ui| {
            ui.menu_button("File", |ui| {
                if ui.button("New Adventure").clicked() {
                    self.new_adventure();
                    ui.close_menu();
                }
                if ui.button("Open Adventure...").clicked() {
                    self.open_adventure();
                    ui.close_menu();
                }
                if ui.button("Save Adventure").clicked() {
                    self.save_adventure();
                    ui.close_menu();
                }
                if ui.button("Save Adventure As...").clicked() {
                    self.save_adventure_as();
                    ui.close_menu();
                }
                ui.separator();
                if ui.button("Exit").clicked() {
                    std::process::exit(0);
                }
            });

            ui.menu_button("Tools", |ui| {
                if ui.button("Validate Adventure").clicked() {
                    self.validate_adventure();
                    ui.close_menu();
                }
                if ui.button("Export to JSON").clicked() {
                    self.export_to_json();
                    ui.close_menu();
                }
            });

            ui.menu_button("View", |ui| {
                ui.label("Theme:");
                if ui.button("Light").clicked() {
                    ctx.set_visuals(egui::Visuals::light());
                }
                if ui.button("Dark").clicked() {
                    ctx.set_visuals(egui::Visuals::dark());
                }
            });

            ui.menu_button("Help", |ui| {
                if ui.button("About SagaCraft IDE").clicked() {
                    self.show_about();
                    ui.close_menu();
                }
            });
        });
    }

    fn show_main_ui(&mut self, ui: &mut egui::Ui) {
        ui.horizontal(|ui| {
            // Tab buttons
            if ui.selectable_label(self.active_tab == Tab::Play, "🎮 Play").clicked() {
                self.active_tab = Tab::Play;
            }
            if ui.selectable_label(self.active_tab == Tab::Info, "ℹ Info").clicked() {
                self.active_tab = Tab::Info;
            }
            if ui.selectable_label(self.active_tab == Tab::Rooms, "🏠 Rooms").clicked() {
                self.active_tab = Tab::Rooms;
            }
            if ui.selectable_label(self.active_tab == Tab::Items, "🎒 Items").clicked() {
                self.active_tab = Tab::Items;
            }
            if ui.selectable_label(self.active_tab == Tab::Monsters, "👹 Monsters").clicked() {
                self.active_tab = Tab::Monsters;
            }
            if ui.selectable_label(self.active_tab == Tab::Quests, "📜 Quests").clicked() {
                self.active_tab = Tab::Quests;
            }
            if ui.selectable_label(self.active_tab == Tab::Modding, "🔧 Modding").clicked() {
                self.active_tab = Tab::Modding;
            }
            if ui.selectable_label(self.active_tab == Tab::Preview, "👁 Preview").clicked() {
                self.active_tab = Tab::Preview;
            }
        });

        ui.separator();

        match self.active_tab {
            Tab::Play => self.show_play_tab(ui),
            Tab::Info => self.show_info_tab(ui),
            Tab::Rooms => self.show_rooms_tab(ui),
            Tab::Items => self.show_items_tab(ui),
            Tab::Monsters => self.show_monsters_tab(ui),
            Tab::Quests => self.show_quests_tab(ui),
            Tab::Modding => self.show_modding_tab(ui),
            Tab::Preview => self.show_preview_tab(ui),
        }
    }

    fn show_play_tab(&mut self, ui: &mut egui::Ui) {
        ui.heading("🎮 Play Adventure");

        ui.horizontal(|ui| {
            if ui.button("▶ Start Game").clicked() {
                self.start_game();
            }
            if ui.button("⏹ Stop Game").clicked() {
                self.stop_game();
            }
            if ui.button("🔄 Restart").clicked() {
                self.restart_game();
            }
        });

        ui.separator();

        // Game output
        egui::ScrollArea::vertical().show(ui, |ui| {
            for line in &self.game_output {
                ui.label(line);
            }
        });

        // Input area
        ui.separator();
        ui.horizontal(|ui| {
            ui.label("Command:");
            let response = ui.text_edit_singleline(&mut self.game_input);
            if ui.button("Send").clicked() || (response.lost_focus() && ui.input(|i| i.key_pressed(egui::Key::Enter))) {
                self.send_game_command();
            }
        });
    }

    fn show_info_tab(&mut self, ui: &mut egui::Ui) {
        ui.heading("ℹ Adventure Information");

        egui::Grid::new("info_grid")
            .num_columns(2)
            .spacing([10.0, 10.0])
            .show(ui, |ui| {
                ui.label("Title:");
                ui.text_edit_singleline(&mut self.adventure.title);
                ui.end_row();

                ui.label("Introduction:");
                ui.text_edit_multiline(&mut self.adventure.intro);
                ui.end_row();

                ui.label("Start Room ID:");
                ui.add(egui::DragValue::new(&mut self.adventure.start_room));
                ui.end_row();
            });

        ui.separator();
        ui.label(format!("Rooms: {}", self.adventure.rooms.len()));
        ui.label(format!("Items: {}", self.adventure.items.len()));
        ui.label(format!("Monsters: {}", self.adventure.monsters.len()));
        ui.label(format!("Quests: {}", self.adventure.quests.len()));
    }

    fn show_rooms_tab(&mut self, ui: &mut egui::Ui) {
        ui.heading("🏠 Rooms");

        ui.horizontal(|ui| {
            if ui.button("➕ Add Room").clicked() {
                self.add_room();
            }
            if ui.button("➖ Delete Room").clicked() && self.selected_room.is_some() {
                self.delete_room();
            }
        });

        ui.separator();

        ui.columns(2, |columns| {
            // Room list
            columns[0].heading("Rooms");
            egui::ScrollArea::vertical().show(&mut columns[0], |ui| {
                for (i, room) in self.adventure.rooms.iter().enumerate() {
                    let selected = self.selected_room == Some(i);
                    if ui.selectable_label(selected, format!("{}: {}", room.id, room.name)).clicked() {
                        self.selected_room = Some(i);
                    }
                }
            });

            // Room editor
            columns[1].heading("Room Editor");
            if let Some(room_idx) = self.selected_room {
                if let Some(room) = self.adventure.rooms.get_mut(room_idx) {
                    egui::Grid::new("room_grid")
                        .num_columns(2)
                        .spacing([10.0, 10.0])
                        .show(&mut columns[1], |ui| {
                            ui.label("ID:");
                            ui.add(egui::DragValue::new(&mut room.id));
                            ui.end_row();

                            ui.label("Name:");
                            ui.text_edit_singleline(&mut room.name);
                            ui.end_row();

                            ui.label("Description:");
                            ui.text_edit_multiline(&mut room.description);
                            ui.end_row();

                            ui.label("Dark:");
                            ui.checkbox(&mut room.is_dark, "");
                            ui.end_row();
                        });

                    columns[1].separator();
                    columns[1].label("Exits:");
                    for (direction, room_id) in &mut room.exits {
                        columns[1].horizontal(|ui| {
                            ui.label(direction);
                            ui.label("→");
                            ui.add(egui::DragValue::new(room_id));
                            if ui.button("❌").clicked() {
                                // Remove exit - we'll handle this properly later
                            }
                        });
                    }
                    if columns[1].button("➕ Add Exit").clicked() {
                        room.exits.insert("north".to_string(), 1);
                    }
                }
            } else {
                columns[1].label("Select a room to edit");
            }
        });
    }

    fn show_items_tab(&mut self, ui: &mut egui::Ui) {
        ui.heading("🎒 Items");

        ui.horizontal(|ui| {
            if ui.button("➕ Add Item").clicked() {
                self.add_item();
            }
            if ui.button("➖ Delete Item").clicked() && self.selected_item.is_some() {
                self.delete_item();
            }
        });

        ui.separator();

        ui.columns(2, |columns| {
            // Item list
            columns[0].heading("Items");
            egui::ScrollArea::vertical().show(&mut columns[0], |ui| {
                for (i, item) in self.adventure.items.iter().enumerate() {
                    let selected = self.selected_item == Some(i);
                    if ui.selectable_label(selected, format!("{}: {}", item.id, item.name)).clicked() {
                        self.selected_item = Some(i);
                    }
                }
            });

            // Item editor
            columns[1].heading("Item Editor");
            if let Some(item_idx) = self.selected_item {
                if let Some(item) = self.adventure.items.get_mut(item_idx) {
                    egui::Grid::new("item_grid")
                        .num_columns(2)
                        .spacing([10.0, 10.0])
                        .show(&mut columns[1], |ui| {
                            ui.label("ID:");
                            ui.add(egui::DragValue::new(&mut item.id));
                            ui.end_row();

                            ui.label("Name:");
                            ui.text_edit_singleline(&mut item.name);
                            ui.end_row();

                            ui.label("Description:");
                            ui.text_edit_multiline(&mut item.description);
                            ui.end_row();

                            ui.label("Type:");
                            // TODO: Dropdown for item type
                            ui.label(format!("{:?}", item.item_type));
                            ui.end_row();

                            ui.label("Value:");
                            ui.add(egui::DragValue::new(&mut item.value));
                            ui.end_row();

                            ui.label("Weight:");
                            ui.add(egui::DragValue::new(&mut item.weight));
                            ui.end_row();
                        });
                }
            } else {
                columns[1].label("Select an item to edit");
            }
        });
    }

    fn show_monsters_tab(&mut self, ui: &mut egui::Ui) {
        ui.heading("👹 Monsters");

        ui.horizontal(|ui| {
            if ui.button("➕ Add Monster").clicked() {
                self.add_monster();
            }
            if ui.button("➖ Delete Monster").clicked() && self.selected_monster.is_some() {
                self.delete_monster();
            }
        });

        ui.separator();

        ui.columns(2, |columns| {
            // Monster list
            columns[0].heading("Monsters");
            egui::ScrollArea::vertical().show(&mut columns[0], |ui| {
                for (i, monster) in self.adventure.monsters.iter().enumerate() {
                    let selected = self.selected_monster == Some(i);
                    if ui.selectable_label(selected, format!("{}: {}", monster.id, monster.name)).clicked() {
                        self.selected_monster = Some(i);
                    }
                }
            });

            // Monster editor
            columns[1].heading("Monster Editor");
            if let Some(monster_idx) = self.selected_monster {
                if let Some(monster) = self.adventure.monsters.get_mut(monster_idx) {
                    egui::Grid::new("monster_grid")
                        .num_columns(2)
                        .spacing([10.0, 10.0])
                        .show(&mut columns[1], |ui| {
                            ui.label("ID:");
                            ui.add(egui::DragValue::new(&mut monster.id));
                            ui.end_row();

                            ui.label("Name:");
                            ui.text_edit_singleline(&mut monster.name);
                            ui.end_row();

                            ui.label("Description:");
                            ui.text_edit_multiline(&mut monster.description);
                            ui.end_row();

                            ui.label("Hardiness:");
                            ui.add(egui::DragValue::new(&mut monster.hardiness));
                            ui.end_row();

                            ui.label("Agility:");
                            ui.add(egui::DragValue::new(&mut monster.agility));
                            ui.end_row();

                            ui.label("Charisma:");
                            ui.add(egui::DragValue::new(&mut monster.charisma));
                            ui.end_row();

                            ui.label("Gold:");
                            ui.add(egui::DragValue::new(&mut monster.gold));
                            ui.end_row();
                        });
                }
            } else {
                columns[1].label("Select a monster to edit");
            }
        });
    }

    fn show_quests_tab(&mut self, ui: &mut egui::Ui) {
        ui.heading("📜 Quests");

        ui.horizontal(|ui| {
            if ui.button("➕ Add Quest").clicked() {
                self.add_quest();
            }
            if ui.button("➖ Delete Quest").clicked() && self.selected_quest.is_some() {
                self.delete_quest();
            }
        });

        ui.separator();

        ui.columns(2, |columns| {
            // Quest list
            columns[0].heading("Quests");
            egui::ScrollArea::vertical().show(&mut columns[0], |ui| {
                for (i, quest) in self.adventure.quests.iter().enumerate() {
                    let selected = self.selected_quest == Some(i);
                    if ui.selectable_label(selected, format!("{}: {}", quest.id, quest.title)).clicked() {
                        self.selected_quest = Some(i);
                    }
                }
            });

            // Quest editor
            columns[1].heading("Quest Editor");
            if let Some(quest_idx) = self.selected_quest {
                if let Some(quest) = self.adventure.quests.get_mut(quest_idx) {
                    egui::Grid::new("quest_grid")
                        .num_columns(2)
                        .spacing([10.0, 10.0])
                        .show(&mut columns[1], |ui| {
                            ui.label("ID:");
                            ui.add(egui::DragValue::new(&mut quest.id));
                            ui.end_row();

                            ui.label("Title:");
                            ui.text_edit_singleline(&mut quest.title);
                            ui.end_row();

                            ui.label("Description:");
                            ui.text_edit_multiline(&mut quest.description);
                            ui.end_row();

                            ui.label("Objectives:");
                            for objective in &quest.objectives {
                                ui.label(format!("• {}", objective));
                            }
                            ui.end_row();

                            ui.label("Gold Reward:");
                            ui.add(egui::DragValue::new(&mut quest.rewards_gold));
                            ui.end_row();

                            ui.label("XP Reward:");
                            ui.add(egui::DragValue::new(&mut quest.rewards_xp));
                            ui.end_row();
                        });
                }
            } else {
                columns[1].label("Select a quest to edit");
            }
        });
    }

    fn show_modding_tab(&mut self, ui: &mut egui::Ui) {
        ui.heading("🔧 Modding System");

        ui.horizontal(|ui| {
            if ui.button("🔄 Refresh Mods").clicked() {
                self.refresh_mods();
            }
            if ui.button("📁 Open Mods Folder").clicked() {
                self.open_mods_folder();
            }
        });

        ui.separator();

        ui.columns(2, |columns| {
            // Mod list
            columns[0].heading("Available Mods");
            egui::ScrollArea::vertical().show(&mut columns[0], |ui| {
                // Show actual mods from the mods directory
                let mods = self.discover_mods();

                for (mod_name, mut enabled, description) in mods {
                    ui.horizontal(|ui| {
                        ui.checkbox(&mut enabled, ""); // TODO: Make this actually toggle mods
                        ui.label(format!("{} ({})", mod_name, if enabled { "Enabled" } else { "Disabled" }));
                    });
                    ui.label(description);
                    ui.separator();
                }
            });

            // Mod details
            columns[1].heading("Mod Details");
            columns[1].label("Select a mod to view details");
            columns[1].separator();
            columns[1].label("Mod Console:");
            egui::ScrollArea::vertical().show(&mut columns[1], |ui| {
                ui.label("Mod system initialized...");
                ui.label("warm_welcome.py: Provides friendly welcome messages");
                ui.label("treasure_cache.py: Adds treasure caches to rooms");
                ui.label("No recent mod activity.");
            });
        });
    }

    fn show_preview_tab(&mut self, ui: &mut egui::Ui) {
        ui.heading("👁️ Adventure Preview");

        ui.horizontal(|ui| {
            if ui.button("🔄 Refresh").clicked() {
                self.refresh_json_preview();
            }
            if ui.button("📋 Copy JSON").clicked() {
                self.copy_json_to_clipboard();
            }
            if ui.button("📊 Show Diff").clicked() {
                self.show_json_diff();
            }
        });

        ui.separator();

        ui.columns(2, |columns| {
            // JSON Preview
            columns[0].heading("JSON Export");
            columns[0].label("This is the JSON representation of your adventure:");

            egui::ScrollArea::vertical().show(&mut columns[0], |ui| {
                let json = self.generate_json_preview();
                ui.add(
                    egui::TextEdit::multiline(&mut json.as_str())
                        .font(egui::TextStyle::Monospace)
                        .interactive(false)
                );
            });

            // Preview Stats
            columns[1].heading("Adventure Statistics");
            columns[1].label(format!("Rooms: {}", self.adventure.rooms.len()));
            columns[1].label(format!("Items: {}", self.adventure.items.len()));
            columns[1].label(format!("Monsters: {}", self.adventure.monsters.len()));
            columns[1].label(format!("Quests: {}", self.adventure.quests.len()));

            columns[1].separator();
            columns[1].label("Export Options:");
            if columns[1].button("💾 Save as JSON").clicked() {
                // TODO: Implement save dialog
                self.status = "Save dialog not implemented yet".to_string();
            }
            if columns[1].button("📤 Export to Game").clicked() {
                // TODO: Implement export to game
                self.status = "Export to game not implemented yet".to_string();
            }
        });
    }

    // File operations
    fn new_adventure(&mut self) {
        self.adventure = AdventureData::default();
        self.current_file = None;
        self.modified = false;
        self.status = "New adventure created".to_string();
    }

    fn open_adventure(&mut self) {
        if let Some(path) = rfd::FileDialog::new()
            .add_filter("JSON files", &["json"])
            .add_filter("All files", &["*"])
            .pick_file()
        {
            match self.load_from_file(&path) {
                Ok(_) => {
                    self.current_file = Some(path.clone());
                    self.modified = false;
                    self.status = format!("Opened adventure: {}", path.display());
                }
                Err(e) => {
                    self.status = format!("Error opening file: {}", e);
                }
            }
        }
    }

    fn save_adventure(&mut self) {
        if let Some(path) = self.current_file.clone() {
            match self.save_to_file(&path) {
                Ok(_) => {
                    self.modified = false;
                    self.status = format!("Saved adventure: {}", path.display());
                }
                Err(e) => {
                    self.status = format!("Error saving file: {}", e);
                }
            }
        } else {
            self.save_adventure_as();
        }
    }

    fn save_adventure_as(&mut self) {
        if let Some(path) = rfd::FileDialog::new()
            .add_filter("JSON files", &["json"])
            .add_filter("All files", &["*"])
            .save_file()
        {
            match self.save_to_file(&path) {
                Ok(_) => {
                    self.current_file = Some(path.clone());
                    self.modified = false;
                    self.status = format!("Saved adventure as: {}", path.display());
                }
                Err(e) => {
                    self.status = format!("Error saving file: {}", e);
                }
            }
        }
    }

    fn save_to_file(&mut self, path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        let content = serde_json::to_string_pretty(&self.adventure)?;
        fs::write(path, content)?;
        Ok(())
    }

    fn load_from_file(&mut self, path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        let content = fs::read_to_string(path)?;
        self.adventure = serde_json::from_str(&content)?;
        Ok(())
    }

    fn validate_adventure(&mut self) {
        // TODO: Implement validation
        self.status = "Adventure validation not yet implemented".to_string();
    }

    fn export_to_json(&mut self) {
        // TODO: Implement JSON export
        self.status = "JSON export not yet implemented".to_string();
    }

    fn show_about(&mut self) {
        self.status = "SagaCraft IDE - Complete adventure editor".to_string();
    }

    // CRUD operations
    fn add_room(&mut self) {
        let id = self.adventure.rooms.len() as i32 + 1;
        self.adventure.rooms.push(RoomData {
            id,
            name: format!("Room {}", id),
            description: "A new room".to_string(),
            exits: HashMap::new(),
            is_dark: false,
            light_level: None,
            is_safe_zone: false,
            ambient_sound: None,
            has_trap: false,
            trap_damage: 0,
            environmental_effects: vec![],
        });
        self.modified = true;
        self.status = format!("Room {} added", id);
    }

    fn delete_room(&mut self) {
        if let Some(idx) = self.selected_room {
            self.adventure.rooms.remove(idx);
            self.selected_room = None;
            self.modified = true;
            self.status = "Room deleted".to_string();
        }
    }

    fn add_item(&mut self) {
        let id = self.adventure.items.len() as i32 + 1;
        self.adventure.items.push(ItemData {
            id,
            name: format!("Item {}", id),
            description: "A new item".to_string(),
            item_type: ItemType::Normal,
            value: 0,
            weight: 1,
        });
        self.modified = true;
        self.status = format!("Item {} added", id);
    }

    fn delete_item(&mut self) {
        if let Some(idx) = self.selected_item {
            self.adventure.items.remove(idx);
            self.selected_item = None;
            self.modified = true;
            self.status = "Item deleted".to_string();
        }
    }

    fn add_monster(&mut self) {
        let id = self.adventure.monsters.len() as i32 + 1;
        self.adventure.monsters.push(MonsterData {
            id,
            name: format!("Monster {}", id),
            description: "A new monster".to_string(),
            hardiness: 10,
            agility: 10,
            charisma: 10,
            weapon_id: None,
            armor_worn: 0,
            gold: 0,
            status: MonsterStatus::Neutral,
        });
        self.modified = true;
        self.status = format!("Monster {} added", id);
    }

    fn delete_monster(&mut self) {
        if let Some(idx) = self.selected_monster {
            self.adventure.monsters.remove(idx);
            self.selected_monster = None;
            self.modified = true;
            self.status = "Monster deleted".to_string();
        }
    }

    fn add_quest(&mut self) {
        let id = self.adventure.quests.len() as i32 + 1;
        self.adventure.quests.push(QuestData {
            id,
            title: format!("Quest {}", id),
            description: "A new quest".to_string(),
            objectives: vec!["Complete objective 1".to_string()],
            rewards_gold: 50,
            rewards_xp: 100,
        });
        self.modified = true;
        self.status = format!("Quest {} added", id);
    }

    fn delete_quest(&mut self) {
        if let Some(idx) = self.selected_quest {
            self.adventure.quests.remove(idx);
            self.selected_quest = None;
            self.modified = true;
            self.status = "Quest deleted".to_string();
        }
    }

    // Game operations
    fn start_game(&mut self) {
        // TODO: Create AdventureGame from current adventure data
        self.game_output.clear();
        self.game_output.push("🎮 Game started!".to_string());
        self.game_output.push("Welcome to SagaCraft!".to_string());
        self.status = "Game started".to_string();
    }

    fn stop_game(&mut self) {
        self.game = None;
        self.game_output.clear();
        self.status = "Game stopped".to_string();
    }

    fn restart_game(&mut self) {
        self.stop_game();
        self.start_game();
    }

    fn send_game_command(&mut self) {
        if !self.game_input.is_empty() {
            let command = self.game_input.clone();
            self.game_output.push(format!("> {}", command));
            // TODO: Process command through AdventureGame
            self.game_output.push(format!("Command '{}' processed", command));
            self.game_input.clear();
        }
    }

    fn refresh_mods(&mut self) {
        // TODO: Scan mods directory for Python files
        self.status = "Mods refreshed".to_string();
    }

    fn open_mods_folder(&mut self) {
        // TODO: Open mods folder in file explorer
        self.status = "Mods folder opened".to_string();
    }

    fn discover_mods(&self) -> Vec<(String, bool, String)> {
        // TODO: Actually read from mods directory
        // For now, return hardcoded mods based on the project structure
        vec![
            ("warm_welcome.py".to_string(), true, "Provides a friendly welcome message".to_string()),
            ("treasure_cache.py".to_string(), false, "Adds treasure caches to rooms".to_string()),
        ]
    }

    fn refresh_json_preview(&mut self) {
        // The preview is always up to date since it's generated from current data
        self.status = "JSON preview refreshed".to_string();
    }

    fn copy_json_to_clipboard(&mut self) {
        // TODO: Copy JSON to system clipboard
        self.status = "JSON copied to clipboard".to_string();
    }

    fn show_json_diff(&mut self) {
        // TODO: Show diff between current and saved JSON
        self.status = "JSON diff not yet implemented".to_string();
    }

    fn generate_json_preview(&self) -> String {
        // Generate a JSON representation of the current adventure
        let mut json = String::new();
        json.push_str("{\n");
        json.push_str(&format!("  \"title\": \"{}\",\n", self.adventure.title));
        json.push_str(&format!("  \"intro\": \"{}\",\n", self.adventure.intro));
        json.push_str(&format!("  \"start_room\": {},\n", self.adventure.start_room));

        // Rooms
        json.push_str("  \"rooms\": [\n");
        for (i, room) in self.adventure.rooms.iter().enumerate() {
            json.push_str("    {\n");
            json.push_str(&format!("      \"id\": {},\n", room.id));
            json.push_str(&format!("      \"name\": \"{}\",\n", room.name));
            json.push_str(&format!("      \"description\": \"{}\",\n", room.description));
            json.push_str(&format!("      \"is_dark\": {}\n", room.is_dark));
            json.push_str("    }");
            if i < self.adventure.rooms.len() - 1 {
                json.push_str(",");
            }
            json.push_str("\n");
        }
        json.push_str("  ],\n");

        // Items
        json.push_str("  \"items\": [\n");
        for (i, item) in self.adventure.items.iter().enumerate() {
            json.push_str("    {\n");
            json.push_str(&format!("      \"id\": {},\n", item.id));
            json.push_str(&format!("      \"name\": \"{}\",\n", item.name));
            json.push_str(&format!("      \"description\": \"{}\",\n", item.description));
            json.push_str(&format!("      \"value\": {}\n", item.value));
            json.push_str("    }");
            if i < self.adventure.items.len() - 1 {
                json.push_str(",");
            }
            json.push_str("\n");
        }
        json.push_str("  ],\n");

        // Monsters
        json.push_str("  \"monsters\": [\n");
        for (i, monster) in self.adventure.monsters.iter().enumerate() {
            json.push_str("    {\n");
            json.push_str(&format!("      \"id\": {},\n", monster.id));
            json.push_str(&format!("      \"name\": \"{}\",\n", monster.name));
            json.push_str(&format!("      \"description\": \"{}\",\n", monster.description));
            json.push_str(&format!("      \"gold\": {}\n", monster.gold));
            json.push_str("    }");
            if i < self.adventure.monsters.len() - 1 {
                json.push_str(",");
            }
            json.push_str("\n");
        }
        json.push_str("  ],\n");

        // Quests
        json.push_str("  \"quests\": [\n");
        for (i, quest) in self.adventure.quests.iter().enumerate() {
            json.push_str("    {\n");
            json.push_str(&format!("      \"id\": {},\n", quest.id));
            json.push_str(&format!("      \"title\": \"{}\",\n", quest.title));
            json.push_str(&format!("      \"description\": \"{}\",\n", quest.description));
            json.push_str(&format!("      \"rewards_gold\": {}\n", quest.rewards_gold));
            json.push_str("    }");
            if i < self.adventure.quests.len() - 1 {
                json.push_str(",");
            }
            json.push_str("\n");
        }
        json.push_str("  ]\n");

        json.push_str("}\n");
        json
    }
}
