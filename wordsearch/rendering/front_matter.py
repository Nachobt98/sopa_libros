"""Renderizado de páginas preliminares del libro: índice e instrucciones."""

from __future__ import annotations

import os
from typing import Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

from wordsearch.config.design import DEFAULT_LAYOUT, DEFAULT_THEME, LayoutConfig, ThemeConfig
from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_PATH_BOLD,
    FONT_TITLE,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.config.paths import build_default_output_file, build_output_file
from wordsearch.rendering.backgrounds import BACKGROUND_PATH
from wordsearch.rendering.common import draw_centered_text, load_font, rounded_rectangle, save_page, text_size, wrap_text

TocEntry = Tuple[str, int, bool]
InstructionEntry = str | tuple[str, str]


def _format_visual_scale(layout: LayoutConfig = DEFAULT_LAYOUT) -> float:
    """Return a modest scale factor so larger trims do not look under-designed."""
    width_scale = layout.page_width_px / DEFAULT_LAYOUT.page_width_px
    height_scale = layout.page_height_px / DEFAULT_LAYOUT.page_height_px
    return min(1.16, max(1.0, min(width_scale, height_scale)))


def _make_background(
    background_path: Optional[str],
    scale: int,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
) -> Image.Image:
    width_hi = layout.page_width_px * scale
    height_hi = layout.page_height_px * scale
    bg_path = background_path or BACKGROUND_PATH

    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((width_hi, height_hi), Image.LANCZOS)
        r, g, b, a = img.split()
        a = a.point(lambda value: int(value * theme.background_opacity))
        return Image.merge("RGBA", (r, g, b, a))

    return Image.new("RGBA", (width_hi, height_hi), theme.page_background_fill)


def _draw_main_panel(
    draw: ImageDraw.ImageDraw,
    scale: int,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
) -> Tuple[int, int, int, int]:
    if layout == DEFAULT_LAYOUT:
        left = int(110 * scale)
        top = int(105 * scale)
        right = layout.page_width_px * scale - int(110 * scale)
        bottom = layout.page_height_px * scale - int(150 * scale)
    else:
        left = int(round(layout.page_width_px * scale * 0.061))
        top = int(round(layout.page_height_px * scale * 0.039))
        right = layout.page_width_px * scale - left
        bottom = layout.page_height_px * scale - int(round(layout.page_height_px * scale * 0.056))

    rounded_rectangle(
        draw,
        (left, top, right, bottom),
        radius=int(theme.panel_radius_px * 0.75 * scale),
        fill=theme.panel_fill,
        outline=theme.panel_border,
        width=max(1, int(theme.panel_border_width_px * 0.70 * scale)),
    )
    return left, top, right, bottom


def _draw_centered_rule(
    draw: ImageDraw.ImageDraw,
    *,
    center_x: int,
    y: int,
    width: int,
    scale: int,
    theme: ThemeConfig,
) -> int:
    """Draw a compact editorial separator and return the next y position."""
    rule_width = max(1, int(1.4 * scale))
    half = width // 2
    dot_radius = max(2, int(4 * scale))
    draw.line(
        (center_x - half, y, center_x - int(20 * scale), y),
        fill=theme.panel_border,
        width=rule_width,
    )
    draw.line(
        (center_x + int(20 * scale), y, center_x + half, y),
        fill=theme.panel_border,
        width=rule_width,
    )
    rounded_rectangle(
        draw,
        (center_x - dot_radius, y - dot_radius, center_x + dot_radius, y + dot_radius),
        radius=dot_radius,
        fill=theme.title_color,
        outline=None,
        width=0,
    )
    return y + int(34 * scale)


def _draw_centered_text_in_box(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    *,
    center_x: float,
    center_y: float,
    fill,
) -> None:
    """Draw text centered on its optical box, with a fallback for old Pillow versions."""
    try:
        draw.text((center_x, center_y), text, font=font, fill=fill, anchor="mm")
    except TypeError:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text((center_x - text_w / 2 - bbox[0], center_y - text_h / 2 - bbox[1]), text, font=font, fill=fill)


