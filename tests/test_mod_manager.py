"""Tests for Mod Management System."""

import unittest
from sagacraft.systems.mod_manager import (
    ModManager,
    ModMarketplace,
    ModInfo,
    ModCategory,
    ModDependency,
)


class TestModMarketplace(unittest.TestCase):
    """Test the mod marketplace."""

    def setUp(self):
        """Set up test fixtures."""
        self.marketplace = ModMarketplace()

    def test_register_mod(self):
        """Test registering a mod."""
        mod = ModInfo(
            mod_id="test_mod",
            name="Test Mod",
            version="1.0.0",
            author="TestAuthor",
            description="A test mod",
            category=ModCategory.GAMEPLAY
        )

        self.marketplace.register_mod(mod)
        self.assertIn("test_mod", self.marketplace.available_mods)

    def test_search_mods_by_query(self):
        """Test searching mods by query."""
        mod1 = ModInfo("mod1", "Dragon Quest", "1.0", "Author", "Dragons!", ModCategory.CONTENT)
        mod2 = ModInfo("mod2", "UI Enhancer", "1.0", "Author", "Better UI", ModCategory.UI)

        self.marketplace.register_mod(mod1)
        self.marketplace.register_mod(mod2)

        results = self.marketplace.search_mods(query="dragon")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].mod_id, "mod1")

    def test_search_mods_by_category(self):
        """Test searching mods by category."""
        mod1 = ModInfo("mod1", "Content", "1.0", "A", "Desc", ModCategory.CONTENT)
        mod2 = ModInfo("mod2", "UI", "1.0", "A", "Desc", ModCategory.UI)

        self.marketplace.register_mod(mod1)
        self.marketplace.register_mod(mod2)

        results = self.marketplace.search_mods(category=ModCategory.UI)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, ModCategory.UI)

    def test_rate_mod(self):
        """Test rating a mod."""
        mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        self.marketplace.register_mod(mod)

        success, msg = self.marketplace.rate_mod("mod1", "user1", 5, "Great!")
        self.assertTrue(success)
        self.assertEqual(mod.rating, 5.0)
        self.assertEqual(mod.rating_count, 1)

    def test_rating_average(self):
        """Test rating average calculation."""
        mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        self.marketplace.register_mod(mod)

        self.marketplace.rate_mod("mod1", "user1", 5)
        self.marketplace.rate_mod("mod1", "user2", 3)

        self.assertEqual(mod.rating, 4.0)  # (5+3)/2
        self.assertEqual(mod.rating_count, 2)

    def test_get_trending_mods(self):
        """Test getting trending mods."""
        mod1 = ModInfo("mod1", "Popular", "1.0", "A", "Desc", ModCategory.GAMEPLAY, downloads=1000)
        mod2 = ModInfo("mod2", "Less Popular", "1.0", "A", "Desc", ModCategory.GAMEPLAY, downloads=100)

        self.marketplace.register_mod(mod1)
        self.marketplace.register_mod(mod2)

        trending = self.marketplace.get_trending_mods(limit=1)
        self.assertEqual(trending[0].mod_id, "mod1")

    def test_get_top_rated_mods(self):
        """Test getting top-rated mods."""
        mod1 = ModInfo("mod1", "Good", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        mod2 = ModInfo("mod2", "Better", "1.0", "A", "Desc", ModCategory.GAMEPLAY)

        self.marketplace.register_mod(mod1)
        self.marketplace.register_mod(mod2)

        # Add enough ratings to qualify
        for i in range(5):
            self.marketplace.rate_mod("mod1", f"user{i}", 3)
            self.marketplace.rate_mod("mod2", f"user{i+5}", 5)

        top_rated = self.marketplace.get_top_rated_mods(limit=1)
        self.assertEqual(top_rated[0].mod_id, "mod2")


class TestModManager(unittest.TestCase):
    """Test the mod manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = ModManager()

    def test_install_mod(self):
        """Test installing a mod."""
        mod = ModInfo("mod1", "Test Mod", "1.0", "Author", "Description", ModCategory.GAMEPLAY)

        success, msg = self.manager.install_mod(mod)

        self.assertTrue(success)
        self.assertIn("mod1", self.manager.installed_mods)

    def test_install_duplicate_mod(self):
        """Test installing duplicate mod fails."""
        mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY)

        self.manager.install_mod(mod)
        success, msg = self.manager.install_mod(mod)

        self.assertFalse(success)
        self.assertIn("already installed", msg)

    def test_install_mod_with_dependencies(self):
        """Test installing mod with missing dependencies fails."""
        dep = ModDependency("required_mod", "1.0", required=True)
        mod = ModInfo(
            "mod1", "Test", "1.0", "A", "Desc",
            ModCategory.GAMEPLAY,
            dependencies=[dep]
        )

        success, msg = self.manager.install_mod(mod)

        self.assertFalse(success)
        self.assertIn("Missing dependencies", msg)

    def test_install_with_satisfied_dependencies(self):
        """Test installing mod with satisfied dependencies."""
        dep_mod = ModInfo("lib", "Library", "1.0", "A", "Lib", ModCategory.LIBRARY)
        dep = ModDependency("lib", "1.0", required=True)
        mod = ModInfo(
            "mod1", "Test", "1.0", "A", "Desc",
            ModCategory.GAMEPLAY,
            dependencies=[dep]
        )

        self.manager.install_mod(dep_mod)
        success, msg = self.manager.install_mod(mod)

        self.assertTrue(success)

    def test_uninstall_mod(self):
        """Test uninstalling a mod."""
        mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        self.manager.install_mod(mod)

        success, msg = self.manager.uninstall_mod("mod1")

        self.assertTrue(success)
        self.assertNotIn("mod1", self.manager.installed_mods)

    def test_uninstall_with_dependents_fails(self):
        """Test uninstalling mod with dependents fails."""
        dep_mod = ModInfo("lib", "Library", "1.0", "A", "Lib", ModCategory.LIBRARY)
        dep = ModDependency("lib", "1.0", required=True)
        mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY, dependencies=[dep])

        self.manager.install_mod(dep_mod)
        self.manager.install_mod(mod)

        success, msg = self.manager.uninstall_mod("lib")

        self.assertFalse(success)
        self.assertIn("depend", msg)

    def test_enable_mod(self):
        """Test enabling a mod."""
        mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        self.manager.install_mod(mod)

        success, msg = self.manager.enable_mod("mod1")

        self.assertTrue(success)
        self.assertIn("mod1", self.manager.enabled_mods)

    def test_disable_mod(self):
        """Test disabling a mod."""
        mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        self.manager.install_mod(mod)
        self.manager.enable_mod("mod1")

        success, msg = self.manager.disable_mod("mod1")

        self.assertTrue(success)
        self.assertNotIn("mod1", self.manager.enabled_mods)

    def test_get_enabled_mods(self):
        """Test getting enabled mods list."""
        mod1 = ModInfo("mod1", "Test1", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        mod2 = ModInfo("mod2", "Test2", "1.0", "A", "Desc", ModCategory.GAMEPLAY)

        self.manager.install_mod(mod1)
        self.manager.install_mod(mod2)
        self.manager.enable_mod("mod1")

        enabled = self.manager.get_enabled_mods()

        self.assertEqual(len(enabled), 1)
        self.assertEqual(enabled[0].mod_id, "mod1")

    def test_reorder_mods(self):
        """Test reordering mod load order."""
        mod1 = ModInfo("mod1", "Test1", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        mod2 = ModInfo("mod2", "Test2", "1.0", "A", "Desc", ModCategory.GAMEPLAY)

        self.manager.install_mod(mod1)
        self.manager.install_mod(mod2)

        success, msg = self.manager.reorder_mods(["mod2", "mod1"])

        self.assertTrue(success)
        self.assertEqual(self.manager.load_order, ["mod2", "mod1"])

    def test_check_for_updates(self):
        """Test checking for mod updates."""
        marketplace = ModMarketplace()

        installed_mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        updated_mod = ModInfo("mod1", "Test", "1.1", "A", "Desc", ModCategory.GAMEPLAY)

        self.manager.install_mod(installed_mod)
        marketplace.register_mod(updated_mod)

        updates = self.manager.check_for_updates(marketplace)

        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0][0], "mod1")  # mod_id
        self.assertEqual(updates[0][1], "1.0")   # current version
        self.assertEqual(updates[0][2], "1.1")   # available version

    def test_export_mod_list(self):
        """Test exporting mod configuration."""
        mod = ModInfo("mod1", "Test", "1.0", "A", "Desc", ModCategory.GAMEPLAY)
        self.manager.install_mod(mod)
        self.manager.enable_mod("mod1")

        exported = self.manager.export_mod_list()

        self.assertIn("mod1", exported)
        self.assertIn("1.0", exported)

    def test_get_mod_profile(self):
        """Test getting mod profile."""
        mod = ModInfo("mod1", "Test", "1.0", "Author", "Description", ModCategory.GAMEPLAY)
        self.manager.install_mod(mod)

        profile = self.manager.get_mod_profile("mod1")

        self.assertIsNotNone(profile)
        self.assertEqual(profile["name"], "Test")
        self.assertEqual(profile["version"], "1.0")


if __name__ == "__main__":
    unittest.main()
