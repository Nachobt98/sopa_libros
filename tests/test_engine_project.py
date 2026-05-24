import json

import pytest

from wordsearch.cli import engine as engine_cli
from wordsearch.config.design import DEFAULT_THEME_NAME
from wordsearch.config.formats import DEFAULT_FORMAT_NAME
from wordsearch.engine import thematic
from wordsearch.engine.events import RunEvent
from wordsearch.engine.project import (
    PROJECT_SCHEMA_VERSION,
    ThematicProject,
    build_default_project_path,
    load_thematic_project,
    save_thematic_project,
)


def test_thematic_project_round_trips_to_json(tmp_path):
    project = ThematicProject(
        book_title="Ancient Egypt Word Search",
        input_path="wordlists/egypt.txt",
        difficulty="hard",
        grid_size=16,
        seed=1234,
        theme_name="premium-neutral",
        format_name="activity-8.5x11",
        theme_manifest_path="assets/generated/egypt/asset_manifest.json",
        output_dir="output_puzzles_kdp/egypt",
        limit=5,
        preview=True,
    )

    path = tmp_path / "egypt.sopa.json"
    written_path = save_thematic_project(project, path)
    loaded = load_thematic_project(path)

    assert written_path == str(path)
    assert loaded == project
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == PROJECT_SCHEMA_VERSION
    assert payload["project_type"] == "thematic"
    assert payload["book_title"] == "Ancient Egypt Word Search"


def test_thematic_project_accepts_engine_aliases_and_defaults():
    project = ThematicProject.from_dict(
        {
            "title": "UI Book",
            "puzzles_txt_path": "wordlists/book.txt",
        }
    )

    assert project.book_title == "UI Book"
    assert project.input_path == "wordlists/book.txt"
    assert project.difficulty == "medium"
    assert project.grid_size == 14
    assert project.theme_name == DEFAULT_THEME_NAME
    assert project.format_name == DEFAULT_FORMAT_NAME


def test_thematic_project_to_engine_request_omits_project_metadata():
    project = ThematicProject(
        book_title="UI Book",
        input_path="wordlists/book.txt",
        preview=True,
    )

    request = project.to_engine_request()

    assert request == {
        "book_title": "UI Book",
        "input_path": "wordlists/book.txt",
        "difficulty": "medium",
        "grid_size": 14,
        "seed": None,
        "theme_name": DEFAULT_THEME_NAME,
        "format_name": DEFAULT_FORMAT_NAME,
        "theme_manifest_path": None,
        "output_dir": None,
        "limit": None,
        "preview": True,
    }


def test_load_thematic_project_rejects_unknown_schema(tmp_path):
    path = tmp_path / "bad.sopa.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 999,
                "project_type": "thematic",
                "book_title": "Book",
                "input_path": "wordlists/book.txt",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported project schema_version"):
        load_thematic_project(path)


def test_load_thematic_project_rejects_unknown_type(tmp_path):
    path = tmp_path / "bad.sopa.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": PROJECT_SCHEMA_VERSION,
                "project_type": "simple",
                "book_title": "Book",
                "input_path": "wordlists/book.txt",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported project_type"):
        load_thematic_project(path)


def test_build_default_project_path_uses_project_extension():
    assert build_default_project_path("My Book") == build_default_project_path("My Book", root_dir="projects")
    assert str(build_default_project_path("My Book")).endswith("my_book.sopa.json")


def test_engine_cli_project_init_writes_project(monkeypatch, tmp_path, capsys):
    project_path = tmp_path / "book.sopa.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "sopa-libros-engine",
            "project",
            "init",
            "--title",
            "UI Book",
            "--input",
            "wordlists/book.txt",
            "--output",
            str(project_path),
            "--grid-size",
            "16",
            "--preview",
        ],
    )

    try:
        engine_cli.main()
    except SystemExit as exc:
        assert exc.code == 0

    payload = json.loads(capsys.readouterr().out)
    loaded = load_thematic_project(project_path)
    assert payload["ok"] is True
    assert payload["command"] == "project.init"
    assert payload["project_path"] == str(project_path)
    assert loaded.book_title == "UI Book"
    assert loaded.grid_size == 16
    assert loaded.preview is True


def test_engine_cli_project_request_prints_engine_payload(monkeypatch, tmp_path, capsys):
    project_path = tmp_path / "book.sopa.json"
    save_thematic_project(
        ThematicProject(
            book_title="UI Book",
            input_path="wordlists/book.txt",
            grid_size=16,
        ),
        project_path,
    )
    monkeypatch.setattr(
        "sys.argv",
        ["sopa-libros-engine", "project", "request", "--project", str(project_path)],
    )

    try:
        engine_cli.main()
    except SystemExit as exc:
        assert exc.code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "project.request"
    assert payload["request"]["book_title"] == "UI Book"
    assert payload["request"]["input_path"] == "wordlists/book.txt"
    assert payload["request"]["grid_size"] == 16
    assert "schema_version" not in payload["request"]


def test_engine_cli_project_validate_uses_project_request(monkeypatch, tmp_path, capsys):
    project_path = tmp_path / "book.sopa.json"
    save_thematic_project(
        ThematicProject(book_title="UI Book", input_path="wordlists/book.txt"),
        project_path,
    )
    calls = {}

    def fake_validate(payload):
        calls["payload"] = payload
        from wordsearch.engine.contracts import ThematicValidationResponse

        return ThematicValidationResponse(ok=True)

    monkeypatch.setattr(engine_cli, "validate_thematic_request", fake_validate)
    monkeypatch.setattr(
        "sys.argv",
        ["sopa-libros-engine", "project", "validate", "--project", str(project_path)],
    )

    try:
        engine_cli.main()
    except SystemExit as exc:
        assert exc.code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "thematic.validate"
    assert calls["payload"]["book_title"] == "UI Book"


def test_engine_cli_project_generate_streams_json_lines(monkeypatch, tmp_path, capsys):
    project_path = tmp_path / "book.sopa.json"
    save_thematic_project(
        ThematicProject(book_title="UI Book", input_path="wordlists/book.txt"),
        project_path,
    )

    def fake_generate_thematic_book(options, *, event_callback=None):
        event_callback(RunEvent(type="run_completed", stage="complete", message="Done."))
        return "out/book.pdf"

    monkeypatch.setattr(thematic, "generate_thematic_book", fake_generate_thematic_book)
    monkeypatch.setattr(
        "sys.argv",
        [
            "sopa-libros-engine",
            "project",
            "generate",
            "--project",
            str(project_path),
            "--json-lines",
        ],
    )

    try:
        engine_cli.main()
    except SystemExit as exc:
        assert exc.code == 0

    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [line["type"] for line in lines] == ["event", "result"]
    assert lines[0]["event"]["stage"] == "complete"
    assert lines[1]["result"]["pdf_path"] == "out/book.pdf"
