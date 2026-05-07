# Clean output

The thematic generator supports an optional `--clean-output` flag.

Use it when you want a fresh generated folder for a book and do not want stale
PNGs or PDFs from previous runs to remain mixed with the new output.

Example:

```bash
sopa-libros-thematic \
  --title "Black History Word Search Collection" \
  --input wordlists/book_block.txt \
  --difficulty medium \
  --grid-size 14 \
  --seed 1234 \
  --clean-output
```

Behavior:

- the book output folder is derived from the title as usual;
- if the folder exists, it is removed before asset validation and generation;
- if the folder does not exist, generation continues normally;
- if the output path exists but is not a directory, generation stops;
- if the folder cannot be removed, generation stops before rendering new files.

`--clean-output` is intentionally scoped to the generated folder for the current
book title. It does not remove the entire `output_puzzles_kdp/` root.
