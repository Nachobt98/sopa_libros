import json

import pytest

from wordsearch.engine.contracts import ThematicValidationRequest, parse_difficulty
from wordsearch.generation.difficulty import DifficultyLevel


def test_parse_difficulty_accepts_names_and_values():
    assert parse_difficulty("medium") == DifficultyLevel.MEDIUM
    assert parse_difficulty("MEDIUM") == DifficultyLevel.MEDIUM
    assert parse_difficulty(DifficultyLevel.HARD.value) == DifficultyLevel.HARD


def test_parse_difficulty_rejects_unknown_values():
    with pytest.raises(ValueError, match="Unsupported difficulty"):
        parse_difficulty("extreme")


def test_thematic_validation_request_accepts_ui_aliases():
    payload = {
        "title": "UI Book",
        "puzzles_txt_path": "wordlists/book_block.txt",
        "difficulty": "hard",
        "grid_size": "16",
        "theme": "bold-modern",
        "format": "activity-8.5x11",
        "seed": "1234",
        "limit": "5",
        "preview": True,
    }

    request = ThematicValidationRequest.from_dict(payload)
    options = request.to_generation_options()

    assert options.book_title == "UI Book"
    assert options.puzzles_txt_path == "wordlists/book_block.txt"
    assert options.difficulty == DifficultyLevel.HARD
    assert options.grid_size == 16
    assert options.theme_name == "bold-modern"
    assert options.format_name == "activity-8.5x11"
    assert options.seed == 1234
    assert options.limit == 5
    assert options.preview is True
    assert options.validate_only is True


def test_validation_response_dict_includes_issue_counts():
    from wordsearch.engine.contracts import EngineIssue, ThematicValidationResponse

    response = ThematicValidationResponse(
        ok=False,
        status="error",
        issues=[
            EngineIssue("error", "bad", "BAD", "engine"),
            EngineIssue("warning", "careful", "WARN", "engine"),
        ],
    )

    payload = response.to_dict()

    assert json.loads(json.dumps(payload))["ok"] is False
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 1