def _draw_small_caps_label(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    *,
    center_x: int,
    y: int,
    scale: int,
    theme: ThemeConfig,
) -> int:
    """Draw a subtle centered label inside a thin rounded chip."""
    label_w, label_h = text_size(draw, text, font)
    pad_x = int(18 * scale)
    pad_y = int(10 * scale)
    box = (
        center_x - label_w // 2 - pad_x,
        y,
        center_x + label_w // 2 + pad_x,
        y + label_h + 2 * pad_y,
    )
    rounded_rectangle(
        draw,
        box,
        radius=(box[3] - box[1]) // 2,
        fill=theme.pill_fill,
        outline=theme.pill_border,
        width=max(1, int(theme.pill_border_width_px * 0.65 * scale)),
    )
    _draw_centered_text_in_box(
        draw,
        text,
        font,
        center_x=center_x,
        center_y=(box[1] + box[3]) / 2,
        fill=theme.pill_text,
    )
    return box[3]


def _draw_instruction_card(
    draw: ImageDraw.ImageDraw,
    *,
    number_text: str,
    title: str,
    body: str,
    number_font: ImageFont.FreeTypeFont,
    title_font: ImageFont.FreeTypeFont,
    body_font: ImageFont.FreeTypeFont,
    left: int,
    top: int,
    right: int,
    card_height: int,
    scale: int,
    theme: ThemeConfig,
) -> int:
    """Draw one instruction as an editorial card with a numbered badge."""
    rounded_rectangle(
        draw,
        (left, top, right, top + card_height),
        radius=int(theme.fact_card_radius_px * 0.72 * scale),
        fill=theme.fact_card_fill,
        outline=theme.fact_card_border,
        width=max(1, int(theme.fact_card_border_width_px * 0.65 * scale)),
    )

    badge_size = int(58 * scale)
    badge_left = left + int(26 * scale)
    badge_top = top + (card_height - badge_size) // 2
    rounded_rectangle(
        draw,
        (badge_left, badge_top, badge_left + badge_size, badge_top + badge_size),
        radius=badge_size // 2,
        fill=theme.fact_header_fill,
        outline=None,
        width=0,
    )
    _draw_centered_text_in_box(
        draw,
        number_text,
        number_font,
        center_x=badge_left + badge_size / 2,
        center_y=badge_top + badge_size / 2,
        fill=theme.fact_header_text,
    )

    text_left = badge_left + badge_size + int(30 * scale)
    title_y = top + int(24 * scale)
    draw.text((text_left, title_y), title, font=title_font, fill=theme.title_color)

    body_y = title_y + text_size(draw, title, title_font)[1] + int(11 * scale)
    max_width = right - text_left - int(30 * scale)
    line_h = int(body_font.size * 1.13)
    for line in wrap_text(draw, body, body_font, max_width):
        draw.text((text_left, body_y), line, font=body_font, fill=theme.body_color)
        body_y += line_h

    return top + card_height


