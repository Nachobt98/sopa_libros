"""
Renderizado de páginas preliminares del libro: índice e instrucciones.

Se mantiene separado de image_rendering.py para evitar seguir creciendo un
módulo que ya contiene el render principal de puzzles y soluciones.
"""

from __future__ import annotations

import os
from typing import Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

from wordsearch.constants_and_layout import (
    FONT_PATH,
    FONT_PATH_BOLD,
    FONT_TITLE,
    PAGE_H_PX,
    PAGE_W_PX,
    wordlist_font_size as WORDLIST_FONT_SIZE,
    title_font_size as TITLE_FONT_SIZE,
)
from wordsearch.rendering.backgrounds import BACKGROUND_PATH
from wordsearch.rendering.common import (
    draw_centered_text,
    load_font,
    rounded_rectangle,
    save_page,
    text_size,
    wrap_text,
)


TocEntry = Tuple[str, int, bool]


def _make_background(background_path: Optional[str], scale: int) -> Image.Image:
    width_hi = PAGE_W_PX * scale
    height_hi = PAGE_H_PX * scale
    bg_path = background_path or BACKGROUND_PATH

    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((width_hi, height_hi), Image.LANCZOS)
        r, g, b, a = img.split()
        a = a.point(lambda value: int(value * 0.72))
        return Image.merge("RGBA", (r, g, b, a))

    return Image.new("RGBA", (width_hi, height_hi), (255, 255, 255, 255))


def _draw_main_panel(draw: ImageDraw.ImageDraw, scale: int) -> Tuple[int, int, int, int]:
    left = int(110 * scale)
    top = int(105 * scale)
    right = PAGE_W_PX * scale - int(110 * scale)
    bottom = PAGE_H_PX * scale - int(150 * scale)

    rounded_rectangle(
        draw,
        (left, top, right, bottom),
        radius=int(26 * scale),
        fill=(255, 255, 255, 150),
        outline=(0, 0, 0, 55),
        width=max(1, int(2 * scale)),
    )
    return left, top, right, bottom


