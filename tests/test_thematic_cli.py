import argparse

import pytest

from wordsearch.cli import thematic
from wordsearch.generation.difficulty import DifficultyLevel


def test_resolve_options_accepts_cli_seed():
    args = argparse.Namespace(
        title="Seeded Book",
        input_path="wordlists/book_block.txt",
        difficulty="medium",
        grid_size=14,
        seed=1234,
        validate_only=False,
    )

    options = thematic._resolve_options(args)

    assert options.book_title == "Seeded Book"
    assert options.puzzles_txt_path == "wordlists/book_block.txt"
    assert options.difficulty == DifficultyLevel.MEDIUM
    assert options.grid_size == 14
    assert options.seed == 1234
    assert options.validate_only is False


def test_resolve_options_accepts_validate_only():
    args = argparse.Namespace(
        title="Validation Book",
        input_path="wordlists/book_block.txt",
        difficulty="medium",
        grid_size=14,
        seed=None,
        validate_only=True,
    )

    options = thematic._resolve_options(args)

    assert options.validate_only is True


def test_resolve_options_defaults_seed_to_none():
    args = argparse.Namespace(
        title="Unseeded Book",
        input_path="wordlists/book_block.txt",
        difficulty="easy",
        grid_size=10,
        seed=None,
        validate_only=False,
    )

    options = thematic._resolve_options(args)

    assert options.seed is None


def test_resolve_options_rejects_non_positive_grid_size():
    args = argparse.Namespace(
        title="Bad Grid",
        input_path="wordlists/book_block.txt",
        difficulty="medium",
        grid_size=0,
        seed=1234,
        validate_only=False,
    )

    with pytest.raises(ValueError, match="--grid-size"):
        thematic._resolve_options(args)
