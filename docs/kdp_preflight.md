# KDP preflight report

The thematic generator writes a basic KDP-oriented preflight report after the final PDF has been exported.

This report is intentionally lightweight. It does not replace Amazon KDP's upload validation or a manual page-by-page review, but it catches common local generation problems before publication work continues.

## Output

Successful thematic generations write:

```text
output_puzzles_kdp/<book_slug>/preflight_report.json
```

The generator also prints a short preflight summary to the console.

## Current checks

The current preflight verifies:

- configured trim size and DPI are recorded;
- expected page count is calculated from generated content pages, one solutions divider page and generated solution pages;
- the output directory exists;
- required font paths exist;
- the final PDF exists, is not empty and starts with a PDF header;
- generated content images exist and match the configured page size;
- generated solution images exist and match the configured page size.

## Current limits

The report does not yet inspect the internal PDF page boxes, embedded metadata, KDP upload rules, bleed settings, text safe-area collisions or visual clipping.

Those checks should be added incrementally in future PRs.

## Recommended workflow

1. Run `sopa-libros-thematic --validate-only` while editing content.
2. Generate the book with a fixed `--seed`.
3. Review `generation_report.json` for generation metadata.
4. Review `preflight_report.json` for basic output problems.
5. Inspect the generated PDF manually before any KDP upload.

## Example command

```bash
sopa-libros-thematic \
  --title "Visual Baseline" \
  --input wordlists/fixtures/visual_baseline.txt \
  --difficulty medium \
  --grid-size 14 \
  --seed 1234 \
  --clean-output
```