def render_table_of_contents(
    toc_entries: Sequence[TocEntry],
    output_dir: str,
    background_path: Optional[str] = None,
) -> list[str]:
    """
    Renderiza un índice editorial con más aire vertical.

    Mantiene la firma histórica para que main_thematic.py no tenga que conocer
    detalles de renderizado.
    """
    scale = 3
    img = _make_background(background_path, scale)
    draw = ImageDraw.Draw(img)
    panel_left, panel_top, panel_right, _panel_bottom = _draw_main_panel(draw, scale)

    center_x = PAGE_W_PX * scale // 2
    title_font = load_font(FONT_TITLE, int(TITLE_FONT_SIZE * 1.15) * scale)
    section_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.74) * scale)
    entry_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.78) * scale)
    page_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.78) * scale)

    y = panel_top + int(96 * scale)
    y = draw_centered_text(draw, "Table of Contents", title_font, center_x, y, (0, 0, 0, 255))

    y += int(54 * scale)
    y = draw_centered_text(draw, "SECTIONS", section_font, center_x, y, (0, 0, 0, 190))

    line_y = y + int(44 * scale)
    line_width = int((panel_right - panel_left) * 0.46)
    draw.line(
        (center_x - line_width // 2, line_y, center_x + line_width // 2, line_y),
        fill=(0, 0, 0, 95),
        width=max(1, int(1.5 * scale)),
    )

    y = line_y + int(110 * scale)
    content_left = panel_left + int(70 * scale)
    content_right = panel_right - int(70 * scale)
    row_gap = int(78 * scale)

    for idx, (label, page_number, _is_section) in enumerate(toc_entries):
        is_solutions = idx == len(toc_entries) - 1 and label.lower() == "solutions"
        if is_solutions:
            y += int(70 * scale)
            draw.line(
                (content_left, y, content_right, y),
                fill=(0, 0, 0, 75),
                width=max(1, int(1 * scale)),
            )
            y += int(72 * scale)

        label_width, label_height = text_size(draw, label, entry_font)
        page_text = str(page_number)
        page_width, page_height = text_size(draw, page_text, page_font)

        page_x = content_right - page_width
        label_x = content_left
        baseline_y = y

        draw.text((label_x, baseline_y), label, font=entry_font, fill=(0, 0, 0, 235))
        draw.text((page_x, baseline_y), page_text, font=page_font, fill=(0, 0, 0, 235))

        dot_start = label_x + label_width + int(18 * scale)
        dot_end = page_x - int(18 * scale)
        dot_y = baseline_y + label_height // 2 + int(2 * scale)
        if dot_end > dot_start:
            dash_w = int(9 * scale)
            gap_w = int(9 * scale)
            x = dot_start
            while x < dot_end:
                draw.line(
                    (x, dot_y, min(x + dash_w, dot_end), dot_y),
                    fill=(0, 0, 0, 70),
                    width=max(1, int(1 * scale)),
                )
                x += dash_w + gap_w

        y += max(label_height, page_height) + row_gap

    filename = os.path.join(output_dir, "01_table_of_contents.png")
    return [save_page(img, filename)]


def _measure_instruction_block_height(
    draw: ImageDraw.ImageDraw,
    instructions: Sequence[str],
    number_font: ImageFont.FreeTypeFont,
    body_font: ImageFont.FreeTypeFont,
    max_text_width: int,
    row_gap: int,
) -> int:
    line_h = int(body_font.size * 1.18)
    total_height = 0

    for instruction in instructions:
        lines = wrap_text(draw, instruction, body_font, max_text_width)
        number_h = text_size(draw, "1.", number_font)[1]
        text_h = len(lines) * line_h
        total_height += max(number_h, text_h) + row_gap

    return max(0, total_height - row_gap)


def render_instructions_page(
    book_title: str,
    filename: Optional[str] = None,
    background_path: Optional[str] = None,
) -> str:
    """
    Renderiza una página de instrucciones limpia y genérica.
    """
    scale = 3
    img = _make_background(background_path, scale)
    draw = ImageDraw.Draw(img)
    panel_left, panel_top, panel_right, panel_bottom = _draw_main_panel(draw, scale)

    center_x = PAGE_W_PX * scale // 2
    title_font = load_font(FONT_TITLE, int(TITLE_FONT_SIZE * 1.05) * scale)
    subtitle_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.9) * scale)
    number_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.72) * scale)
    body_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.70) * scale)

    title_y = panel_top + int(78 * scale)
    title_bottom = draw_centered_text(draw, "Instructions", title_font, center_x, title_y, (0, 0, 0, 255))

    subtitle_y = title_bottom + int(46 * scale)
    subtitle_bottom = draw_centered_text(
        draw,
        "How to enjoy this book",
        subtitle_font,
        center_x,
        subtitle_y,
        (0, 0, 0, 220),
    )

    instructions = [
        "Find each word from the list at the bottom of the puzzle page.",
        "Words may appear horizontally, vertically or diagonally.",
        "Depending on the difficulty, some words may also appear backwards.",
        "Circle or highlight each word as you find it in the grid.",
        "Use the fun facts to learn something new as you play.",
        "Check the solutions section at the back of the book if you get stuck.",
    ]

    content_left = panel_left + int(82 * scale)
    content_right = panel_right - int(82 * scale)
    number_col_width = int(74 * scale)
    number_text_gap = int(18 * scale)
    text_left = content_left + number_col_width + number_text_gap
    max_text_width = content_right - text_left
    row_gap = int(42 * scale)

    block_height = _measure_instruction_block_height(
        draw,
        instructions,
        number_font,
        body_font,
        max_text_width,
        row_gap,
    )

    min_content_y = subtitle_bottom + int(115 * scale)
    available_center_y = (subtitle_bottom + int(160 * scale) + panel_bottom - int(100 * scale)) // 2
    y = max(min_content_y, available_center_y - block_height // 2)

    for idx, instruction in enumerate(instructions, start=1):
        number_text = f"{idx}."
        num_w, _num_h = text_size(draw, number_text, number_font)
        draw.text(
            (content_left + number_col_width - num_w, y),
            number_text,
            font=number_font,
            fill=(0, 0, 0, 235),
        )

        lines = wrap_text(draw, instruction, body_font, max_text_width)
        text_y = y
        line_h = int(body_font.size * 1.18)
        for line in lines:
            draw.text((text_left, text_y), line, font=body_font, fill=(0, 0, 0, 235))
            text_y += line_h

        number_h = text_size(draw, number_text, number_font)[1]
        y = max(y + number_h, text_y) + row_gap

    if filename is None:
        filename = os.path.join("output_puzzles_kdp", "02_instructions.png")

    return save_page(img, filename)
