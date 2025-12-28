"""Tests for Loot Crafting System."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sagacraft.systems.crafting import (
    CraftingSystem,
    CraftingRecipe,
    RecipeRequirement,
    LootItem,
    ItemRarity,
    CraftingMaterial,
)


def test_create_loot_item() -> None:
    """Test creating a loot item."""
    item = LootItem(
        id="iron_ore_1",
        name="Iron Ore",
        rarity=ItemRarity.COMMON,
        materials={CraftingMaterial.METAL: 5},
    )

    assert item.id == "iron_ore_1"
    assert item.name == "Iron Ore"
    assert item.rarity == ItemRarity.COMMON


def test_loot_item_material_value() -> None:
    """Test calculating material value."""
    item = LootItem(
        id="mixed_1",
        name="Mixed Materials",
        rarity=ItemRarity.UNCOMMON,
        materials={
            CraftingMaterial.METAL: 3,
            CraftingMaterial.ESSENCE: 2,
        },
    )

    value = item.get_material_value()
    # METAL=1, ESSENCE=2, so 3*1 + 2*2 = 7
    assert value == 7


def test_create_recipe() -> None:
    """Test creating a crafting recipe."""
    recipe = CraftingRecipe(
        id="iron_sword",
        name="Iron Sword",
        slot="weapon",
        level_requirement=5,
        requirements=[
            RecipeRequirement(CraftingMaterial.METAL, 3),
        ],
        output_base_stats={"damage": 15},
        output_rarity=ItemRarity.UNCOMMON,
    )

    assert recipe.id == "iron_sword"
    assert recipe.name == "Iron Sword"
    assert recipe.level_requirement == 5


def test_recipe_validation_success() -> None:
    """Test validating materials for a recipe."""
    recipe = CraftingRecipe(
        id="test_recipe",
        name="Test",
        slot="weapon",
        level_requirement=1,
        requirements=[
            RecipeRequirement(CraftingMaterial.METAL, 2),
        ],
    )

    inventory = {
        CraftingMaterial.METAL: [
            LootItem("m1", "Metal", ItemRarity.COMMON, {}, quantity=2),
        ]
    }

    valid, msg = recipe.validate_materials(inventory)
    assert valid is True
    assert "met" in msg.lower()


def test_recipe_validation_insufficient() -> None:
    """Test validation fails with insufficient materials."""
    recipe = CraftingRecipe(
        id="test_recipe",
        name="Test",
        slot="weapon",
        level_requirement=1,
        requirements=[
            RecipeRequirement(CraftingMaterial.METAL, 5),
        ],
    )

    inventory = {
        CraftingMaterial.METAL: [
            LootItem("m1", "Metal", ItemRarity.COMMON, {}, quantity=2),
        ]
    }

    valid, msg = recipe.validate_materials(inventory)
    assert valid is False
    assert "5" in msg


def test_recipe_validation_rarity() -> None:
    """Test validation checks rarity requirements."""
    recipe = CraftingRecipe(
        id="test_recipe",
        name="Test",
        slot="weapon",
        level_requirement=1,
        requirements=[
            RecipeRequirement(
                CraftingMaterial.METAL, 1, rarity_minimum=ItemRarity.RARE
            ),
        ],
    )

    # Have COMMON quality metal
    inventory = {
        CraftingMaterial.METAL: [
            LootItem("m1", "Metal", ItemRarity.COMMON, {}, quantity=1),
        ]
    }

    valid, msg = recipe.validate_materials(inventory)
    assert valid is False
    assert "RARE" in msg


def test_crafting_system_add_recipe() -> None:
    """Test adding recipes to crafting system."""
    system = CraftingSystem()
    recipe = CraftingRecipe(
        id="test",
        name="Test Recipe",
        slot="weapon",
        level_requirement=1,
        requirements=[],
    )

    system.add_recipe(recipe)
    assert system.get_recipe("test") is recipe


def test_discover_recipe() -> None:
    """Test discovering a recipe."""
    system = CraftingSystem()
    recipe = CraftingRecipe(
        id="hidden_recipe",
        name="Hidden",
        slot="weapon",
        level_requirement=1,
        requirements=[],
    )
    system.add_recipe(recipe)

    discovered = system.discover_recipe("player_1", "hidden_recipe")
    assert discovered is True

    recipes = system.get_discovered_recipes("player_1")
    assert len(recipes) == 1
    assert recipes[0].id == "hidden_recipe"


def test_craft_item_success() -> None:
    """Test successfully crafting an item."""
    system = CraftingSystem()
    recipe = CraftingRecipe(
        id="test_craft",
        name="Crafted Sword",
        slot="weapon",
        level_requirement=1,
        requirements=[
            RecipeRequirement(CraftingMaterial.METAL, 2),
        ],
        output_base_stats={"damage": 10},
    )
    system.add_recipe(recipe)
    system.discover_recipe("player_1", "test_craft")

    inventory = {
        CraftingMaterial.METAL: [
            LootItem("m1", "Metal", ItemRarity.COMMON, {}, quantity=2),
        ]
    }

    crafted, msg = system.craft_item("player_1", "test_craft", inventory, player_level=5)

    assert crafted is not None
    assert crafted.name == "Crafted Sword"
    assert "damage" in crafted.base_stats
    assert "Successfully" in msg


def test_craft_item_level_requirement() -> None:
    """Test crafting fails with insufficient level."""
    system = CraftingSystem()
    recipe = CraftingRecipe(
        id="advanced",
        name="Advanced Item",
        slot="weapon",
        level_requirement=20,
        requirements=[],
    )
    system.add_recipe(recipe)
    system.discover_recipe("player_1", "advanced")

    crafted, msg = system.craft_item("player_1", "advanced", {}, player_level=5)

    assert crafted is None
    assert "Requires level 20" in msg


def test_craft_item_not_discovered() -> None:
    """Test crafting fails if recipe not discovered."""
    system = CraftingSystem()
    recipe = CraftingRecipe(
        id="secret",
        name="Secret Recipe",
        slot="weapon",
        level_requirement=1,
        requirements=[],
    )
    system.add_recipe(recipe)

    crafted, msg = system.craft_item("player_1", "secret", {}, player_level=5)

    assert crafted is None
    assert "not discovered" in msg


def test_default_recipes() -> None:
    """Test creating default recipes."""
    system = CraftingSystem()
    system.create_default_recipes()

    recipes = system.list_all_recipes()
    assert len(recipes) == 4
    assert any(r.id == "iron_sword" for r in recipes)
    assert any(r.id == "legendary_blade" for r in recipes)


def test_material_consumption() -> None:
    """Test that materials are consumed during crafting."""
    system = CraftingSystem()
    recipe = CraftingRecipe(
        id="test",
        name="Test",
        slot="weapon",
        level_requirement=1,
        requirements=[
            RecipeRequirement(CraftingMaterial.METAL, 3),
        ],
    )
    system.add_recipe(recipe)
    system.discover_recipe("player_1", "test")

    item = LootItem("m1", "Metal", ItemRarity.COMMON, {}, quantity=5)
    inventory = {CraftingMaterial.METAL: [item]}

    # Craft once
    system.craft_item("player_1", "test", inventory)

    # Materials should be reduced
    assert item.quantity == 2


def test_item_rarity_levels() -> None:
    """Test all rarity levels."""
    rarities = [
        (ItemRarity.COMMON, 1),
        (ItemRarity.UNCOMMON, 2),
        (ItemRarity.RARE, 3),
        (ItemRarity.EPIC, 4),
        (ItemRarity.LEGENDARY, 5),
    ]

    for rarity, value in rarities:
        assert rarity.value == value


if __name__ == "__main__":
    test_create_loot_item()
    test_loot_item_material_value()
    test_create_recipe()
    test_recipe_validation_success()
    test_recipe_validation_insufficient()
    test_recipe_validation_rarity()
    test_crafting_system_add_recipe()
    test_discover_recipe()
    test_craft_item_success()
    test_craft_item_level_requirement()
    test_craft_item_not_discovered()
    test_default_recipes()
    test_material_consumption()
    test_item_rarity_levels()
    print("✓ All crafting tests passed!")
