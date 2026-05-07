# Visual baseline

This fixture is a small deterministic thematic book used to review visual changes before editing the rendering layer.

It is not a production book. It intentionally mixes short and long titles, short and long facts, visible phrases, dense word lists and multiple blocks so layout regressions are easier to spot.

## Fixture

```text
wordlists/fixtures/visual_baseline.txt
```

## Recommended command

```bash
sopa-libros-thematic \
  --title "Visual Baseline" \
  --input wordlists/fixtures/visual_baseline.txt \
  --difficulty medium \
  --grid-size 14 \
  --seed 1234 \
  --clean-output
```

## Output to inspect

The generated files should be written under:

```text
output_puzzles_kdp/visual_baseline/
```

Review at least:

- the title page;
- the table of contents;
- the instructions page;
- both block covers;
- all puzzle pages;
- all solution pages;
- the final PDF.

## What this baseline should catch

- title wrapping regressions;
- fun fact overflow or cramped spacing;
- grid placement changes;
- word list column balance issues;
- solution highlight regressions;
- unexpected PDF assembly changes.

## Workflow before visual PRs

1. Generate the baseline from `main`.
2. Save or inspect the generated PDF/PNGs locally.
3. Switch to the visual-change branch.
4. Generate the same baseline again with the same seed.
5. Compare the outputs before merging.

Keep production output files out of Git. The fixture and this document are the tracked reference; generated PNGs/PDFs remain local artifacts.
