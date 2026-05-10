"""Batch grid generation for thematic books."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import List, Sequence

from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.grid import GridGenerationFailure
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.generation.difficulty import DifficultyLevel
from wordsearch.generation.grid import generate_word_search_grid
from wordsearch.text_normalization import normalize_words_for_grid


@dataclass
class GridBatchResult:
    """Result of generating all grids for a thematic book."""

    generated_puzzles: List[GeneratedPuzzle] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        return bool(self.failures)


def generate_thematic_grids(
    specs: Sequence[PuzzleSpec],
    difficulty: DifficultyLevel,
    grid_size: int,
    *,
    seed: int | None = None,
    progress_callback: Callable[[], None] | None = None,
) -> GridBatchResult:
    """
    Generate every puzzle grid before rendering anything.

    This keeps page numbering reliable: if any puzzle cannot be generated, the
    caller can stop before creating partial PNG/PDF output with incorrect page
    references.
    """
    result = GridBatchResult()
    rng = random.Random(seed) if seed is not None else None

    for spec in specs:
        words_for_grid = normalize_words_for_grid(spec.words)
        grid_result = generate_word_search_grid(
            words_for_grid,
            difficulty=difficulty,
            grid_size=grid_size,
            rng=rng,
        )

        if isinstance(grid_result, GridGenerationFailure):
            result.failures.append(
                f"Puzzle {spec.index + 1} - {spec.title}: no se pudo colocar "
                f"{len(words_for_grid)} palabra(s) en un grid {grid_size}x{grid_size}. "
                f"{grid_result.reason}"
            )
            if progress_callback is not None:
                progress_callback()
            continue

        result.generated_puzzles.append(
            GeneratedPuzzle(
                spec=spec,
                words_for_grid=words_for_grid,
                grid=grid_result.grid,
                placed_words=grid_result.placed_words,
            )
        )
        if progress_callback is not None:
            progress_callback()

    return result
