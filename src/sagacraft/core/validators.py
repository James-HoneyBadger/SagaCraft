"""Shared validators and utilities for all systems."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    errors: List[str]
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.valid and len(self.errors) == 0

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


class ResourceValidator:
    """Validates resource costs and availability."""

    @staticmethod
    def validate_cost(
        available: Dict[str, int],
        cost: Dict[str, int]
    ) -> ValidationResult:
        """Check if resources available for cost."""
        result = ValidationResult(valid=True, errors=[])

        for resource, amount in cost.items():
            available_amount = available.get(resource, 0)
            if available_amount < amount:
                result.add_error(
                    f"Insufficient {resource}: need {amount}, have {available_amount}"
                )

        return result

    @staticmethod
    def consume_resources(
        available: Dict[str, int],
        cost: Dict[str, int]
    ) -> ValidationResult:
        """Consume resources and return result."""
        # Validate first
        result = ResourceValidator.validate_cost(available, cost)
        if not result.is_valid():
            return result

        # Consume
        for resource, amount in cost.items():
            available[resource] -= amount

        return result

    @staticmethod
    def grant_resources(
        available: Dict[str, int],
        rewards: Dict[str, int]
    ) -> None:
        """Grant resources to pool."""
        for resource, amount in rewards.items():
            available[resource] = available.get(resource, 0) + amount


class LevelValidator:
    """Validates level requirements."""

    @staticmethod
    def validate_level_requirement(
        player_level: int,
        required_level: int
    ) -> Tuple[bool, str]:
        """Check if player meets level requirement."""
        if player_level >= required_level:
            return True, "Level requirement met"
        return False, f"Requires level {required_level}, you are level {player_level}"

    @staticmethod
    def validate_level_range(level: int, min_level: int = 1, max_level: int = 999) -> bool:
        """Check if level is in valid range."""
        return min_level <= level <= max_level


class RarityValidator:
    """Validates rarity requirements."""

    @staticmethod
    def validate_rarity_requirement(
        item_rarity: int,
        required_rarity: int
    ) -> Tuple[bool, str]:
        """Check if item meets rarity requirement."""
        if item_rarity >= required_rarity:
            return True, "Rarity requirement met"
        return False, f"Requires rarity {required_rarity}, item is rarity {item_rarity}"


class RangeValidator:
    """Validates numeric ranges."""

    @staticmethod
    def validate_range(
        value: int | float,
        min_val: int | float = 0,
        max_val: int | float = 100,
        name: str = "value"
    ) -> ValidationResult:
        """Validate value is within range."""
        result = ValidationResult(valid=True, errors=[])

        if value < min_val:
            result.add_error(f"{name} too low: {value} < {min_val}")
        if value > max_val:
            result.add_error(f"{name} too high: {value} > {max_val}")

        return result

    @staticmethod
    def clamp(
        value: int | float,
        min_val: int | float = 0,
        max_val: int | float = 100
    ) -> int | float:
        """Clamp value to range."""
        return max(min_val, min(max_val, value))


class PlayerValidator:
    """Validates player state and properties."""

    @staticmethod
    def validate_player_exists(player_id: str, player_registry: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if player exists."""
        if not player_id:
            return False, "Invalid player ID"
        if player_id not in player_registry:
            return False, f"Player {player_id} not found"
        return True, "Player exists"

    @staticmethod
    def validate_player_state(
        player_id: str,
        required_state_keys: List[str],
        player_state: Dict[str, Dict[str, Any]]
    ) -> ValidationResult:
        """Validate player has required state."""
        result = ValidationResult(valid=True, errors=[])

        if player_id not in player_state:
            result.add_error(f"No state for player {player_id}")
            return result

        player_data = player_state[player_id]
        for key in required_state_keys:
            if key not in player_data:
                result.add_warning(f"Missing state key: {key}")

        return result


class ConfigValidator:
    """Validates system configurations."""

    @staticmethod
    def validate_not_empty(value: Any, field_name: str) -> ValidationResult:
        """Validate value is not empty."""
        result = ValidationResult(valid=True, errors=[])
        if not value:
            result.add_error(f"{field_name} cannot be empty")
        return result

    @staticmethod
    def validate_string_length(
        value: str,
        min_length: int = 1,
        max_length: int = 255,
        field_name: str = "string"
    ) -> ValidationResult:
        """Validate string length."""
        result = ValidationResult(valid=True, errors=[])

        if len(value) < min_length:
            result.add_error(f"{field_name} too short (min {min_length})")
        if len(value) > max_length:
            result.add_error(f"{field_name} too long (max {max_length})")

        return result

    @staticmethod
    def validate_enum_value(
        value: Any,
        enum_class: type,
        field_name: str = "value"
    ) -> ValidationResult:
        """Validate value is valid enum."""
        result = ValidationResult(valid=True, errors=[])

        try:
            if not isinstance(value, enum_class):
                result.add_error(f"{field_name} not valid {enum_class.__name__}")
        except Exception as e:
            result.add_error(f"Error validating {field_name}: {str(e)}")

        return result


class DataValidator:
    """Validates data structures."""

    @staticmethod
    def validate_dict_structure(
        data: Dict[str, Any],
        required_keys: List[str],
        optional_keys: List[str] = None
    ) -> ValidationResult:
        """Validate dictionary has required and optional keys."""
        result = ValidationResult(valid=True, errors=[])
        optional_keys = optional_keys or []

        # Check required
        for key in required_keys:
            if key not in data:
                result.add_error(f"Missing required key: {key}")

        # Warn about unknown keys
        valid_keys = set(required_keys) | set(optional_keys)
        for key in data:
            if key not in valid_keys:
                result.add_warning(f"Unknown key: {key}")

        return result

    @staticmethod
    def validate_list_not_empty(
        data: List[Any],
        field_name: str = "list"
    ) -> ValidationResult:
        """Validate list is not empty."""
        result = ValidationResult(valid=True, errors=[])
        if not data or len(data) == 0:
            result.add_error(f"{field_name} cannot be empty")
        return result


class ProbabilityValidator:
    """Validates probability values."""

    @staticmethod
    def validate_probability(
        value: float,
        field_name: str = "probability"
    ) -> ValidationResult:
        """Validate value is 0-1 probability."""
        result = ValidationResult(valid=True, errors=[])

        if not isinstance(value, (int, float)):
            result.add_error(f"{field_name} must be numeric")
        elif value < 0.0 or value > 1.0:
            result.add_error(f"{field_name} must be between 0 and 1, got {value}")

        return result

    @staticmethod
    def validate_probabilities_sum(
        probabilities: Dict[str, float],
        tolerance: float = 0.001
    ) -> ValidationResult:
        """Validate probabilities sum to 1."""
        result = ValidationResult(valid=True, errors=[])
        total = sum(probabilities.values())

        if abs(total - 1.0) > tolerance:
            result.add_error(f"Probabilities sum to {total}, expected 1.0")

        return result


# Helper functions for common validations
def validate_positive_int(value: int, field_name: str = "value") -> ValidationResult:
    """Validate positive integer."""
    result = ValidationResult(valid=True, errors=[])
    if not isinstance(value, int):
        result.add_error(f"{field_name} must be integer")
    elif value <= 0:
        result.add_error(f"{field_name} must be positive")
    return result


def validate_non_negative_int(value: int, field_name: str = "value") -> ValidationResult:
    """Validate non-negative integer."""
    result = ValidationResult(valid=True, errors=[])
    if not isinstance(value, int):
        result.add_error(f"{field_name} must be integer")
    elif value < 0:
        result.add_error(f"{field_name} must be non-negative")
    return result
