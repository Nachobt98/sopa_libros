# App engine JSON contract

This document describes the first non-interactive engine contract intended for a
future desktop UI such as Tauri + React.

The existing CLIs remain the human-facing entry points:

```text
sopa-libros
sopa-libros-thematic
sopa-libros-assets
```

The app-facing entry point is:

```text
sopa-libros-engine validate --config request.json
```

It writes JSON to stdout and exits with:

- `0` when validation has no blocking errors;
- `1` when the request, content or assets contain blocking errors.

## Validate Request

Minimal thematic validation request:

```json
{
  "book_title": "Ancient Egypt Word Search",
  "input_path": "wordlists/book_block.txt",
  "difficulty": "medium",
  "grid_size": 14
}
```

Supported optional fields:

```json
{
  "seed": 1234,
  "theme_name": "premium-neutral",
  "format_name": "trade-6x9",
  "theme_manifest_path": "assets/generated/book/asset_manifest.json",
  "output_dir": "output_puzzles_kdp/custom_book",
  "limit": 5,
  "preview": true
}
```

The request also accepts UI-friendly aliases:

- `title` for `book_title`;
- `puzzles_txt_path` for `input_path`;
- `theme` for `theme_name`;
- `format` for `format_name`.

## Validate Response

Successful validation returns the selected puzzle summaries and output path:

```json
{
  "ok": true,
  "command": "thematic.validate",
  "status": "ok",
  "issues": [],
  "parsed_puzzle_count": 10,
  "selected_puzzle_count": 5,
  "output_dir": "output_puzzles_kdp/ancient_egypt_word_search",
  "puzzles": [
    {
      "index": 0,
      "title": "Pharaohs",
      "word_count": 12,
      "block_name": "Ancient Egypt",
      "has_fact": true,
      "block_background": null
    }
  ],
  "error_count": 0,
  "warning_count": 0
}
```

Errors and warnings are returned as structured `issues`:

```json
{
  "severity": "error",
  "message": "Input file not found: missing.txt",
  "code": "INPUT_NOT_FOUND",
  "source": "engine",
  "path": "missing.txt",
  "puzzle_index": null,
  "puzzle_title": null,
  "context": null
}
```

Current issue sources:

- `engine`: request parsing, missing input files and parse errors;
- `assets`: required fonts, backgrounds, output writability and manifest assets;
- `asset_manifest`: malformed or missing theme manifest files;
- `content`: thematic puzzle validation.

This contract intentionally stops before grid generation, rendering and PDF
assembly. Preview and full generation should be added as separate engine
commands so a GUI can show quick validation feedback before starting heavier
work.

## Run Events

Long-running generation code can emit structured `RunEvent` objects through an
optional callback. The existing CLI output remains unchanged, but app callers can
subscribe to these events instead of scraping terminal text.

Event shape:

```json
{
  "type": "stage_started",
  "stage": "grid_generation",
  "message": "Generating puzzle grids.",
  "current": 0,
  "total": 10,
  "metadata": {}
}
```

Current event types:

- `run_started`;
- `stage_started`;
- `progress`;
- `stage_completed`;
- `run_completed`;
- `run_failed`.

Current thematic stages:

- `setup`;
- `parsing`;
- `validation`;
- `grid_generation`;
- `rendering`;
- `visual_regression`;
- `pdf_assembly`;
- `preflight`;
- `complete`.

Python callers can use:

```python
events = []
pdf_path = generate_thematic_book(options, event_callback=events.append)
payload = [event.to_dict() for event in events]
```

The future Tauri sidecar command should serialize these events as JSON lines or
as a final `events` array, depending on whether the UI needs live progress or
only a completed run summary.
