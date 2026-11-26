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

## Current integration

Named presets are available through the thematic CLI and desktop theme selectors. The shared background helper applies page-specific opacity where configured; legacy presets retain their previous rendering behavior.

The opt-in `christmas-vintage` preset uses a grayscale palette and page-specific background opacities: title `0.60`, block cover `0.35`, puzzle `0.12`, contents and instructions `0.08`, and solutions `0.00`. It reuses the existing user-supplied asset manifest and does not change the project-file schema.

## Visual baselines

`christmas-vintage` is opt-in. Existing presets keep their previous rendering behavior, and no existing visual baseline files need to change for this preset.
