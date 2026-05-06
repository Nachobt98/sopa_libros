"""Generated puzzle domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from wordsearch.domain.grid import PlacedWord
from wordsearch.domain.puzzle import PuzzleSpec


@dataclass
class GeneratedPuzzle:
    """Puzzle data after validation and successful grid generation."""

    spec: PuzzleSpec
    words_for_grid: List[str]
    grid: Sequence[Sequence[str]]
    placed_words: Sequence[PlacedWord]
