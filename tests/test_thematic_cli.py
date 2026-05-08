import argparse
import builtins
import sys

import pytest

from wordsearch.cli import thematic
from wordsearch.config.design import DEFAULT_THEME_NAME
from wordsearch.generation.difficulty import DifficultyLevel


def _mock_inputs(monkeypatch, values):
    answers = iter(values)
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(answers))


def test_ask_difficulty_default(monkeypatch):
    _mock_inputs(monkeypatch, [""])
    assert thematic._ask_difficulty() is DifficultyLevel.MEDIUM


def test_ask_difficulty_easy(monkeypatch):
    _mock_inputs(monkeypatch, ["1"])
    assert thematic._ask_difficulty() is DifficultyLevel.EASY


def test_ask_difficulty_medium(monkeypatch):
    _mock_inputs(monkeypatch, ["2"])
    assert thematic._ask_difficulty() is DifficultyLevel.MEDIUM


def test_ask_difficulty_hard(monkeypatch):
    _mock_inputs(monkeypatch, ["3"])
    assert thematic._ask_difficulty() is DifficultyLevel.HARD


def test_ask_difficulty_invalid_then_valid(monkeypatch, capsys):
    _mock_inputs(monkeypatch, ["x", "2"])
    result = thematic._ask_difficulty()
    assert result is DifficultyLevel.MEDIUM
    captured = capsys.readouterr()

    assert "Opción no válida" in captured.out


def make_args(**overrides):
    values = {
        "title": "Seeded Book",
        "input_path": "wordlists/book_block.txt",
        "difficulty": "medium",
        "grid_size": 14,
        "seed": 1234,
        "theme": DEFAULT_THEME_NAME,
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
    assert options.theme_name == DEFAULT_THEME_NAME
    assert options.validate_only is False
    assert options.clean_output is False


def test_resolve_options_accepts_theme():
    options = thematic._resolve_options(make_args(theme="premium-neutral"))

    assert options.theme_name == "premium-neutral"


def test_resolve_options_accepts_validate_only():
    options = thematic._resolve_options(make_args(title="Validation Book", seed=None, validate_only=True))

    assert options.validate_only is True


def test_resolve_options_accepts_clean_output():
    options = thematic._resolve_options(make_args(clean_output=True))

    assert options.clean_output is True


def test_resolve_options_rejects_validate_only_with_clean_output():
    with pytest.raises(ValueError, match="--clean-output"):
        thematic._resolve_options(make_args(validate_only=True, clean_output=True))


def test_parse_args_accepts_clean_output(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sopa-libros-thematic",
            "--title",
            "Clean Book",
            "--input",
            "wordlists/book_block.txt",
            "--difficulty",
            "medium",
            "--grid-size",
            "14",
            "--clean-output",
        ],
    )

    args = thematic._parse_args()

    assert args.clean_output is True


def test_parse_args_accepts_theme(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sopa-libros-thematic",
            "--title",
            "Theme Book",
            "--input",
            "wordlists/book_block.txt",
            "--difficulty",
            "medium",
            "--grid-size",
            "14",
            "--theme",
            "kids",
        ],
    )

    args = thematic._parse_args()

    assert args.theme == "kids"


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
