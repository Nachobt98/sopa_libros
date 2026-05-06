"""Letter grid rendering helpers."""

from __future__ import annotations

from typing import Sequence

from PIL import Image, ImageDraw

from wordsearch.config.fonts import FONT_PATH, FONT_PATH_BOLD
from wordsearch.domain.grid import PlacedWord
from wordsearch.rendering.common import load_font, text_size
from wordsearch.rendering.highlights import build_solution_highlight_layer


def draw_letter_grid(
    *,
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    grid: Sequence[Sequence[str]],
    placed_words: Sequence[PlacedWord] | None,
    is_solution: bool,
    grid_left_hi: int,
    grid_top_hi: int,
    cell_size_hi: int,
    scale: int,
    page_w_hi: int,
    page_h_hi: int,
    highlight_fill: tuple[int, int, int, int],
    highlight_border: tuple[int, int, int, int],
) -> int:
    """Draw the letter grid and return its bottom y coordinate."""
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    grid_w_hi = cell_size_hi * cols
    grid_h_hi = cell_size_hi * rows

    letter_font_size_hi = max(int(cell_size_hi * 0.70), int(18 * scale))
    font_letter = load_font(FONT_PATH, letter_font_size_hi)
    font_letter_bold = load_font(FONT_PATH_BOLD, letter_font_size_hi)

    grid_line_width_hi = max(1, int(1.2 * scale))
    grid_line_color = "#444444"

    highlight_layer = build_solution_highlight_layer(
        placed_words=placed_words if is_solution else None,
        rows=rows,
        cols=cols,
        grid_left_hi=grid_left_hi,
        grid_top_hi=grid_top_hi,
        cell_size_hi=cell_size_hi,
        page_w_hi=page_w_hi,
        page_h_hi=page_h_hi,
        scale=scale,
        highlight_fill=highlight_fill,
        highlight_border=highlight_border,
    )

    for row in range(rows + 1):
        y = grid_top_hi + row * cell_size_hi
        draw.line(
            (grid_left_hi, y, grid_left_hi + grid_w_hi, y),
            fill=grid_line_color,
            width=grid_line_width_hi,
        )
    for col in range(cols + 1):
        x = grid_left_hi + col * cell_size_hi
        draw.line(
            (x, grid_top_hi, x, grid_top_hi + grid_h_hi),
            fill=grid_line_color,
            width=grid_line_width_hi,
        )

    for row in range(rows):
        for col in range(cols):
            _draw_centered_letter(
                draw=draw,
                letter=grid[row][col],
                font=font_letter,
                center_x=grid_left_hi + col * cell_size_hi + cell_size_hi / 2,
                center_y=grid_top_hi + row * cell_size_hi + cell_size_hi / 2,
            )

    img.alpha_composite(highlight_layer.overlay)
    if is_solution and highlight_layer.positions:
        for row, col in highlight_layer.positions:
            _draw_centered_letter(
                draw=draw,
                letter=grid[row][col],
                font=font_letter_bold,
                center_x=grid_left_hi + col * cell_size_hi + cell_size_hi / 2,
                center_y=grid_top_hi + row * cell_size_hi + cell_size_hi / 2,
            )

    return grid_top_hi + grid_h_hi


def _draw_centered_letter(
    *,
    draw: ImageDraw.ImageDraw,
    letter: str,
    font,
    center_x: float,
    center_y: float,
) -> None:
    try:
        draw.text(
            (center_x, center_y),
            letter,
            fill="black",
            font=font,
            anchor="mm",
        )
    except TypeError:
        letter_w, letter_h = text_size(draw, letter, font)
        draw.text(
            (center_x - letter_w / 2, center_y - letter_h / 2),
            letter,
            fill="black",
            font=font,
        )
