# Generation report

Successful thematic generation writes a `generation_report.json` file inside the
book output folder.

Example path:

```text
output_puzzles_kdp/black_history_word_search_collection/generation_report.json
```

The report records the parameters and output metadata for the run:

- report schema version;
- UTC generation timestamp;
- book title;
- input TXT path;
- difficulty;
- grid size;
- seed;
- whether `--clean-output` was used;
- puzzle count;
- block count;
- rendered content/solution image counts;
- first solution page;
- output directory;
- final PDF path.

Use this file to reproduce or audit a generated book without relying on terminal
history. It is especially useful when comparing seeded runs or checking which
input/settings produced a reviewed PDF.

`--validate-only` does not write a generation report because it intentionally
stops before grid generation, image rendering and PDF export.
