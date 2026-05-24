import json

from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.engine import thematic
from wordsearch.engine.events import RunEvent
from wordsearch.engine.thematic import generate_thematic_request, validate_thematic_request
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


def test_generate_thematic_request_returns_pdf_path_and_events(monkeypatch):
    def fake_generate_thematic_book(options, *, event_callback=None):
        assert options.validate_only is False
        assert options.book_title == "Engine Book"
        assert options.puzzles_txt_path == "wordlists/book.txt"
        event_callback(
            RunEvent(
                type="run_completed",
                stage="complete",
                message="Done.",
                metadata={"pdf_path": "out/book.pdf"},
            )
        )
        return "out/book.pdf"

    monkeypatch.setattr(thematic, "generate_thematic_book", fake_generate_thematic_book)

    response = generate_thematic_request(
        {
            "book_title": "Engine Book",
            "input_path": "wordlists/book.txt",
            "difficulty": "medium",
            "grid_size": 14,
        }
    )

    payload = response.to_dict()

    assert response.ok is True
    assert payload["command"] == "thematic.generate"
    assert payload["pdf_path"] == "out/book.pdf"
    assert payload["event_count"] == 1
    assert payload["events"][0]["type"] == "run_completed"


def test_generate_thematic_request_supports_validate_only(monkeypatch):
    def fake_generate_thematic_book(options, *, event_callback=None):
        assert options.validate_only is True
        event_callback(RunEvent(type="run_completed", stage="validation", message="Validated."))
        return None

    monkeypatch.setattr(thematic, "generate_thematic_book", fake_generate_thematic_book)

    response = generate_thematic_request(
        {
            "book_title": "Engine Book",
            "input_path": "wordlists/book.txt",
            "difficulty": "medium",
            "grid_size": 14,
            "validate_only": True,
        }
    )

    assert response.ok is True
    assert response.pdf_path is None
    assert response.events[0].stage == "validation"


def test_generate_thematic_request_returns_issue_when_pipeline_fails(monkeypatch):
    def fake_generate_thematic_book(options, *, event_callback=None):
        event_callback(RunEvent(type="run_failed", stage="grid_generation", message="Grid failed."))
        return None

    monkeypatch.setattr(thematic, "generate_thematic_book", fake_generate_thematic_book)

    response = generate_thematic_request(
        {
            "book_title": "Engine Book",
            "input_path": "wordlists/book.txt",
            "difficulty": "medium",
            "grid_size": 14,
        }
    )

    assert response.ok is False
    assert response.issues[0].code == "GRID_GENERATION_FAILED"
    assert response.issues[0].message == "Grid failed."


def test_engine_cli_generate_writes_json(monkeypatch, tmp_path, capsys):
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

    def fake_generate_thematic_book(options, *, event_callback=None):
        event_callback(RunEvent(type="run_completed", stage="complete", message="Done."))
        return "out/book.pdf"

    monkeypatch.setattr(thematic, "generate_thematic_book", fake_generate_thematic_book)
    monkeypatch.setattr("sys.argv", ["sopa-libros-engine", "generate", "--config", str(config_path)])

    try:
        engine_cli.main()
    except SystemExit as exc:
        assert exc.code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "thematic.generate"
    assert payload["pdf_path"] == "out/book.pdf"


def test_engine_cli_generate_redirects_human_output_to_stderr(monkeypatch, tmp_path, capsys):
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

    def fake_generate_thematic_book(options, *, event_callback=None):
        print("human pipeline log")
        event_callback(RunEvent(type="run_completed", stage="complete", message="Done."))
        return "out/book.pdf"

    monkeypatch.setattr(thematic, "generate_thematic_book", fake_generate_thematic_book)
    monkeypatch.setattr("sys.argv", ["sopa-libros-engine", "generate", "--config", str(config_path)])

    try:
        engine_cli.main()
    except SystemExit as exc:
        assert exc.code == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["ok"] is True
    assert "human pipeline log" not in captured.out
    assert "human pipeline log" in captured.err


def test_engine_cli_generate_json_lines_streams_events_and_result(monkeypatch, tmp_path, capsys):
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

    def fake_generate_thematic_book(options, *, event_callback=None):
        print("human pipeline log")
        event_callback(RunEvent(type="stage_started", stage="parsing", message="Parsing."))
        event_callback(RunEvent(type="run_completed", stage="complete", message="Done."))
        return "out/book.pdf"

    monkeypatch.setattr(thematic, "generate_thematic_book", fake_generate_thematic_book)
    monkeypatch.setattr(
        "sys.argv",
        ["sopa-libros-engine", "generate", "--config", str(config_path), "--json-lines"],
    )

    try:
        engine_cli.main()
    except SystemExit as exc:
        assert exc.code == 0

    captured = capsys.readouterr()
    lines = [json.loads(line) for line in captured.out.splitlines()]
    assert [line["type"] for line in lines] == ["event", "event", "result"]
    assert lines[0]["event"]["stage"] == "parsing"
    assert lines[1]["event"]["type"] == "run_completed"
    assert lines[2]["result"]["ok"] is True
    assert lines[2]["result"]["pdf_path"] == "out/book.pdf"
    assert lines[2]["result"]["events"] == []
    assert "human pipeline log" in captured.err
