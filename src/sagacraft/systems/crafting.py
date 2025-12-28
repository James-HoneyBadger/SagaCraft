"""Loot Crafting System - combine items to create unique equipment."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from random import random


class CraftingMaterial(Enum):
    """Types of crafting materials."""
    ESSENCE = 2  # Magical properties
    METAL = 1  # Physical durability
    CRYSTAL = 3  # Special effects
    RUNE = 4  # Enchantments
    THREAD = 1  # Binding agent


class ItemRarity(Enum):
    """Item rarity levels."""
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


@dataclass
class LootItem:
    """A loot drop that can be crafted."""
    id: str
    name: str
    rarity: ItemRarity
    materials: Dict[CraftingMaterial, int]
    base_stats: Dict[str, int] = field(default_factory=dict)
    quantity: int = 1

    def get_material_value(self) -> int:
        """Calculate total material value for estimation."""
        return sum(count * (mat.value) for mat, count in self.materials.items())


@dataclass
class RecipeRequirement:
    """A requirement for crafting a recipe."""
    material: CraftingMaterial
    quantity: int
    rarity_minimum: ItemRarity = ItemRarity.COMMON


@dataclass
class CraftingRecipe:
    """A recipe for crafting equipment."""
    id: str
    name: str
    slot: str  # weapon, armor, accessory
    level_requirement: int
    requirements: List[RecipeRequirement]
    output_base_stats: Dict[str, int] = field(default_factory=dict)
    output_rarity: ItemRarity = ItemRarity.RARE

    def validate_materials(self, inventory_materials: Dict[CraftingMaterial, List[LootItem]]) -> Tuple[bool, str]:
        """Check if player has required materials."""
        for req in self.requirements:
            items = inventory_materials.get(req.material, [])

            # Check quantity
            total_available = sum(item.quantity for item in items)
            if total_available < req.quantity:
                return False, f"Need {req.quantity} {req.material.value}, have {total_available}"

            # Check rarity
            rarity_items = [item for item in items if item.rarity.value >= req.rarity_minimum.value]
            if not rarity_items:
                return False, f"Need {req.rarity_minimum.name} {req.material.value}"

        return True, "Recipe requirements met"


class CraftingSystem:
    """Manages loot crafting and item synthesis."""

    def __init__(self):
        self.recipes: Dict[str, CraftingRecipe] = {}
        self.player_crafting_progress: Dict[str, Dict[str, int]] = {}
        self.discovered_recipes: Dict[str, Set[str]] = {}
        self.crafting_xp_per_item: int = 100

    def add_recipe(self, recipe: CraftingRecipe) -> None:
        """Register a crafting recipe."""
        self.recipes[recipe.id] = recipe

    def discover_recipe(self, player_id: str, recipe_id: str) -> bool:
        """Discover a new recipe (unlock crafting)."""
        if player_id not in self.discovered_recipes:
            self.discovered_recipes[player_id] = set()

        if recipe_id in self.recipes:
            self.discovered_recipes[player_id].add(recipe_id)
            return True
        return False

    def get_discovered_recipes(self, player_id: str) -> List[CraftingRecipe]:
        """Get all recipes a player has discovered."""
        discovered_ids = self.discovered_recipes.get(player_id, set())
        return [self.recipes[rid] for rid in discovered_ids if rid in self.recipes]

    def craft_item(
        self,
        player_id: str,
        recipe_id: str,
        inventory_materials: Dict[CraftingMaterial, List[LootItem]],
        player_level: int = 1,
    ) -> Tuple[Optional[LootItem], str]:
        """Attempt to craft an item from a recipe."""
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return None, "Recipe not found"

        # Check player level
        if player_level < recipe.level_requirement:
            return None, f"Requires level {recipe.level_requirement}, you are level {player_level}"

        # Check if discovered
        if player_id not in self.discovered_recipes or recipe_id not in self.discovered_recipes[player_id]:
            return None, "Recipe not discovered"

        # Validate materials
        valid, msg = recipe.validate_materials(inventory_materials)
        if not valid:
            return None, msg

        # Consume materials
        materials_to_remove = {req.material: req.quantity for req in recipe.requirements}
        for material, quantity in materials_to_remove.items():
            items = inventory_materials.get(material, [])
            remaining = quantity
            for item in items[:]:
                if remaining <= 0:
                    break
                consumed = min(item.quantity, remaining)
                item.quantity -= consumed
                remaining -= consumed
                if item.quantity == 0:
                    items.remove(item)

        # Create crafted item
        crafted = LootItem(
            id=f"crafted_{recipe_id}_{hash(str(inventory_materials))}",
            name=recipe.name,
            rarity=recipe.output_rarity,
            materials={},
            base_stats=recipe.output_base_stats.copy(),
            quantity=1,
        )

        # Add crafting bonus (small variance based on rarity)
        if random() > 0.5:
            for stat, value in crafted.base_stats.items():
                crafted.base_stats[stat] = int(value * 1.1)

        return crafted, f"Successfully crafted {recipe.name}"

    def create_default_recipes(self) -> None:
        """Create some basic crafting recipes."""
        # Iron Sword recipe
        self.add_recipe(CraftingRecipe(
            id="iron_sword",
            name="Forged Iron Sword",
            slot="weapon",
            level_requirement=5,
            requirements=[
                RecipeRequirement(CraftingMaterial.METAL, 3, ItemRarity.UNCOMMON),
                RecipeRequirement(CraftingMaterial.THREAD, 1, ItemRarity.COMMON),
            ],
            output_base_stats={"damage": 15, "durability": 100},
            output_rarity=ItemRarity.UNCOMMON,
        ))

        # Essence Shield recipe
        self.add_recipe(CraftingRecipe(
            id="essence_shield",
            name="Enchanted Shield",
            slot="armor",
            level_requirement=10,
            requirements=[
                RecipeRequirement(CraftingMaterial.METAL, 2, ItemRarity.UNCOMMON),
                RecipeRequirement(CraftingMaterial.ESSENCE, 2, ItemRarity.UNCOMMON),
                RecipeRequirement(CraftingMaterial.RUNE, 1, ItemRarity.RARE),
            ],
            output_base_stats={"defense": 20, "magical_resistance": 10},
            output_rarity=ItemRarity.RARE,
        ))

        # Crystal Amulet recipe
        self.add_recipe(CraftingRecipe(
            id="crystal_amulet",
            name="Crystal Amulet",
            slot="accessory",
            level_requirement=8,
            requirements=[
                RecipeRequirement(CraftingMaterial.CRYSTAL, 2, ItemRarity.RARE),
                RecipeRequirement(CraftingMaterial.ESSENCE, 1, ItemRarity.UNCOMMON),
            ],
            output_base_stats={"mana": 25, "mana_regen": 5},
            output_rarity=ItemRarity.RARE,
        ))

        # Legendary Blade recipe
        self.add_recipe(CraftingRecipe(
            id="legendary_blade",
            name="Legendary Blade of Eternity",
            slot="weapon",
            level_requirement=20,
            requirements=[
                RecipeRequirement(CraftingMaterial.METAL, 5, ItemRarity.EPIC),
                RecipeRequirement(CraftingMaterial.CRYSTAL, 3, ItemRarity.EPIC),
                RecipeRequirement(CraftingMaterial.RUNE, 2, ItemRarity.LEGENDARY),
                RecipeRequirement(CraftingMaterial.ESSENCE, 4, ItemRarity.EPIC),
            ],
            output_base_stats={"damage": 50, "critical_chance": 25, "lifesteal": 10},
            output_rarity=ItemRarity.LEGENDARY,
        ))

    def get_recipe(self, recipe_id: str) -> Optional[CraftingRecipe]:
        """Get a recipe by ID."""
        return self.recipes.get(recipe_id)

    def list_all_recipes(self) -> List[CraftingRecipe]:
        """List all available recipes."""
        return list(self.recipes.values())
