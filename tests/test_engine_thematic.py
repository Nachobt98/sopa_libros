import json

from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.engine import thematic
from wordsearch.engine.thematic import validate_thematic_request
from wordsearch.validation.assets import AssetValidationReport


def make_spec(index: int = 0) -> PuzzleSpec:
    return PuzzleSpec(
        index=index,
        title=f"Puzzle {index + 1}",
        fact="Fact",
        words=["WORD", "SEARCH"],
        block_name="Block A",
    )


def test_validate_thematic_request_returns_structured_success(monkeypatch, tmp_path):
    specs = [make_spec(0), make_spec(1)]

    monkeypatch.setattr(thematic, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(thematic, "parse_puzzle_file", lambda path: specs)
    monkeypatch.setattr(thematic, "validate_generation_assets", lambda **kwargs: AssetValidationReport())

    response = validate_thematic_request(
        {
            "book_title": "Engine Book",
            "input_path": "wordlists/book.txt",
            "difficulty": "medium",
            "grid_size": 14,
        }
    )

    payload = response.to_dict()

    assert response.ok is True
    assert payload["status"] == "ok"
    assert payload["error_count"] == 0
    assert payload["warning_count"] == 0
    assert payload["parsed_puzzle_count"] == 2
    assert payload["selected_puzzle_count"] == 2
    assert payload["output_dir"] == str(tmp_path / "engine_book")
    assert payload["puzzles"][0] == {
        "index": 0,
        "title": "Puzzle 1",
        "word_count": 2,
        "block_name": "Block A",
        "has_fact": True,
        "block_background": None,
    }


def test_validate_thematic_request_applies_limit(monkeypatch, tmp_path):
    specs = [make_spec(0), make_spec(1), make_spec(2)]

    monkeypatch.setattr(thematic, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(thematic, "parse_puzzle_file", lambda path: specs)
    monkeypatch.setattr(thematic, "validate_generation_assets", lambda **kwargs: AssetValidationReport())

    response = validate_thematic_request(
        {
            "book_title": "Engine Book",
            "input_path": "wordlists/book.txt",
            "difficulty": "medium",
            "grid_size": 14,
            "limit": 1,
        }
    )

    assert response.ok is True
    assert response.parsed_puzzle_count == 3
    assert response.selected_puzzle_count == 1
    assert [puzzle.index for puzzle in response.puzzles] == [0]


def test_validate_thematic_request_reports_invalid_request():
    response = validate_thematic_request(
        {
            "book_title": "Engine Book",
            "input_path": "wordlists/book.txt",
            "difficulty": "medium",
            "grid_size": 0,
        }
    )

    assert response.ok is False
    assert response.issues[0].code == "INVALID_REQUEST"
    assert "grid_size" in response.issues[0].message


def test_validate_thematic_request_reports_missing_input(monkeypatch):
    def missing_file(path):
        raise FileNotFoundError

    monkeypatch.setattr(thematic, "parse_puzzle_file", missing_file)

    response = validate_thematic_request(
        {
            "book_title": "Engine Book",
            "input_path": "missing.txt",
            "difficulty": "medium",
            "grid_size": 14,
        }
    )

    assert response.ok is False
    assert response.issues[0].code == "INPUT_NOT_FOUND"
    assert response.issues[0].path == "missing.txt"


def test_validate_thematic_request_reports_content_errors(monkeypatch, tmp_path):
    spec = make_spec()
    spec.words = ["SUPERCALIFRAGILISTIC"]

    monkeypatch.setattr(thematic, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(thematic, "parse_puzzle_file", lambda path: [spec])
    monkeypatch.setattr(thematic, "validate_generation_assets", lambda **kwargs: AssetValidationReport())

    response = validate_thematic_request(
        {
            "book_title": "Engine Book",
            "input_path": "wordlists/book.txt",
            "difficulty": "medium",
            "grid_size": 8,
        }
    )

    assert response.ok is False
    assert response.issues[0].source == "content"
    assert response.issues[0].puzzle_index == 0
    assert "no cabe" in response.issues[0].message


def test_engine_cli_validate_writes_json(monkeypatch, tmp_path, capsys):
    from wordsearch.cli import engine as engine_cli

    config_path = tmp_path / "request.json"
    config_path.write_text(
        json.dumps(
            {
                "book_title": "Engine Book",
                "input_path": "wordlists/book.txt",
                "difficulty": "medium",
                "grid_size": 14,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(thematic, "BASE_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(thematic, "parse_puzzle_file", lambda path: [make_spec()])
    monkeypatch.setattr(thematic, "validate_generation_assets", lambda **kwargs: AssetValidationReport())
    monkeypatch.setattr("sys.argv", ["sopa-libros-engine", "validate", "--config", str(config_path)])

    try:
        engine_cli.main()
    except SystemExit as exc:
        assert exc.code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "thematic.validate"
    assert payload["selected_puzzle_count"] == 1
