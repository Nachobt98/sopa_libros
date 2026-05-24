"""Non-interactive thematic engine operations for app integrations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wordsearch.asset_generation.manifest import AssetManifest
from wordsearch.config.design import get_theme
from wordsearch.config.formats import get_format_preset
from wordsearch.config.paths import BASE_OUTPUT_DIR, build_book_output_dir
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.engine.contracts import (
    EngineIssue,
    PuzzleSummary,
    ThematicValidationRequest,
    ThematicValidationResponse,
)
from wordsearch.parsing.thematic import PuzzleParseError, parse_puzzle_file
from wordsearch.validation.asset_manifest import validate_asset_manifest_assets
from wordsearch.validation.assets import AssetValidationIssue, validate_generation_assets
from wordsearch.validation.thematic import ValidationIssue, validate_thematic_specs
from wordsearch.utils.slug import slugify


def validate_thematic_request(payload: dict[str, Any]) -> ThematicValidationResponse:
    """Validate a thematic book request and return a GUI-friendly JSON response."""
    try:
        request = ThematicValidationRequest.from_dict(payload)
        options = request.to_generation_options()
        get_theme(options.theme_name)
        get_format_preset(options.format_name)
        _validate_request_shape(request)
    except (TypeError, ValueError) as exc:
        return _error_response(str(exc), code="INVALID_REQUEST")

    try:
        parsed_specs = parse_puzzle_file(options.puzzles_txt_path)
    except FileNotFoundError:
        return _error_response(
            f"Input file not found: {options.puzzles_txt_path}",
            code="INPUT_NOT_FOUND",
            path=options.puzzles_txt_path,
        )
    except PuzzleParseError as exc:
        return _error_response(str(exc), code="PARSE_ERROR", path=options.puzzles_txt_path)

    if not parsed_specs:
        return _error_response(
            "No [Puzzle] blocks were found in the input file.",
            code="NO_PUZZLES",
            path=options.puzzles_txt_path,
        )

    selected_specs = _apply_limit(parsed_specs, options.limit)
    if not selected_specs:
        return _error_response("No puzzles remain after applying the generation limit.", code="EMPTY_SELECTION")

    output_dir = _resolve_output_dir(options.output_dir, options.book_title)
    issues: list[EngineIssue] = []

    asset_report = validate_generation_assets(
        output_dir=output_dir,
        optional_backgrounds=(spec.block_background for spec in selected_specs),
    )
    issues.extend(_asset_issue_to_engine(issue) for issue in asset_report.issues)

    if options.theme_manifest_path:
        manifest = _load_asset_manifest(options.theme_manifest_path)
        if isinstance(manifest, EngineIssue):
            issues.append(manifest)
        else:
            manifest_report = validate_asset_manifest_assets(manifest)
            issues.extend(_asset_issue_to_engine(issue) for issue in manifest_report.issues)

    content_report = validate_thematic_specs(
        selected_specs,
        options.grid_size,
        check_background_files=False,
    )
    issues.extend(_content_issue_to_engine(issue) for issue in content_report.issues)

    ok = not any(issue.severity == "error" for issue in issues)
    return ThematicValidationResponse(
        ok=ok,
        status="ok" if ok else "error",
        issues=issues,
        parsed_puzzle_count=len(parsed_specs),
        selected_puzzle_count=len(selected_specs),
        output_dir=output_dir,
        puzzles=[PuzzleSummary.from_spec(spec) for spec in selected_specs],
    )


def _validate_request_shape(request: ThematicValidationRequest) -> None:
    if not request.input_path:
        raise ValueError("input_path is required.")
    if request.grid_size <= 0:
        raise ValueError("grid_size must be a positive integer.")
    if request.limit is not None and request.limit <= 0:
        raise ValueError("limit must be a positive integer.")


def _apply_limit(specs: list[PuzzleSpec], limit: int | None) -> list[PuzzleSpec]:
    return specs if limit is None else specs[:limit]


def _resolve_output_dir(output_dir: str | None, book_title: str) -> str:
    if output_dir:
        return str(Path(output_dir))
    return build_book_output_dir(slugify(book_title or "Wordsearch Thematic Book"), BASE_OUTPUT_DIR)


def _load_asset_manifest(path: str) -> AssetManifest | EngineIssue:
    try:
        return AssetManifest.load(path)
    except FileNotFoundError:
        return EngineIssue(
            severity="error",
            message=f"Theme manifest not found: {path}",
            code="THEME_MANIFEST_NOT_FOUND",
            source="asset_manifest",
            path=path,
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return EngineIssue(
            severity="error",
            message=f"Could not read theme manifest: {exc}",
            code="THEME_MANIFEST_INVALID",
            source="asset_manifest",
            path=path,
        )


def _asset_issue_to_engine(issue: AssetValidationIssue) -> EngineIssue:
    return EngineIssue(
        severity=issue.severity,
        message=issue.message,
        code="ASSET_VALIDATION",
        source="assets",
        path=issue.path,
    )


def _content_issue_to_engine(issue: ValidationIssue) -> EngineIssue:
    return EngineIssue(
        severity=issue.severity,
        message=issue.message,
        code="THEMATIC_VALIDATION",
        source="content",
        puzzle_index=issue.puzzle_index,
        puzzle_title=issue.puzzle_title,
        context=issue.context,
    )


def _error_response(message: str, *, code: str, path: str | None = None) -> ThematicValidationResponse:
    return ThematicValidationResponse(
        ok=False,
        status="error",
        issues=[
            EngineIssue(
                severity="error",
                message=message,
                code=code,
                source="engine",
                path=path,
            )
        ],
    )

