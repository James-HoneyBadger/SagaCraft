#!/usr/bin/env python3
"""SagaCraft - RPG Progression System (Phase II)

Implements character classes, skill trees, leveling, and attributes.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple
import json
from pathlib import Path


class CharacterClass(Enum):
    """Character classes available"""
    WARRIOR = "warrior"
    ROGUE = "rogue"
    MAGE = "mage"
    PALADIN = "paladin"
    RANGER = "ranger"


class Attribute(Enum):
    """Character attributes"""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


@dataclass
class Skill:
    """Represents a learnable skill"""
    id: str
    name: str
    description: str
    level_required: int = 1
    prerequisites: List[str] = field(default_factory=list)
    damage_bonus: int = 0
    critical_chance: float = 0.0  # 0-1
    cooldown: int = 0  # seconds
    mana_cost: int = 0
    passive: bool = False
    category: str = "combat"  # combat, utility, magic, etc.
    
    def to_dict(self) -> Dict:
        """Serialize skill"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Skill":
        """Deserialize skill"""
        return cls(**data)


@dataclass
class SkillTree:
    """Represents a skill tree for a class"""
    name: str
    class_type: CharacterClass
    skills: Dict[str, Skill] = field(default_factory=dict)
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the tree"""
        self.skills[skill.id] = skill
    
    def get_available_skills(self, level: int, learned_skills: Set[str]) -> List[Skill]:
        """Get skills available at current level"""
        available = []
        for skill in self.skills.values():
            if skill.level_required <= level and skill.id not in learned_skills:
                # Check prerequisites
                if all(prereq in learned_skills for prereq in skill.prerequisites):
                    available.append(skill)
        return available
    
    def to_dict(self) -> Dict:
        """Serialize skill tree"""
        return {
            "name": self.name,
            "class_type": self.class_type.value,
            "skills": {k: v.to_dict() for k, v in self.skills.items()}
        }


@dataclass
class ClassDefinition:
    """Defines a character class"""
    class_type: CharacterClass
    description: str
    primary_attribute: Attribute
    attribute_bonuses: Dict[Attribute, int] = field(default_factory=dict)
    starting_health: int = 100
    starting_mana: int = 50
    skill_tree: Optional[SkillTree] = None
    starting_abilities: List[str] = field(default_factory=list)
    
    def get_attribute_bonus(self, attribute: Attribute) -> int:
        """Get bonus for an attribute"""
        return self.attribute_bonuses.get(attribute, 0)
    
    def to_dict(self) -> Dict:
        """Serialize class definition"""
        return {
            "class_type": self.class_type.value,
            "description": self.description,
            "primary_attribute": self.primary_attribute.value,
            "attribute_bonuses": {k.value: v for k, v in self.attribute_bonuses.items()},
            "starting_health": self.starting_health,
            "starting_mana": self.starting_mana,
            "starting_abilities": self.starting_abilities,
        }


@dataclass
class CharacterAttributes:
    """Character attribute values"""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    def get_attribute(self, attr: Attribute) -> int:
        """Get attribute value"""
        attr_map = {
            Attribute.STRENGTH: self.strength,
            Attribute.DEXTERITY: self.dexterity,
            Attribute.CONSTITUTION: self.constitution,
            Attribute.INTELLIGENCE: self.intelligence,
            Attribute.WISDOM: self.wisdom,
            Attribute.CHARISMA: self.charisma,
        }
        return attr_map.get(attr, 10)
    
    def set_attribute(self, attr: Attribute, value: int) -> None:
        """Set attribute value"""
        attr_map = {
            Attribute.STRENGTH: "strength",
            Attribute.DEXTERITY: "dexterity",
            Attribute.CONSTITUTION: "constitution",
            Attribute.INTELLIGENCE: "intelligence",
            Attribute.WISDOM: "wisdom",
            Attribute.CHARISMA: "charisma",
        }
        if attr in attr_map:
            setattr(self, attr_map[attr], value)
    
    def to_dict(self) -> Dict[str, int]:
        """Serialize attributes"""
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "CharacterAttributes":
        """Deserialize attributes"""
        return cls(**data)


@dataclass
class CharacterProgression:
    """Tracks character progression"""
    level: int = 1
    experience: int = 0
    experience_to_next_level: int = 1000
    learned_skills: Set[str] = field(default_factory=set)
    skill_points: int = 0
    
    def add_experience(self, amount: int) -> bool:
        """
        Add experience, return True if level up
        
        Experience requirement scales quadratically
        """
        self.experience += amount
        
        if self.experience >= self.experience_to_next_level:
            self.level_up()
            return True
        return False
    
    def level_up(self) -> None:
        """Handle level up"""
        self.level += 1
        self.experience = 0
        # Quadratic scaling: next_level = base * level^2
        self.experience_to_next_level = int(1000 * (self.level ** 1.5))
        self.skill_points += 2  # Grant skill points on level up
    
    def learn_skill(self, skill_id: str) -> bool:
        """Learn a skill if available"""
        if skill_id not in self.learned_skills and self.skill_points > 0:
            self.learned_skills.add(skill_id)
            self.skill_points -= 1
            return True
        return False
    
    def get_xp_to_next_level(self) -> int:
        """Get experience remaining to next level"""
        return self.experience_to_next_level - self.experience
    
    def to_dict(self) -> Dict:
        """Serialize progression"""
        return {
            "level": self.level,
            "experience": self.experience,
            "experience_to_next_level": self.experience_to_next_level,
            "learned_skills": list(self.learned_skills),
            "skill_points": self.skill_points,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CharacterProgression":
        """Deserialize progression"""
        obj = cls()
        obj.level = data.get("level", 1)
        obj.experience = data.get("experience", 0)
        obj.experience_to_next_level = data.get("experience_to_next_level", 1000)
        obj.learned_skills = set(data.get("learned_skills", []))
        obj.skill_points = data.get("skill_points", 0)
        return obj


class ProgressionSystem:
    """Manages character progression"""
    
    def __init__(self):
        """Initialize progression system"""
        self.class_definitions: Dict[CharacterClass, ClassDefinition] = {}
        self.skill_trees: Dict[CharacterClass, SkillTree] = {}
        self._register_default_classes()
    
    def _register_default_classes(self) -> None:
        """Register default character classes"""
        
        # Warrior
        warrior = ClassDefinition(
            class_type=CharacterClass.WARRIOR,
            description="Strong melee fighter with high health and damage",
            primary_attribute=Attribute.STRENGTH,
            attribute_bonuses={
                Attribute.STRENGTH: 3,
                Attribute.CONSTITUTION: 2,
            },
            starting_health=150,
            starting_mana=25,
            starting_abilities=["slash", "block"],
        )
        self.class_definitions[CharacterClass.WARRIOR] = warrior
        
        # Rogue
        rogue = ClassDefinition(
            class_type=CharacterClass.ROGUE,
            description="Swift and precise with high critical strike chance",
            primary_attribute=Attribute.DEXTERITY,
            attribute_bonuses={
                Attribute.DEXTERITY: 3,
                Attribute.INTELLIGENCE: 1,
            },
            starting_health=80,
            starting_mana=50,
            starting_abilities=["backstab", "dodge"],
        )
        self.class_definitions[CharacterClass.ROGUE] = rogue
        
        # Mage
        mage = ClassDefinition(
            class_type=CharacterClass.MAGE,
            description="Master of spells with high mana and intelligence",
            primary_attribute=Attribute.INTELLIGENCE,
            attribute_bonuses={
                Attribute.INTELLIGENCE: 3,
                Attribute.WISDOM: 2,
            },
            starting_health=60,
            starting_mana=150,
            starting_abilities=["fireball", "frost_bolt"],
        )
        self.class_definitions[CharacterClass.MAGE] = mage
        
        # Paladin
        paladin = ClassDefinition(
            class_type=CharacterClass.PALADIN,
            description="Holy warrior balancing offense and protection",
            primary_attribute=Attribute.WISDOM,
            attribute_bonuses={
                Attribute.WISDOM: 2,
                Attribute.STRENGTH: 2,
                Attribute.CHARISMA: 1,
            },
            starting_health=120,
            starting_mana=80,
            starting_abilities=["holy_strike", "divine_protection"],
        )
        self.class_definitions[CharacterClass.PALADIN] = paladin
        
        # Ranger
        ranger = ClassDefinition(
            class_type=CharacterClass.RANGER,
            description="Skilled archer with nature affinity",
            primary_attribute=Attribute.DEXTERITY,
            attribute_bonuses={
                Attribute.DEXTERITY: 2,
                Attribute.WISDOM: 2,
            },
            starting_health=100,
            starting_mana=60,
            starting_abilities=["arrow_shot", "multishot"],
        )
        self.class_definitions[CharacterClass.RANGER] = ranger
    
    def get_class_definition(self, class_type: CharacterClass) -> Optional[ClassDefinition]:
        """Get a class definition"""
        return self.class_definitions.get(class_type)
    
    def create_character(
        self,
        name: str,
        class_type: CharacterClass
    ) -> Optional[Dict]:
        """
        Create a new character with starting values
        
        Args:
            name: Character name
            class_type: Character class
            
        Returns:
            Character data dictionary or None if class invalid
        """
        class_def = self.get_class_definition(class_type)
        if not class_def:
            return None
        
        return {
            "name": name,
            "class": class_type.value,
            "attributes": CharacterAttributes(
                **{
                    attr.value: 10 + class_def.get_attribute_bonus(attr)
                    for attr in Attribute
                }
            ).to_dict(),
            "progression": CharacterProgression().to_dict(),
            "health": class_def.starting_health,
            "max_health": class_def.starting_health,
            "mana": class_def.starting_mana,
            "max_mana": class_def.starting_mana,
        }


def get_experience_for_level(level: int) -> int:
    """Calculate cumulative experience needed for a level"""
    if level <= 1:
        return 0
    total = 0
    for i in range(1, level):
        total += int(1000 * (i ** 1.5))
    return total


def get_difficulty_multiplier(player_level: int, enemy_level: int) -> float:
    """
    Calculate difficulty multiplier for enemy scaling
    
    Args:
        player_level: Player character level
        enemy_level: Enemy character level
        
    Returns:
        Multiplier for enemy stats (health, damage, etc.)
    """
    level_diff = enemy_level - player_level
    # Each level difference is ~10% difficulty change
    return 1.0 + (level_diff * 0.1)


__all__ = [
    "CharacterClass",
    "Attribute",
    "Skill",
    "SkillTree",
    "ClassDefinition",
    "CharacterAttributes",
    "CharacterProgression",
    "ProgressionSystem",
    "get_experience_for_level",
    "get_difficulty_multiplier",
]
