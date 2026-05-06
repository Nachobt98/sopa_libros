"""Book-level generation options and domain data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from wordsearch.generation.difficulty import DifficultyLevel


@dataclass
class ThematicGenerationOptions:
    """Runtime options resolved from CLI arguments and/or interactive prompts."""

    book_title: str
    puzzles_txt_path: str
    difficulty: DifficultyLevel
    grid_size: int


@dataclass
class SimpleGenerationOptions:
    """Runtime options for the simple word-list generator."""

    book_title: str
    wordlists: Sequence[Sequence[str]]
    difficulty: DifficultyLevel
    grid_size: int
    total_puzzles: int
