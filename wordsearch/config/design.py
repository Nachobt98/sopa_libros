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
