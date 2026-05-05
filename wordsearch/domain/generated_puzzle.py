"""Generated puzzle domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from wordsearch.puzzle_parser import PuzzleSpec


@dataclass
class GeneratedPuzzle:
    """Puzzle data after validation and successful grid generation."""

    spec: PuzzleSpec
    words_for_grid: List[str]
    grid: Sequence[Sequence[str]]
    placed_words: Sequence[Tuple[str, Tuple[int, int, int, int]]]
