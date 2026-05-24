"""Machine-readable engine CLI for desktop app integrations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from wordsearch.engine.thematic import validate_thematic_request


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sopa-libros engine commands with JSON I/O.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a thematic book request.")
    validate_parser.add_argument("--config", required=True, help="Path to a JSON request file.")

    return parser.parse_args()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    args = _parse_args()

    if args.command == "validate":
        response = validate_thematic_request(_load_json(args.config))
    else:
        raise AssertionError(f"Unhandled command: {args.command}")

    sys.stdout.write(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    raise SystemExit(0 if response.ok else 1)


if __name__ == "__main__":
    main()
