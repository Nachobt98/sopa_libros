"""Book-level generation options and domain data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from wordsearch.config.design import DEFAULT_THEME_NAME
from wordsearch.config.formats import DEFAULT_FORMAT_NAME
from wordsearch.generation.difficulty import DifficultyLevel


@dataclass
class ThematicGenerationOptions:
    """Runtime options resolved from CLI arguments and/or interactive prompts."""

    book_title: str
    puzzles_txt_path: str
    difficulty: DifficultyLevel
    grid_size: int
    seed: int | None = None
    validate_only: bool = False
    clean_output: bool = False
    theme_name: str = DEFAULT_THEME_NAME
    format_name: str = DEFAULT_FORMAT_NAME
    output_dir: str | None = None
    limit: int | None = None
    preview: bool = False


@dataclass
class SimpleGenerationOptions:
    """Runtime options for the simple word-list generator."""

    book_title: str
    wordlists: Sequence[Sequence[str]]
    difficulty: DifficultyLevel
    grid_size: int
    total_puzzles: int
