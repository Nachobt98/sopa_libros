# KDP preflight report

The thematic generator writes a KDP-oriented preflight report after the final PDF has been exported.

This report does not replace Amazon KDP's upload validation or a manual page-by-page review, but it catches common local generation problems before publication work continues.

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
- the PDF can be inspected internally when possible;
- the real PDF page count matches the expected page count;
- the first PDF page box matches the configured trim size;
- all PDF pages share the same physical page size;
- generated content images exist and match the configured page size;
- generated solution images exist and match the configured page size;
- expected PDF metadata is recorded;
- embedded PDF metadata is read back and compared against expected values.

## PDF metadata

The thematic pipeline currently writes basic metadata into the final PDF:

```text
title    = book title
author   = empty by default
subject  = generated word search difficulty summary
keywords = word search, puzzle book, KDP, difficulty and selected theme
creator  = sopa-libros
```

The preflight report stores both `expected_pdf_metadata` and `actual_pdf_metadata`. Metadata mismatches are warnings, not blocking errors, because they do not usually make the PDF technically invalid for KDP.

## Current limits

The report does not yet validate Amazon's live upload rules, bleed-specific requirements, text safe-area collisions, visual clipping, embedded font licensing or content factuality.

Those checks should be added incrementally in future PRs.

## Recommended workflow

1. Run `sopa-libros-thematic --validate-only` while editing content.
2. Generate the book with a fixed `--seed`.
3. Review `generation_report.json` for generation metadata.
4. Review `preflight_report.json` for output, PDF and metadata problems.
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
