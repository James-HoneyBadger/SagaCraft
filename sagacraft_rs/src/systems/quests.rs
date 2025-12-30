use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::collections::HashSet;
use crate::systems::System;
use crate::game_state::AdventureGame;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum QuestStatus {
    Available,
    Active,
    Completed,
    Failed,
    Abandoned,
    Blocked,
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
    Trivial,
    Easy,
    Moderate,
    Challenging,
    Hard,
    Legendary,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuestObjective {
    pub objective_id: String,
    pub obj_type: ObjectiveType,
    pub description: String,
    pub target: String,
    pub required_count: i32,
    pub current_count: i32,
    pub is_optional: bool,
    pub completion_reward: i32,
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
            is_optional: false,
            completion_reward: 0,
        }
    }

    pub fn is_complete(&self) -> bool {
        self.current_count >= self.required_count
    }

    pub fn progress(&mut self, _amount: i32) -> i32 {
        let old_count = self.current_count;
        self.current_count = self.current_count.min(self.required_count);
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
        let mut required = self.objectives.iter().filter(|o| !o.is_optional);
        required.all(|o| o.is_complete())
    }

    pub fn get_progress_percentage(&self) -> i32 {
        if self.objectives.is_empty() {
            100
        } else {
            let total_progress: i32 = self.objectives.iter().map(|o| o.get_progress_percentage()).sum();
            total_progress / self.objectives.len() as i32
        }
    }

    pub fn get_optional_completed(&self) -> i32 {
        self.objectives.iter().filter(|o| o.is_optional && o.is_complete()).count() as i32
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuestReward {
    pub experience_points: i32,
    pub gold: i32,
    pub items: Vec<String>,
    pub reputation_changes: HashMap<String, i32>,
    pub special_rewards: HashMap<String, serde_json::Value>,
}

impl Default for QuestReward {
    fn default() -> Self {
        Self {
            experience_points: 0,
            gold: 0,
            items: Vec::new(),
            reputation_changes: HashMap::new(),
            special_rewards: HashMap::new(),
        }
    }
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
    pub prerequisites: Vec<String>,
    pub blocking_quests: Vec<String>,
    pub time_limit_hours: Option<i32>,
    pub status: QuestStatus,
    pub acceptance_time: Option<String>,
    pub completion_time: Option<String>,
    pub current_stage_index: usize,
    pub is_radiant: bool,
    pub chain_id: Option<String>,
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
            prerequisites: Vec::new(),
            blocking_quests: Vec::new(),
            time_limit_hours: None,
            status: QuestStatus::Available,
            acceptance_time: None,
            completion_time: None,
            current_stage_index: 0,
            is_radiant: false,
            chain_id: None,
        }
    }

    pub fn get_current_stage(&self) -> Option<&QuestStage> {
        self.stages.get(self.current_stage_index)
    }

    pub fn advance_stage(&mut self) -> bool {
        if self.current_stage_index < self.stages.len() - 1 {
            self.current_stage_index += 1;
            true
        } else {
            false
        }
    }

    pub fn is_complete(&self) -> bool {
        self.current_stage_index >= self.stages.len() - 1 &&
        self.get_current_stage().map_or(false, |s: &QuestStage| s.is_complete())
    }

    pub fn mark_complete(&mut self) {
        self.status = QuestStatus::Completed;
        self.completion_time = Some(chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string());
    }

    pub fn mark_failed(&mut self) {
        self.status = QuestStatus::Failed;
        self.completion_time = Some(chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string());
    }

    pub fn can_accept(&self, completed_quests: &HashSet<String>) -> bool {
        self.prerequisites.iter().all(|prereq| completed_quests.contains(prereq))
    }

    pub fn get_level_adjusted_rewards(&self, player_level: i32) -> QuestReward {
        let level_diff = player_level - self.quest_giver_level;
        let xp_multiplier = if level_diff < 0 {
            1.0 + (level_diff.abs() as f32) * 0.1
        } else if level_diff > 5 {
            0.5
        } else {
            1.0
        };

        QuestReward {
            experience_points: ((self.rewards.experience_points as f32) * xp_multiplier) as i32,
            gold: self.rewards.gold,
            items: self.rewards.items.clone(),
            reputation_changes: self.rewards.reputation_changes.clone(),
            special_rewards: self.rewards.special_rewards.clone(),
        }
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

    pub fn complete_quest(&mut self, quest_id: &str) -> bool {
        if let Some(quest) = self.active_quests.get_mut(quest_id) {
            quest.mark_complete();
            self.completed_quests.insert(quest_id.to_string());
            self.active_quests.remove(quest_id);
            self.record_history(quest_id.to_string(), QuestStatus::Completed);
            true
        } else {
            false
        }
    }

    pub fn fail_quest(&mut self, quest_id: &str) -> bool {
        if let Some(quest) = self.active_quests.get_mut(quest_id) {
            quest.mark_failed();
            self.failed_quests.insert(quest_id.to_string());
            self.active_quests.remove(quest_id);
            self.record_history(quest_id.to_string(), QuestStatus::Failed);
            true
        } else {
            false
        }
    }

    pub fn get_quest(&self, quest_id: &str) -> Option<&Quest> {
        self.active_quests.get(quest_id)
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
}

pub struct QuestSystem {
    pub tracker: QuestTracker,
    pub available_quests: HashMap<String, Quest>,
}

impl QuestSystem {
    pub fn new() -> Self {
        Self {
            tracker: QuestTracker::new(),
            available_quests: HashMap::new(),
        }
    }

    pub fn load_quests_from_game(&mut self, game: &AdventureGame) {
        if !self.available_quests.is_empty() {
            return; // Already loaded
        }

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

        let mut stages = Vec::new();
        let mut objectives = Vec::new();

        // Parse objectives
        if let Some(obj_data) = data.get("objectives").and_then(|v| v.as_array()) {
            for obj in obj_data {
                let obj_type = match obj.get("type").and_then(|v| v.as_str()).unwrap_or("") {
                    "kill_monster" => ObjectiveType::Kill,
                    "collect_item" => ObjectiveType::Collect,
                    "reach_room" => ObjectiveType::Explore,
                    "talk_to_npc" => ObjectiveType::Talk,
                    _ => ObjectiveType::Discover,
                };

                let target = obj.get("target_id").and_then(|v| v.as_i64()).unwrap_or(0).to_string();
                let desc = obj.get("description").and_then(|v| v.as_str()).unwrap_or("").to_string();

                objectives.push(QuestObjective::new(
                    format!("obj_{}", objectives.len()),
                    obj_type,
                    desc,
                    target,
                    1, // required_count
                ));
            }
        }

        // Create a single stage quest for now
        stages.push(QuestStage {
            stage_id: "main".to_string(),
            stage_number: 1,
            title: "Main Quest".to_string(),
            description: description.clone(),
            objectives,
            stage_reward_xp: 0, // TODO: parse rewards
        });

        Ok(Quest {
            quest_id: id.to_string(),
            title,
            description,
            giver_npc: "".to_string(), // TODO: parse from JSON
            quest_giver_level: 1,
            difficulty: QuestDifficulty::Moderate,
            stages,
            rewards: QuestReward::default(), // TODO: parse rewards
            prerequisites: vec![],
            blocking_quests: vec![],
            time_limit_hours: None,
            status: QuestStatus::Available,
            acceptance_time: None,
            completion_time: None,
            current_stage_index: 0,
            is_radiant: false,
            chain_id: None,
        })
    }

    pub fn add_available_quest(&mut self, quest: Quest) {
        self.available_quests.insert(quest.quest_id.clone(), quest);
    }

    pub fn get_available_quests(&self) -> Vec<&Quest> {
        self.available_quests.values().collect()
    }

    pub fn accept_quest(&mut self, quest_id: &str) -> Result<String, String> {
        if let Some(quest) = self.available_quests.get(quest_id) {
            if quest.can_accept(&self.tracker.completed_quests) {
                let quest_clone = quest.clone();
                let title = quest.title.clone();
                if self.tracker.accept_quest(quest_clone) {
                    self.available_quests.remove(quest_id); // Remove from available
                    Ok(format!("Accepted quest: {}", title))
                } else {
                    Err("Failed to accept quest".to_string())
                }
            } else {
                Err("Prerequisites not met".to_string())
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
            if quest.can_accept(&self.tracker.completed_quests) {
                result.push_str(&format!("- {}: {}\n", quest.title, quest.description));
            }
        }
        result
    }
}

impl System for QuestSystem {
    fn on_command(&mut self, command: &str, args: &[&str], game: &mut AdventureGame) -> Option<String> {
        self.load_quests_from_game(game);

        match command {
            "quests" => Some(self.show_quests()),
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
            "complete" => {
                if args.is_empty() {
                    Some("Usage: complete <quest_id>. Use 'quests' to see active quests.".to_string())
                } else {
                    if self.tracker.complete_quest(args[0]) {
                        Some(format!("Completed quest: {}", args[0]))
                    } else {
                        Some(format!("Quest '{}' not found or not completable.", args[0]))
                    }
                }
            }
            _ => None,
        }
    }
}