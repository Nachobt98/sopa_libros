import random

import pytest

from wordsearch.difficulty_levels import DifficultyLevel
from wordsearch.domain.grid import GridGenerationFailure, GridGenerationResult, PlacedWord
from wordsearch.generation import grid as gg
from wordsearch.generation.grid import generate_word_search_grid, place_words_on_grid


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


def test_place_words_on_grid_keeps_legacy_tuple_contract():
    legacy_result = place_words_on_grid(
        ["CAT"],
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        seed=123,
    )

    assert legacy_result is not None
    grid, placed_words = legacy_result
    assert len(grid) == 8
    assert placed_words
    assert isinstance(placed_words[0], tuple)
    assert placed_words[0][0] == "CAT"


def test_place_words_on_grid_can_return_structured_result():
    result = place_words_on_grid(
        ["CAT"],
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        seed=123,
        return_result=True,
    )

    assert isinstance(result, GridGenerationResult)


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
