"""
Word search grid generation.

The structured API is `generate_word_search_grid`. The legacy
`place_words_on_grid` wrapper still returns `(grid, placed_words)` by default
so older callers can migrate incrementally.
"""

from __future__ import annotations

import random
from typing import Iterable

from wordsearch.difficulty_levels import DifficultyLevel, difficulty_settings
from wordsearch.domain.grid import (
    GridGenerationFailure,
    GridGenerationOutcome,
    GridGenerationResult,
    PlacedWord,
)

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DEFAULT_MAX_ATTEMPTS = 50


def _resolve_rng(
    *,
    seed: int | None,
    rng: random.Random | None,
) -> random.Random:
    if seed is not None and rng is not None:
        raise ValueError("Use seed or rng, not both.")
    if rng is not None:
        return rng
    return random.Random(seed)


def _normalize_generation_words(words: Iterable[str]) -> list[str]:
    return [str(word).upper() for word in words if str(word).strip()]


def _candidate_positions(
    size: int,
    directions: list[tuple[int, int]],
) -> list[tuple[int, int, int, int]]:
    return [
        (row, col, d_row, d_col)
        for row in range(size)
        for col in range(size)
        for d_row, d_col in directions
    ]


def _can_place_word(
    grid: list[list[str]],
    word: str,
    row: int,
    col: int,
    d_row: int,
    d_col: int,
) -> bool:
    size = len(grid)
    rr, cc = row, col

    for char in word:
        if not (0 <= rr < size and 0 <= cc < size):
            return False
        if grid[rr][cc] not in ("", char):
            return False
        rr += d_row
        cc += d_col

    return True


def _place_word(
    grid: list[list[str]],
    word: str,
    row: int,
    col: int,
    d_row: int,
    d_col: int,
) -> None:
    rr, cc = row, col

    for char in word:
        grid[rr][cc] = char
        rr += d_row
        cc += d_col


def _try_generate_once(
    words: list[str],
    difficulty: DifficultyLevel,
    size: int,
    rng: random.Random,
) -> GridGenerationResult | None:
    settings = difficulty_settings[difficulty]
    directions = settings["directions"]
    grid = [["" for _ in range(size)] for _ in range(size)]
    placed_words: list[PlacedWord] = []

    for word in sorted(words, key=len, reverse=True):
        candidates = _candidate_positions(size, directions)
        rng.shuffle(candidates)

        for row, col, d_row, d_col in candidates:
            if not _can_place_word(grid, word, row, col, d_row, d_col):
                continue

            _place_word(grid, word, row, col, d_row, d_col)
            placed_words.append(
                PlacedWord(
                    word=word,
                    row=row,
                    col=col,
                    d_row=d_row,
                    d_col=d_col,
                )
            )
            break
        else:
            return None

    for row in range(size):
        for col in range(size):
            if grid[row][col] == "":
                grid[row][col] = rng.choice(ALPHABET)

    return GridGenerationResult(
        grid=grid,
        placed_words=placed_words,
        attempts_used=1,
    )


def generate_word_search_grid(
    words: Iterable[str],
    difficulty: DifficultyLevel,
    grid_size: int | None = None,
    *,
    seed: int | None = None,
    rng: random.Random | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> GridGenerationOutcome:
    """
    Generate a word search grid with real whole-grid retries.

    Returns a structured result on success or a structured failure otherwise.
    """
    if max_attempts <= 0:
        raise ValueError("max_attempts must be a positive integer.")

    settings = difficulty_settings[difficulty]
    size = grid_size if grid_size is not None else settings["grid_default"]
    if size <= 0:
        raise ValueError("grid_size must be a positive integer.")

    generation_words = _normalize_generation_words(words)
    oversized_words = [word for word in generation_words if len(word) > size]
    if oversized_words:
        return GridGenerationFailure(
            reason=f"One or more words exceed the {size}x{size} grid size.",
            attempts_used=0,
            failed_words=oversized_words,
        )

    local_rng = _resolve_rng(seed=seed, rng=rng)

    for attempt in range(1, max_attempts + 1):
        result = _try_generate_once(generation_words, difficulty, size, local_rng)
        if result is not None:
            return GridGenerationResult(
                grid=result.grid,
                placed_words=result.placed_words,
                attempts_used=attempt,
            )

    return GridGenerationFailure(
        reason=f"Could not place all words after {max_attempts} attempt(s).",
        attempts_used=max_attempts,
        failed_words=generation_words,
    )


def place_words_on_grid(
    words: Iterable[str],
    difficulty: DifficultyLevel,
    grid_size: int | None = None,
    *,
    seed: int | None = None,
    rng: random.Random | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    return_result: bool = False,
):
    """
    Backward-compatible wrapper around `generate_word_search_grid`.

    By default it returns the historical `(grid, placed_words)` tuple or None
    on failure. Pass `return_result=True` to receive the structured generation
    outcome.
    """
    result = generate_word_search_grid(
        words,
        difficulty=difficulty,
        grid_size=grid_size,
        seed=seed,
        rng=rng,
        max_attempts=max_attempts,
    )

    if return_result:
        return result

    if isinstance(result, GridGenerationFailure):
        return None

    return result.as_legacy_tuple()
