"""App project file model for desktop/UI integrations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from wordsearch.config.design import DEFAULT_THEME_NAME
from wordsearch.config.formats import DEFAULT_FORMAT_NAME

PROJECT_SCHEMA_VERSION = 1
DEFAULT_PROJECT_EXTENSION = ".sopa.json"


@dataclass
class ThematicProject:
    """Serializable app project that can be converted into an engine request."""

    book_title: str
    input_path: str
    difficulty: str = "medium"
    grid_size: int = 14
    seed: int | None = None
    theme_name: str = DEFAULT_THEME_NAME
    format_name: str = DEFAULT_FORMAT_NAME
    theme_manifest_path: str | None = None
    output_dir: str | None = None
    limit: int | None = None
    preview: bool = False
    schema_version: int = PROJECT_SCHEMA_VERSION

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ThematicProject":
        schema_version = int(payload.get("schema_version", PROJECT_SCHEMA_VERSION))
        if schema_version != PROJECT_SCHEMA_VERSION:
            raise ValueError(f"Unsupported project schema_version: {schema_version}")
        project_type = str(payload.get("project_type", "thematic")).strip().lower()
        if project_type != "thematic":
            raise ValueError(f"Unsupported project_type: {project_type}")

        return cls(
            schema_version=schema_version,
            book_title=str(payload.get("book_title") or payload.get("title") or "").strip(),
            input_path=str(payload.get("input_path") or payload.get("puzzles_txt_path") or "").strip(),
            difficulty=str(payload.get("difficulty") or "medium").strip().lower(),
            grid_size=int(payload.get("grid_size", 14)),
            seed=_optional_int(payload.get("seed")),
            theme_name=str(payload.get("theme_name") or payload.get("theme") or DEFAULT_THEME_NAME).strip(),
            format_name=str(payload.get("format_name") or payload.get("format") or DEFAULT_FORMAT_NAME).strip(),
            theme_manifest_path=_optional_str(payload.get("theme_manifest_path")),
            output_dir=_optional_str(payload.get("output_dir")),
            limit=_optional_int(payload.get("limit")),
            preview=bool(payload.get("preview", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["project_type"] = "thematic"
        return payload

    def to_engine_request(self) -> dict[str, Any]:
        payload = self.to_dict()
        payload.pop("schema_version", None)
        payload.pop("project_type", None)
        return payload


def load_thematic_project(path: str | Path) -> ThematicProject:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Project file must contain a JSON object.")
    return ThematicProject.from_dict(payload)


def save_thematic_project(project: ThematicProject, path: str | Path) -> str:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(project.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return str(output_path)


def build_default_project_path(book_title: str, *, root_dir: str | Path = "projects") -> Path:
    from wordsearch.utils.slug import slugify

    return Path(root_dir) / f"{slugify(book_title or 'wordsearch_project')}{DEFAULT_PROJECT_EXTENSION}"


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
