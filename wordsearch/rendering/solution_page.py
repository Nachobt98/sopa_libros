"""Solution page renderer."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

from PIL import ImageDraw

from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_TITLE,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.config.paths import build_default_output_file
from wordsearch.domain.grid import PlacedWord
from wordsearch.rendering.common import load_font, save_page
from wordsearch.rendering.grid import draw_letter_grid
from wordsearch.rendering.page_frame import (
    create_page_canvas,
    draw_page_frame,
    draw_wrapped_centered_title,
)
from wordsearch.rendering.word_list import draw_word_list


def render_solution_page(
    grid: Sequence[Sequence[str]],
    words: Iterable[str],
    idx: int,
    *,
    background_path: Optional[str] = None,
    filename: Optional[str] = None,
    placed_words: Optional[Sequence[PlacedWord]] = None,
    puzzle_title: Optional[str] = None,
) -> str:
    """Render a solution page with highlighted placed words."""
    scale = 3
    img = create_page_canvas(background_path, scale)
    draw = ImageDraw.Draw(img)
    frame = draw_page_frame(draw=draw, scale=scale)

    page_w_hi = frame.page_w_hi
    page_h_hi = frame.page_h_hi
    safe_bottom_hi = frame.safe_bottom_hi
    panel_top = frame.panel_top
    content_left_hi = frame.content_left_hi
    content_right_hi = frame.content_right_hi
    grid_top_base = frame.grid_top_base

    font_title = load_font(FONT_TITLE, TITLE_FONT_SIZE * scale)
    text_color = (0, 0, 0, 255)
    highlight_fill = (243, 226, 200, 230)
    highlight_border = (0, 0, 0, 255)

    title_text = f"Solution – {idx}. {puzzle_title}" if puzzle_title else f"Solution {idx}"
    draw_wrapped_centered_title(
        draw,
        title_text,
        font_title,
        max_width=int(content_right_hi - content_left_hi),
        start_y=panel_top + int(25 * scale),
        area_left=content_left_hi,
        area_right=content_right_hi,
        line_spacing=1.05,
    )

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    content_width_hi = content_right_hi - content_left_hi
    grid_width_target_hi = int(content_width_hi * 0.85)
    cell_size_hi = int(grid_width_target_hi / max(cols, 1))
    grid_w_hi = cell_size_hi * cols
    grid_top_hi = grid_top_base
    grid_left_hi = int((content_left_hi + content_right_hi - grid_w_hi) // 2)

    grid_bottom_hi = draw_letter_grid(
        img=img,
        draw=draw,
        grid=grid,
        placed_words=placed_words,
        is_solution=True,
        grid_left_hi=grid_left_hi,
        grid_top_hi=grid_top_hi,
        cell_size_hi=cell_size_hi,
        scale=scale,
        page_w_hi=page_w_hi,
        page_h_hi=page_h_hi,
        highlight_fill=highlight_fill,
        highlight_border=highlight_border,
    )

    base_gap_hi = int(60 * scale)
    gap_pill_to_words_hi = int(70 * scale)
    words_area_height_hi = int(850 * scale)
    words_bottom_hi = safe_bottom_hi - int(8 * scale)
    words_top_hi = max(0, words_bottom_hi - words_area_height_hi)

    desired_words_top_hi = grid_bottom_hi + base_gap_hi + gap_pill_to_words_hi
    if desired_words_top_hi > words_top_hi:
        words_top_hi = desired_words_top_hi
    if words_top_hi > words_bottom_hi:
        words_top_hi = words_bottom_hi

    draw_word_list(
        draw=draw,
        words=words,
        words_top_hi=words_top_hi,
        words_bottom_hi=words_bottom_hi,
        content_left_hi=content_left_hi,
        content_right_hi=content_right_hi,
        scale=scale,
        font_path=FONT_PATH,
        wordlist_font_size=WORDLIST_FONT_SIZE,
        text_color=text_color,
    )

    if filename is None:
        filename = build_default_output_file(f"puzzle_{idx}_sol.png")

    return save_page(img, filename)
