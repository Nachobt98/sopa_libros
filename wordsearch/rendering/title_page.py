"""Renderizado de la portada interior del libro temático."""

from __future__ import annotations

from typing import Optional

from PIL import ImageDraw

from wordsearch.config.design import DEFAULT_LAYOUT, DEFAULT_THEME, LayoutConfig, ThemeConfig
from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_TITLE,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.config.paths import build_default_output_file
from wordsearch.rendering.common import draw_centered_lines, load_font, rounded_rectangle, save_page, text_size, wrap_text
from wordsearch.rendering.page_frame import create_page_canvas


def _draw_soft_panel(
    draw: ImageDraw.ImageDraw,
    scale: int,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
) -> None:
    margin_x = int(layout.page_width_px * scale * 0.075)
    margin_top = int(layout.page_height_px * scale * 0.078)
    margin_bottom = int(layout.page_height_px * scale * 0.282)
    radius = int(theme.panel_radius_px * 0.86 * scale)
    outline_width = max(1, int(theme.panel_border_width_px * 0.70 * scale))

    rounded_rectangle(
        draw,
        (
            margin_x,
            margin_top,
            layout.page_width_px * scale - margin_x,
            layout.page_height_px * scale - margin_bottom,
        ),
        radius=radius,
        fill=theme.panel_fill,
        outline=theme.panel_border,
        width=outline_width,
    )


def _draw_ornamental_separator(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    y: int,
    width: int,
    scale: int,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
) -> None:
    gap = int(18 * scale)
    dot_r = int(5 * scale)
    line_w = max(1, int(2 * scale))
    draw.line((center_x - width // 2, y, center_x - gap, y), fill=theme.panel_border, width=line_w)
    draw.line((center_x + gap, y, center_x + width // 2, y), fill=theme.panel_border, width=line_w)
    draw.ellipse((center_x - dot_r, y - dot_r, center_x + dot_r, y + dot_r), fill=theme.title_color)


def render_title_page(
    book_title: str,
    *,
    subtitle: str = "A themed collection of word search puzzles",
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
) -> str:
    """Renderiza una portada interior para el libro."""
    scale = 3
    width_hi = layout.page_width_px * scale
    height_hi = layout.page_height_px * scale

    img = create_page_canvas(background_path, scale, theme=theme, layout=layout)
    draw = ImageDraw.Draw(img)
    _draw_soft_panel(draw, scale, theme=theme, layout=layout)

    center_x = width_hi // 2
    max_width = int(width_hi * 0.70)
    title_size = int(TITLE_FONT_SIZE * 1.70) * scale
    min_title_size = int(TITLE_FONT_SIZE * 0.98) * scale
    title = book_title.strip() or "Word Search Book"

    while title_size > min_title_size:
        title_font = load_font(FONT_TITLE, title_size)
        title_lines = wrap_text(draw, title, title_font, max_width)
        widest = max((text_size(draw, line, title_font)[0] for line in title_lines), default=0)
        if widest <= max_width and len(title_lines) <= 4:
            break
        title_size = int(title_size * 0.90)

    title_font = load_font(FONT_TITLE, title_size)
    title_lines = wrap_text(draw, title, title_font, max_width)
    subtitle_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 1.03) * scale)

    title_block_height = sum(text_size(draw, line, title_font)[1] for line in title_lines)
    title_block_height += int(title_size * 0.12) * max(0, len(title_lines) - 1)
    title_start_y = int(height_hi * 0.265) - title_block_height // 2
    shadow = tuple(max(0, min(255, channel - 40)) for channel in theme.panel_border[:3]) + (65,)

    y = draw_centered_lines(
        draw,
        title_lines,
        title_font,
        center_x,
        title_start_y,
        theme.title_color,
        line_spacing=1.07,
        shadow_fill=shadow,
        shadow_offset=int(2 * scale),
    )

    sep_y = y + int(120 * scale)
    _draw_ornamental_separator(draw, center_x, sep_y, int(width_hi * 0.38), scale, theme=theme)

    subtitle_lines = wrap_text(draw, subtitle, subtitle_font, max_width)
    draw_centered_lines(
        draw,
        subtitle_lines,
        subtitle_font,
        center_x,
        sep_y + int(95 * scale),
        theme.body_color,
        line_spacing=1.18,
    )

    if filename is None:
        filename = build_default_output_file("00_title_page.png")

    return save_page(img, filename, output_width_px=layout.page_width_px, output_height_px=layout.page_height_px, dpi=layout.dpi)
