"""Machine-readable engine CLI for desktop app integrations."""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import Any

from wordsearch.config.design import DEFAULT_THEME_NAME
from wordsearch.config.formats import DEFAULT_FORMAT_NAME
from wordsearch.asset_generation.user_assets import USER_SUPPLIED_PROVIDER, build_user_asset_manifest_for_book
from wordsearch.engine.events import RunEvent
from wordsearch.engine.project import (
    ThematicProject,
    build_default_project_path,
    load_thematic_project,
    save_thematic_project,
)
from wordsearch.engine.thematic import generate_thematic_request, validate_thematic_request


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sopa-libros engine commands with JSON I/O.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a thematic book request.")
    validate_parser.add_argument("--config", required=True, help="Path to a JSON request file.")

    generate_parser = subparsers.add_parser("generate", help="Generate a thematic book from a JSON request.")
    generate_parser.add_argument("--config", required=True, help="Path to a JSON request file.")
    generate_parser.add_argument(
        "--json-lines",
        action="store_true",
        help="Stream events as JSON Lines and finish with one result line.",
    )

    project_parser = subparsers.add_parser("project", help="Work with .sopa.json project files.")
    project_subparsers = project_parser.add_subparsers(dest="project_command", required=True)

    init_parser = project_subparsers.add_parser("init", help="Create a thematic .sopa.json project file.")
    init_parser.add_argument("--title", required=True, help="Book title.")
    init_parser.add_argument("--input", dest="input_path", required=True, help="Path to thematic TXT input.")
    init_parser.add_argument("--output", help="Project output path. Defaults to projects/<title>.sopa.json.")
    init_parser.add_argument("--difficulty", default="medium", choices=("easy", "medium", "hard"))
    init_parser.add_argument("--grid-size", type=int, default=14)
    init_parser.add_argument("--seed", type=int)
    init_parser.add_argument("--theme", dest="theme_name")
    init_parser.add_argument("--format", dest="format_name")
    init_parser.add_argument("--theme-manifest", dest="theme_manifest_path")
    init_parser.add_argument("--output-dir")
    init_parser.add_argument("--limit", type=int)
    init_parser.add_argument("--preview", action="store_true")

    request_parser = project_subparsers.add_parser("request", help="Print the engine request for a project.")
    request_parser.add_argument("--project", required=True, help="Path to .sopa.json project file.")

    validate_project_parser = project_subparsers.add_parser("validate", help="Validate a project file.")
    validate_project_parser.add_argument("--project", required=True, help="Path to .sopa.json project file.")

    generate_project_parser = project_subparsers.add_parser("generate", help="Generate from a project file.")
    generate_project_parser.add_argument("--project", required=True, help="Path to .sopa.json project file.")
    generate_project_parser.add_argument(
        "--json-lines",
        action="store_true",
        help="Stream events as JSON Lines and finish with one result line.",
    )

    assets_project_parser = project_subparsers.add_parser(
        "assets",
        help="Build a reviewed asset_manifest.json for a project.",
    )
    assets_project_parser.add_argument("--project", required=True, help="Path to .sopa.json project file.")
    assets_project_parser.add_argument("--user-assets-dir", required=True, help="Directory with user-supplied images.")
    assets_project_parser.add_argument("--output", dest="output_dir", help="Asset output directory.")
    assets_project_parser.add_argument("--style", default=USER_SUPPLIED_PROVIDER, help="Style label for the manifest.")

    return parser.parse_args()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json_line(payload: dict[str, Any], *, stream) -> None:
    stream.write(json.dumps(payload, ensure_ascii=False))
    stream.write("\n")
    stream.flush()


def _generate_response(args: argparse.Namespace):
    payload = _load_json(args.config) if hasattr(args, "config") else _load_project_request(args.project)
    if not args.json_lines:
        with contextlib.redirect_stdout(sys.stderr):
            return generate_thematic_request(payload)

    stdout = sys.stdout

    def emit_event(event: RunEvent) -> None:
        _write_json_line({"type": "event", "event": event.to_dict()}, stream=stdout)

    with contextlib.redirect_stdout(sys.stderr):
        response = generate_thematic_request(
            payload,
            event_callback=emit_event,
            include_events=False,
        )
    _write_json_line({"type": "result", "result": response.to_dict()}, stream=stdout)
    return response


def _load_project_request(path: str) -> dict[str, Any]:
    return load_thematic_project(path).to_engine_request()


def _build_project_from_args(args: argparse.Namespace) -> ThematicProject:
    return ThematicProject(
        book_title=args.title,
        input_path=args.input_path,
        difficulty=args.difficulty,
        grid_size=args.grid_size,
        seed=args.seed,
        theme_name=args.theme_name or DEFAULT_THEME_NAME,
        format_name=args.format_name or DEFAULT_FORMAT_NAME,
        theme_manifest_path=args.theme_manifest_path,
        output_dir=args.output_dir,
        limit=args.limit,
        preview=args.preview,
    )


def _project_response(args: argparse.Namespace):
    if args.project_command == "init":
        project = _build_project_from_args(args)
        output_path = args.output or build_default_project_path(project.book_title)
        project_path = save_thematic_project(project, output_path)
        return {
            "ok": True,
            "command": "project.init",
            "project_path": project_path,
            "project": project.to_dict(),
        }
    if args.project_command == "request":
        project = load_thematic_project(args.project)
        return {
            "ok": True,
            "command": "project.request",
            "project_path": args.project,
            "request": project.to_engine_request(),
        }
    if args.project_command == "validate":
        return validate_thematic_request(_load_project_request(args.project))
    if args.project_command == "generate":
        return _generate_response(args)
    if args.project_command == "assets":
        project = load_thematic_project(args.project)
        result = build_user_asset_manifest_for_book(
            title=project.book_title,
            input_path=project.input_path,
            user_assets_dir=args.user_assets_dir,
            output_dir=args.output_dir,
            style=args.style,
        )
        project.theme_manifest_path = result.manifest_path
        save_thematic_project(project, args.project)
        return {
            "ok": True,
            "command": "project.assets",
            "project_path": args.project,
            "project": project.to_dict(),
            "assets": {
                "output_dir": result.output_dir,
                "manifest_path": result.manifest_path,
                "source_map_path": result.source_map_path,
                "asset_count": result.asset_count,
                "block_count": result.block_count,
                "warning_count": result.warning_count,
            },
        }
    raise AssertionError(f"Unhandled project command: {args.project_command}")


def _is_ok(response) -> bool:
    if isinstance(response, dict):
        return bool(response.get("ok", False))
    return bool(response.ok)


def _response_to_dict(response) -> dict[str, Any]:
    if isinstance(response, dict):
        return response
    return response.to_dict()


def main() -> None:
    args = _parse_args()

    if args.command == "validate":
        response = validate_thematic_request(_load_json(args.config))
    elif args.command == "generate":
        response = _generate_response(args)
    elif args.command == "project":
        response = _project_response(args)
    else:
        raise AssertionError(f"Unhandled command: {args.command}")

    is_json_lines = getattr(args, "json_lines", False) and (
        args.command == "generate" or getattr(args, "project_command", None) == "generate"
    )
    if not is_json_lines:
        sys.stdout.write(json.dumps(_response_to_dict(response), ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
    raise SystemExit(0 if _is_ok(response) else 1)


if __name__ == "__main__":
    main()
