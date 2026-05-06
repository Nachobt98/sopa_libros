"""Grid generation domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple


@dataclass(frozen=True)
class PlacedWord:
    """A word placed in the puzzle grid."""

    word: str
    row: int
    col: int
    d_row: int
    d_col: int

    @property
    def position(self) -> Tuple[int, int, int, int]:
        return (self.row, self.col, self.d_row, self.d_col)


@dataclass(frozen=True)
class GridGenerationResult:
    """Successful grid generation output."""

    grid: Sequence[Sequence[str]]
    placed_words: Sequence[PlacedWord]
    attempts_used: int


@dataclass(frozen=True)
class GridGenerationFailure:
    """Unsuccessful grid generation output with an actionable reason."""

    reason: str
    attempts_used: int
    failed_words: Sequence[str]


GridGenerationOutcome = GridGenerationResult | GridGenerationFailure
