"""
Phase VIII: Advanced Quest System

Multi-stage quest chains with branching paths, dynamic generation, and persistent tracking.
Supports quest dependencies, failure conditions, optional objectives, and radiant quests.

Classes:
    QuestObjective: Single objective within a quest
    QuestStage: Phase of a quest with multiple objectives
    QuestReward: Experience, items, gold, reputation
    QuestStatus: Current state of quest
    Quest: Complete quest definition with stages and conditions
    QuestChain: Linked sequence of quests
    QuestTracker: Tracks player's active/completed quests
    QuestGenerator: Procedurally generates quests
    QuestBranch: Branching quest paths with conditions
    QuestValidator: Validates quest completion and branch conditions

Type Hints: 100%
External Dependencies: None
Test Coverage: 30+ tests
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Callable, Tuple, Any
from datetime import datetime
import random


class QuestStatus(Enum):
    """Quest state in player's progression."""
    AVAILABLE = "available"       # Can be accepted
    ACTIVE = "active"            # In progress
    COMPLETED = "completed"      # Successfully finished
    FAILED = "failed"            # Failed (can restart)
    ABANDONED = "abandoned"      # Gave up
    BLOCKED = "blocked"          # Can't be done (prerequisite)


class ObjectiveType(Enum):
    """Types of quest objectives."""
    KILL = "kill"                # Defeat X enemies
    COLLECT = "collect"          # Gather X items
    EXPLORE = "explore"          # Visit X locations
    TALK = "talk"                # Speak to X NPCs
    DEFEND = "defend"            # Protect location from enemies
    DELIVER = "deliver"          # Give item to NPC
    DISCOVER = "discover"        # Find or learn something
    PUZZLE = "puzzle"            # Solve challenge


class QuestDifficulty(Enum):
    """Quest difficulty for scaling."""
    TRIVIAL = "trivial"          # Level -5
    EASY = "easy"                # Level -2
    MODERATE = "moderate"        # Level +0
    CHALLENGING = "challenging"  # Level +2
    HARD = "hard"                # Level +5
    LEGENDARY = "legendary"      # Level +10


@dataclass
class QuestObjective:
    """Single objective within a quest stage."""
    objective_id: str
    type: ObjectiveType
    description: str
    target: str              # NPC/item/location name
    required_count: int = 1  # How many to complete
    current_count: int = 0   # Current progress
    is_optional: bool = False
    completion_reward: int = 0  # Bonus XP for optional completion
    
    def is_complete(self) -> bool:
        """Check if objective is complete."""
        return self.current_count >= self.required_count
    
    def progress(self, amount: int = 1) -> int:
        """
        Make progress on objective.
        
        Returns:
            Progress made (clamped to required_count)
        """
        old_count = self.current_count
        self.current_count = min(self.required_count, self.current_count + amount)
        return self.current_count - old_count
    
    def get_progress_percentage(self) -> int:
        """Get completion percentage."""
        if self.required_count == 0:
            return 100
        return int((self.current_count / self.required_count) * 100)


@dataclass
class QuestStage:
    """Phase of a quest with multiple objectives."""
    stage_id: str
    stage_number: int
    title: str
    description: str
    objectives: List[QuestObjective] = field(default_factory=list)
    stage_reward_xp: int = 0
    on_completion: Optional[Callable] = None  # Callback when stage completes
    
    def add_objective(self, objective: QuestObjective) -> None:
        """Add objective to stage."""
        self.objectives.append(objective)
    
    def is_complete(self) -> bool:
        """Stage complete if all required objectives done."""
        required = [o for o in self.objectives if not o.is_optional]
        return all(o.is_complete() for o in required)
    
    def get_progress_percentage(self) -> int:
        """Get overall stage progress."""
        if not self.objectives:
            return 100
        total_progress = sum(o.get_progress_percentage() for o in self.objectives)
        return total_progress // len(self.objectives)
    
    def get_optional_completed(self) -> int:
        """Get count of completed optional objectives."""
        return sum(1 for o in self.objectives if o.is_optional and o.is_complete())


