from types import SimpleNamespace

from PIL import Image, ImageDraw

from wordsearch.config.design import DEFAULT_THEME
from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.rendering import adaptive_layout
from wordsearch.rendering.adaptive_layout import (
    plan_fact_layout,
    plan_title_layout,
    plan_word_list_layout,
)
from wordsearch.rendering.page_frame import draw_page_frame


def make_draw():
    image = Image.new("RGBA", (PAGE_W_PX * 3, PAGE_H_PX * 3), DEFAULT_THEME.page_background_fill)
    return ImageDraw.Draw(image)


def test_title_layout_keeps_short_titles_unchanged():
    draw = make_draw()
    frame = draw_page_frame(draw=draw, scale=3, theme=DEFAULT_THEME)

    plan = plan_title_layout(
        draw=draw,
        title_text="1. Short Title",
        max_width_hi=int(frame.content_right_hi - frame.content_left_hi),
        start_y_hi=frame.panel_top + int(25 * 3),
        scale=3,
    )

    assert plan.font_scale == 1.0
    assert len(plan.lines) == 1
    assert plan.title_to_fact_gap_hi == 80 * 3


def test_title_layout_reduces_dense_titles_deterministically(monkeypatch):
    draw = make_draw()
    frame = draw_page_frame(draw=draw, scale=3, theme=DEFAULT_THEME)

    def fake_load_font(path, size):
        return SimpleNamespace(size=size)

    def fake_wrap_text(draw, text, font, max_width):
        if font.size > int(100 * 3 * 0.92):
            return ["Line 1", "Line 2", "Line 3", "Line 4"]
        return ["Line 1", "Line 2", "Line 3"]

    monkeypatch.setattr(adaptive_layout, "load_font", fake_load_font)
    monkeypatch.setattr(adaptive_layout, "wrap_text", fake_wrap_text)
    monkeypatch.setattr(adaptive_layout, "text_size", lambda draw, text, font: (80, 20))

    plan = plan_title_layout(
        draw=draw,
        title_text="1. Dense Title",
        max_width_hi=int(frame.content_right_hi - frame.content_left_hi),
        start_y_hi=frame.panel_top + int(25 * 3),
        scale=3,
    )

    assert plan.font_scale == 0.92
    assert len(plan.lines) == 3
    assert plan.title_to_fact_gap_hi == 62 * 3


def test_fact_layout_prefers_small_editorial_adjustment_before_truncating():
    draw = make_draw()
    frame = draw_page_frame(draw=draw, scale=3, theme=DEFAULT_THEME)
    long_fact = (
        "This fact is intentionally long enough to require editorial layout pressure. "
        "It contains additional context, explanatory wording, and enough detail to "
        "force the planner to consider a slightly smaller text size before deciding "
        "whether the card truly needs truncation."
    )

    plan = plan_fact_layout(
        draw=draw,
        fun_fact=long_fact,
        content_left_hi=frame.content_left_hi,
        content_right_hi=frame.content_right_hi,
        grid_top_base_hi=frame.grid_top_base,
        y_cursor_hi=frame.panel_top + 220 * 3,
        scale=3,
    )

    assert plan.present is True
    assert plan.text_font_scale in {0.5, 0.47, 0.44}
    assert plan.rendered_line_count <= plan.max_lines_fit
    assert plan.box_bottom_hi > 0


def test_word_list_layout_adapts_dense_lists_without_forcing_when_possible():
    draw = make_draw()
    frame = draw_page_frame(draw=draw, scale=3, theme=DEFAULT_THEME)
    words = [
        "Alpha",
        "Beta",
        "Gamma",
        "Delta",
        "Eagle",
        "River",
        "Stone",
        "Light",
        "Music",
        "Dance",
        "Dream",
        "Honor",
        "Unity",
        "Voice",
        "Power",
        "Truth",
        "Peace",
        "Pride",
        "Roots",
        "Story",
        "March",
        "Brave",
        "Hope",
        "Rise",
        "Skill",
        "Focus",
    ]

    plan = plan_word_list_layout(
        draw=draw,
        words=words,
        words_top_hi=frame.safe_bottom_hi - 850 * 3,
        words_bottom_hi=frame.safe_bottom_hi - 8 * 3,
        content_left_hi=frame.content_left_hi,
        content_right_hi=frame.content_right_hi,
        scale=3,
    )

    assert plan.present is True
    assert 2 <= plan.col_count <= 6
    assert plan.max_word_width_ratio <= 0.92
    assert plan.fill_ratio <= 0.88
    assert plan.forced_layout is False
