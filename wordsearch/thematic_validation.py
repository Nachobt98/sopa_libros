"""
Validation helpers for thematic word search books.

The goal is to fail early before rendering pages, because page numbering and
"Solution on page X" references depend on every puzzle being viable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from wordsearch.puzzle_parser import PuzzleSpec
from wordsearch.text_normalization import normalize_word_for_grid


@dataclass
class ValidationIssue:
    severity: str  # "error" | "warning"
    message: str
    puzzle_index: int | None = None
    puzzle_title: str | None = None

    def format(self) -> str:
        prefix = "ERROR" if self.severity == "error" else "WARNING"
        if self.puzzle_index is not None:
            title = f" - {self.puzzle_title}" if self.puzzle_title else ""
            return f"[{prefix}] Puzzle {self.puzzle_index + 1}{title}: {self.message}"
        return f"[{prefix}] {self.message}"


@dataclass
class ThematicValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def add_error(
        self,
        message: str,
        puzzle: PuzzleSpec | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity="error",
                message=message,
                puzzle_index=puzzle.index if puzzle else None,
                puzzle_title=puzzle.title if puzzle else None,
            )
        )

    def add_warning(
        self,
        message: str,
        puzzle: PuzzleSpec | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity="warning",
                message=message,
                puzzle_index=puzzle.index if puzzle else None,
                puzzle_title=puzzle.title if puzzle else None,
            )
        )

    def print_summary(self) -> None:
        print("\n=== Validation report ===")
        if not self.issues:
            print("OK: no validation issues found.")
            return

        for issue in self.issues:
            print(issue.format())

        print(
            f"\nSummary: {len(self.errors)} error(s), "
            f"{len(self.warnings)} warning(s)."
        )


def validate_thematic_specs(
    specs: Sequence[PuzzleSpec],
    grid_size: int,
    *,
    min_words_per_puzzle: int = 1,
    max_fact_chars_warning: int = 260,
    check_background_files: bool = True,
) -> ThematicValidationReport:
    """
    Validate parsed thematic puzzle specs before any rendering happens.

    Errors stop generation. Warnings are informative and do not stop generation.
    """
    report = ThematicValidationReport()

    if not specs:
        report.add_error("No puzzles found in the thematic file.")
        return report

    for spec in specs:
        _validate_single_spec(
            spec,
            grid_size,
            report,
            min_words_per_puzzle=min_words_per_puzzle,
            max_fact_chars_warning=max_fact_chars_warning,
            check_background_files=check_background_files,
        )

    return report


def _validate_single_spec(
    spec: PuzzleSpec,
    grid_size: int,
    report: ThematicValidationReport,
    *,
    min_words_per_puzzle: int,
    max_fact_chars_warning: int,
    check_background_files: bool,
) -> None:
    if not spec.title or not spec.title.strip():
        report.add_error("Missing puzzle title.", spec)

    if not spec.fact or not spec.fact.strip():
        report.add_error("Missing fun fact.", spec)
    elif len(spec.fact.strip()) > max_fact_chars_warning:
        report.add_warning(
            f"Fun fact has {len(spec.fact.strip())} characters; it may be truncated in the layout.",
            spec,
        )

    if not spec.words:
        report.add_error("No words defined.", spec)
        return

    normalized_seen: Dict[str, str] = {}
    valid_normalized_count = 0

    for original in spec.words:
        normalized = normalize_word_for_grid(original)

        if not normalized:
            report.add_error(
                f"Word '{original}' becomes empty after grid normalization.",
                spec,
            )
            continue

        valid_normalized_count += 1

        if len(normalized) > grid_size:
            report.add_error(
                f"Word '{original}' normalizes to '{normalized}' with length {len(normalized)}, "
                f"which is greater than grid size {grid_size}.",
                spec,
            )

        if normalized in normalized_seen and normalized_seen[normalized] != original:
            report.add_warning(
                f"Words '{normalized_seen[normalized]}' and '{original}' normalize to the same grid text '{normalized}'.",
                spec,
            )
        else:
            normalized_seen[normalized] = original

    if valid_normalized_count < min_words_per_puzzle:
        report.add_error(
            f"Only {valid_normalized_count} valid word(s) after normalization; "
            f"minimum required is {min_words_per_puzzle}.",
            spec,
        )

    if check_background_files and spec.block_background:
        if not os.path.exists(spec.block_background):
            report.add_warning(
                f"Background file '{spec.block_background}' does not exist. White/default background will be used.",
                spec,
            )
