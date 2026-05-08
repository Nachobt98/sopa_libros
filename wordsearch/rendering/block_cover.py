"""Block cover page renderer."""

from __future__ import annotations

from typing import Optional

from PIL import ImageDraw

from wordsearch.config.design import DEFAULT_LAYOUT, DEFAULT_THEME, LayoutConfig, ThemeConfig
from wordsearch.config.fonts import FONT_PATH, FONT_TITLE, title_font_size as TITLE_FONT_SIZE, wordlist_font_size as WORDLIST_FONT_SIZE
from wordsearch.config.paths import build_default_output_file
from wordsearch.rendering.common import load_font, rounded_rectangle, save_page, text_size, wrap_text
from wordsearch.rendering.page_frame import create_page_canvas


def _shadow_for(color: tuple[int, int, int, int], alpha: int = 85) -> tuple[int, int, int, int]:
    brightness = sum(color[:3]) / 3
    return (0, 0, 0, alpha) if brightness > 128 else (255, 255, 255, alpha)


def render_block_cover(
    block_name: str,
    block_index: int,
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
) -> str:
    """Generate a themed section cover page."""
    scale = 3
    page_w_hi = layout.page_width_px * scale
    page_h_hi = layout.page_height_px * scale

    img = create_page_canvas(background_path, scale, theme=theme, layout=layout)
    draw = ImageDraw.Draw(img)

    margin_x = int(page_w_hi * 0.10)
    max_text_width = page_w_hi - 2 * margin_x
    panel_left = int(page_w_hi * 0.075)
    panel_top = int(page_h_hi * 0.225)
    panel_right = page_w_hi - panel_left
    panel_bottom = int(page_h_hi * 0.60)

    rounded_rectangle(
        draw,
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=int(theme.panel_radius_px * scale),
        fill=theme.panel_fill,
        outline=theme.panel_border,
        width=max(1, int(theme.panel_border_width_px * scale)),
    )

    center_x = page_w_hi // 2
    title_y = int(page_h_hi * 0.35)
    subtitle_gap = int(40 * scale)
    main_color = theme.title_color
    body_color = theme.body_color
    shadow_color = _shadow_for(main_color)
    raw_title = block_name.strip() or f"Block {block_index}"

    base_size = int(TITLE_FONT_SIZE * 1.6) * scale
    min_size = int(TITLE_FONT_SIZE * 1.0) * scale
    font_size = base_size
    while font_size > min_size:
        font_title = load_font(FONT_TITLE, font_size)
        title_lines = wrap_text(draw, raw_title, font_title, max_text_width)
        widest = max((text_size(draw, line, font_title)[0] for line in title_lines), default=0)
        if widest <= max_text_width:
            break
        font_size = int(font_size * 0.9)

    font_title = load_font(FONT_TITLE, font_size)
    title_lines = wrap_text(draw, raw_title, font_title, max_text_width)
    line_height = int(font_size * 1.1)
    y = title_y - (len(title_lines) * line_height) // 2
    shadow_offset = int(3 * scale)

    for line in title_lines:
        width, height = text_size(draw, line, font_title)
        try:
            draw.text((center_x + shadow_offset, y + height / 2 + shadow_offset), line, font=font_title, fill=shadow_color, anchor="mm")
            draw.text((center_x, y + height / 2), line, font=font_title, fill=main_color, anchor="mm")
        except TypeError:
            x = center_x - width / 2
            draw.text((x + shadow_offset, y + shadow_offset), line, font=font_title, fill=shadow_color)
            draw.text((x, y), line, font=font_title, fill=main_color)
        y += line_height

    subtitle = "A themed collection of word search puzzles"
    font_sub_size = int(WORDLIST_FONT_SIZE * 1.3) * scale
    font_sub = load_font(FONT_PATH, font_sub_size)
    sub_w, sub_h = text_size(draw, subtitle, font_sub)
    while sub_w > max_text_width and font_sub_size > int(WORDLIST_FONT_SIZE * 0.9) * scale:
        font_sub_size = int(font_sub_size * 0.9)
        font_sub = load_font(FONT_PATH, font_sub_size)
        sub_w, sub_h = text_size(draw, subtitle, font_sub)

    subtitle_y = y + subtitle_gap
    subtitle_shadow = _shadow_for(body_color, alpha=70)
    try:
        draw.text((center_x + shadow_offset, subtitle_y + sub_h / 2 + shadow_offset), subtitle, font=font_sub, fill=subtitle_shadow, anchor="mm")
        draw.text((center_x, subtitle_y + sub_h / 2), subtitle, font=font_sub, fill=body_color, anchor="mm")
    except TypeError:
        sx = center_x - sub_w / 2
        draw.text((sx + shadow_offset, subtitle_y + shadow_offset), subtitle, font=font_sub, fill=subtitle_shadow)
        draw.text((sx, subtitle_y), subtitle, font=font_sub, fill=body_color)

    if filename is None:
        filename = build_default_output_file(f"block_{block_index}.png")

    return save_page(img, filename, output_width_px=layout.page_width_px, output_height_px=layout.page_height_px, dpi=layout.dpi)
