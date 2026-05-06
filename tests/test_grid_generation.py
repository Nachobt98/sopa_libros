import random

import pytest

from wordsearch.domain.grid import GridGenerationFailure, GridGenerationResult, PlacedWord
from wordsearch.generation import grid as gg
from wordsearch.generation.difficulty import DifficultyLevel
from wordsearch.generation.grid import generate_word_search_grid


def test_generate_word_search_grid_returns_structured_result():
    result = generate_word_search_grid(
        ["CAT", "DOG"],
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        seed=123,
    )

    assert isinstance(result, GridGenerationResult)
    assert len(result.grid) == 8
    assert all(len(row) == 8 for row in result.grid)
    assert all(isinstance(placed, PlacedWord) for placed in result.placed_words)
    assert {placed.word for placed in result.placed_words} == {"CAT", "DOG"}
    assert result.attempts_used >= 1


def test_generate_word_search_grid_is_reproducible_with_seed():
    first = generate_word_search_grid(
        ["ALPHA", "BETA", "GAMMA"],
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=12,
        seed=42,
    )
    second = generate_word_search_grid(
        ["ALPHA", "BETA", "GAMMA"],
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=12,
        seed=42,
    )

    assert isinstance(first, GridGenerationResult)
    assert isinstance(second, GridGenerationResult)
    assert first.grid == second.grid
    assert first.placed_words == second.placed_words


def test_placed_words_expose_position_tuple():
    result = generate_word_search_grid(
        ["CAT"],
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        seed=123,
    )

    assert isinstance(result, GridGenerationResult)
    placed_word = result.placed_words[0]
    assert placed_word.word == "CAT"
    assert placed_word.position == (
        placed_word.row,
        placed_word.col,
        placed_word.d_row,
        placed_word.d_col,
    )


def test_generate_word_search_grid_returns_failure_for_word_that_cannot_fit():
    result = generate_word_search_grid(
        ["TOOLONG"],
        difficulty=DifficultyLevel.EASY,
        grid_size=3,
        seed=123,
    )

    assert isinstance(result, GridGenerationFailure)
    assert result.attempts_used == 0
    assert result.failed_words == ["TOOLONG"]


def test_generate_word_search_grid_retries_whole_grid(monkeypatch):
    original_try_generate_once = gg._try_generate_once
    calls = {"count": 0}

    def fail_twice_then_succeed(words, difficulty, size, rng):
        calls["count"] += 1
        if calls["count"] < 3:
            return None
        return original_try_generate_once(words, difficulty, size, rng)

    monkeypatch.setattr(gg, "_try_generate_once", fail_twice_then_succeed)

    result = generate_word_search_grid(
        ["CAT"],
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        seed=123,
        max_attempts=3,
    )

    assert isinstance(result, GridGenerationResult)
    assert result.attempts_used == 3
    assert calls["count"] == 3


def test_generate_word_search_grid_returns_failure_after_retry_limit(monkeypatch):
    calls = {"count": 0}

    def always_fail(words, difficulty, size, rng):
        calls["count"] += 1
        return None

    monkeypatch.setattr(gg, "_try_generate_once", always_fail)

    result = generate_word_search_grid(
        ["CAT"],
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        seed=123,
        max_attempts=3,
    )

    assert isinstance(result, GridGenerationFailure)
    assert result.attempts_used == 3
    assert result.failed_words == ["CAT"]
    assert calls["count"] == 3


def test_generate_word_search_grid_rejects_seed_and_rng_together():
    with pytest.raises(ValueError, match="Use seed or rng"):
        generate_word_search_grid(
            ["CAT"],
            difficulty=DifficultyLevel.EASY,
            grid_size=8,
            seed=123,
            rng=random.Random(123),
        )


def test_easy_generation_uses_only_easy_directions():
    result = generate_word_search_grid(
        ["CAT", "DOG", "SUN"],
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        seed=123,
    )

    assert isinstance(result, GridGenerationResult)
    assert {
        (placed.d_row, placed.d_col)
        for placed in result.placed_words
    }.issubset({(0, 1), (1, 0)})
