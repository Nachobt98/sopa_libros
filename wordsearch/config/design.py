"""Editorial design configuration for generated KDP interiors.

This module groups layout and theme decisions into explicit immutable objects.
The default configs mirror the current renderer constants so introducing this
layer does not intentionally change the generated visual output.
"""

from __future__ import annotations

from dataclasses import dataclass

from wordsearch.config.fonts import FONT_PATH, FONT_PATH_BOLD, FONT_TITLE
from wordsearch.config.layout import (
    BOTTOM_PX,
    DPI,
    PAGE_H_PX,
    PAGE_W_PX,
    SAFE_BOTTOM,
    SAFE_LEFT,
    SAFE_RIGHT,
    SAFE_TOP,
    TOP_PX,
    TRIM_H_IN,
    TRIM_W_IN,
)

ColorRgba = tuple[int, int, int, int]


@dataclass(frozen=True)
class LayoutConfig:
    """Physical page and safe-area configuration."""

    name: str
    trim_width_in: float
    trim_height_in: float
    dpi: int
    page_width_px: int
    page_height_px: int
    safe_left_px: int
    safe_right_px: int
    safe_top_px: int
    safe_bottom_px: int
    top_px: int
    bottom_px: int
    default_title_area_px: int = 600
    panel_pad_x_px: int = 30
    panel_pad_top_px: int = 40
    panel_pad_bottom_px: int = 40
    panel_radius_px: int = 35
    panel_border_width_px: int = 3
    content_margin_x_px: int = 40


@dataclass(frozen=True)
class TypographyConfig:
    """Font paths and base type sizes used by the current renderer."""

    body_font_path: str
    bold_font_path: str
    title_font_path: str
    title_font_size: int = 100
    wordlist_font_size: int = 80


@dataclass(frozen=True)
class ThemeConfig:
    """Visual theme tokens for renderer defaults."""

    name: str
    background_opacity: float
    page_background_fill: ColorRgba
    panel_fill: ColorRgba
    panel_border: ColorRgba
    title_color: ColorRgba
    body_color: ColorRgba
    panel_radius_px: int
    panel_border_width_px: int


DEFAULT_LAYOUT = LayoutConfig(
    name="kdp-6x9-no-bleed",
    trim_width_in=TRIM_W_IN,
    trim_height_in=TRIM_H_IN,
    dpi=DPI,
    page_width_px=PAGE_W_PX,
    page_height_px=PAGE_H_PX,
    safe_left_px=SAFE_LEFT,
    safe_right_px=SAFE_RIGHT,
    safe_top_px=SAFE_TOP,
    safe_bottom_px=SAFE_BOTTOM,
    top_px=TOP_PX,
    bottom_px=BOTTOM_PX,
)

DEFAULT_TYPOGRAPHY = TypographyConfig(
    body_font_path=FONT_PATH,
    bold_font_path=FONT_PATH_BOLD,
    title_font_path=FONT_TITLE,
)

DEFAULT_THEME = ThemeConfig(
    name="current-default",
    background_opacity=0.7,
    page_background_fill=(255, 255, 255, 255),
    panel_fill=(255, 255, 255, 150),
    panel_border=(0, 0, 0, 60),
    title_color=(0, 0, 0, 255),
    body_color=(0, 0, 0, 255),
    panel_radius_px=DEFAULT_LAYOUT.panel_radius_px,
    panel_border_width_px=DEFAULT_LAYOUT.panel_border_width_px,
)

PREMIUM_NEUTRAL_THEME = ThemeConfig(
    name="premium-neutral",
    background_opacity=0.55,
    page_background_fill=(250, 247, 241, 255),
    panel_fill=(255, 252, 246, 210),
    panel_border=(84, 70, 55, 80),
    title_color=(42, 35, 28, 255),
    body_color=(42, 35, 28, 255),
    panel_radius_px=DEFAULT_LAYOUT.panel_radius_px,
    panel_border_width_px=DEFAULT_LAYOUT.panel_border_width_px,
)

BOLD_MODERN_THEME = ThemeConfig(
    name="bold-modern",
    background_opacity=0.45,
    page_background_fill=(248, 250, 252, 255),
    panel_fill=(255, 255, 255, 220),
    panel_border=(15, 23, 42, 110),
    title_color=(15, 23, 42, 255),
    body_color=(15, 23, 42, 255),
    panel_radius_px=28,
    panel_border_width_px=4,
)

KIDS_THEME = ThemeConfig(
    name="kids",
    background_opacity=0.5,
    page_background_fill=(255, 253, 239, 255),
    panel_fill=(255, 255, 255, 225),
    panel_border=(80, 130, 180, 120),
    title_color=(32, 80, 130, 255),
    body_color=(25, 40, 60, 255),
    panel_radius_px=46,
    panel_border_width_px=4,
)

THEME_PRESETS: dict[str, ThemeConfig] = {
    DEFAULT_THEME.name: DEFAULT_THEME,
    PREMIUM_NEUTRAL_THEME.name: PREMIUM_NEUTRAL_THEME,
    BOLD_MODERN_THEME.name: BOLD_MODERN_THEME,
    KIDS_THEME.name: KIDS_THEME,
}

DEFAULT_THEME_NAME = DEFAULT_THEME.name


def theme_names() -> tuple[str, ...]:
    """Return available theme preset names sorted for CLI/documentation use."""
    return tuple(sorted(THEME_PRESETS))


def get_theme(name: str | None) -> ThemeConfig:
    """Return a theme preset by name."""
    normalized = (name or DEFAULT_THEME_NAME).strip().lower()
    try:
        return THEME_PRESETS[normalized]
    except KeyError as exc:
        supported = ", ".join(theme_names())
        raise ValueError(f"Tema no soportado: {name}. Temas disponibles: {supported}") from exc
