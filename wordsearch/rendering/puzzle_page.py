"""
Puzzle and solution page renderer.

This module contains the main word-search page renderer previously hosted in
`wordsearch.image_rendering`.
"""

from __future__ import annotations

import os
from typing import Iterable, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

from wordsearch.constants_and_layout import (
    FONT_PATH,
    FONT_PATH_BOLD,
    FONT_TITLE,
    PAGE_H_PX,
    PAGE_W_PX,
    SAFE_BOTTOM,
    SAFE_LEFT,
    SAFE_RIGHT,
    TOP_PX,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.rendering.backgrounds import BACKGROUND_PATH
from wordsearch.rendering.common import (
    load_font,
    rounded_rectangle,
    save_page,
    text_size,
    wrap_text,
)
from wordsearch.rendering.highlights import build_solution_highlight_layer
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
    """
    Dibuja el título centrado con word-wrap si es muy largo.
    Devuelve la coordenada y justo debajo del bloque de título.
    """
    lines = wrap_text(draw, text, font, max_width)
    y = start_y
    container_width = max(0, area_right - area_left)
    for line in lines:
        width, height = text_size(draw, line, font)
        x = area_left + max(0, (container_width - width) // 2)
        draw.text((x, y), line, font=font, fill=(0, 0, 0, 255))
        y += int(height * line_spacing)
    return y


def render_page(
    grid: Sequence[Sequence[str]],
    words: Iterable[str],
    idx: int,
    is_solution: bool = False,
    solution_positions=None,  # compatibilidad con código viejo
    background_path: Optional[str] = None,
    filename: Optional[str] = None,
    placed_words: Optional[Sequence[Tuple[str, Tuple[int, int, int, int]]]] = None,
    puzzle_title: Optional[str] = None,
    fun_fact: Optional[str] = None,
    solution_page_number: Optional[int] = None,
) -> str:
    """Renderiza una página de puzzle o solución."""
    scale = 3
    page_w_hi = PAGE_W_PX * scale
    page_h_hi = PAGE_H_PX * scale

    safe_left_hi = SAFE_LEFT * scale
    safe_right_hi = SAFE_RIGHT * scale
    safe_bottom_hi = SAFE_BOTTOM * scale
    top_px_hi = TOP_PX * scale

    # --- Fondo de página (PNG opcional) ---
    bg_path = background_path or BACKGROUND_PATH

    if bg_path and os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((page_w_hi, page_h_hi), Image.LANCZOS)

        if bg.mode == "RGBA":
            r, g, b, a = bg.split()
            a = a.point(lambda value: int(value * 0.7))  # 70% opacidad
            bg = Image.merge("RGBA", (r, g, b, a))

        img = bg
    else:
        img = Image.new("RGBA", (page_w_hi, page_h_hi), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)

    # === PANEL BLANCO PRINCIPAL PARA TODO EL CONTENIDO ===
    panel_pad_x = int(30 * scale)
    panel_pad_top = int(40 * scale)
    panel_pad_bottom = int(40 * scale)

    panel_left = safe_left_hi - panel_pad_x
    panel_right = safe_right_hi + panel_pad_x
    panel_top = top_px_hi - panel_pad_top
    panel_bottom = safe_bottom_hi + panel_pad_bottom

    # Altura máxima permitida para título + FUN FACT
    title_fact_area_hi = int(600 * scale)
    grid_top_base = panel_top + title_fact_area_hi

    panel_left = max(0, panel_left)
    panel_top = max(0, panel_top)
    panel_right = min(page_w_hi, panel_right)
    panel_bottom = min(page_h_hi, panel_bottom)

    rounded_rectangle(
        draw,
        (panel_left, panel_top, panel_right, panel_bottom),
        radius=int(35 * scale),
        fill=(255, 255, 255, 150),
        outline=(0, 0, 0, 60),
        width=max(1, int(3 * scale)),
    )

    # Área común de contenido dentro del panel
    content_margin_x = int(40 * scale)
    content_left_hi = panel_left + content_margin_x
    content_right_hi = panel_right - content_margin_x
    min_gap_hi = int(30 * scale)

    # Fuentes
    font_title = load_font(FONT_TITLE, TITLE_FONT_SIZE * scale)

    text_color = (0, 0, 0, 255)

    # FUN FACT
    fact_bg = (245, 245, 245, 245)
    fact_border = (170, 170, 170, 255)
    fact_header_bg = (30, 30, 30, 255)
    fact_header_text = (255, 255, 255, 255)

    pill_bg = (230, 230, 230, 255)
    pill_border = (120, 120, 120, 255)

    # Resaltado soluciones
    highlight_fill = (243, 226, 200, 230)  # beige
    highlight_border = (0, 0, 0, 255)  # borde oscuro

    # --------------------------------------------------------
    # TÍTULO (con wrap)
    # --------------------------------------------------------
    if puzzle_title:
        if is_solution:
            title_text = f"Solution – {idx}. {puzzle_title}"
        else:
            title_text = f"{idx}. {puzzle_title}"
    else:
        title_text = f"Solution {idx}" if is_solution else f"Puzzle {idx}"

    title_max_width = int(content_right_hi - content_left_hi)
    y_after_title = _draw_wrapped_centered_title(
        draw,
        title_text,
        font_title,
        max_width=title_max_width,
        start_y=panel_top + int(25 * scale),
        area_left=content_left_hi,
        area_right=content_right_hi,
        line_spacing=1.05,
    )

    # Más separación título → fact
    y_cursor_hi = y_after_title + int(80 * scale)

    # --------------------------------------------------------
    # FUN FACT – tarjeta con cabecera
    # --------------------------------------------------------
    if (not is_solution) and fun_fact:
        fact_label_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.9) * scale)
        fact_text_font_size_hi = int(WORDLIST_FONT_SIZE * 0.5) * scale

        left_hi = content_left_hi
        right_hi = content_right_hi

        inner_horizontal_pad = int(18 * scale)
        max_text_width_hi = int((right_hi - left_hi) - 2 * inner_horizontal_pad)

        fact_label = "FUN FACT"
        label_w, label_h = text_size(draw, fact_label, fact_label_font)

        header_pad_v_hi = int(8 * scale)
        text_pad_v_hi = int(10 * scale)
        header_height_hi = label_h + 2 * header_pad_v_hi

        fact_text_font = load_font(FONT_PATH, fact_text_font_size_hi)
        line_height_hi = int(fact_text_font.size * 1.10)

        min_fact_block_hi = header_height_hi + 2 * text_pad_v_hi + line_height_hi
        max_fact_height_hi = max(min_fact_block_hi, grid_top_base - y_cursor_hi - min_gap_hi)

        fact_lines = wrap_text(draw, fun_fact, fact_text_font, max_text_width_hi)

        available_text_h = max(0, max_fact_height_hi - header_height_hi - 2 * text_pad_v_hi)
        max_lines_fit = max(1, available_text_h // line_height_hi)
        if len(fact_lines) > max_lines_fit:
            fact_lines = fact_lines[:max_lines_fit]
            last_line = fact_lines[-1] if fact_lines else ""
            ellipsis = "..."
            while last_line and text_size(draw, last_line + ellipsis, fact_text_font)[0] > max_text_width_hi:
                last_line = last_line[:-1].rstrip()
            if last_line:
                fact_lines[-1] = last_line + ellipsis
            else:
                fact_lines[-1] = ellipsis

        fact_text_height_hi = len(fact_lines) * line_height_hi
        box_height_hi = header_height_hi + text_pad_v_hi + fact_text_height_hi + text_pad_v_hi

        box_top_hi = y_cursor_hi
        box_bottom_hi = box_top_hi + box_height_hi

        card_radius = int(18 * scale)
        rounded_rectangle(
            draw,
            (int(left_hi), int(box_top_hi), int(right_hi), int(box_bottom_hi)),
            radius=card_radius,
            fill=fact_bg,
            outline=fact_border,
            width=max(1, int(2 * scale)),
        )

        header_left_hi = left_hi
        header_right_hi = right_hi
        header_top_hi = box_top_hi
        header_bottom_hi = header_top_hi + header_height_hi

        header_radius = min(card_radius, header_height_hi // 2)
        rounded_rectangle(
            draw,
            (int(header_left_hi), int(header_top_hi), int(header_right_hi), int(header_bottom_hi)),
            radius=header_radius,
            fill=fact_header_bg,
            outline=None,
            width=0,
        )
        draw.rectangle(
            (
                int(header_left_hi),
                int(header_top_hi + header_radius),
                int(header_right_hi),
                int(header_bottom_hi),
            ),
            fill=fact_header_bg,
            outline=None,
        )

        header_cx = (header_left_hi + header_right_hi) / 2
        header_cy = (header_top_hi + header_bottom_hi) / 2
        try:
            draw.text(
                (header_cx, header_cy),
                fact_label,
                font=fact_label_font,
                fill=fact_header_text,
                anchor="mm",
            )
        except TypeError:
            hx = header_cx - label_w / 2
            hy = header_cy - label_h / 2
            draw.text((hx, hy), fact_label, font=fact_label_font, fill=fact_header_text)

        text_x_hi = left_hi + inner_horizontal_pad
        text_y_hi = header_bottom_hi + text_pad_v_hi

        for line in fact_lines:
            draw.text((text_x_hi, text_y_hi), line, font=fact_text_font, fill=text_color)
            text_y_hi += line_height_hi

        y_cursor_hi = box_bottom_hi + int(50 * scale)

    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    content_width_hi = content_right_hi - content_left_hi
    grid_width_target_hi = int(content_width_hi * 0.85)
    cell_size_hi = int(grid_width_target_hi / max(cols, 1))

    grid_w_hi = cell_size_hi * cols
    grid_h_hi = cell_size_hi * rows

    grid_top_hi = grid_top_base
    grid_left_hi = int((content_left_hi + content_right_hi - grid_w_hi) // 2)

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

    # --------------------------------------------------------
    # GRID (líneas + letras normales)
    # --------------------------------------------------------
    for r in range(rows + 1):
        y = grid_top_hi + r * cell_size_hi
        draw.line(
            (grid_left_hi, y, grid_left_hi + grid_w_hi, y),
            fill=grid_line_color,
            width=grid_line_width_hi,
        )
    for c in range(cols + 1):
        x = grid_left_hi + c * cell_size_hi
        draw.line(
            (x, grid_top_hi, x, grid_top_hi + grid_h_hi),
            fill=grid_line_color,
            width=grid_line_width_hi,
        )

    for r in range(rows):
        for c in range(cols):
            x0 = grid_left_hi + c * cell_size_hi
            y0 = grid_top_hi + r * cell_size_hi
            cx = x0 + cell_size_hi / 2
            cy = y0 + cell_size_hi / 2
            letter = grid[r][c]

            try:
                draw.text(
                    (cx, cy),
                    letter,
                    fill="black",
                    font=font_letter,
                    anchor="mm",
                )
            except TypeError:
                letter_w, letter_h = text_size(draw, letter, font_letter)
                draw.text(
                    (cx - letter_w / 2, cy - letter_h / 2),
                    letter,
                    fill="black",
                    font=font_letter,
                )


    # Redibujar letras de las posiciones resaltadas en negrita
    img.alpha_composite(highlight_layer.overlay)
    highlight_positions = highlight_layer.positions
    if is_solution and highlight_positions:
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in highlight_positions:
                    continue
                x0 = grid_left_hi + c * cell_size_hi
                y0 = grid_top_hi + r * cell_size_hi
                cx = x0 + cell_size_hi / 2
                cy = y0 + cell_size_hi / 2
                letter = grid[r][c]
                try:
                    draw.text(
                        (cx, cy),
                        letter,
                        fill="black",
                        font=font_letter_bold,
                        anchor="mm",
                    )
                except TypeError:
                    letter_w, letter_h = text_size(draw, letter, font_letter_bold)
                    draw.text(
                        (cx - letter_w / 2, cy - letter_h / 2),
                        letter,
                        fill="black",
                        font=font_letter_bold,
                    )

    grid_bottom_hi = grid_top_hi + grid_h_hi

    # --------------------------------------------------------
    # ÁREA INFERIOR (pill + lista)
    # --------------------------------------------------------
    base_gap_hi = int(60 * scale)
    gap_pill_to_words_hi = int(70 * scale)
    words_area_height_hi = int(850 * scale)
    words_bottom_hi = safe_bottom_hi - int(8 * scale)
    words_top_hi = max(0, words_bottom_hi - words_area_height_hi)

    # PASTILLA "Solution on page X"
    pill_box_h = 0
    pill_y = grid_bottom_hi + base_gap_hi
    if (not is_solution) and solution_page_number is not None:
        pill_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.75) * scale)
        pill_text = f"Solution on page {solution_page_number}"
        tw_pill, th_pill = text_size(draw, pill_text, pill_font)

        pad_h = int(16 * scale)
        pad_w = int(16 * scale)
        box_w = tw_pill + 2 * pad_w
        box_h = th_pill + 2 * pad_h
        pill_box_h = box_h

        pill_x = int((content_left_hi + content_right_hi - box_w) // 2)
        target_pill_y = words_top_hi - gap_pill_to_words_hi - box_h
        min_pill_y = grid_bottom_hi + base_gap_hi
        pill_y = max(min_pill_y, target_pill_y)

        rounded_rectangle(
            draw,
            (pill_x, pill_y, pill_x + box_w, pill_y + box_h),
            radius=box_h // 2,
            fill=pill_bg,
            outline=pill_border,
            width=max(1, int(2 * scale)),
        )

        tx = pill_x + box_w / 2
        ty = pill_y + box_h / 2
        try:
            draw.text((tx, ty), pill_text, font=pill_font, fill=text_color, anchor="mm")
        except TypeError:
            draw.text((tx - tw_pill / 2, ty - th_pill / 2), pill_text, font=pill_font, fill=text_color)

    desired_words_top_hi = pill_y + pill_box_h + gap_pill_to_words_hi
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

    # --------------------------------------------------------
    # Guardar
    # --------------------------------------------------------
    if filename is None:
        filename = os.path.join(
            "output_puzzles_kdp",
            f"puzzle_{idx}{'_sol' if is_solution else ''}.png",
        )

    return save_page(img, filename)