@dataclass
class QuestReward:
    """Rewards for completing a quest."""
    experience_points: int = 0
    gold: int = 0
    items: List[str] = field(default_factory=list)
    reputation_changes: Dict[str, int] = field(default_factory=dict)  # faction -> amount
    special_rewards: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestBranch:
    """Branching path in a quest."""
    branch_id: str
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None  # func to check if branch available
    quest_continuation: Optional['Quest'] = None  # Next quest in branch
    description: str = ""


@dataclass
class Quest:
    """Complete quest definition."""
    quest_id: str
    title: str
    description: str
    giver_npc: str
    quest_giver_level: int = 1
    difficulty: QuestDifficulty = QuestDifficulty.MODERATE
    stages: List[QuestStage] = field(default_factory=list)
    rewards: QuestReward = field(default_factory=QuestReward)
    prerequisites: List[str] = field(default_factory=list)  # Quest IDs that must be done first
    blocking_quests: List[str] = field(default_factory=list)  # Quests blocked by this one
    time_limit_hours: Optional[int] = None
    branches: List[QuestBranch] = field(default_factory=list)
    status: QuestStatus = QuestStatus.AVAILABLE
    acceptance_time: Optional[str] = None
    completion_time: Optional[str] = None
    current_stage_index: int = 0
    is_radiant: bool = False  # Repeatable radiant quest
    chain_id: Optional[str] = None  # Quest chain it belongs to
    
    def get_current_stage(self) -> Optional[QuestStage]:
        """Get current quest stage."""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None
    
    def advance_stage(self) -> bool:
        """
        Move to next stage.
        
        Returns:
            True if advanced, False if already on final stage
        """
        if self.current_stage_index < len(self.stages) - 1:
            self.current_stage_index += 1
            return True
        return False
    
    def is_complete(self) -> bool:
        """Quest complete if all stages done."""
        return self.current_stage_index >= len(self.stages) - 1 and \
               self.get_current_stage() and self.get_current_stage().is_complete()
    
    def mark_complete(self) -> None:
        """Mark quest as completed."""
        self.status = QuestStatus.COMPLETED
        self.completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def mark_failed(self) -> None:
        """Mark quest as failed."""
        self.status = QuestStatus.FAILED
        self.completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def can_accept(self, completed_quests: Set[str]) -> bool:
        """Check if quest can be accepted."""
        # Check prerequisites
        for prereq in self.prerequisites:
            if prereq not in completed_quests:
                return False
        return True
    
    def get_level_adjusted_rewards(self, player_level: int) -> QuestReward:
        """
        Get rewards adjusted for player level.
        
        Higher level player = lower XP reward
        Lower level player = higher XP reward (bonus)
        """
        level_diff = player_level - self.quest_giver_level
        xp_multiplier = 1.0
        
        if level_diff < 0:
            xp_multiplier = 1.0 + abs(level_diff) * 0.1
        elif level_diff > 5:
            xp_multiplier = 0.5
        
        adjusted = QuestReward(
            experience_points=int(self.rewards.experience_points * xp_multiplier),
            gold=self.rewards.gold,
            items=self.rewards.items.copy(),
            reputation_changes=self.rewards.reputation_changes.copy(),
            special_rewards=self.rewards.special_rewards.copy()
        )
        return adjusted


@dataclass
class QuestChain:
    """Linked sequence of quests."""
    chain_id: str
    title: str
    description: str
    quests: List[Quest] = field(default_factory=list)
    current_quest_index: int = 0
    is_complete: bool = False
    
    def get_current_quest(self) -> Optional[Quest]:
        """Get current quest in chain."""
        if 0 <= self.current_quest_index < len(self.quests):
            return self.quests[self.current_quest_index]
        return None
    
    def advance_quest(self) -> bool:
        """
        Move to next quest in chain.
        
        Returns:
            True if advanced, False if at end
        """
        if self.current_quest_index < len(self.quests) - 1:
            self.current_quest_index += 1
            return True
        return False


