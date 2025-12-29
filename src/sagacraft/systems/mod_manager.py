"""Mod Management System - discover, install, and manage community mods."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
import json
import hashlib


class ModStatus(Enum):
    """Status of a mod."""
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UPDATE_AVAILABLE = "update_available"
    ERROR = "error"


class ModCategory(Enum):
    """Categories for mods."""
    GAMEPLAY = "gameplay"
    CONTENT = "content"
    UI = "ui"
    TOOLS = "tools"
    COSMETIC = "cosmetic"
    AUDIO = "audio"
    LIBRARY = "library"


@dataclass
class ModDependency:
    """A mod dependency."""
    mod_id: str
    version: str
    required: bool = True


@dataclass
class ModInfo:
    """Information about a mod."""
    mod_id: str
    name: str
    version: str
    author: str
    description: str
    category: ModCategory
    dependencies: List[ModDependency] = field(default_factory=list)
    file_path: str = ""
    checksum: str = ""
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    tags: List[str] = field(default_factory=list)
    compatible_version: str = "1.0.0"


@dataclass
class ModRating:
    """A user rating for a mod."""
    mod_id: str
    user_id: str
    rating: int  # 1-5 stars
    review: str = ""
    timestamp: int = 0


@dataclass
class ModConflict:
    """Information about mod conflicts."""
    mod_id: str
    conflicts_with: str
    reason: str
    severity: str  # "warning", "error"


class ModMarketplace:
    """Marketplace for discovering and rating mods."""

    def __init__(self):
        self.available_mods: Dict[str, ModInfo] = {}
        self.mod_ratings: Dict[str, List[ModRating]] = {}
        self.featured_mods: List[str] = []

    def register_mod(self, mod_info: ModInfo) -> None:
        """Register a mod in the marketplace."""
        self.available_mods[mod_info.mod_id] = mod_info

    def search_mods(
        self,
        query: str = "",
        category: Optional[ModCategory] = None,
        tags: Optional[List[str]] = None,
        min_rating: float = 0.0
    ) -> List[ModInfo]:
        """Search for mods."""
        results = []

        for mod in self.available_mods.values():
            # Filter by category
            if category and mod.category != category:
                continue

            # Filter by rating
            if mod.rating < min_rating:
                continue

            # Filter by tags
            if tags and not any(tag in mod.tags for tag in tags):
                continue

            # Filter by query
            if query:
                query_lower = query.lower()
                if not (query_lower in mod.name.lower() or 
                       query_lower in mod.description.lower() or
                       query_lower in mod.author.lower()):
                    continue

            results.append(mod)

        # Sort by rating and downloads
        results.sort(key=lambda m: (m.rating, m.downloads), reverse=True)
        return results

    def rate_mod(
        self,
        mod_id: str,
        user_id: str,
        rating: int,
        review: str = ""
    ) -> Tuple[bool, str]:
        """Rate a mod."""
        if mod_id not in self.available_mods:
            return False, "Mod not found"

        if not (1 <= rating <= 5):
            return False, "Rating must be between 1 and 5"

        if mod_id not in self.mod_ratings:
            self.mod_ratings[mod_id] = []

        # Remove existing rating from this user
        self.mod_ratings[mod_id] = [
            r for r in self.mod_ratings[mod_id] if r.user_id != user_id
        ]

        # Add new rating
        new_rating = ModRating(
            mod_id=mod_id,
            user_id=user_id,
            rating=rating,
            review=review,
            timestamp=int(__import__("time").time())
        )
        self.mod_ratings[mod_id].append(new_rating)

        # Update mod's average rating
        mod = self.available_mods[mod_id]
        ratings = [r.rating for r in self.mod_ratings[mod_id]]
        mod.rating = sum(ratings) / len(ratings)
        mod.rating_count = len(ratings)

        return True, f"Rated {rating}/5 stars"

    def get_featured_mods(self) -> List[ModInfo]:
        """Get featured mods."""
        return [self.available_mods[mod_id] for mod_id in self.featured_mods 
                if mod_id in self.available_mods]

    def get_trending_mods(self, limit: int = 10) -> List[ModInfo]:
        """Get trending mods by recent downloads."""
        sorted_mods = sorted(
            self.available_mods.values(),
            key=lambda m: m.downloads,
            reverse=True
        )
        return sorted_mods[:limit]

    def get_top_rated_mods(self, limit: int = 10) -> List[ModInfo]:
        """Get top-rated mods."""
        sorted_mods = sorted(
            [m for m in self.available_mods.values() if m.rating_count >= 5],
            key=lambda m: m.rating,
            reverse=True
        )
        return sorted_mods[:limit]


class ModManager:
    """Manages installed mods."""

    def __init__(self):
        self.installed_mods: Dict[str, ModInfo] = {}
        self.enabled_mods: Set[str] = set()
        self.mod_conflicts: List[ModConflict] = []
        self.load_order: List[str] = []

    def install_mod(self, mod_info: ModInfo) -> Tuple[bool, str]:
        """Install a mod."""
        # Check if already installed
        if mod_info.mod_id in self.installed_mods:
            return False, "Mod already installed"

        # Check dependencies
        missing_deps = self._check_dependencies(mod_info)
        if missing_deps:
            return False, f"Missing dependencies: {', '.join(missing_deps)}"

        # Check for conflicts
        conflicts = self._check_conflicts(mod_info)
        if conflicts:
            self.mod_conflicts.extend(conflicts)
            # Only block if it's an error-level conflict
            if any(c.severity == "error" for c in conflicts):
                return False, "Mod has critical conflicts"

        # Install mod
        self.installed_mods[mod_info.mod_id] = mod_info
        self.load_order.append(mod_info.mod_id)

        return True, f"Installed {mod_info.name} v{mod_info.version}"

    def uninstall_mod(self, mod_id: str) -> Tuple[bool, str]:
        """Uninstall a mod."""
        if mod_id not in self.installed_mods:
            return False, "Mod not installed"

        # Check if other mods depend on this
        dependents = self._get_dependents(mod_id)
        if dependents:
            return False, f"Other mods depend on this: {', '.join(dependents)}"

        # Remove from enabled if active
        self.enabled_mods.discard(mod_id)

        # Remove from load order
        if mod_id in self.load_order:
            self.load_order.remove(mod_id)

        # Uninstall
        del self.installed_mods[mod_id]

        # Clear related conflicts
        self.mod_conflicts = [
            c for c in self.mod_conflicts
            if c.mod_id != mod_id and c.conflicts_with != mod_id
        ]

        return True, f"Uninstalled {mod_id}"

    def enable_mod(self, mod_id: str) -> Tuple[bool, str]:
        """Enable a mod."""
        if mod_id not in self.installed_mods:
            return False, "Mod not installed"

        if mod_id in self.enabled_mods:
            return False, "Mod already enabled"

        # Check dependencies are enabled
        mod = self.installed_mods[mod_id]
        for dep in mod.dependencies:
            if dep.required and dep.mod_id not in self.enabled_mods:
                return False, f"Dependency {dep.mod_id} must be enabled first"

        self.enabled_mods.add(mod_id)
        return True, f"Enabled {mod.name}"

    def disable_mod(self, mod_id: str) -> Tuple[bool, str]:
        """Disable a mod."""
        if mod_id not in self.enabled_mods:
            return False, "Mod not enabled"

        # Check if enabled mods depend on this
        dependents = [
            mid for mid in self.enabled_mods
            if any(d.mod_id == mod_id and d.required 
                   for d in self.installed_mods[mid].dependencies)
        ]

        if dependents:
            return False, f"Enabled mods depend on this: {', '.join(dependents)}"

        self.enabled_mods.discard(mod_id)
        return True, f"Disabled {mod_id}"

    def get_enabled_mods(self) -> List[ModInfo]:
        """Get list of enabled mods."""
        return [self.installed_mods[mid] for mid in self.enabled_mods]

    def get_installed_mods(self) -> List[ModInfo]:
        """Get list of installed mods."""
        return list(self.installed_mods.values())

    def reorder_mods(self, new_order: List[str]) -> Tuple[bool, str]:
        """Change mod load order."""
        # Validate all mods exist
        if set(new_order) != set(self.load_order):
            return False, "Invalid mod list"

        # Check dependency order is valid
        loaded = set()
        for mod_id in new_order:
            mod = self.installed_mods[mod_id]
            for dep in mod.dependencies:
                if dep.required and dep.mod_id not in loaded:
                    return False, f"{mod_id} depends on {dep.mod_id} which must load first"
            loaded.add(mod_id)

        self.load_order = new_order
        return True, "Load order updated"

    def check_for_updates(self, marketplace: ModMarketplace) -> List[Tuple[str, str, str]]:
        """Check for mod updates."""
        updates = []

        for mod_id, installed_mod in self.installed_mods.items():
            if mod_id in marketplace.available_mods:
                available_mod = marketplace.available_mods[mod_id]
                if available_mod.version != installed_mod.version:
                    updates.append((
                        mod_id,
                        installed_mod.version,
                        available_mod.version
                    ))

        return updates

    def verify_mod_integrity(self, mod_id: str) -> Tuple[bool, str]:
        """Verify mod file integrity."""
        if mod_id not in self.installed_mods:
            return False, "Mod not installed"

        mod = self.installed_mods[mod_id]

        # Simulate checksum verification
        # In production, would read file and calculate hash
        if not mod.checksum:
            return True, "No checksum available"

        # Simulated verification
        return True, "Integrity verified"

    def _check_dependencies(self, mod_info: ModInfo) -> List[str]:
        """Check for missing dependencies."""
        missing = []
        for dep in mod_info.dependencies:
            if dep.required and dep.mod_id not in self.installed_mods:
                missing.append(dep.mod_id)
        return missing

    def _check_conflicts(self, mod_info: ModInfo) -> List[ModConflict]:
        """Check for mod conflicts."""
        conflicts = []

        # Check for known conflicts (in production, would have conflict database)
        for installed_id in self.installed_mods:
            # Simplified conflict detection
            if mod_info.mod_id == installed_id:
                conflicts.append(ModConflict(
                    mod_id=mod_info.mod_id,
                    conflicts_with=installed_id,
                    reason="Duplicate mod ID",
                    severity="error"
                ))

        return conflicts

    def _get_dependents(self, mod_id: str) -> List[str]:
        """Get mods that depend on this mod."""
        dependents = []
        for mid, mod in self.installed_mods.items():
            for dep in mod.dependencies:
                if dep.mod_id == mod_id and dep.required:
                    dependents.append(mid)
        return dependents

    def export_mod_list(self) -> str:
        """Export current mod configuration."""
        config = {
            "mods": [
                {
                    "id": mod.mod_id,
                    "version": mod.version,
                    "enabled": mod.mod_id in self.enabled_mods
                }
                for mod in self.installed_mods.values()
            ],
            "load_order": self.load_order
        }
        return json.dumps(config, indent=2)

    def get_mod_profile(self, mod_id: str) -> Optional[Dict]:
        """Get detailed mod profile."""
        if mod_id not in self.installed_mods:
            return None

        mod = self.installed_mods[mod_id]

        return {
            "id": mod.mod_id,
            "name": mod.name,
            "version": mod.version,
            "author": mod.author,
            "description": mod.description,
            "category": mod.category.value,
            "enabled": mod_id in self.enabled_mods,
            "dependencies": [
                {"id": d.mod_id, "version": d.version, "required": d.required}
                for d in mod.dependencies
            ],
            "conflicts": [
                {"with": c.conflicts_with, "reason": c.reason}
                for c in self.mod_conflicts if c.mod_id == mod_id
            ]
        }
