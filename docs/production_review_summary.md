# Production review summary

The thematic pipeline writes a final human-readable review file after a successful generation:

```text
output_puzzles_kdp/<book_slug>/production_review_summary.txt
```

This file does not replace the underlying machine-readable reports. It summarizes the most important signals from:

- `generation_report.json`
- `preflight_report.json`
- `visual_regression_report.json` when running preview mode
- the render-quality section embedded in `generation_report.json`

## What it contains

The summary includes:

- generated PDF path;
- total page count;
- puzzle count;
- generation/preflight/visual-report paths;
- preflight error and warning counts;
- render-quality error, warning and info counts;
- pages/assets that deserve manual inspection;
- a final recommendation.

Example shape:

```text
=== Production review summary ===
Book: Visual Baseline Preview
PDF: output_puzzles_kdp/visual_baseline_preview/visual_baseline_preview.pdf
Pages: 12
Puzzles: 5
Generation report: output_puzzles_kdp/visual_baseline_preview/generation_report.json
Preflight report: output_puzzles_kdp/visual_baseline_preview/preflight_report.json
Visual regression report: output_puzzles_kdp/visual_baseline_preview/visual_regression_report.json

Preflight:
- errors: 0
- warnings: 0

Render quality:
- errors: 0
- warnings: 1
- info: 2

Pages/assets to inspect:
- WARNING FACT_TRUNCATED | puzzle, page 5, puzzle index 2 | puzzle_3.png | Fun fact is still truncated after adaptive font/gap adjustments.

Recommendation:
Review the flagged pages/assets before full production or KDP upload.
```

## Recommendation meanings

- `Fix blocking errors before using this PDF for publication.` means a preflight or render-quality error exists.
- `Review the flagged pages/assets before full production or KDP upload.` means there are non-blocking warnings.
- `No blocking issues found; skim the informational render-quality pages before publishing.` means only low-risk density/readability notes were found.
- `Preview looks clean; compare visual fingerprints if this run is validating layout changes.` means preview mode produced no automated issues.
- `No automated issues found. Do a final manual PDF review before publishing.` means no automated checks flagged the output.

## Recommended workflow

1. Run `--validate-only` first for content/assets.
2. Run a seeded preview:

```bash
sopa-libros-thematic --title "Visual Baseline Preview" --input wordlists/fixtures/visual_baseline.txt --difficulty medium --grid-size 14 --preview --clean-output
```

3. Open `production_review_summary.txt` first.
4. Inspect only the listed pages/assets before broad PDF review.
5. If the summary is clean, do a final manual pass through the PDF before publishing.

The summary intentionally remains text-based so it is easy to read in terminals, CI logs, editors and pull-request artifacts.
