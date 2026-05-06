"""Solution page renderer."""

from __future__ import annotations

import os
from typing import Iterable, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_TITLE,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.config.layout import (
    PAGE_H_PX,
    PAGE_W_PX,
    SAFE_BOTTOM,
    SAFE_LEFT,
    SAFE_RIGHT,
    TOP_PX,
)
from wordsearch.rendering.backgrounds import BACKGROUND_PATH
from wordsearch.rendering.common import (
    load_font,
    rounded_rectangle,
    save_page,
    text_size,
    wrap_text,
)
from wordsearch.rendering.grid import draw_letter_grid
from wordsearch.rendering.word_list import draw_word_list


def _draw_wrapped_centered_title(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    start_y: int,
    area_left: int,
    area_right: int,
    line_spacing: float = 1.05,
) -> int:
    lines = wrap_text(draw, text, font, max_width)
    y = start_y
    container_width = max(0, area_right - area_left)
    for line in lines:
        width, height = text_size(draw, line, font)
        x = area_left + max(0, (container_width - width) // 2)
        draw.text((x, y), line, font=font, fill=(0, 0, 0, 255))
        y += int(height * line_spacing)
    return y


def render_solution_page(
    grid: Sequence[Sequence[str]],
    words: Iterable[str],
    idx: int,
    *,
    background_path: Optional[str] = None,
    filename: Optional[str] = None,
    placed_words: Optional[Sequence[Tuple[str, Tuple[int, int, int, int]]]] = None,
    puzzle_title: Optional[str] = None,
) -> str:
    """Render a solution page with highlighted placed words."""
    scale = 3
    page_w_hi = PAGE_W_PX * scale
    page_h_hi = PAGE_H_PX * scale

    safe_left_hi = SAFE_LEFT * scale
    safe_right_hi = SAFE_RIGHT * scale
    safe_bottom_hi = SAFE_BOTTOM * scale
    top_px_hi = TOP_PX * scale

    bg_path = background_path or BACKGROUND_PATH
    if bg_path and os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((page_w_hi, page_h_hi), Image.LANCZOS)
        if bg.mode == "RGBA":
            red, green, blue, alpha = bg.split()
            alpha = alpha.point(lambda value: int(value * 0.7))
            bg = Image.merge("RGBA", (red, green, blue, alpha))
        img = bg
    else:
        img = Image.new("RGBA", (page_w_hi, page_h_hi), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    panel_pad_x = int(30 * scale)
    panel_pad_top = int(40 * scale)
    panel_pad_bottom = int(40 * scale)

    panel_left = max(0, safe_left_hi - panel_pad_x)
    panel_top = max(0, top_px_hi - panel_pad_top)
    panel_right = min(page_w_hi, safe_right_hi + panel_pad_x)
    panel_bottom = min(page_h_hi, safe_bottom_hi + panel_pad_bottom)

    title_fact_area_hi = int(600 * scale)
    grid_top_base = panel_top + title_fact_area_hi

    rounded_rectangle(
        draw,
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=int(35 * scale),
        fill=(255, 255, 255, 150),
        outline=(0, 0, 0, 60),
        width=max(1, int(3 * scale)),
    )

    content_margin_x = int(40 * scale)
    content_left_hi = panel_left + content_margin_x
    content_right_hi = panel_right - content_margin_x

    font_title = load_font(FONT_TITLE, TITLE_FONT_SIZE * scale)
    text_color = (0, 0, 0, 255)
    highlight_fill = (243, 226, 200, 230)
    highlight_border = (0, 0, 0, 255)

    title_text = f"Solution – {idx}. {puzzle_title}" if puzzle_title else f"Solution {idx}"
    _draw_wrapped_centered_title(
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
        filename = os.path.join("output_puzzles_kdp", f"puzzle_{idx}_sol.png")

    return save_page(img, filename)
