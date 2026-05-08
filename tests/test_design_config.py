import pytest

from wordsearch.config.design import (
    DEFAULT_LAYOUT,
    DEFAULT_THEME,
    DEFAULT_TYPOGRAPHY,
    THEME_PRESETS,
    get_theme,
    theme_names,
)
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


def test_default_layout_mirrors_existing_layout_constants():
    assert DEFAULT_LAYOUT.trim_width_in == TRIM_W_IN
    assert DEFAULT_LAYOUT.trim_height_in == TRIM_H_IN
    assert DEFAULT_LAYOUT.dpi == DPI
    assert DEFAULT_LAYOUT.page_width_px == PAGE_W_PX
    assert DEFAULT_LAYOUT.page_height_px == PAGE_H_PX
    assert DEFAULT_LAYOUT.safe_left_px == SAFE_LEFT
    assert DEFAULT_LAYOUT.safe_right_px == SAFE_RIGHT
    assert DEFAULT_LAYOUT.safe_top_px == SAFE_TOP
    assert DEFAULT_LAYOUT.safe_bottom_px == SAFE_BOTTOM
    assert DEFAULT_LAYOUT.top_px == TOP_PX
    assert DEFAULT_LAYOUT.bottom_px == BOTTOM_PX


def test_default_typography_mirrors_existing_font_paths():
    assert DEFAULT_TYPOGRAPHY.body_font_path == FONT_PATH
    assert DEFAULT_TYPOGRAPHY.bold_font_path == FONT_PATH_BOLD
    assert DEFAULT_TYPOGRAPHY.title_font_path == FONT_TITLE


def test_default_theme_preserves_current_page_frame_tokens():
    assert DEFAULT_THEME.name == "current-default"
    assert DEFAULT_THEME.background_opacity == 0.7
    assert DEFAULT_THEME.page_background_fill == (255, 255, 255, 255)
    assert DEFAULT_THEME.panel_fill == (255, 255, 255, 150)
    assert DEFAULT_THEME.panel_border == (0, 0, 0, 60)
    assert DEFAULT_THEME.title_color == (0, 0, 0, 255)
    assert DEFAULT_THEME.body_color == (0, 0, 0, 255)


def test_default_theme_preserves_existing_puzzle_component_tokens():
    assert DEFAULT_THEME.fact_card_fill == (245, 245, 245, 245)
    assert DEFAULT_THEME.fact_card_border == (170, 170, 170, 255)
    assert DEFAULT_THEME.fact_header_fill == (30, 30, 30, 255)
    assert DEFAULT_THEME.fact_header_text == (255, 255, 255, 255)
    assert DEFAULT_THEME.pill_fill == (230, 230, 230, 255)
    assert DEFAULT_THEME.pill_border == (120, 120, 120, 255)
    assert DEFAULT_THEME.highlight_fill == (243, 226, 200, 230)
    assert DEFAULT_THEME.highlight_border == (0, 0, 0, 255)
    assert DEFAULT_THEME.grid_line_color == "#444444"
    assert DEFAULT_THEME.letter_color == (0, 0, 0, 255)


def test_theme_presets_are_registered_by_name():
    assert set(theme_names()) == set(THEME_PRESETS)
    assert get_theme("current-default") is DEFAULT_THEME
    assert get_theme(None) is DEFAULT_THEME
    assert get_theme("premium-neutral").name == "premium-neutral"
    assert get_theme("bold-modern").name == "bold-modern"
    assert get_theme("kids").name == "kids"


def test_non_default_themes_have_distinct_component_tokens():
    premium = get_theme("premium-neutral")
    modern = get_theme("bold-modern")
    kids = get_theme("kids")

    assert premium.fact_header_fill != modern.fact_header_fill != kids.fact_header_fill
    assert premium.highlight_fill != modern.highlight_fill != kids.highlight_fill
    assert premium.pill_fill != modern.pill_fill != kids.pill_fill
    assert premium.grid_line_color != modern.grid_line_color != kids.grid_line_color
    assert premium.panel_radius_px != modern.panel_radius_px != kids.panel_radius_px


def test_get_theme_rejects_unknown_theme():
    with pytest.raises(ValueError, match="Tema no soportado"):
        get_theme("unknown")
