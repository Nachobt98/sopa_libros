# Book format presets

The thematic generator supports editorial book format presets through:

```bash
sopa-libros-thematic --format trade-6x9
```

A format preset controls the physical product format, not the visual theme. Use:

- `--theme` for color/style direction;
- `--format` for trim size, safe area, page size and KDP preflight expectations.

## Why presets exist

Amazon KDP defines minimum margin requirements for print interiors. For no-bleed interiors, top/bottom/outside margins can be as low as 0.25 in, while the inside gutter depends on page count. For 24–150 pages, the inside gutter minimum is 0.375 in. The presets in this project use those values as a floor and add editorial padding so puzzle pages have more breathing room than the bare minimum.

The current presets are no-bleed interiors because word-search interiors usually benefit from clean safe areas and predictable KDP uploads.

## Available presets

### `trade-6x9`

Compact trade paperback, 6 x 9 in.

Best for:

- lower print cost;
- adult/premium small paperback collections;
- moderate grids.

Recommended grid range: 10–14.

### `activity-8.5x11`

Large activity workbook, 8.5 x 11 in.

Best for:

- classic activity-book format;
- larger grids;
- more generous word lists;
- children's or general puzzle books.

Recommended grid range: 14–20.

### `large-print-8x10`

Large-print puzzle book, 8 x 10 in.

Best for:

- senior-friendly books;
- lower page density;
- larger letters and calmer layout.

Recommended grid range: 12–16.

### `square-8.5`

Square gift/activity format, 8.5 x 8.5 in.

Best for:

- novelty/giftable puzzle books;
- themed collections;
- moderate grids where visual identity matters.

Recommended grid range: 12–16.

## Examples

Compact premium trade book:

```bash
sopa-libros-thematic --title "Black Culture Word Search" --input wordlists/book_block.txt --difficulty medium --grid-size 14 --theme premium-neutral --format trade-6x9 --clean-output
```

Large activity workbook:

```bash
sopa-libros-thematic --title "Black Culture Activity Word Search" --input wordlists/book_block.txt --difficulty medium --grid-size 18 --theme bold-modern --format activity-8.5x11 --clean-output
```

Large-print version:

```bash
sopa-libros-thematic --title "Black Culture Large Print Word Search" --input wordlists/book_block.txt --difficulty medium --grid-size 14 --theme premium-neutral --format large-print-8x10 --clean-output
```

Preview a square edition:

```bash
sopa-libros-thematic --title "Square Preview" --input wordlists/fixtures/visual_baseline.txt --difficulty medium --grid-size 14 --preview --format square-8.5 --clean-output
```

## Notes

- The default format is `trade-6x9` to preserve existing behavior.
- Non-default formats are opt-in and pass a layout configuration through rendering, PDF assembly and KDP preflight.
- The preflight report records the selected `format_name` and validates image dimensions/PDF trim against that format.
- A format preset does not automatically choose a grid size. Use the recommended ranges as editorial guidance.
