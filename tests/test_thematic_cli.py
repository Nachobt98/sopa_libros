import argparse

import pytest

from wordsearch.cli import thematic
from wordsearch.generation.difficulty import DifficultyLevel


def make_args(**overrides):
    values = {
        "title": "Seeded Book",
        "input_path": "wordlists/book_block.txt",
        "difficulty": "medium",
        "grid_size": 14,
        "seed": 1234,
        "validate_only": False,
        "clean_output": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_resolve_options_accepts_cli_seed():
    options = thematic._resolve_options(make_args())

    assert options.book_title == "Seeded Book"
    assert options.puzzles_txt_path == "wordlists/book_block.txt"
    assert options.difficulty == DifficultyLevel.MEDIUM
    assert options.grid_size == 14
    assert options.seed == 1234
    assert options.validate_only is False
    assert options.clean_output is False


def test_resolve_options_accepts_validate_only():
    options = thematic._resolve_options(make_args(title="Validation Book", seed=None, validate_only=True))

    assert options.validate_only is True


def test_resolve_options_accepts_clean_output():
    options = thematic._resolve_options(make_args(clean_output=True))

    assert options.clean_output is True


def test_resolve_options_defaults_seed_to_none():
    options = thematic._resolve_options(
        make_args(
            title="Unseeded Book",
            difficulty="easy",
            grid_size=10,
            seed=None,
        )
    )

    assert options.seed is None


def test_resolve_options_rejects_non_positive_grid_size():
    with pytest.raises(ValueError, match="--grid-size"):
        thematic._resolve_options(make_args(title="Bad Grid", grid_size=0))