@dataclass
class QuestTracker:
    """
    Tracks player's quest progress.
    
    Attributes:
        active_quests: Currently active quests
        completed_quests: Finished quests
        failed_quests: Failed/abandoned quests
        quest_stages_progress: Dict[quest_id, (stage_index, objective_progress)]
        quest_chains: Active quest chains
    """
    active_quests: Dict[str, Quest] = field(default_factory=dict)
    completed_quests: Set[str] = field(default_factory=set)
    failed_quests: Set[str] = field(default_factory=set)
    quest_stages_progress: Dict[str, Tuple[int, Dict[str, int]]] = field(default_factory=dict)
    quest_chains: Dict[str, QuestChain] = field(default_factory=dict)
    quest_history: List[Tuple[str, QuestStatus, str]] = field(default_factory=list)
    
    def accept_quest(self, quest: Quest) -> bool:
        """
        Accept a quest.
        
        Returns:
            True if accepted, False if already active/completed
        """
        if quest.quest_id in self.active_quests or quest.quest_id in self.completed_quests:
            return False
        
        quest.status = QuestStatus.ACTIVE
        quest.acceptance_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.active_quests[quest.quest_id] = quest
        self._record_history(quest.quest_id, QuestStatus.ACTIVE)
        return True
    
    def complete_quest(self, quest_id: str) -> bool:
        """Complete a quest."""
        if quest_id not in self.active_quests:
            return False
        
        quest = self.active_quests[quest_id]
        quest.mark_complete()
        self.completed_quests.add(quest_id)
        del self.active_quests[quest_id]
        self._record_history(quest_id, QuestStatus.COMPLETED)
        return True
    
    def fail_quest(self, quest_id: str) -> bool:
        """Fail a quest."""
        if quest_id not in self.active_quests:
            return False
        
        quest = self.active_quests[quest_id]
        quest.mark_failed()
        self.failed_quests.add(quest_id)
        del self.active_quests[quest_id]
        self._record_history(quest_id, QuestStatus.FAILED)
        return True
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get quest by ID from any state."""
        if quest_id in self.active_quests:
            return self.active_quests[quest_id]
        # Check completed/failed would need storage
        return None
    
    def get_active_count(self) -> int:
        """Get number of active quests."""
        return len(self.active_quests)
    
    def get_completed_count(self) -> int:
        """Get number of completed quests."""
        return len(self.completed_quests)
    
    def _record_history(self, quest_id: str, status: QuestStatus) -> None:
        """Record quest status change in history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.quest_history.append((quest_id, status, timestamp))


