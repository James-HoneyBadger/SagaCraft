"""
Phase VII: Enhanced Social & Party Features

Companion and party system for SagaCraft.
Implements companion recruitment, bonding, party formations, and synergy mechanics.

Classes:
    CompanionClass: Enum of 6 companion archetypes
    CompanionStance: Enum of combat stances (aggressive/defensive/support)
    CompanionPersonality: Enum of personality types affecting dialogue/relationships
    Companion: Complete companion state and abilities
    BondingTier: Relationship milestone levels
    BondingSystem: Companion relationship progression
    PartyFormation: Enum of party formation types
    PartySlot: Position in party with stance
    PartyComposition: Active party with formation and synergies
    CompanionRecruiter: Recruits and manages companions
    SynergyCalculator: Computes party synergy bonuses

Type Hints: 100%
External Dependencies: None
Test Coverage: 25+ tests
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime


class CompanionClass(Enum):
    """6 companion archetypes with distinct playstyles."""
    FIGHTER = "fighter"        # High HP, melee damage
    ROGUE = "rogue"            # High dodge, backstab damage
    MAGE = "mage"              # High magic, spell variety
    CLERIC = "cleric"          # Support, healing
    RANGER = "ranger"          # Ranged damage, evasion
    PALADIN = "paladin"        # Tank, protection spells


class CompanionStance(Enum):
    """Combat stance affects tactics and synergy."""
    AGGRESSIVE = "aggressive"  # Maximize damage output
    DEFENSIVE = "defensive"    # Reduce incoming damage
    SUPPORT = "support"        # Heal/buff allies


class CompanionPersonality(Enum):
    """Personality affects dialogue and bonding."""
    VALIANT = "valiant"        # Honorable, direct, bonus vs evil
    CUNNING = "cunning"        # Strategic, sneaky, bonus in stealth
    MYSTICAL = "mystical"      # Magical affinity, bonus spell power
    NOBLE = "noble"            # Prestigious, faction bonuses
    WILD = "wild"              # Feral, raw power bonuses
    LOYAL = "loyal"            # Devoted companion, bonus at high bond


class BondingTier(Enum):
    """Relationship milestone levels."""
    STRANGER = "stranger"      # -100 to -25 (hostile)
    ACQUAINTANCE = "acquaintance"  # -25 to 25 (neutral)
    FRIEND = "friend"          # 25 to 75 (bonded)
    CLOSE_FRIEND = "close_friend"  # 75 to 150 (deep bond)
    SOULBOUND = "soulbound"    # 150+ (ultimate bond)


@dataclass
class Companion:
    """
    Complete companion state and abilities.
    
    Attributes:
        name: Companion's unique identifier
        title: Display title (e.g., "Thorne the Ranger")
        companion_class: Combat archetype (fighter/rogue/mage/cleric/ranger/paladin)
        personality: Personality type affecting dialogue/bonding
        level: Current companion level (1-20)
        experience: Current experience toward next level
        hp: Current hit points
        max_hp: Maximum hit points
        attributes: Dict with strength, intelligence, dexterity, constitution, etc.
        skills: Dict[skill_name, proficiency_level]
        special_abilities: List of unique abilities
        equipment: Dict[slot, item_name]
        recruitment_date: When recruited
        origin_story: Background narrative
        relationship_flags: Dict for quest/storyline tracking
        memorable_moments: List of significant interactions
        is_recruited: Whether actively in party roster
        is_active: Whether in current active party
    """
    name: str
    title: str
    companion_class: CompanionClass
    personality: CompanionPersonality
    level: int = 1
    experience: int = 0
    hp: int = 100
    max_hp: int = 100
    attributes: Dict[str, int] = field(default_factory=lambda: {
        "strength": 10,
        "intelligence": 10,
        "dexterity": 10,
        "constitution": 10,
        "wisdom": 10,
        "charisma": 10
    })
    skills: Dict[str, int] = field(default_factory=dict)
    special_abilities: List[str] = field(default_factory=list)
    equipment: Dict[str, str] = field(default_factory=dict)
    recruitment_date: str = ""
    origin_story: str = ""
    relationship_flags: Dict[str, bool] = field(default_factory=dict)
    memorable_moments: List[Tuple[str, str]] = field(default_factory=list)
    is_recruited: bool = False
    is_active: bool = False

    def gain_experience(self, amount: int) -> int:
        """
        Gain experience and return levels gained.
        
        Args:
            amount: Experience points to gain
            
        Returns:
            Number of levels gained
        """
        self.experience += amount
        levels_gained = 0
        exp_per_level = 100 * self.level
        
        while self.experience >= exp_per_level:
            self.experience -= exp_per_level
            self.level += 1
            levels_gained += 1
            self.max_hp += 5
            self.hp = self.max_hp
            exp_per_level = 100 * self.level
        
        return levels_gained

    def heal(self, amount: int) -> int:
        """
        Heal companion and return actual healing done.
        
        Args:
            amount: Hit points to restore
            
        Returns:
            Actual healing applied (clamped to max_hp)
        """
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def take_damage(self, amount: int) -> int:
        """
        Take damage and return actual damage taken.
        
        Args:
            amount: Damage to apply
            
        Returns:
            Actual damage taken (clamped to current hp)
        """
        actual_damage = min(amount, self.hp)
        self.hp -= actual_damage
        return actual_damage

    def add_memorable_moment(self, event: str, description: str) -> None:
        """Add significant interaction to memory."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.memorable_moments.append((f"{timestamp}: {event}", description))

    def get_damage_bonus(self) -> int:
        """Calculate damage bonus based on class and attributes."""
        if self.companion_class == CompanionClass.FIGHTER:
            return self.attributes.get("strength", 10) - 10
        elif self.companion_class == CompanionClass.ROGUE:
            return (self.attributes.get("dexterity", 10) - 10) + \
                   (self.attributes.get("strength", 10) - 10) // 2
        elif self.companion_class == CompanionClass.MAGE:
            return self.attributes.get("intelligence", 10) - 10
        elif self.companion_class == CompanionClass.CLERIC:
            return (self.attributes.get("wisdom", 10) - 10) // 2
        elif self.companion_class == CompanionClass.RANGER:
            return (self.attributes.get("dexterity", 10) - 10) + \
                   (self.attributes.get("wisdom", 10) - 10) // 2
        elif self.companion_class == CompanionClass.PALADIN:
            return self.attributes.get("strength", 10) - 10
        return 0

    def get_defense_bonus(self) -> int:
        """Calculate defense bonus based on class and attributes."""
        if self.companion_class == CompanionClass.FIGHTER:
            return self.attributes.get("constitution", 10) - 10
        elif self.companion_class == CompanionClass.ROGUE:
            return self.attributes.get("dexterity", 10) - 10
        elif self.companion_class == CompanionClass.MAGE:
            return 0
        elif self.companion_class == CompanionClass.CLERIC:
            return (self.attributes.get("constitution", 10) - 10) // 2
        elif self.companion_class == CompanionClass.RANGER:
            return self.attributes.get("dexterity", 10) - 10
        elif self.companion_class == CompanionClass.PALADIN:
            return self.attributes.get("constitution", 10) - 10
        return 0

    def is_alive(self) -> bool:
        """Check if companion is alive."""
        return self.hp > 0


