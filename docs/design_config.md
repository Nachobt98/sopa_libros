# Design configuration foundation

The renderer now has explicit immutable design config objects in:

```text
wordsearch/config/design.py
```

This is a foundation for future theme and layout presets. It does not introduce a user-facing `--theme` option yet and should not intentionally change the generated visual output.

## Config objects

### `LayoutConfig`

Groups physical page and safe-area decisions:

- trim size;
- DPI;
- page size in pixels;
- safe-area bounds;
- shared panel padding;
- default title area;
- content margin.

The default layout currently mirrors the existing 6x9 KDP no-bleed constants.

### `TypographyConfig`

Groups font paths and base sizes:

- body font;
- bold/body emphasis font;
- title font;
- title font size;
- word-list font size.

### `ThemeConfig`

Groups visual tokens that can later vary by editorial theme:

- background opacity;
- page background fill;
- panel fill;
- panel border;
- title color;
- body color;
- panel radius;
- panel border width.

## Current integration

The shared puzzle/solution page frame uses `DEFAULT_LAYOUT` and `DEFAULT_THEME` for page bounds, background opacity, panel styling and title color.

Other renderers can be migrated incrementally as visual changes become necessary.

## Future work

Recommended next steps:

1. Move more repeated renderer constants into these configs.
2. Add named theme presets such as `classic`, `premium-neutral`, `bold-modern`, `kids` and `large-print`.
3. Add CLI support for selecting a theme.
4. Add visual-regression checks against `wordlists/fixtures/visual_baseline.txt`.

Keep visual refactors separate from intentional visual redesigns so baseline changes remain reviewable.
