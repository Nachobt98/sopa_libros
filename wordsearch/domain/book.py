"""Book-level generation options and domain data."""

from __future__ import annotations

from dataclasses import dataclass

from wordsearch.difficulty_levels import DifficultyLevel


@dataclass
class ThematicGenerationOptions:
    """Runtime options resolved from CLI arguments and/or interactive prompts."""

    book_title: str
    puzzles_txt_path: str
    difficulty: DifficultyLevel
    grid_size: int
