# Manual regression checklist

Use this checklist after each refactor that may affect generation, rendering, page planning or output paths.

The goal is not to prove that every pixel is identical. The goal is to catch broken structure, wrong pagination, missing pages, duplicated page numbers and obvious visual regressions before merging.

## Reference command

From the repository root:

```powershell
sopa-libros-thematic --title "Black History Word Search Collection" --input wordlists/book_block.txt --difficulty medium --grid-size 14
```

Expected output folder:

```text
output_puzzles_kdp/black_history_word_search_collection/
```

Expected PDF:

```text
output_puzzles_kdp/black_history_word_search_collection/black_history_word_search_collection.pdf
```

If the PDF is open and Windows blocks overwriting it, close the PDF viewer/browser tab and run the command again.

## Console checks

Before opening the PDF, check the terminal output:

```text
[ ] The command finishes without traceback.
[ ] The generation summary shows the expected title.
[ ] The generation summary shows the expected input file.
[ ] The generation summary shows MEDIUM difficulty.
[ ] The generation summary shows 14x14 grid.
[ ] Validation report shows no blocking errors.
[ ] All expected grids are generated.
[ ] The final PDF path is printed.
```

## File checks

```text
[ ] Output folder exists.
[ ] Final PDF exists.
[ ] 00_title_page.png exists.
[ ] 01_table_of_contents.png exists.
[ ] 02_instructions.png exists.
[ ] Block cover images exist.
[ ] Puzzle images exist.
[ ] Solution images exist.
[ ] No obviously stale/old files are mixed into the generated PDF.
```

## PDF structure checks

Open the final PDF and verify:

```text
[ ] Page 1 is the interior title page.
[ ] Page 2 is Table of Contents.
[ ] Page 3 is Instructions.
[ ] Page 4 is the first block cover.
[ ] The first puzzle page appears immediately after the first block cover.
[ ] Every block cover appears before its block puzzles.
[ ] A SOLUTIONS cover appears before the solution pages.
[ ] Solution pages appear after the SOLUTIONS cover.
[ ] The PDF has no missing first pages.
[ ] The PDF does not start directly at Puzzle 1.
```

## Table of contents checks

```text
[ ] Table of Contents page is present.
[ ] Section names are readable.
[ ] Page numbers are readable.
[ ] Dotted/dashed leaders do not overlap labels or page numbers.
[ ] There is enough spacing between title, subtitle/section label and entries.
[ ] Solutions entry points to the first real solution page, not necessarily the decorative SOLUTIONS cover.
[ ] There is no duplicated footer page number.
```

## Instructions page checks

```text
[ ] Instructions page is present.
[ ] Title and subtitle have clear spacing.
[ ] Numbered instructions are readable.
[ ] Numbers do not collide with text.
[ ] The content block is visually balanced vertically.
[ ] There is no duplicated footer page number.
```

## Puzzle page checks

For a few puzzle pages across different blocks:

```text
[ ] Puzzle title is visible and not clipped.
[ ] FUN FACT box is visible and not clipped.
[ ] Grid is centered and readable.
[ ] Word list is readable.
[ ] "Solution on page X" pill is visible.
[ ] The referenced solution page exists.
[ ] Background does not hurt readability.
```

## Solution page checks

For a few solution pages:

```text
[ ] Solution title is visible and not clipped.
[ ] Grid is readable.
[ ] Highlight overlays are aligned with words.
[ ] Highlight overlays do not obscure letters too much.
[ ] Solution page number matches the puzzle reference.
```

## Pagination checks

Use the reference sample book and verify the expected structure:

```text
[ ] Page 1: title page.
[ ] Page 2: table of contents.
[ ] Page 3: instructions.
[ ] Page 4: first block cover.
[ ] Solutions entry in the table of contents matches the first real solution page.
[ ] Puzzle 1 "Solution on page X" matches the actual first solution page.
[ ] Puzzle 2 points to the next solution page.
[ ] Last puzzle points to the last solution page.
```

## Invalid input checks

Use a deliberately invalid file when changing validation or parsing.

Expected behavior:

```text
[ ] The validation report lists blocking errors.
[ ] The process stops before grid generation.
[ ] No partial PDF is generated from invalid input.
[ ] Missing backgrounds are warnings, not blocking errors.
[ ] Duplicate normalized words are warnings, not blocking errors.
```

## Merge readiness

A PR that touches generation/rendering/page planning should not be merged until:

```text
[ ] Reference command works.
[ ] PDF structure checks pass.
[ ] Table of contents checks pass.
[ ] Instructions checks pass.
[ ] Puzzle checks pass on at least 3 pages.
[ ] Solution checks pass on at least 3 pages.
[ ] Any intentional visual changes are described in the PR.
```