def render_table_of_contents(
    toc_entries: Sequence[TocEntry],
    output_dir: str,
    background_path: Optional[str] = None,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
) -> list[str]:
    """Renderiza un índice editorial con jerarquía visual y dot leaders."""
    scale = 3
    visual_scale = _format_visual_scale(layout)
    img = _make_background(background_path, scale, theme=theme, layout=layout)
    draw = ImageDraw.Draw(img)
    panel_left, panel_top, panel_right, panel_bottom = _draw_main_panel(draw, scale, theme=theme, layout=layout)

    center_x = layout.page_width_px * scale // 2
    title_font = load_font(FONT_TITLE, int(TITLE_FONT_SIZE * 1.02 * visual_scale) * scale)
    subtitle_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.52 * visual_scale) * scale)
    chip_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.40 * visual_scale) * scale)
    section_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.64 * visual_scale) * scale)
    entry_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.70 * visual_scale) * scale)
    page_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.70 * visual_scale) * scale)

    y = panel_top + int(78 * scale)
    y = draw_centered_text(draw, "Contents", title_font, center_x, y, theme.title_color)
    y += int(70 * scale)
    y = draw_centered_text(draw, "A guided path through every puzzle section", subtitle_font, center_x, y, theme.body_color)
    y += int(58 * scale)
    y = _draw_centered_rule(
        draw,
        center_x=center_x,
        y=y,
        width=int((panel_right - panel_left) * 0.46),
        scale=scale,
        theme=theme,
    )
    y += int(24 * scale)
    y = _draw_small_caps_label(draw, "BOOK MAP", chip_font, center_x=center_x, y=y, scale=scale, theme=theme)

    content_left = panel_left + int(74 * scale)
    content_right = panel_right - int(74 * scale)
    y += int(90 * scale)
    row_gap = int(44 * scale)

    section_entries = [entry for entry in toc_entries if not (entry[0].lower() == "solutions")]
    solution_entries = [entry for entry in toc_entries if entry[0].lower() == "solutions"]

    def draw_group_heading(label: str, current_y: int) -> int:
        draw.text((content_left, current_y), label, font=section_font, fill=theme.title_color)
        label_w, label_h = text_size(draw, label, section_font)
        rule_y = current_y + label_h // 2
        draw.line(
            (content_left + label_w + int(20 * scale), rule_y, content_right, rule_y),
            fill=theme.panel_border,
            width=max(1, int(scale)),
        )
        return current_y + label_h + int(34 * scale)

    y = draw_group_heading("PUZZLE SECTIONS", y)

    max_row_bottom = panel_bottom - int(190 * scale)
    for label, page_number, _is_section in section_entries:
        if y > max_row_bottom:
            break

        label_width, label_height = text_size(draw, label, entry_font)
        page_text = str(page_number)
        page_width, page_height = text_size(draw, page_text, page_font)
        page_x = content_right - page_width

        draw.text((content_left, y), label, font=entry_font, fill=theme.body_color)
        draw.text((page_x, y), page_text, font=page_font, fill=theme.body_color)

        dot_start = content_left + label_width + int(18 * scale)
        dot_end = page_x - int(18 * scale)
        dot_y = y + label_height // 2 + int(2 * scale)
        if dot_end > dot_start:
            dash_w = int(8 * scale)
            gap_w = int(10 * scale)
            x = dot_start
            while x < dot_end:
                draw.line((x, dot_y, min(x + dash_w, dot_end), dot_y), fill=theme.panel_border, width=max(1, int(scale)))
                x += dash_w + gap_w

        y += max(label_height, page_height) + row_gap

    if solution_entries:
        y += int(38 * scale)
        y = draw_group_heading("REFERENCE", y)
        for label, page_number, _is_section in solution_entries:
            label_width, label_height = text_size(draw, label, entry_font)
            page_text = str(page_number)
            page_width, page_height = text_size(draw, page_text, page_font)
            page_x = content_right - page_width
            draw.text((content_left, y), label, font=entry_font, fill=theme.body_color)
            draw.text((page_x, y), page_text, font=page_font, fill=theme.body_color)
            dot_start = content_left + label_width + int(18 * scale)
            dot_end = page_x - int(18 * scale)
            dot_y = y + label_height // 2 + int(2 * scale)
            if dot_end > dot_start:
                draw.line((dot_start, dot_y, dot_end, dot_y), fill=theme.panel_border, width=max(1, int(scale)))
            y += max(label_height, page_height) + row_gap

    filename = build_output_file(output_dir, "01_table_of_contents.png")
    return [save_page(img, filename, output_width_px=layout.page_width_px, output_height_px=layout.page_height_px, dpi=layout.dpi)]


def _split_instruction_entry(instruction: InstructionEntry) -> tuple[str, str]:
    if isinstance(instruction, tuple):
        return instruction
    return "", instruction


def _measure_instruction_block_height(
    draw: ImageDraw.ImageDraw,
    instructions: Sequence[InstructionEntry],
    title_font: ImageFont.FreeTypeFont,
    body_font: ImageFont.FreeTypeFont,
    max_text_width: int,
    card_height: int = 0,
    row_gap: int = 0,
) -> int:
    """Measure instruction content while accepting legacy string-only entries."""
    total_height = 0
    line_h = int(body_font.size * 1.13)
    for instruction_entry in instructions:
        title, instruction = _split_instruction_entry(instruction_entry)
        title_h = text_size(draw, title, title_font)[1] if title else 0
        title_gap = 10 * 3 if title else 0
        line_count = len(wrap_text(draw, instruction, body_font, max_text_width))
        required_height = 26 * 3 + title_h + title_gap + line_count * line_h + 22 * 3
        total_height += max(card_height, required_height) + row_gap
    return max(0, total_height - row_gap)


