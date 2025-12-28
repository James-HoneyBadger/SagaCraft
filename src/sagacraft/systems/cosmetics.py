"""Cosmetic Shop System - character skins, emotes, mount appearances, weapon skins."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class CosmeticType(Enum):
    """Types of cosmetics."""
    CHARACTER_SKIN = "character_skin"
    EMOTE = "emote"
    MOUNT_SKIN = "mount_skin"
    WEAPON_SKIN = "weapon_skin"
    ARMOR_SKIN = "armor_skin"
    PARTICLE_EFFECT = "particle_effect"
    VOICE_PACK = "voice_pack"
    TITLE = "title"


class CosmeticRarity(Enum):
    """Rarity tiers for cosmetics."""
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


@dataclass
class Cosmetic:
    """A cosmetic item."""
    id: str
    name: str
    cosmetic_type: CosmeticType
    rarity: CosmeticRarity
    price_premium_currency: int
    price_gold: Optional[int] = None  # Some only available for premium currency
    description: str = ""
    preview_image: str = ""
    seasonal: bool = False  # Limited time availability
    exclusive: bool = False  # Only available through events


@dataclass
class PlayerCosmeticsInventory:
    """Cosmetics owned by a player."""
    player_id: str
    owned_cosmetics: List[str] = field(default_factory=list)
    equipped_cosmetic: Optional[str] = None  # Currently visible cosmetic


class CosmeticShopSystem:
    """Manages cosmetic shop and player cosmetics."""

    def __init__(self):
        self.cosmetics: Dict[str, Cosmetic] = {}
        self.player_inventories: Dict[str, PlayerCosmeticsInventory] = {}
        self.shop_rotation: List[str] = []  # Featured items
        self._init_default_cosmetics()

    def _init_default_cosmetics(self) -> None:
        """Initialize default cosmetics."""
        # Character skins
        self.cosmetics["knight_skin"] = Cosmetic(
            id="knight_skin",
            name="Valiant Knight",
            cosmetic_type=CosmeticType.CHARACTER_SKIN,
            rarity=CosmeticRarity.UNCOMMON,
            price_premium_currency=500,
            description="Gleaming armor of a legendary knight.",
        )

        self.cosmetics["shadow_assassin"] = Cosmetic(
            id="shadow_assassin",
            name="Shadow Assassin",
            cosmetic_type=CosmeticType.CHARACTER_SKIN,
            rarity=CosmeticRarity.RARE,
            price_premium_currency=1200,
            description="Mysterious black robes and twin daggers.",
        )

        self.cosmetics["dragon_rider"] = Cosmetic(
            id="dragon_rider",
            name="Dragon Rider",
            cosmetic_type=CosmeticType.CHARACTER_SKIN,
            rarity=CosmeticRarity.EPIC,
            price_premium_currency=2000,
            exclusive=True,
            description="Armor infused with dragon essence.",
        )

        # Emotes
        self.cosmetics["laugh_emote"] = Cosmetic(
            id="laugh_emote",
            name="Laugh",
            cosmetic_type=CosmeticType.EMOTE,
            rarity=CosmeticRarity.COMMON,
            price_gold=500,
            description="Hearty laugh animation.",
        )

        self.cosmetics["dance_emote"] = Cosmetic(
            id="dance_emote",
            name="Victory Dance",
            cosmetic_type=CosmeticType.EMOTE,
            rarity=CosmeticRarity.UNCOMMON,
            price_premium_currency=200,
            description="Celebratory dance moves.",
        )

        # Mount skins
        self.cosmetics["flaming_horse"] = Cosmetic(
            id="flaming_horse",
            name="Flaming Steed",
            cosmetic_type=CosmeticType.MOUNT_SKIN,
            rarity=CosmeticRarity.EPIC,
            price_premium_currency=1800,
            description="Horse wreathed in magical flames.",
        )

        # Weapon skins
        self.cosmetics["ice_sword"] = Cosmetic(
            id="ice_sword",
            name="Frostbyte Blade",
            cosmetic_type=CosmeticType.WEAPON_SKIN,
            rarity=CosmeticRarity.RARE,
            price_premium_currency=800,
            description="Sword forged from eternal ice.",
        )

        # Particle effects
        self.cosmetics["golden_aura"] = Cosmetic(
            id="golden_aura",
            name="Golden Aura",
            cosmetic_type=CosmeticType.PARTICLE_EFFECT,
            rarity=CosmeticRarity.LEGENDARY,
            price_premium_currency=3000,
            description="Radiant golden particles surround you.",
        )

        # Titles
        self.cosmetics["title_legend"] = Cosmetic(
            id="title_legend",
            name="the Legendary",
            cosmetic_type=CosmeticType.TITLE,
            rarity=CosmeticRarity.LEGENDARY,
            price_premium_currency=500,
            description="Exclusive title for heroes of legend.",
        )

    def add_cosmetic_to_shop(self, cosmetic_id: str) -> bool:
        """Add cosmetic to rotation (featured items)."""
        if cosmetic_id in self.cosmetics:
            if cosmetic_id not in self.shop_rotation:
                self.shop_rotation.append(cosmetic_id)
            return True
        return False

    def get_shop_items(self) -> List[Cosmetic]:
        """Get currently featured shop items."""
        return [self.cosmetics[cid] for cid in self.shop_rotation if cid in self.cosmetics]

    def get_all_cosmetics(self, cosmetic_type: Optional[CosmeticType] = None) -> List[Cosmetic]:
        """Get all cosmetics, optionally filtered by type."""
        cosmetics = list(self.cosmetics.values())
        if cosmetic_type:
            cosmetics = [c for c in cosmetics if c.cosmetic_type == cosmetic_type]
        return cosmetics

    def get_inventory(self, player_id: str) -> PlayerCosmeticsInventory:
        """Get or create player cosmetics inventory."""
        if player_id not in self.player_inventories:
            self.player_inventories[player_id] = PlayerCosmeticsInventory(player_id=player_id)
        return self.player_inventories[player_id]

    def purchase_cosmetic(
        self, player_id: str, cosmetic_id: str, premium_balance: int
    ) -> Tuple[bool, str, int]:
        """Purchase a cosmetic item."""
        cosmetic = self.cosmetics.get(cosmetic_id)
        if not cosmetic:
            return False, "Cosmetic not found", premium_balance

        inventory = self.get_inventory(player_id)

        # Check if already owned
        if cosmetic_id in inventory.owned_cosmetics:
            return False, "Already owned", premium_balance

        # Check balance
        if premium_balance < cosmetic.price_premium_currency:
            return False, f"Insufficient funds ({premium_balance} < {cosmetic.price_premium_currency})", premium_balance

        # Purchase
        new_balance = premium_balance - cosmetic.price_premium_currency
        inventory.owned_cosmetics.append(cosmetic_id)

        return True, f"Purchased {cosmetic.name}!", new_balance

    def equip_cosmetic(self, player_id: str, cosmetic_id: str) -> Tuple[bool, str]:
        """Equip a cosmetic."""
        inventory = self.get_inventory(player_id)

        if cosmetic_id not in inventory.owned_cosmetics:
            return False, "Cosmetic not owned"

        inventory.equipped_cosmetic = cosmetic_id
        return True, f"Equipped {self.cosmetics[cosmetic_id].name}"

    def get_owned_cosmetics(self, player_id: str) -> List[Cosmetic]:
        """Get all cosmetics owned by a player."""
        inventory = self.get_inventory(player_id)
        return [self.cosmetics[cid] for cid in inventory.owned_cosmetics if cid in self.cosmetics]

    def get_equipped_cosmetic(self, player_id: str) -> Optional[Cosmetic]:
        """Get currently equipped cosmetic."""
        inventory = self.get_inventory(player_id)
        if inventory.equipped_cosmetic:
            return self.cosmetics.get(inventory.equipped_cosmetic)
        return None

    def get_rarest_cosmetic(self, player_id: str) -> Optional[Cosmetic]:
        """Get rarest cosmetic owned by player."""
        owned = self.get_owned_cosmetics(player_id)
        if not owned:
            return None
        return max(owned, key=lambda c: c.rarity.value)

    def rotate_shop(self, new_featured: List[str]) -> None:
        """Update shop featured items."""
        self.shop_rotation = [cid for cid in new_featured if cid in self.cosmetics]
