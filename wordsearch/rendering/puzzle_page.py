"""Puzzle page renderer."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

from PIL import ImageDraw

from wordsearch.config.design import DEFAULT_LAYOUT, DEFAULT_THEME, LayoutConfig, ThemeConfig
from wordsearch.config.fonts import FONT_PATH, FONT_PATH_BOLD, wordlist_font_size as WORDLIST_FONT_SIZE
from wordsearch.config.paths import build_default_output_file
from wordsearch.rendering.adaptive_layout import plan_fact_layout, plan_title_layout
from wordsearch.rendering.common import load_font, rounded_rectangle, save_page, text_size
from wordsearch.rendering.grid import draw_letter_grid
from wordsearch.rendering.page_frame import create_page_canvas, draw_page_frame
from wordsearch.rendering.word_list import draw_word_list


def _draw_title_separator(
    draw: ImageDraw.ImageDraw,
    *,
    content_left_hi: int,
    content_right_hi: int,
    y_hi: int,
    scale: int,
    theme: ThemeConfig,
) -> int:
    """Draw a subtle editorial rule below the puzzle title."""
    center_x = (content_left_hi + content_right_hi) // 2
    rule_w = int((content_right_hi - content_left_hi) * 0.28)
    gap = int(18 * scale)
    dot_radius = max(2, int(3.5 * scale))
    draw.line(
        (center_x - rule_w // 2, y_hi, center_x - gap, y_hi),
        fill=theme.panel_border,
        width=max(1, int(scale)),
    )
    draw.line(
        (center_x + gap, y_hi, center_x + rule_w // 2, y_hi),
        fill=theme.panel_border,
        width=max(1, int(scale)),
    )
    rounded_rectangle(
        draw,
        (center_x - dot_radius, y_hi - dot_radius, center_x + dot_radius, y_hi + dot_radius),
        radius=dot_radius,
        fill=theme.title_color,
        outline=None,
        width=0,
    )
    return y_hi + int(28 * scale)


def _draw_grid_backplate(
    draw: ImageDraw.ImageDraw,
    *,
    grid_left_hi: int,
    grid_top_hi: int,
    grid_w_hi: int,
    grid_h_hi: int,
    scale: int,
    theme: ThemeConfig,
) -> None:
    """Add a quiet print-friendly card behind the letter grid."""
    pad = int(19 * scale)
    rounded_rectangle(
        draw,
        (
            grid_left_hi - pad,
            grid_top_hi - pad,
            grid_left_hi + grid_w_hi + pad,
            grid_top_hi + grid_h_hi + pad,
        ),
        radius=int(theme.fact_card_radius_px * 0.58 * scale),
        fill=theme.fact_card_fill,
        outline=theme.panel_border,
        width=max(1, int(theme.panel_border_width_px * 0.55 * scale)),
    )


def _draw_word_bank_heading(
    draw: ImageDraw.ImageDraw,
    *,
    words_top_hi: int,
    content_left_hi: int,
    content_right_hi: int,
    scale: int,
    theme: ThemeConfig,
) -> int:
    """Draw a compact word-bank label above the word list and return adjusted list top."""
    heading_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.38) * scale)
    heading = "WORD BANK"
    heading_w, heading_h = text_size(draw, heading, heading_font)
    center_x = (content_left_hi + content_right_hi) // 2
    y_hi = words_top_hi

    rule_y = y_hi + heading_h // 2
    side_gap = int(22 * scale)
    line_width = max(1, int(scale))
    draw.line(
        (content_left_hi + int(55 * scale), rule_y, center_x - heading_w // 2 - side_gap, rule_y),
        fill=theme.panel_border,
        width=line_width,
    )
    draw.line(
        (center_x + heading_w // 2 + side_gap, rule_y, content_right_hi - int(55 * scale), rule_y),
        fill=theme.panel_border,
        width=line_width,
    )
    draw.text((center_x - heading_w // 2, y_hi), heading, font=heading_font, fill=theme.title_color)
    return y_hi + heading_h + int(24 * scale)


def render_page(
    grid: Sequence[Sequence[str]],
    words: Iterable[str],
    idx: int,
    background_path: Optional[str] = None,
    filename: Optional[str] = None,
    puzzle_title: Optional[str] = None,
    fun_fact: Optional[str] = None,
    solution_page_number: Optional[int] = None,
    theme: ThemeConfig = DEFAULT_THEME,
    layout: LayoutConfig = DEFAULT_LAYOUT,
) -> str:
    """Renderiza una página de puzzle."""
    scale = 3
    img = create_page_canvas(background_path, scale, theme=theme, layout=layout)
    draw = ImageDraw.Draw(img)
    frame = draw_page_frame(draw=draw, scale=scale, theme=theme, layout=layout)

    safe_bottom_hi = frame.safe_bottom_hi
    panel_top = frame.panel_top
    content_left_hi = frame.content_left_hi
    content_right_hi = frame.content_right_hi
    grid_top_base = frame.grid_top_base
    text_color = theme.body_color

    title_text = f"{idx}. {puzzle_title}" if puzzle_title else f"Puzzle {idx}"
    title_plan = plan_title_layout(
        draw=draw,
        title_text=title_text,
        max_width_hi=int(content_right_hi - content_left_hi),
        start_y_hi=panel_top + int(25 * scale),
        scale=scale,
    )

    title_y_hi = panel_top + int(25 * scale)
    container_width = max(0, content_right_hi - content_left_hi)
    for line in title_plan.lines:
        width, height = text_size(draw, line, title_plan.font)
        x = content_left_hi + max(0, (container_width - width) // 2)
        draw.text((x, title_y_hi), line, font=title_plan.font, fill=theme.title_color)
        title_y_hi += int(height * 1.05)

    separator_y_hi = title_plan.y_after_title_hi + int(17 * scale)
    y_cursor_hi = _draw_title_separator(
        draw,
        content_left_hi=content_left_hi,
        content_right_hi=content_right_hi,
        y_hi=separator_y_hi,
        scale=scale,
        theme=theme,
    ) + max(int(0.45 * title_plan.title_to_fact_gap_hi), int(24 * scale))

    if fun_fact:
        fact_plan = plan_fact_layout(
            draw=draw,
            fun_fact=fun_fact,
            content_left_hi=content_left_hi,
            content_right_hi=content_right_hi,
            grid_top_base_hi=grid_top_base,
            y_cursor_hi=y_cursor_hi,
            scale=scale,
        )
        left_hi = content_left_hi
        right_hi = content_right_hi
        box_top_hi = y_cursor_hi
        box_bottom_hi = box_top_hi + fact_plan.box_height_hi

        card_radius = int(theme.fact_card_radius_px * scale)
        rounded_rectangle(
            draw,
            (int(left_hi), int(box_top_hi), int(right_hi), int(box_bottom_hi)),
            radius=card_radius,
            fill=theme.fact_card_fill,
            outline=theme.fact_card_border,
            width=max(1, int(theme.fact_card_border_width_px * scale)),
        )

        header_top_hi = box_top_hi
        header_bottom_hi = header_top_hi + fact_plan.header_height_hi
        header_radius = min(card_radius, fact_plan.header_height_hi // 2)
        rounded_rectangle(
            draw,
            (int(left_hi), int(header_top_hi), int(right_hi), int(header_bottom_hi)),
            radius=header_radius,
            fill=theme.fact_header_fill,
            outline=None,
            width=0,
        )
        draw.rectangle(
            (int(left_hi), int(header_top_hi + header_radius), int(right_hi), int(header_bottom_hi)),
            fill=theme.fact_header_fill,
            outline=None,
        )

        fact_label = "FUN FACT"
        label_w, label_h = text_size(draw, fact_label, fact_plan.label_font)
        header_cx = (left_hi + right_hi) / 2
        header_cy = (header_top_hi + header_bottom_hi) / 2
        try:
            draw.text(
                (header_cx, header_cy),
                fact_label,
                font=fact_plan.label_font,
                fill=theme.fact_header_text,
                anchor="mm",
            )
        except TypeError:
            draw.text(
                (header_cx - label_w / 2, header_cy - label_h / 2),
                fact_label,
                font=fact_plan.label_font,
                fill=theme.fact_header_text,
            )

        text_x_hi = left_hi + fact_plan.inner_horizontal_pad_hi
        text_y_hi = header_bottom_hi + fact_plan.text_pad_v_hi
        accent_left = left_hi + int(17 * scale)
        accent_top = text_y_hi + int(2 * scale)
        accent_bottom = box_bottom_hi - int(16 * scale)
        if accent_bottom > accent_top:
            rounded_rectangle(
                draw,
                (accent_left, accent_top, accent_left + int(4 * scale), accent_bottom),
                radius=int(2 * scale),
                fill=theme.fact_header_fill,
                outline=None,
                width=0,
            )
            text_x_hi += int(18 * scale)

        for line in fact_plan.rendered_lines or []:
            draw.text((text_x_hi, text_y_hi), line, font=fact_plan.text_font, fill=text_color)
            text_y_hi += fact_plan.line_height_hi
        y_cursor_hi = box_bottom_hi + fact_plan.after_gap_hi

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    content_width_hi = content_right_hi - content_left_hi
    grid_width_target_hi = int(content_width_hi * 0.85)
    cell_size_hi = int(grid_width_target_hi / max(cols, 1))
    grid_w_hi = cell_size_hi * cols
    grid_h_hi = cell_size_hi * rows
    grid_top_hi = max(grid_top_base, y_cursor_hi)
    grid_left_hi = int((content_left_hi + content_right_hi - grid_w_hi) // 2)

    _draw_grid_backplate(
        draw,
        grid_left_hi=grid_left_hi,
        grid_top_hi=grid_top_hi,
        grid_w_hi=grid_w_hi,
        grid_h_hi=grid_h_hi,
        scale=scale,
        theme=theme,
    )

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
        highlight_fill=theme.highlight_fill,
        highlight_border=theme.highlight_border,
        theme=theme,
    )

    base_gap_hi = int(60 * scale)
    gap_pill_to_words_hi = int(60 * scale)
    words_area_height_hi = int(880 * scale)
    words_bottom_hi = safe_bottom_hi - int(8 * scale)
    words_top_hi = max(0, words_bottom_hi - words_area_height_hi)

    pill_box_h = 0
    pill_y = grid_bottom_hi + base_gap_hi
    if solution_page_number is not None:
        pill_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.75) * scale)
        pill_text = f"Solution on page {solution_page_number}"
        tw_pill, th_pill = text_size(draw, pill_text, pill_font)
        pad_h = int(16 * scale)
        pad_w = int(18 * scale)
        box_w = tw_pill + 2 * pad_w
        box_h = th_pill + 2 * pad_h
        pill_box_h = box_h
        pill_x = int((content_left_hi + content_right_hi - box_w) // 2)
        target_pill_y = words_top_hi - gap_pill_to_words_hi - box_h
        pill_y = max(grid_bottom_hi + base_gap_hi, target_pill_y)
        rounded_rectangle(
            draw,
            (pill_x, pill_y, pill_x + box_w, pill_y + box_h),
            radius=box_h // 2,
            fill=theme.pill_fill,
            outline=theme.pill_border,
            width=max(1, int(theme.pill_border_width_px * scale)),
        )
        tx = pill_x + box_w / 2
        ty = pill_y + box_h / 2
        try:
            draw.text((tx, ty), pill_text, font=pill_font, fill=theme.pill_text, anchor="mm")
        except TypeError:
            draw.text((tx - tw_pill / 2, ty - th_pill / 2), pill_text, font=pill_font, fill=theme.pill_text)

    desired_words_top_hi = pill_y + pill_box_h + gap_pill_to_words_hi
    if desired_words_top_hi > words_top_hi:
        words_top_hi = desired_words_top_hi
    if words_top_hi > words_bottom_hi:
        words_top_hi = words_bottom_hi

    heading_bottom_hi = _draw_word_bank_heading(
        draw,
        words_top_hi=words_top_hi,
        content_left_hi=content_left_hi,
        content_right_hi=content_right_hi,
        scale=scale,
        theme=theme,
    )
    words_top_hi = min(max(heading_bottom_hi, words_top_hi), words_bottom_hi)

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
        filename = build_default_output_file(f"puzzle_{idx}.png")

    return save_page(
        img,
        filename,
        output_width_px=layout.page_width_px,
        output_height_px=layout.page_height_px,
        dpi=layout.dpi,
    )