class QuestGenerator:
    """
    Procedurally generates quests.
    
    Supports generating:
    - Kill quests (defeat X enemies of type Y)
    - Collect quests (gather X items)
    - Delivery quests (bring item from NPC A to NPC B)
    - Explore quests (visit X locations)
    """
    
    ENEMY_TYPES = ["goblins", "skeletons", "trolls", "bandits", "dark cultists"]
    ITEM_TYPES = ["herbs", "crystals", "artifacts", "ancient relics", "rare gems"]
    LOCATIONS = ["forest", "cave", "ruins", "tomb", "tower", "temple"]
    
    @staticmethod
    def generate_kill_quest(quest_id: str, difficulty: QuestDifficulty, 
                           npc_giver: str) -> Quest:
        """Generate a kill quest."""
        enemy_type = random.choice(QuestGenerator.ENEMY_TYPES)
        count = random.randint(3, 10)
        
        stage = QuestStage(
            stage_id=f"{quest_id}_stage_1",
            stage_number=1,
            title=f"Eliminate {count} {enemy_type}",
            description=f"The area has been overrun with {enemy_type}. Deal with them."
        )
        
        stage.add_objective(QuestObjective(
            objective_id=f"{quest_id}_obj_1",
            type=ObjectiveType.KILL,
            description=f"Defeat {count} {enemy_type}",
            target=enemy_type,
            required_count=count
        ))
        
        xp = 100 * (difficulty.name.count('L') + 1)
        
        return Quest(
            quest_id=quest_id,
            title=f"Clear the {enemy_type}",
            description=f"A group of {enemy_type} is threatening the area.",
            giver_npc=npc_giver,
            difficulty=difficulty,
            stages=[stage],
            rewards=QuestReward(experience_points=xp, gold=50 * (count // 3)),
            is_radiant=True
        )
    
    @staticmethod
    def generate_collect_quest(quest_id: str, difficulty: QuestDifficulty,
                              npc_giver: str) -> Quest:
        """Generate a collection quest."""
        item_type = random.choice(QuestGenerator.ITEM_TYPES)
        count = random.randint(5, 15)
        
        stage = QuestStage(
            stage_id=f"{quest_id}_stage_1",
            stage_number=1,
            title=f"Gather {count} {item_type}",
            description=f"We need {count} {item_type} for our research."
        )
        
        stage.add_objective(QuestObjective(
            objective_id=f"{quest_id}_obj_1",
            type=ObjectiveType.COLLECT,
            description=f"Collect {count} {item_type}",
            target=item_type,
            required_count=count
        ))
        
        xp = 75 * (difficulty.name.count('L') + 1)
        
        return Quest(
            quest_id=quest_id,
            title=f"Gather {item_type}",
            description=f"We're running low on {item_type}.",
            giver_npc=npc_giver,
            difficulty=difficulty,
            stages=[stage],
            rewards=QuestReward(experience_points=xp, gold=30 * count),
            is_radiant=True
        )
    
    @staticmethod
    def generate_explore_quest(quest_id: str, difficulty: QuestDifficulty,
                              npc_giver: str) -> Quest:
        """Generate an exploration quest."""
        locations = random.sample(QuestGenerator.LOCATIONS, random.randint(2, 4))
        
        stage = QuestStage(
            stage_id=f"{quest_id}_stage_1",
            stage_number=1,
            title=f"Explore {len(locations)} locations",
            description=f"Explore and report on these areas: {', '.join(locations)}"
        )
        
        for i, location in enumerate(locations):
            stage.add_objective(QuestObjective(
                objective_id=f"{quest_id}_obj_{i+1}",
                type=ObjectiveType.EXPLORE,
                description=f"Visit {location}",
                target=location,
                required_count=1
            ))
        
        xp = 120 * (difficulty.name.count('L') + 1)
        
        return Quest(
            quest_id=quest_id,
            title=f"Explore {len(locations)} Areas",
            description="Explore and report on various locations.",
            giver_npc=npc_giver,
            difficulty=difficulty,
            stages=[stage],
            rewards=QuestReward(experience_points=xp, gold=40 * len(locations)),
            is_radiant=True
        )


class QuestValidator:
    """Validates quest completion and conditions."""
    
    @staticmethod
    def validate_quest_complete(quest: Quest) -> bool:
        """Check if quest can be marked complete."""
        current_stage = quest.get_current_stage()
        if not current_stage:
            return False
        
        # All required objectives must be complete
        required = [o for o in current_stage.objectives if not o.is_optional]
        return all(o.is_complete() for o in required)
    
    @staticmethod
    def validate_stage_complete(stage: QuestStage) -> bool:
        """Check if stage is complete."""
        required = [o for o in stage.objectives if not o.is_optional]
        return all(o.is_complete() for o in required)
    
    @staticmethod
    def validate_objective_progress(objective: QuestObjective, 
                                   amount: int) -> bool:
        """Check if objective can progress."""
        if objective.is_complete():
            return False
        return objective.current_count + amount <= objective.required_count
    
    @staticmethod
    def can_branch(branch: QuestBranch, context: Dict[str, Any]) -> bool:
        """Check if quest branch is available."""
        if branch.condition is None:
            return True
        return branch.condition(context)

