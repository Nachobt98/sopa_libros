# Project architecture

This document describes the current generation flow and the target direction for future refactors.

The project is a Python-based word search book generator focused on KDP-ready interiors. The thematic flow reads a structured text file, validates the content, generates puzzle grids, renders pages as images, and exports a final PDF.

## Current high-level flow

```text
input TXT
  ↓
parse thematic blocks and puzzles
  ↓
resolve CLI / interactive options
  ↓
validate parsed puzzle specs
  ↓
generate every grid in memory
  ↓
build the real page plan
  ↓
render title page, table of contents, instructions, block covers, puzzles and solutions
  ↓
export PDF
```

The important design rule is that validation and grid generation happen before rendering. This avoids creating partial PDFs with incorrect table of contents entries or wrong `Solution on page X` references.

## Main entry points

### `main_thematic.py`

Current thematic generator entry point. It supports both interactive execution and CLI arguments.

Example:

```powershell
py main_thematic.py --title "Black History Word Search Collection" --input wordlists/book_block.txt --difficulty medium --grid-size 14
```

### `main.py`

Legacy/simple generator entry point. It should eventually share more infrastructure with the thematic pipeline.

## Core modules

### Parsing

Current module:

```text
wordsearch/puzzle_parser.py
```

Responsibility:

```text
- Parse [Block] / [Puzzle] themed input files.
- Produce puzzle specs used by the generation pipeline.
- Raise parse errors for malformed input.
```

Future target:

```text
wordsearch/parsing/thematic_parser.py
wordsearch/domain/puzzle.py
```

The parser should parse input, but the domain model should live outside the parser.

### Text normalization

Current module:

```text
wordsearch/text_normalization.py
```

Responsibility:

```text
- Convert display words into grid-safe words.
- Remove accents and unsupported characters.
- Keep normalization consistent between validation and generation.
```

### Validation

Current module:

```text
wordsearch/thematic_validation.py
```

Responsibility:

```text
- Validate parsed puzzle specs before rendering.
- Detect blocking errors such as words that do not fit the grid.
- Report non-blocking warnings such as missing backgrounds or duplicate normalized words.
```

Future target:

```text
wordsearch/validation/thematic.py
```

### Grid generation

Current module:

```text
wordsearch/generation/grid.py
```

Responsibility:

```text
- Place words into a letter grid according to difficulty.
- Return the generated grid and placed word positions.
```

Compatibility wrapper:

```text
wordsearch/grid_generation.py
```

The generated result uses explicit dataclasses in `wordsearch/domain/grid.py`.
The root-level module remains as a backward-compatible import wrapper during
the package reorganization.

### Difficulty and grid size

Current modules:

```text
wordsearch/difficulty_levels.py
wordsearch/grid_size_utils.py
```

Responsibility:

```text
- Define difficulty settings.
- Ask for or validate grid sizes.
```

Future target:

```text
wordsearch/generation/difficulty.py
wordsearch/cli/prompts.py
```

Difficulty data should remain separate from interactive prompts.

### Page planning

Current location:

```text
wordsearch/domain/page_plan.py
```

Responsibility:

```text
- Calculate block cover pages.
- Calculate puzzle pages.
- Calculate first real solution page.
```

The current page plan is represented by an explicit `PagePlan` dataclass.

### Rendering

Current modules:

```text
wordsearch/rendering/common.py
wordsearch/rendering/backgrounds.py
wordsearch/rendering/title_page.py
wordsearch/rendering/front_matter.py
wordsearch/rendering/block_cover.py
wordsearch/rendering/highlights.py
wordsearch/rendering/word_list.py
wordsearch/rendering/puzzle_page.py
wordsearch/rendering/pdf.py
```

Responsibility:

```text
- Render puzzle pages and solution pages.
- Render title page, table of contents and instructions.
- Render block covers.
- Export final PDF.
```

Future target:

```text
wordsearch/rendering/solution_page.py
```

The old root-level rendering wrappers have been removed. Rendering code now lives under `wordsearch/rendering/`.

### Configuration

Current module:

```text
wordsearch/constants_and_layout.py
```

Responsibility:

```text
- Page size.
- DPI.
- Margins.
- Font paths.
- Output directory.
```

Future target:

```text
wordsearch/config/layout.py
wordsearch/config/paths.py
wordsearch/config/fonts.py
```

Eventually this should move from global constants to explicit layout/font/theme config objects.

## Current pain points

```text
1. Rendering submodules can still be split further: solution-page concerns and layout configuration.
2. Coverage is still low outside parser, normalization, grid generation and page planning.
3. Ruff is enabled only for basic correctness checks so far.
4. Simple and thematic generation do not share a unified pipeline.
5. Layout/font/theme config still lives in global constants.
```

## Refactor direction

The refactor should be incremental. Avoid large PRs that move files, change behavior and add tests at the same time.

Recommended order:

```text
1. Document architecture and manual regression checklist.
2. Extract CLI from main_thematic.py.
3. Extract thematic generation pipeline.
4. Add explicit domain models.
5. Add tests for parser, normalization, validation and page planning.
6. Extract common rendering helpers.
7. Move already-separated renderers into a rendering package.
8. Split image_rendering.py.
9. Remove legacy rendering wrappers.
10. Add tooling: pytest, ruff, CI.
11. Add advanced CLI options such as --seed, --validate-only and --clean-output.
```

## Stability rule

Every refactor PR should preserve the same public generation command unless the PR explicitly changes the CLI.

Reference command:

```powershell
py main_thematic.py --title "Black History Word Search Collection" --input wordlists/book_block.txt --difficulty medium --grid-size 14
```

After each refactor, run the reference command and compare the generated PDF structure against the manual regression checklist.
