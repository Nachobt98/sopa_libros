"""Backward-compatible imports for thematic validation."""

from wordsearch.validation.thematic import (
    ThematicValidationReport,
    ValidationIssue,
    validate_thematic_specs,
)

__all__ = [
    "ThematicValidationReport",
    "ValidationIssue",
    "validate_thematic_specs",
]