def render_instructions_page(
    book_title: str,
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
) -> str:
    """Renderiza una página de instrucciones con tarjetas compactas y jerarquía editorial."""
    scale = 3
    visual_scale = _format_visual_scale(layout)
    img = _make_background(background_path, scale, theme=theme, layout=layout)
    draw = ImageDraw.Draw(img)
    panel_left, panel_top, panel_right, panel_bottom = _draw_main_panel(draw, scale, theme=theme, layout=layout)

    center_x = layout.page_width_px * scale // 2
    title_font = load_font(FONT_TITLE, int(TITLE_FONT_SIZE * 0.96 * visual_scale) * scale)
    subtitle_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.52 * visual_scale) * scale)
    chip_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.40 * visual_scale) * scale)
    number_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.66 * visual_scale) * scale)
    card_title_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.50 * visual_scale) * scale)
    body_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.47 * visual_scale) * scale)

    y = panel_top + int(78 * scale)
    y = draw_centered_text(draw, "How to Use This Book", title_font, center_x, y, theme.title_color)
    y += int(70 * scale)
    y = draw_centered_text(draw, "Find the words, enjoy the facts, check the answers when needed.", subtitle_font, center_x, y, theme.body_color)
    y += int(58 * scale)
    y = _draw_centered_rule(
        draw,
        center_x=center_x,
        y=y,
        width=int((panel_right - panel_left) * 0.42),
        scale=scale,
        theme=theme,
    )
    y += int(18 * scale)
    y = _draw_small_caps_label(draw, "PLAY GUIDE", chip_font, center_x=center_x, y=y, scale=scale, theme=theme)

    instructions = [
        ("Scan the word bank", "Start with the list at the bottom of each puzzle page."),
        ("Search every direction", "Words can run horizontally, vertically or diagonally depending on the difficulty."),
        ("Mark each discovery", "Circle or highlight every word as you find it in the letter grid."),
        ("Read the fun fact", "Each puzzle includes a short themed note to make the page more memorable."),
        ("Use solutions wisely", "If you get stuck, check the solutions section at the back of the book."),
    ]

    content_left = panel_left + int(64 * scale)
    content_right = panel_right - int(64 * scale)
    badge_reserved = int(58 * scale) + int(30 * scale) + int(56 * scale)
    max_text_width = content_right - content_left - badge_reserved
    card_height = int(140 * visual_scale * scale)
    row_gap = int(24 * visual_scale * scale)
    block_height = _measure_instruction_block_height(
        draw,
        instructions,
        card_title_font,
        body_font,
        max_text_width,
        card_height,
        row_gap,
    )

    min_content_y = y + int(70 * scale)
    available_bottom = panel_bottom - int(118 * scale)
    centered_y = min_content_y + max(0, (available_bottom - min_content_y - block_height) // 2)
    y = min(centered_y, min_content_y + int(135 * scale))

    for idx, (title, instruction) in enumerate(instructions, start=1):
        y = _draw_instruction_card(
            draw,
            number_text=str(idx),
            title=title,
            body=instruction,
            number_font=number_font,
            title_font=card_title_font,
            body_font=body_font,
            left=content_left,
            top=y,
            right=content_right,
            card_height=card_height,
            scale=scale,
            theme=theme,
        )
        y += row_gap

    note_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.40 * visual_scale) * scale)
    note = f"{book_title} · Solutions are placed at the end for easy checking."
    note_w, _note_h = text_size(draw, note, note_font)
    note_y = min(panel_bottom - int(70 * scale), max(y + int(22 * scale), panel_bottom - int(78 * scale)))
    draw.text((center_x - note_w // 2, note_y), note, font=note_font, fill=theme.body_color)

    if filename is None:
        filename = build_default_output_file("02_instructions.png")

    return save_page(img, filename, output_width_px=layout.page_width_px, output_height_px=layout.page_height_px, dpi=layout.dpi)
