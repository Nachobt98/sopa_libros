"""Machine-readable engine CLI for desktop app integrations."""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import Any

from wordsearch.engine.events import RunEvent
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

    return parser.parse_args()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json_line(payload: dict[str, Any], *, stream) -> None:
    stream.write(json.dumps(payload, ensure_ascii=False))
    stream.write("\n")
    stream.flush()


def _generate_response(args: argparse.Namespace):
    payload = _load_json(args.config)
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


def main() -> None:
    args = _parse_args()

    if args.command == "validate":
        response = validate_thematic_request(_load_json(args.config))
    elif args.command == "generate":
        response = _generate_response(args)
    else:
        raise AssertionError(f"Unhandled command: {args.command}")

    if args.command != "generate" or not args.json_lines:
        sys.stdout.write(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
    raise SystemExit(0 if response.ok else 1)


if __name__ == "__main__":
    main()
