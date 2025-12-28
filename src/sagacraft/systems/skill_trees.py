"""Skill Trees & Specializations System - deep progression with branching paths."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Tuple


class SkillCategory(Enum):
    """Types of skill categories."""
    COMBAT = "combat"
    MAGIC = "magic"
    SURVIVAL = "survival"
    SOCIAL = "social"
    CRAFTING = "crafting"


class SpecializationType(Enum):
    """Character specialization types."""
    WARRIOR = "warrior"  # Physical damage, defense
    MAGE = "mage"  # Magic, elemental damage
    RANGER = "ranger"  # Ranged, agility
    PALADIN = "paladin"  # Support, healing
    ROGUE = "rogue"  # Critical chance, stealth
    DRUID = "druid"  # Nature, support, transformation


@dataclass
class Skill:
    """A single skill that can be learned."""
    id: str
    name: str
    description: str
    category: SkillCategory
    level_requirement: int
    base_damage_or_healing: float = 0.0
    mana_cost: int = 0
    cooldown_turns: int = 0
    passive: bool = False  # Passive skills always active
    prerequisites: List[str] = field(default_factory=list)  # Skill IDs required first


@dataclass
class SkillTreeNode:
    """A node in the skill tree."""
    skill: Skill
    tier: int  # 1-5, higher tier = more powerful
    prerequisites: List[str] = field(default_factory=list)  # Node IDs


@dataclass
class Specialization:
    """A character specialization with its own skill tree."""
    id: str
    name: str
    type: SpecializationType
    description: str
    skill_tree: Dict[str, SkillTreeNode] = field(default_factory=dict)
    passive_bonuses: Dict[str, float] = field(default_factory=dict)  # stat: bonus %
    unique_mechanic: str = ""  # Special mechanic description


@dataclass
class CharacterSpecialization:
    """A player's specialization progress."""
    player_id: str
    specialization: Specialization
    learned_skills: Set[str] = field(default_factory=set)
    skill_points_available: int = 0
    proficiency_level: int = 1  # 1-50, increases with usage
    mastery_bonus: Dict[str, float] = field(default_factory=dict)


