# Reproducible generation

The thematic generator supports an optional `--seed` argument so the same input,
settings and code version can produce the same word placements again.

Example:

```bash
sopa-libros-thematic \
  --title "Black History Word Search Collection" \
  --input wordlists/book_block.txt \
  --difficulty medium \
  --grid-size 14 \
  --seed 1234
```

Use a seed when you need to:

- regenerate a previously reviewed book;
- debug a specific failed or awkward puzzle layout;
- compare rendering changes against a stable visual baseline;
- build visual regression fixtures.

The seed is applied once at book level and the resulting random stream is shared
across all thematic puzzles. This avoids resetting every puzzle to the same
random sequence while still making the whole book deterministic.

If `--seed` is omitted, generation keeps the normal non-deterministic behavior.
