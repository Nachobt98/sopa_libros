import json

import pytest

from wordsearch.config.design import DEFAULT_THEME_NAME
from wordsearch.config.formats import DEFAULT_FORMAT_NAME
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