class SkillTreeSystem:
    """Manages skill trees and character specializations."""

    def __init__(self):
        self.specializations: Dict[str, Specialization] = {}
        self.all_skills: Dict[str, Skill] = {}
        self.player_specializations: Dict[str, CharacterSpecialization] = {}
        self._init_specializations()

    def _init_specializations(self) -> None:
        """Initialize all specializations."""
        # Warrior specialization
        warrior = Specialization(
            id="warrior",
            name="Warrior",
            type=SpecializationType.WARRIOR,
            description="Master of arms and defense. High HP and physical damage.",
            passive_bonuses={"health": 0.20, "armor": 0.15},
            unique_mechanic="Stance switching for defense or offense"
        )
        self.specializations["warrior"] = warrior

        # Mage specialization
        mage = Specialization(
            id="mage",
            name="Mage",
            type=SpecializationType.MAGE,
            description="Master of elemental magic. High mana and spell damage.",
            passive_bonuses={"mana": 0.25, "magical_damage": 0.20},
            unique_mechanic="Mana reflection - convert damage to mana"
        )
        self.specializations["mage"] = mage

        # Ranger specialization
        ranger = Specialization(
            id="ranger",
            name="Ranger",
            type=SpecializationType.RANGER,
            description="Swift and deadly. High agility and critical chance.",
            passive_bonuses={"agility": 0.20, "critical_chance": 0.15},
            unique_mechanic="Multi-shot - attack all enemies at cost"
        )
        self.specializations["ranger"] = ranger

        # Paladin specialization
        paladin = Specialization(
            id="paladin",
            name="Paladin",
            type=SpecializationType.PALADIN,
            description="Holy defender. Balance of offense and healing.",
            passive_bonuses={"defense": 0.20, "healing": 0.25},
            unique_mechanic="Holy shield - damage reduction for party"
        )
        self.specializations["paladin"] = paladin

        # Rogue specialization
        rogue = Specialization(
            id="rogue",
            name="Rogue",
            type=SpecializationType.ROGUE,
            description="Deadly and sneaky. Critical damage and evasion.",
            passive_bonuses={"critical_damage": 0.30, "evasion": 0.20},
            unique_mechanic="Shadow clone - create decoy to confuse enemies"
        )
        self.specializations["rogue"] = rogue

        # Druid specialization
        druid = Specialization(
            id="druid",
            name="Druid",
            type=SpecializationType.DRUID,
            description="Nature's protector. Transformation and healing.",
            passive_bonuses={"healing": 0.20, "nature_damage": 0.15},
            unique_mechanic="Animal form - transform for different abilities"
        )
        self.specializations["druid"] = druid

    def create_specialization(
        self, player_id: str, spec_id: str
    ) -> Tuple[Optional[CharacterSpecialization], str]:
        """Create a specialization for a player."""
        if spec_id not in self.specializations:
            return None, "Specialization not found"

        if player_id in self.player_specializations:
            return None, "Player already has a specialization"

        spec = self.specializations[spec_id]
        char_spec = CharacterSpecialization(
            player_id=player_id,
            specialization=spec,
            skill_points_available=3,  # Starting skill points
        )
        self.player_specializations[player_id] = char_spec
        return char_spec, f"Selected {spec.name} specialization"

    def get_player_specialization(self, player_id: str) -> Optional[CharacterSpecialization]:
        """Get a player's specialization."""
        return self.player_specializations.get(player_id)

    def learn_skill(self, player_id: str, skill_id: str) -> Tuple[bool, str]:
        """Learn a new skill."""
        char_spec = self.get_player_specialization(player_id)
        if not char_spec:
            return False, "No specialization selected"

        if skill_id in char_spec.learned_skills:
            return False, "Skill already learned"

        if char_spec.skill_points_available <= 0:
            return False, "No skill points available"

        skill = self.all_skills.get(skill_id)
        if not skill:
            return False, "Skill not found"

        # Check prerequisites
        for prereq in skill.prerequisites:
            if prereq not in char_spec.learned_skills:
                return False, f"Prerequisite skill {prereq} not learned"

        char_spec.learned_skills.add(skill_id)
        char_spec.skill_points_available -= 1
        return True, f"Learned {skill.name}"

    def gain_skill_points(self, player_id: str, points: int) -> None:
        """Award skill points (from leveling)."""
        char_spec = self.get_player_specialization(player_id)
        if char_spec:
            char_spec.skill_points_available += points

    def increase_proficiency(self, player_id: str, skill_id: str) -> None:
        """Increase proficiency by using a skill."""
        char_spec = self.get_player_specialization(player_id)
        if char_spec and skill_id in char_spec.learned_skills:
            if char_spec.proficiency_level < 50:
                char_spec.proficiency_level += 1

    def get_passive_bonuses(self, player_id: str) -> Dict[str, float]:
        """Get all passive bonuses for a player."""
        char_spec = self.get_player_specialization(player_id)
        if not char_spec:
            return {}

        bonuses = char_spec.specialization.passive_bonuses.copy()

        # Add proficiency bonuses
        proficiency_mult = 1.0 + (char_spec.proficiency_level / 100.0)
        for stat in bonuses:
            bonuses[stat] *= proficiency_mult

        return bonuses

    def get_available_skills(self, player_id: str) -> List[Skill]:
        """Get all skills available to learn for a player."""
        char_spec = self.get_player_specialization(player_id)
        if not char_spec:
            return []

        available = []
        for skill in self.all_skills.values():
            if skill.id not in char_spec.learned_skills:
                if all(p in char_spec.learned_skills for p in skill.prerequisites):
                    available.append(skill)

        return available

    def add_skill(self, skill: Skill) -> None:
        """Register a skill globally."""
        self.all_skills[skill.id] = skill

    def reset_specialization(self, player_id: str) -> Tuple[bool, str]:
        """Reset specialization (refund skill points)."""
        char_spec = self.get_player_specialization(player_id)
        if not char_spec:
            return False, "No specialization to reset"

        # Refund all skill points
        char_spec.skill_points_available += len(char_spec.learned_skills)
        char_spec.learned_skills.clear()
        return True, "Specialization reset. Skills refunded."

    def get_specialization_description(self, spec_id: str) -> str:
        """Get description of a specialization."""
        spec = self.specializations.get(spec_id)
        if spec:
            return f"{spec.name}: {spec.description}\nUnique Mechanic: {spec.unique_mechanic}"
        return "Unknown specialization"
