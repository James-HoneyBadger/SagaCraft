use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::collections::HashSet;
use crate::systems::System;
use crate::game_state::{AdventureGame, GameEvent};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum QuestStatus {
    Available,
    Active,
    Completed,
    Failed,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ObjectiveType {
    Kill,
    Collect,
    Explore,
    Talk,
    Defend,
    Deliver,
    Discover,
    Puzzle,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum QuestDifficulty {
    Easy,
    Moderate,
    Challenging,
    Hard,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuestObjective {
    pub objective_id: String,
    pub obj_type: ObjectiveType,
    pub description: String,
    pub target: String,
    pub required_count: i32,
    pub current_count: i32,
}

impl QuestObjective {
    pub fn new(objective_id: String, obj_type: ObjectiveType, description: String, target: String, required_count: i32) -> Self {
        Self {
            objective_id,
            obj_type,
            description,
            target,
            required_count,
            current_count: 0,
        }
    }

    pub fn is_complete(&self) -> bool {
        self.current_count >= self.required_count
    }

    pub fn progress(&mut self, amount: i32) -> i32 {
        let old_count = self.current_count;
        self.current_count = (self.current_count + amount).min(self.required_count);
        self.current_count - old_count
    }

    pub fn get_progress_percentage(&self) -> i32 {
        if self.required_count == 0 {
            100
        } else {
            ((self.current_count as f32 / self.required_count as f32) * 100.0) as i32
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuestStage {
    pub stage_id: String,
    pub stage_number: i32,
    pub title: String,
    pub description: String,
    pub objectives: Vec<QuestObjective>,
    pub stage_reward_xp: i32,
}

impl QuestStage {
    pub fn new(stage_id: String, stage_number: i32, title: String, description: String) -> Self {
        Self {
            stage_id,
            stage_number,
            title,
            description,
            objectives: Vec::new(),
            stage_reward_xp: 0,
        }
    }

    pub fn add_objective(&mut self, objective: QuestObjective) {
        self.objectives.push(objective);
    }

    pub fn is_complete(&self) -> bool {
        self.objectives.iter().all(|o| o.is_complete())
    }

    pub fn get_progress_percentage(&self) -> i32 {
        if self.objectives.is_empty() {
            100
        } else {
            let total_progress: i32 = self.objectives.iter().map(|o| o.get_progress_percentage()).sum();
            total_progress / self.objectives.len() as i32
        }
    }
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct QuestReward {
    pub experience_points: i32,
    pub gold: i32,
    pub items: Vec<String>,
    pub reputation_changes: HashMap<String, i32>,
    pub special_rewards: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quest {
    pub quest_id: String,
    pub title: String,
    pub description: String,
    pub giver_npc: String,
    pub quest_giver_level: i32,
    pub difficulty: QuestDifficulty,
    pub stages: Vec<QuestStage>,
    pub rewards: QuestReward,
    pub status: QuestStatus,
    pub acceptance_time: Option<String>,
    pub completion_time: Option<String>,
    pub current_stage_index: usize,
}

impl Quest {
    pub fn new(quest_id: String, title: String, description: String, giver_npc: String) -> Self {
        Self {
            quest_id,
            title,
            description,
            giver_npc,
            quest_giver_level: 1,
            difficulty: QuestDifficulty::Moderate,
            stages: Vec::new(),
            rewards: QuestReward::default(),
            status: QuestStatus::Available,
            acceptance_time: None,
            completion_time: None,
            current_stage_index: 0,
        }
    }

    pub fn get_current_stage(&self) -> Option<&QuestStage> {
        self.stages.get(self.current_stage_index)
    }

    pub fn is_complete(&self) -> bool {
        !self.stages.is_empty()
            && self.current_stage_index >= self.stages.len() - 1
            && self.get_current_stage().is_some_and(|s: &QuestStage| s.is_complete())
    }

    pub fn mark_complete(&mut self) {
        self.status = QuestStatus::Completed;
        self.completion_time = Some(chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string());
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuestTracker {
    pub active_quests: HashMap<String, Quest>,
    pub completed_quests: HashSet<String>,
    pub failed_quests: HashSet<String>,
    pub quest_history: Vec<(String, QuestStatus, String)>,
}

impl QuestTracker {
    pub fn new() -> Self {
        Self {
            active_quests: HashMap::new(),
            completed_quests: HashSet::new(),
            failed_quests: HashSet::new(),
            quest_history: Vec::new(),
        }
    }
}

impl Default for QuestTracker {
    fn default() -> Self {
        Self::new()
    }
}

impl QuestTracker {
    pub fn accept_quest(&mut self, mut quest: Quest) -> bool {
        if self.active_quests.contains_key(&quest.quest_id) ||
           self.completed_quests.contains(&quest.quest_id) {
            return false;
        }

        quest.status = QuestStatus::Active;
        quest.acceptance_time = Some(chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string());
        let quest_id = quest.quest_id.clone();
        self.active_quests.insert(quest_id.clone(), quest);
        self.record_history(quest_id, QuestStatus::Active);
        true
    }

    pub fn complete_quest(&mut self, quest_id: &str) -> Option<QuestReward> {
        if let Some(quest) = self.active_quests.get_mut(quest_id) {
            quest.mark_complete();
            let reward = quest.rewards.clone();
            self.completed_quests.insert(quest_id.to_string());
            self.active_quests.remove(quest_id);
            self.record_history(quest_id.to_string(), QuestStatus::Completed);
            Some(reward)
        } else {
            None
        }
    }

    pub fn get_active_count(&self) -> usize {
        self.active_quests.len()
    }

    pub fn get_completed_count(&self) -> usize {
        self.completed_quests.len()
    }

    fn record_history(&mut self, quest_id: String, status: QuestStatus) {
        let timestamp = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();
        self.quest_history.push((quest_id, status, timestamp));
    }
} // end impl QuestTracker (methods)

pub struct QuestSystem {
    pub tracker: QuestTracker,
    pub available_quests: HashMap<String, Quest>,
    loaded: bool,
}

impl QuestSystem {
    pub fn new() -> Self {
        Self {
            tracker: QuestTracker::new(),
            available_quests: HashMap::new(),
            loaded: false,
        }
    }
}

impl Default for QuestSystem {
    fn default() -> Self {
        Self::new()
    }
}

impl QuestSystem {
    pub fn load_quests_from_game(&mut self, game: &AdventureGame) {
        if self.loaded {
            return; // Already loaded — guard prevents reset when available_quests empties later
        }
        self.loaded = true;

        for quest_data in &game.quests {
            if let Ok(quest) = self.parse_quest_from_json(quest_data) {
                self.available_quests.insert(quest.quest_id.clone(), quest);
            }
        }
    }

    fn parse_quest_from_json(&self, data: &serde_json::Value) -> Result<Quest, Box<dyn std::error::Error>> {
        let id = data.get("id").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
        let title = data.get("title").and_then(|v| v.as_str()).unwrap_or("").to_string();
        let description = data.get("description").and_then(|v| v.as_str()).unwrap_or("").to_string();
        let giver_npc = data.get("giver_npc").and_then(|v| v.as_str()).unwrap_or("").to_string();

        // Parse rewards: supports both {"rewards": {"gold": N, "xp": N}} and flat fields
        let (reward_gold, reward_xp) = if let Some(rewards) = data.get("rewards") {
            let gold = rewards.get("gold").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
            let xp = rewards.get("xp")
                .or_else(|| rewards.get("experience_points"))
                .and_then(|v| v.as_i64()).unwrap_or(0) as i32;
            (gold, xp)
        } else {
            let gold = data.get("rewards_gold").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
            let xp = data.get("rewards_xp").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
            (gold, xp)
        };

        let mut stages = Vec::new();
        let mut objectives = Vec::new();

        // Parse objectives
        if let Some(obj_data) = data.get("objectives").and_then(|v| v.as_array()) {
            for obj in obj_data {
                // Skip plain-string objectives (e.g. from GUI IDE)
                let obj_type = match obj.get("type").and_then(|v| v.as_str()).unwrap_or("") {
                    "kill_monster" => ObjectiveType::Kill,
                    "collect_item"  => ObjectiveType::Collect,
                    "reach_room"    => ObjectiveType::Explore,
                    "talk_to_npc"   => ObjectiveType::Talk,
                    _               => ObjectiveType::Discover,
                };

                // target_id can be a string name or an integer id
                let target = obj.get("target_id")
                    .and_then(|v| v.as_str().map(str::to_string)
                        .or_else(|| v.as_i64().map(|n| n.to_string())))
                    .unwrap_or_default();

                let desc = obj.get("description").and_then(|v| v.as_str()).unwrap_or("").to_string();
                let required = obj.get("count").and_then(|v| v.as_i64()).unwrap_or(1) as i32;

                objectives.push(QuestObjective::new(
                    format!("obj_{}", objectives.len()),
                    obj_type,
                    desc,
                    target,
                    required,
                ));
            }
        }

        // Wrap objectives in a single stage
        stages.push(QuestStage {
            stage_id: "main".to_string(),
            stage_number: 1,
            title: "Main Objectives".to_string(),
            description: description.clone(),
            objectives,
            stage_reward_xp: reward_xp,
        });

        Ok(Quest {
            quest_id: id.to_string(),
            title,
            description,
            giver_npc,
            quest_giver_level: 1,
            difficulty: QuestDifficulty::Moderate,
            stages,
            rewards: QuestReward {
                experience_points: reward_xp,
                gold: reward_gold,
                ..QuestReward::default()
            },
            status: QuestStatus::Available,
            acceptance_time: None,
            completion_time: None,
            current_stage_index: 0,
        })
    }

    pub fn add_available_quest(&mut self, quest: Quest) {
        self.available_quests.insert(quest.quest_id.clone(), quest);
    }

    pub fn get_available_quests(&self) -> Vec<&Quest> {
        self.available_quests.values().collect()
    }

    pub fn accept_quest(&mut self, quest_id: &str) -> Result<String, String> {
        if let Some(quest) = self.available_quests.remove(quest_id) {
            let title = quest.title.clone();
            if self.tracker.accept_quest(quest) {
                Ok(format!("Accepted quest: {}", title))
            } else {
                Err("Quest already active or completed".to_string())
            }
        } else {
            Err("Quest not found".to_string())
        }
    }

    pub fn show_quests(&self) -> String {
        let mut result = String::new();
        result.push_str("Active Quests:\n");
        for quest in self.tracker.active_quests.values() {
            result.push_str(&format!("- {}: {}\n", quest.title, quest.description));
            if let Some(stage) = quest.get_current_stage() {
                result.push_str(&format!("  Current Stage: {}\n", stage.title));
                for obj in &stage.objectives {
                    result.push_str(&format!("    - {} ({}/{})\n",
                        obj.description, obj.current_count, obj.required_count));
                }
            }
        }
        result.push_str("\nAvailable Quests:\n");
        for quest in self.available_quests.values() {
            result.push_str(&format!("- {}: {}\n", quest.title, quest.description));
        }
        result
    }
}

impl System for QuestSystem {
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String> {
        self.load_quests_from_game(game);

        match command {
            "quests" | "journal" => Some(self.show_quests()),
            "accept" => {
                if args.is_empty() {
                    Some("Usage: accept <quest_id>. Use 'quests' to see available quests.".to_string())
                } else {
                    match self.accept_quest(args[0]) {
                        Ok(msg) => Some(msg),
                        Err(err) => Some(format!("Error: {}", err)),
                    }
                }
            }
            "complete" | "finish" => {
                if args.is_empty() {
                    Some("Usage: complete <quest_id>. Use 'quests' to see active quests.".to_string())
                } else {
                    match self.tracker.complete_quest(args[0]) {
                        Some(reward) => {
                            game.player.gold += reward.gold;
                            game.player.experience_points += reward.experience_points;
                            let mut msg = format!("Completed quest: {}", args[0]);
                            if reward.gold > 0 {
                                msg.push_str(&format!(" (+{} gold)", reward.gold));
                            }
                            if reward.experience_points > 0 {
                                msg.push_str(&format!(" (+{} XP)", reward.experience_points));
                            }
                            Some(msg)
                        }
                        None => Some(format!("Quest '{}' not found or not active.", args[0])),
                    }
                }
            }
            _ => None,
        }
    }

    fn on_events(&mut self, events: &[GameEvent], _game: &mut AdventureGame) -> Option<String> {
        let mut notifications: Vec<String> = Vec::new();

        for event in events {
            match event {
                GameEvent::MonsterKilled { monster_name, .. } => {
                    for quest in self.tracker.active_quests.values_mut() {
                        if let Some(stage) = quest.stages.get_mut(quest.current_stage_index) {
                            for obj in &mut stage.objectives {
                                if obj.obj_type == ObjectiveType::Kill
                                    && !obj.target.is_empty()
                                    && monster_name.to_lowercase().contains(&obj.target.to_lowercase())
                                    && !obj.is_complete()
                                {
                                    let gained = obj.progress(1);
                                    if gained > 0 {
                                        notifications.push(format!(
                                            "[Quest: {}] {} ({}/{})",
                                            quest.title, obj.description,
                                            obj.current_count, obj.required_count
                                        ));
                                    }
                                }
                            }
                        }
                    }
                }
                GameEvent::ItemCollected { item_name, .. } => {
                    for quest in self.tracker.active_quests.values_mut() {
                        if let Some(stage) = quest.stages.get_mut(quest.current_stage_index) {
                            for obj in &mut stage.objectives {
                                if obj.obj_type == ObjectiveType::Collect
                                    && !obj.target.is_empty()
                                    && item_name.to_lowercase().contains(&obj.target.to_lowercase())
                                    && !obj.is_complete()
                                {
                                    let gained = obj.progress(1);
                                    if gained > 0 {
                                        notifications.push(format!(
                                            "[Quest: {}] {} ({}/{})",
                                            quest.title, obj.description,
                                            obj.current_count, obj.required_count
                                        ));
                                    }
                                }
                            }
                        }
                    }
                }
                GameEvent::RoomEntered { room_id } => {
                    for quest in self.tracker.active_quests.values_mut() {
                        if let Some(stage) = quest.stages.get_mut(quest.current_stage_index) {
                            for obj in &mut stage.objectives {
                                if obj.obj_type == ObjectiveType::Explore
                                    && obj.target == room_id.to_string()
                                    && !obj.is_complete()
                                {
                                    obj.progress(1);
                                    notifications.push(format!(
                                        "[Quest: {}] {}",
                                        quest.title, obj.description
                                    ));
                                }
                            }
                        }
                    }
                }
                _ => {}
            }
        }

        if notifications.is_empty() {
            None
        } else {
            Some(format!("Quest update:\n{}", notifications.join("\n")))
        }
    }
}