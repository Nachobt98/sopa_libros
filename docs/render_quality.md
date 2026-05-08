# Render quality warnings

The thematic generator runs an editorial render-quality pass after PNG pages are created and before the final generation report is written.

These checks are heuristic. They do not replace manually reviewing the generated PNGs/PDF, but they point to pages that are more likely to need visual inspection.

## Adaptive layout pass

Puzzle pages now use a small shared adaptive layout planner before the render-quality report is built. The same planner is used by the renderer and by the analyzer, so warnings describe the final adaptive page rather than a separate approximation.

The planner is intentionally conservative:

- short titles keep the default title size and spacing;
- crowded puzzle titles may receive a small deterministic font reduction and a slightly tighter title-to-fact gap;
- long fun facts try modest text-size/gap adjustments before truncation;
- dense word lists may use an extra column and/or a small font reduction before being reported as dense;
- grid cell size is not auto-fixed because changing grid size would alter the puzzle product itself.

Adaptive layout does not try to hide all warnings. A warning after adaptation means the page still deserves manual review.

## Where warnings appear

Warnings are printed in the console summary:

```text
=== Render quality ===
Warnings: 3
  - FACT_TRUNCATED: 1
  - GRID_CELL_SMALL: 1
  - WORD_LIST_DENSE: 1
```

They are also embedded in:

```text
output_puzzles_kdp/<book_slug>/generation_report.json
```

under:

```json
"render_quality": {
  "warning_count": 1,
  "by_severity": {
    "warning": 1
  },
  "by_code": {
    "FACT_TRUNCATED": 1
  },
  "warnings": []
}
```

## Severities

- `info`: the page probably fits, but it is dense enough to review.
- `warning`: likely visual/editorial issue; inspect the page before publishing.
- `error`: high risk that the rendered result is not acceptable without adjustment.

Render-quality errors do not currently stop PDF generation. They are production review signals, not hard build failures.

## Current warning codes

### `TITLE_PAGE_DENSE_TITLE`

The book title fits the title page but required many lines or substantial font reduction.

Recommended action: inspect the title page and consider shortening the title/subtitle or using a less dense title layout.

### `TITLE_PAGE_OVERFLOW_RISK`

The book title still exceeds the intended title-page line budget after font reduction.

Recommended action: shorten the title or improve the title-page layout before publication.

### `BLOCK_COVER_DENSE_TITLE`

A block cover title is dense after wrapping/font reduction.

Recommended action: inspect the block cover and consider shortening the block name.

### `PUZZLE_TITLE_DENSE`

A puzzle title still wraps to too many lines after adaptive title sizing.

Recommended action: inspect the puzzle page and shorten the title if it still looks cramped.

### `FACT_TRUNCATED`

The fun fact is still expected to be truncated after adaptive text sizing and spacing.

Recommended action: shorten the fact or split the content across a different puzzle/topic.

### `FACT_CARD_TIGHT`

The fun fact fits after adaptive layout but uses nearly all available card text space.

Recommended action: inspect the page; shortening the fact may improve readability.

### `WORD_LIST_COLUMN_OVERFLOW_RISK`

At least one word/phrase remains too wide for the adaptive word-list columns.

Recommended action: shorten the phrase, replace it with a tighter term, or increase layout space in a future preset.

### `WORD_LIST_DENSE`

The word list fits after adaptive layout but remains dense.

Recommended action: inspect the bottom word-list area and consider reducing word count.

### `GRID_WORD_LIST_SPACING_TIGHT`

The lower area was compacted to keep the solution pill and word list inside safe bounds.

Recommended action: inspect spacing between grid, solution pill and word list.

### `GRID_CELL_SMALL`

Grid cells are small for print readability.

Recommended action: reduce grid size, use a larger trim preset, or review at actual print size before publishing.

## Recommended workflow

1. Run a preview:

```bash
sopa-libros-thematic --title "Visual Baseline Preview" --input wordlists/fixtures/visual_baseline.txt --difficulty medium --grid-size 14 --preview --clean-output
```

2. Open `generation_report.json`.
3. Check `render_quality.warning_count`.
4. Inspect pages listed in `render_quality.warnings[*].path`.
5. Fix content/layout only where warnings are meaningful.

Warnings are intentionally conservative. A warning means "review this page", not always "this page is broken".
