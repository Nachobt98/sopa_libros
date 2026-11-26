# Design configuration foundation

Immutable renderer configuration is defined in:

```text
wordsearch/config/design.py
```

These objects drive page layout and named visual themes. Existing theme presets retain their established visual behavior.

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

Groups visual tokens that vary by editorial theme:

- background opacity;
- page background fill;
- panel fill;
- panel border;
- title color;
- body color;
- panel radius;
- panel border width;
- page-specific background opacity overrides;
- optional compositing of translucent backgrounds over the configured page fill.
- optional grayscale conversion for shared background images;
- optional procedural decorations, with explicit block-level defaults.

## Current integration

Named presets are available through the thematic CLI and desktop theme selectors. The shared background helper applies page-specific opacity where configured; legacy presets retain their previous rendering behavior.

The opt-in `christmas-vintage` preset uses a grayscale palette and page-specific background opacities: title `0.60`, block cover `0.35`, puzzle `0.12`, contents and instructions `0.08`, and solutions `0.00`. It reuses the existing user-supplied asset manifest and does not change the project-file schema.

## Procedural editorial decorations

`DecorationConfig`, `PageDecorationConfig`, and `DecorationPlacement` are immutable settings in `wordsearch/config/design.py`. Decorations use deterministic Pillow line art and are disabled for existing themes. The motif catalog is theme-agnostic: `star`, `snowflake`, `evergreen_tree`, `bell`, `botanical_branch`, `holly`, `lantern`, `candle`, `gift`, `ornament`, `flower`, `house`, `star_lantern`, `globe`, `compass`, `geometric_ornament`, and `garland`.

The Christmas preset selects these motifs for its blocks:

| Block | Motifs |
| --- | --- |
| Christmas Classics | bell, holly, star |
| Western European Christmas | lantern, garland, house |
| Nordic Christmas Magic | snowflake, evergreen tree |
| Central and Eastern European Traditions | star, geometric ornament |
| Mediterranean Christmas | botanical branch, candle, star |
| A North American Christmas | gift, evergreen tree, ornament |
| Latin American Christmas | star lantern, flower, lantern |
| Christmas Across Asia and Oceania | star lantern, botanical branch, flower |
| Christmas in Africa and the Middle East | candle, star, geometric ornament |
| Global Christmas Treasures | globe, compass, star |

An existing asset manifest can override selected page settings for a block; omitted page types inherit that block's theme defaults. For example, this changes the Christmas Classics puzzle separators while retaining its cover motifs:

```json
{
  "blocks": {
    "christmas_classics": {
      "decorations": {
        "enabled": true,
        "pages": [
          {
            "page_type": "puzzle",
            "region": "separator",
            "placements": [
              {
                "motif": "compass",
                "x": 0.22,
                "y": 0.5,
                "size_ratio": 0.018,
                "stroke_width_ratio": 0.05,
                "color": 68,
                "opacity": 0.62,
                "rotation_degrees": 0
              },
              {
                "motif": "star",
                "x": 0.78,
                "y": 0.5
              }
            ]
          }
        ]
      }
    }
  }
}
```

Placement coordinates are normalized to the reserved page or separator area. The `separator` region is currently available only for puzzle-page word-bank dividers; `page` uses the full safe area, so custom placements should be kept clear of text and other content. `size_ratio` is relative to the shorter trim dimension; `color` is one grayscale value from 0 to 255, and opacity is from 0 to 1. Set the top-level `enabled` value to `false` to disable a block's decorations; set a page's `enabled` value to `false` to suppress just that page type. Solutions have no Christmas default decorations.

The decoration order is behind page content and text, but reserved ornaments are drawn above the translucent content panel so the panel cannot wash them out. Puzzle ornaments use the word-bank separator area and do not enter the grid or word list. No procedural decorations require external assets. Generated visual previews are written to `output/previews/christmas-vintage/`.

There is no Christmas-specific background image in the repository. The previews use the existing `assets/world.png` fallback, converted to grayscale by the theme; a shared user-provided background can still be supplied through the asset manifest.

## Visual baselines

`christmas-vintage` is opt-in. Existing presets keep their previous rendering behavior, and no existing visual baseline files need to change for this preset or its decorations.
