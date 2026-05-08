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
ColorValue = ColorRgba | str


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
    fact_card_fill: ColorRgba
    fact_card_border: ColorRgba
    fact_header_fill: ColorRgba
    fact_header_text: ColorRgba
    fact_card_radius_px: int
    fact_card_border_width_px: int
    pill_fill: ColorRgba
    pill_border: ColorRgba
    pill_text: ColorRgba
    pill_border_width_px: int
    grid_line_color: ColorValue
    letter_color: ColorRgba
    solution_letter_color: ColorRgba
    highlight_fill: ColorRgba
    highlight_border: ColorRgba


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
    fact_card_fill=(245, 245, 245, 245),
    fact_card_border=(170, 170, 170, 255),
    fact_header_fill=(30, 30, 30, 255),
    fact_header_text=(255, 255, 255, 255),
    fact_card_radius_px=18,
    fact_card_border_width_px=2,
    pill_fill=(230, 230, 230, 255),
    pill_border=(120, 120, 120, 255),
    pill_text=(0, 0, 0, 255),
    pill_border_width_px=2,
    grid_line_color="#444444",
    letter_color=(0, 0, 0, 255),
    solution_letter_color=(0, 0, 0, 255),
    highlight_fill=(243, 226, 200, 230),
    highlight_border=(0, 0, 0, 255),
)

PREMIUM_NEUTRAL_THEME = ThemeConfig(
    name="premium-neutral",
    background_opacity=0.42,
    page_background_fill=(247, 241, 229, 255),
    panel_fill=(255, 251, 242, 232),
    panel_border=(106, 84, 58, 150),
    title_color=(54, 43, 30, 255),
    body_color=(59, 48, 35, 255),
    panel_radius_px=34,
    panel_border_width_px=4,
    fact_card_fill=(253, 246, 235, 250),
    fact_card_border=(151, 119, 78, 190),
    fact_header_fill=(92, 70, 44, 255),
    fact_header_text=(255, 247, 232, 255),
    fact_card_radius_px=22,
    fact_card_border_width_px=3,
    pill_fill=(238, 221, 195, 255),
    pill_border=(137, 101, 60, 220),
    pill_text=(69, 50, 29, 255),
    pill_border_width_px=3,
    grid_line_color=(116, 93, 64, 255),
    letter_color=(48, 38, 27, 255),
    solution_letter_color=(36, 29, 21, 255),
    highlight_fill=(215, 169, 98, 138),
    highlight_border=(101, 72, 38, 235),
)

BOLD_MODERN_THEME = ThemeConfig(
    name="bold-modern",
    background_opacity=0.22,
    page_background_fill=(241, 245, 249, 255),
    panel_fill=(255, 255, 255, 238),
    panel_border=(15, 23, 42, 215),
    title_color=(2, 6, 23, 255),
    body_color=(15, 23, 42, 255),
    panel_radius_px=18,
    panel_border_width_px=6,
    fact_card_fill=(226, 232, 240, 255),
    fact_card_border=(15, 23, 42, 230),
    fact_header_fill=(15, 23, 42, 255),
    fact_header_text=(248, 250, 252, 255),
    fact_card_radius_px=14,
    fact_card_border_width_px=4,
    pill_fill=(219, 234, 254, 255),
    pill_border=(29, 78, 216, 245),
    pill_text=(30, 64, 175, 255),
    pill_border_width_px=4,
    grid_line_color=(30, 41, 59, 255),
    letter_color=(2, 6, 23, 255),
    solution_letter_color=(2, 6, 23, 255),
    highlight_fill=(96, 165, 250, 115),
    highlight_border=(29, 78, 216, 245),
)

KIDS_THEME = ThemeConfig(
    name="kids",
    background_opacity=0.36,
    page_background_fill=(255, 248, 220, 255),
    panel_fill=(255, 255, 255, 238),
    panel_border=(37, 99, 235, 175),
    title_color=(190, 24, 93, 255),
    body_color=(31, 41, 55, 255),
    panel_radius_px=58,
    panel_border_width_px=6,
    fact_card_fill=(255, 247, 237, 255),
    fact_card_border=(249, 115, 22, 220),
    fact_header_fill=(37, 99, 235, 255),
    fact_header_text=(255, 255, 255, 255),
    fact_card_radius_px=32,
    fact_card_border_width_px=5,
    pill_fill=(254, 240, 138, 255),
    pill_border=(234, 88, 12, 235),
    pill_text=(124, 45, 18, 255),
    pill_border_width_px=5,
    grid_line_color=(37, 99, 235, 210),
    letter_color=(17, 24, 39, 255),
    solution_letter_color=(17, 24, 39, 255),
    highlight_fill=(244, 114, 182, 120),
    highlight_border=(190, 24, 93, 235),
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
