"""
Renderizado de la portada interior del libro temático.

Esta página no es la cubierta de KDP, sino una title page interior que aparece
antes del índice para dar al PDF una estructura más editorial.
"""

from __future__ import annotations

from typing import Optional

from PIL import ImageDraw

from wordsearch.config.design import DEFAULT_THEME, ThemeConfig
from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_TITLE,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.config.layout import (
    PAGE_H_PX,
    PAGE_W_PX,
)
from wordsearch.config.paths import build_default_output_file
from wordsearch.rendering.common import (
    draw_centered_lines,
    load_font,
    rounded_rectangle,
    save_page,
    text_size,
    wrap_text,
)
from wordsearch.rendering.page_frame import create_page_canvas


def _draw_soft_panel(
    draw: ImageDraw.ImageDraw,
    scale: int,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
) -> None:
    """Draw a compact editorial panel, leaving visible textured background."""
    margin_x = int(135 * scale)
    margin_top = int(210 * scale)
    margin_bottom = int(760 * scale)
    radius = int(theme.panel_radius_px * 0.86 * scale)
    outline_width = max(1, int(theme.panel_border_width_px * 0.70 * scale))

    rounded_rectangle(
        draw,
        (
            margin_x,
            margin_top,
            PAGE_W_PX * scale - margin_x,
            PAGE_H_PX * scale - margin_bottom,
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
    """Draw a small centered separator used in the title page."""
    gap = int(18 * scale)
    dot_r = int(5 * scale)
    line_w = max(1, int(2 * scale))

    left_outer = center_x - width // 2
    left_inner = center_x - gap
    right_inner = center_x + gap
    right_outer = center_x + width // 2

    draw.line((left_outer, y, left_inner, y), fill=theme.panel_border, width=line_w)
    draw.line((right_inner, y, right_outer, y), fill=theme.panel_border, width=line_w)
    draw.ellipse(
        (center_x - dot_r, y - dot_r, center_x + dot_r, y + dot_r),
        fill=theme.title_color,
    )


def render_title_page(
    book_title: str,
    *,
    subtitle: str = "A themed collection of word search puzzles",
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
    theme: ThemeConfig = DEFAULT_THEME,
) -> str:
    """
    Renderiza una portada interior para el libro.

    Devuelve la ruta del PNG generado.
    """
    scale = 3
    width_hi = PAGE_W_PX * scale
    height_hi = PAGE_H_PX * scale

    img = create_page_canvas(background_path, scale, theme=theme)
    draw = ImageDraw.Draw(img)
    _draw_soft_panel(draw, scale, theme=theme)

    center_x = width_hi // 2
    max_width = int(width_hi * 0.70)

    # Título principal: se reduce si el título es largo.
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
    sep_w = int(width_hi * 0.38)
    _draw_ornamental_separator(draw, center_x, sep_y, sep_w, scale, theme=theme)

    subtitle_lines = wrap_text(draw, subtitle, subtitle_font, max_width)
    subtitle_y = sep_y + int(95 * scale)
    draw_centered_lines(
        draw,
        subtitle_lines,
        subtitle_font,
        center_x,
        subtitle_y,
        theme.body_color,
        line_spacing=1.18,
    )

    if filename is None:
        filename = build_default_output_file("00_title_page.png")

    return save_page(img, filename)
