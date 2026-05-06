"""Backward-compatible layout/font/path constants.

New code should import from `wordsearch.config.layout`,
`wordsearch.config.fonts` and `wordsearch.config.paths`.
"""

from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_PATH_BOLD,
    FONT_TITLE,
    title_font_size,
    wordlist_font_size,
)
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
    bottom_in,
    bottom_px,
    gutter_in,
    gutter_px,
    outside_in,
    outside_px,
    top_in,
    top_px,
)
from wordsearch.config.paths import BASE_OUTPUT_DIR

__all__ = [
    "BASE_OUTPUT_DIR",
    "BOTTOM_PX",
    "DPI",
    "FONT_PATH",
    "FONT_PATH_BOLD",
    "FONT_TITLE",
    "PAGE_H_PX",
    "PAGE_W_PX",
    "SAFE_BOTTOM",
    "SAFE_LEFT",
    "SAFE_RIGHT",
    "SAFE_TOP",
    "TOP_PX",
    "TRIM_H_IN",
    "TRIM_W_IN",
    "bottom_in",
    "bottom_px",
    "gutter_in",
    "gutter_px",
    "outside_in",
    "outside_px",
    "outside_px",
    "title_font_size",
    "top_in",
    "top_px",
    "wordlist_font_size",
]