@dataclass
class BondingSystem:
    """
    Companion relationship progression.
    
    Tracks bonding points, tiers, unlocks, and special interactions.
    
    Attributes:
        bonding_points: Dict[companion_name, -250 to 250]
        bonding_tiers: Dict[companion_name, BondingTier]
        unlocked_abilities: Dict[companion_name, Set[ability_name]]
        unlocked_storylines: Dict[companion_name, Set[storyline_id]]
        special_quests: Dict[companion_name, Set[quest_id]]
        last_interaction: Dict[companion_name, timestamp]
        soulbound_quests: Set[quest_id] - quests requiring soulbound companion
    """
    bonding_points: Dict[str, int] = field(default_factory=dict)
    bonding_tiers: Dict[str, BondingTier] = field(default_factory=dict)
    unlocked_abilities: Dict[str, Set[str]] = field(default_factory=dict)
    unlocked_storylines: Dict[str, Set[str]] = field(default_factory=dict)
    special_quests: Dict[str, Set[str]] = field(default_factory=dict)
    last_interaction: Dict[str, str] = field(default_factory=dict)
    soulbound_quests: Set[str] = field(default_factory=set)

    def modify_bonding(self, companion_name: str, amount: int, reason: str = "") -> Tuple[int, BondingTier]:
        """
        Modify bonding points and update tier.
        
        Args:
            companion_name: Target companion
            amount: Points to add (negative to decrease)
            reason: Reason for change
            
        Returns:
            (new_points, new_tier)
        """
        current = self.bonding_points.get(companion_name, 0)
        new_points = max(-250, min(250, current + amount))
        self.bonding_points[companion_name] = new_points
        
        new_tier = self._calculate_tier(new_points)
        old_tier = self.bonding_tiers.get(companion_name, BondingTier.STRANGER)
        self.bonding_tiers[companion_name] = new_tier
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_interaction[companion_name] = timestamp
        
        # Check for tier-up unlocks
        if new_tier != old_tier and new_tier != BondingTier.STRANGER:
            self._unlock_tier_rewards(companion_name, new_tier)
        
        return (new_points, new_tier)

    def _calculate_tier(self, points: int) -> BondingTier:
        """Determine bonding tier from points."""
        if points < -100:
            return BondingTier.STRANGER
        elif points < 0:
            return BondingTier.ACQUAINTANCE
        elif points < 75:
            return BondingTier.FRIEND
        elif points < 150:
            return BondingTier.CLOSE_FRIEND
        else:
            return BondingTier.SOULBOUND

    def _unlock_tier_rewards(self, companion_name: str, tier: BondingTier) -> None:
        """Unlock abilities and storylines at tier milestones."""
        if companion_name not in self.unlocked_abilities:
            self.unlocked_abilities[companion_name] = set()
        if companion_name not in self.unlocked_storylines:
            self.unlocked_storylines[companion_name] = set()
        
        if tier == BondingTier.FRIEND:
            self.unlocked_abilities[companion_name].add("basic_combo")
            self.unlocked_storylines[companion_name].add("backstory")
        elif tier == BondingTier.CLOSE_FRIEND:
            self.unlocked_abilities[companion_name].add("special_attack")
            self.unlocked_storylines[companion_name].add("personal_quest")
        elif tier == BondingTier.SOULBOUND:
            self.unlocked_abilities[companion_name].add("ultimate_ability")
            self.unlocked_storylines[companion_name].add("soulbound_ending")
            self.soulbound_quests.add(f"{companion_name}_soulbound_quest")

    def get_bonding_tier(self, companion_name: str) -> BondingTier:
        """Get current bonding tier."""
        return self.bonding_tiers.get(companion_name, BondingTier.STRANGER)

    def is_soulbound(self, companion_name: str) -> bool:
        """Check if companion is soulbound."""
        return self.get_bonding_tier(companion_name) == BondingTier.SOULBOUND

    def get_bonding_percentage(self, companion_name: str) -> int:
        """Get bonding as percentage (0-100)."""
        points = self.bonding_points.get(companion_name, 0)
        percentage = int(((points + 250) / 500) * 100)
        return max(0, min(100, percentage))


