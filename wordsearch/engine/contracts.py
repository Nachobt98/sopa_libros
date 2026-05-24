"""JSON contracts for the non-interactive generation engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from wordsearch.config.design import DEFAULT_THEME_NAME
from wordsearch.config.formats import DEFAULT_FORMAT_NAME
from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.engine.events import RunEvent
from wordsearch.generation.difficulty import DifficultyLevel


@dataclass
class EngineIssue:
    """Serializable validation or runtime issue for app-facing clients."""

    severity: str
    message: str
    code: str
    source: str
    path: str | None = None
    puzzle_index: int | None = None
    puzzle_title: str | None = None
    context: str | None = None


@dataclass
class PuzzleSummary:
    """Small parsed-puzzle summary for preview lists in a GUI."""

    index: int
    title: str
    word_count: int
    block_name: str | None = None
    has_fact: bool = False
    block_background: str | None = None

    @classmethod
    def from_spec(cls, spec: PuzzleSpec) -> "PuzzleSummary":
        return cls(
            index=spec.index,
            title=spec.title,
            word_count=len(spec.words),
            block_name=spec.block_name,
            has_fact=bool(spec.fact and spec.fact.strip()),
            block_background=spec.block_background,
        )


@dataclass
class ThematicValidationRequest:
    """Input payload for validating a thematic book without rendering it."""

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

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ThematicValidationRequest":
        return cls(
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

    def to_generation_options(self, *, validate_only: bool = True) -> ThematicGenerationOptions:
        return ThematicGenerationOptions(
            book_title=self.book_title or "Wordsearch Thematic Book",
            puzzles_txt_path=self.input_path,
            difficulty=parse_difficulty(self.difficulty),
            grid_size=self.grid_size,
            seed=self.seed,
            validate_only=validate_only,
            theme_name=self.theme_name or DEFAULT_THEME_NAME,
            format_name=self.format_name or DEFAULT_FORMAT_NAME,
            theme_manifest_path=self.theme_manifest_path,
            output_dir=self.output_dir,
            limit=self.limit,
            preview=self.preview,
        )


@dataclass
class ThematicValidationResponse:
    """Output payload returned by the thematic validation engine command."""

    ok: bool
    command: str = "thematic.validate"
    status: str = "ok"
    issues: list[EngineIssue] = field(default_factory=list)
    parsed_puzzle_count: int = 0
    selected_puzzle_count: int = 0
    output_dir: str | None = None
    puzzles: list[PuzzleSummary] = field(default_factory=list)

    @property
    def errors(self) -> list[EngineIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[EngineIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["error_count"] = len(self.errors)
        payload["warning_count"] = len(self.warnings)
        return payload


@dataclass
class ThematicRunResponse:
    """Output payload returned by preview/full thematic engine generation."""

    ok: bool
    command: str = "thematic.generate"
    status: str = "ok"
    pdf_path: str | None = None
    issues: list[EngineIssue] = field(default_factory=list)
    events: list[RunEvent] = field(default_factory=list)

    @property
    def errors(self) -> list[EngineIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[EngineIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["error_count"] = len(self.errors)
        payload["warning_count"] = len(self.warnings)
        payload["event_count"] = len(self.events)
        return payload


def parse_difficulty(value: str) -> DifficultyLevel:
    normalized = value.strip().lower()
    for level in DifficultyLevel:
        if normalized in {level.value.lower(), level.name.lower()}:
            return level
    supported = ", ".join(level.value for level in DifficultyLevel)
    raise ValueError(f"Unsupported difficulty '{value}'. Supported values: {supported}.")


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
