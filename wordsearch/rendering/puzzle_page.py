"""Puzzle page renderer."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

from PIL import ImageDraw

from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_PATH_BOLD,
    FONT_TITLE,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.config.paths import build_default_output_file
from wordsearch.rendering.common import (
    load_font,
    rounded_rectangle,
    save_page,
    text_size,
    wrap_text,
)
from wordsearch.rendering.grid import draw_letter_grid
from wordsearch.rendering.page_frame import (
    create_page_canvas,
    draw_page_frame,
    draw_wrapped_centered_title,
)
from wordsearch.rendering.word_list import draw_word_list


def render_page(
    grid: Sequence[Sequence[str]],
    words: Iterable[str],
    idx: int,
    background_path: Optional[str] = None,
    filename: Optional[str] = None,
    puzzle_title: Optional[str] = None,
    fun_fact: Optional[str] = None,
    solution_page_number: Optional[int] = None,
) -> str:
    """Renderiza una página de puzzle."""
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
        title_text = f"{idx}. {puzzle_title}"
    else:
        title_text = f"Puzzle {idx}"

    title_max_width = int(content_right_hi - content_left_hi)
    y_after_title = draw_wrapped_centered_title(
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
    if fun_fact:
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

    grid_top_hi = grid_top_base
    grid_left_hi = int((content_left_hi + content_right_hi - grid_w_hi) // 2)

    grid_bottom_hi = draw_letter_grid(
        img=img,
        draw=draw,
        grid=grid,
        placed_words=None,
        is_solution=False,
        grid_left_hi=grid_left_hi,
        grid_top_hi=grid_top_hi,
        cell_size_hi=cell_size_hi,
        scale=scale,
        page_w_hi=page_w_hi,
        page_h_hi=page_h_hi,
        highlight_fill=highlight_fill,
        highlight_border=highlight_border,
    )

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
    if solution_page_number is not None:
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
        filename = build_default_output_file(f"puzzle_{idx}.png")

    return save_page(img, filename)