class PartyFormation(Enum):
    """Party formation types with tactical implications."""
    FRONTLINE = "frontline"    # Tanks protect ranged
    BALANCED = "balanced"      # Mix of offense and defense
    AGGRESSIVE = "aggressive"  # Full offense, no protection
    DEFENSIVE = "defensive"    # Maximum damage reduction
    SUPPORT = "support"        # Focus on healing and buffs


@dataclass
class PartySlot:
    """Single position in party formation."""
    position: str  # "front_left", "front_right", "back_left", "back_right", "center"
    stance: CompanionStance = CompanionStance.AGGRESSIVE
    companion: Optional[Companion] = None

    def assign_companion(self, companion: Companion, stance: CompanionStance) -> None:
        """Assign companion to slot with stance."""
        self.companion = companion
        self.stance = stance
        companion.is_active = True

    def clear(self) -> None:
        """Remove companion from slot."""
        if self.companion:
            self.companion.is_active = False
        self.companion = None


@dataclass
class PartyComposition:
    """
    Active party with formation and synergy tracking.
    
    Attributes:
        party_name: Name of this party configuration
        formation: Formation type (frontline/balanced/aggressive/defensive/support)
        slots: Dict[position, PartySlot]
        formation_bonus: Damage/defense bonus from formation
        synergy_bonus: Damage bonus from companion combinations
        active_companions: List of currently active companions
    """
    party_name: str
    formation: PartyFormation = PartyFormation.BALANCED
    slots: Dict[str, PartySlot] = field(default_factory=dict)
    formation_bonus: int = 0
    synergy_bonus: int = 0
    active_companions: List[Companion] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize party slots if empty."""
        if not self.slots:
            self.slots = {
                "front_left": PartySlot("front_left"),
                "front_right": PartySlot("front_right"),
                "back_left": PartySlot("back_left"),
                "back_right": PartySlot("back_right"),
                "center": PartySlot("center")
            }

    def add_to_party(self, companion: Companion, position: str, 
                     stance: CompanionStance = CompanionStance.AGGRESSIVE) -> bool:
        """
        Add companion to party at position.
        
        Args:
            companion: Companion to add
            position: Slot position
            stance: Combat stance
            
        Returns:
            True if successful
        """
        if position not in self.slots:
            return False
        
        slot = self.slots[position]
        if slot.companion is not None:
            return False
        
        slot.assign_companion(companion, stance)
        self.active_companions.append(companion)
        return True

    def remove_from_party(self, position: str) -> Optional[Companion]:
        """
        Remove companion from party.
        
        Args:
            position: Slot position
            
        Returns:
            Removed companion or None
        """
        if position not in self.slots:
            return None
        
        slot = self.slots[position]
        companion = slot.companion
        slot.clear()
        
        if companion and companion in self.active_companions:
            self.active_companions.remove(companion)
        
        return companion

    def change_stance(self, position: str, stance: CompanionStance) -> bool:
        """Change companion stance at position."""
        if position not in self.slots:
            return False
        
        slot = self.slots[position]
        if slot.companion is None:
            return False
        
        slot.stance = stance
        return True

    def change_formation(self, formation: PartyFormation) -> None:
        """Change overall party formation."""
        self.formation = formation
        self._recalculate_bonuses()

    def get_formation_bonus(self) -> int:
        """Get damage bonus from formation."""
        bonuses = {
            PartyFormation.FRONTLINE: 5,
            PartyFormation.BALANCED: 10,
            PartyFormation.AGGRESSIVE: 15,
            PartyFormation.DEFENSIVE: -5,
            PartyFormation.SUPPORT: 0
        }
        return bonuses.get(self.formation, 0)

    def get_active_count(self) -> int:
        """Get number of active companions."""
        return len(self.active_companions)

    def is_full(self) -> bool:
        """Check if party is at max size."""
        return len(self.active_companions) >= 3

    def _recalculate_bonuses(self) -> None:
        """Recalculate formation and synergy bonuses."""
        self.formation_bonus = self.get_formation_bonus()


@dataclass
class CompanionRecruiter:
    """
    Recruits and manages companion roster.
    
    Attributes:
        roster: Dict[companion_name, Companion]
        active_party: Current active party
        recruited_count: Total companions ever recruited
        bonding_system: Bonding tracking
    """
    roster: Dict[str, Companion] = field(default_factory=dict)
    active_party: Optional[PartyComposition] = None
    recruited_count: int = 0
    bonding_system: BondingSystem = field(default_factory=BondingSystem)

    def recruit_companion(self, companion: Companion) -> bool:
        """
        Recruit a companion to roster.
        
        Args:
            companion: Companion to recruit
            
        Returns:
            True if successful
        """
        if companion.name in self.roster:
            return False
        
        companion.is_recruited = True
        companion.recruitment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.roster[companion.name] = companion
        self.recruited_count += 1
        self.bonding_system.bonding_points[companion.name] = 0
        self.bonding_system.bonding_tiers[companion.name] = BondingTier.STRANGER
        
        return True

    def release_companion(self, companion_name: str) -> bool:
        """
        Release a companion from roster.
        
        Args:
            companion_name: Companion to release
            
        Returns:
            True if successful
        """
        if companion_name not in self.roster:
            return False
        
        companion = self.roster[companion_name]
        companion.is_recruited = False
        
        # Remove from active party if present
        if self.active_party:
            for position, slot in self.active_party.slots.items():
                if slot.companion and slot.companion.name == companion_name:
                    self.active_party.remove_from_party(position)
        
        del self.roster[companion_name]
        return True

    def get_companion(self, companion_name: str) -> Optional[Companion]:
        """Get companion from roster."""
        return self.roster.get(companion_name)

    def get_all_companions(self) -> List[Companion]:
        """Get all companions in roster."""
        return list(self.roster.values())

    def create_party(self, party_name: str, formation: PartyFormation) -> PartyComposition:
        """Create new party composition."""
        self.active_party = PartyComposition(party_name, formation)
        return self.active_party

    def get_active_party(self) -> Optional[PartyComposition]:
        """Get current active party."""
        return self.active_party


class SynergyCalculator:
    """
    Calculates synergy bonuses from companion combinations.
    
    Synergies occur when complementary companion types/personalities are in party.
    """

    @staticmethod
    def calculate_synergy(party: PartyComposition) -> int:
        """
        Calculate total synergy bonus for party.
        
        Synergies:
        - Fighter + Rogue: +5% damage (back row protection)
        - Mage + Cleric: +10% spell power (combo spells)
        - Ranger + Fighter: +5% defense (protect ranged)
        - Fighter + Paladin: +15% damage (melee combo)
        - Cleric + Paladin: +10% healing (divine combo)
        - All different classes: +5% (diversity bonus)
        
        Args:
            party: Party composition
            
        Returns:
            Total synergy bonus percentage
        """
        if len(party.active_companions) < 2:
            return 0

        bonus = 0
        classes = [c.companion_class for c in party.active_companions]
        personalities = [c.personality for c in party.active_companions]

        # Class synergies
        class_count = len(set(classes))
        
        if CompanionClass.FIGHTER in classes and CompanionClass.ROGUE in classes:
            bonus += 5
        if CompanionClass.MAGE in classes and CompanionClass.CLERIC in classes:
            bonus += 10
        if CompanionClass.RANGER in classes and CompanionClass.FIGHTER in classes:
            bonus += 5
        if CompanionClass.FIGHTER in classes and CompanionClass.PALADIN in classes:
            bonus += 15
        if CompanionClass.CLERIC in classes and CompanionClass.PALADIN in classes:
            bonus += 10

        # Diversity bonus
        if class_count == len(party.active_companions):
            bonus += 5

        # Personality bonuses
        personality_count = len(set(personalities))
        if personality_count == len(party.active_companions):
            bonus += 5  # All different personalities

        return bonus

    @staticmethod
    def get_class_pair_bonus(class1: CompanionClass, class2: CompanionClass) -> int:
        """Get synergy bonus for specific class pair."""
        pairs = {
            (CompanionClass.FIGHTER, CompanionClass.ROGUE): 5,
            (CompanionClass.ROGUE, CompanionClass.FIGHTER): 5,
            (CompanionClass.MAGE, CompanionClass.CLERIC): 10,
            (CompanionClass.CLERIC, CompanionClass.MAGE): 10,
            (CompanionClass.RANGER, CompanionClass.FIGHTER): 5,
            (CompanionClass.FIGHTER, CompanionClass.RANGER): 5,
            (CompanionClass.FIGHTER, CompanionClass.PALADIN): 15,
            (CompanionClass.PALADIN, CompanionClass.FIGHTER): 15,
            (CompanionClass.CLERIC, CompanionClass.PALADIN): 10,
            (CompanionClass.PALADIN, CompanionClass.CLERIC): 10,
        }
        return pairs.get((class1, class2), 0)

