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

### `sopa-libros-thematic`

Current thematic generator command. It supports both interactive execution and CLI arguments.

Example:

```powershell
sopa-libros-thematic --title "Black History Word Search Collection" --input wordlists/book_block.txt --difficulty medium --grid-size 14
```

### `sopa-libros`

Simple generator command. It resolves interactive options and delegates
generation to `wordsearch/generation/simple_pipeline.py`.

`main.py` and `main_thematic.py` are compatibility wrappers for direct script execution.

## Core modules

### Parsing

Current modules:

```text
wordsearch/parsing/thematic.py
wordsearch/domain/puzzle.py
```

Responsibility:

```text
- Parse [Block] / [Puzzle] themed input files.
- Produce puzzle specs used by the generation pipeline.
- Raise parse errors for malformed input.
```

The parser owns file parsing. `PuzzleSpec` lives in the domain package so
generation, validation and page planning do not depend on a parser module.

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

Current modules:

```text
wordsearch/validation/assets.py
wordsearch/validation/simple_wordlists.py
wordsearch/validation/thematic.py
```

Responsibility:

```text
- Validate required fonts, optional backgrounds and output writability.
- Validate simple word lists before simple generation.
- Validate parsed puzzle specs before rendering.
- Detect blocking errors such as words that do not fit the grid.
- Report non-blocking warnings such as missing backgrounds or duplicate normalized words.
```

Validation code now lives under `wordsearch/validation/`.

### Grid generation

Current module:

```text
wordsearch/generation/grid.py
wordsearch/generation/simple_pipeline.py
wordsearch/generation/thematic_pipeline.py
wordsearch/generation/grid_batch.py
wordsearch/generation/book_assembly.py
```

Responsibility:

```text
- Place words into a letter grid according to difficulty.
- Return the generated grid and placed word positions.
- Orchestrate simple and thematic book generation after CLI options are resolved.
```

The generated result uses explicit dataclasses in `wordsearch/domain/grid.py`.

### Difficulty and grid size

Current modules:

```text
wordsearch/generation/difficulty.py
wordsearch/cli/grid_size_prompts.py
```

Responsibility:

```text
- Define difficulty settings.
- Ask for or validate grid sizes.
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

### Word list input and slugs

Current modules:

```text
wordsearch/io/wordlists.py
wordsearch/cli/wordlist_prompts.py
wordsearch/utils/slug.py
```

Responsibility:

```text
- Load simple word lists from TXT files.
- Prompt for simple word list source in the simple CLI.
- Build filesystem-safe output slugs for book folders and filenames.
```

The old mixed utility module has been removed. Code should import from the
responsibility-specific modules above.

### Rendering

Current modules:

```text
wordsearch/rendering/common.py
wordsearch/rendering/backgrounds.py
wordsearch/rendering/title_page.py
wordsearch/rendering/front_matter.py
wordsearch/rendering/block_cover.py
wordsearch/rendering/grid.py
wordsearch/rendering/highlights.py
wordsearch/rendering/word_list.py
wordsearch/rendering/page_frame.py
wordsearch/rendering/puzzle_page.py
wordsearch/rendering/solution_page.py
wordsearch/rendering/pdf.py
```

Responsibility:

```text
- Render puzzle pages and solution pages.
- Share common puzzle/solution page frame, background and title layout.
- Render title page, table of contents and instructions.
- Render block covers.
- Export final PDF.
```

The old root-level rendering wrappers have been removed. Rendering code now lives under `wordsearch/rendering/`.

### Configuration

Current modules:

```text
wordsearch/config/layout.py
wordsearch/config/paths.py
wordsearch/config/fonts.py
```

Responsibility:

```text
- Page size.
- DPI.
- Margins.
- Font paths.
- Output root, generated book folders, generated filenames and default wordlist paths.
```

The root-level constants wrapper has been removed. Internal code imports
directly from `wordsearch/config/`. Output and wordlist paths are built through
`wordsearch/config/paths.py` helpers so pipelines and renderers do not duplicate
filesystem defaults. The next step is to move from module constants to explicit
layout/font/theme config objects where that improves testing or format
customization.

## Current pain points

```text
1. Coverage is still low in low-level rendering modules.
2. Ruff is enabled only for basic correctness checks so far.
3. Simple and thematic generation still have some duplicated orchestration concepts.
4. Layout/font/theme config still uses module constants instead of explicit config objects.
```

## Refactor direction

The refactor should be incremental. Avoid large PRs that move files, change behavior and add tests at the same time.

Recommended order:

```text
1. Expand coverage around validation and low-level rendering helpers.
2. Introduce explicit layout/font/theme config objects when customization requires it.
3. Add advanced CLI options such as --seed, --validate-only and --clean-output.
```

## Stability rule

Every refactor PR should preserve the same public generation command unless the PR explicitly changes the CLI.

Reference command:

```powershell
sopa-libros-thematic --title "Black History Word Search Collection" --input wordlists/book_block.txt --difficulty medium --grid-size 14
```

After each refactor, run the reference command and compare the generated PDF structure against the manual regression checklist.
