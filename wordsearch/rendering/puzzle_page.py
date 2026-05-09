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


def _format_visual_scale(layout: LayoutConfig = DEFAULT_LAYOUT) -> float:
    width_scale = layout.page_width_px / DEFAULT_LAYOUT.page_width_px
    height_scale = layout.page_height_px / DEFAULT_LAYOUT.page_height_px
    return min(1.15, max(1.0, min(width_scale, height_scale)))


def _draw_centered_text_in_box(draw: ImageDraw.ImageDraw, text: str, font, *, center_x: float, center_y: float, fill) -> None:
    try:
        draw.text((center_x, center_y), text, font=font, fill=fill, anchor="mm")
    except TypeError:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text((center_x - text_w / 2 - bbox[0], center_y - text_h / 2 - bbox[1]), text, font=font, fill=fill)


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
    rule_w = int((content_right_hi - content_left_hi) * 0.24)
    gap = int(18 * scale)
    dot_radius = max(2, int(3.0 * scale))
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
    return y_hi + int(24 * scale)


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
    visual_scale: float = 1.0,
) -> int:
    """Draw a compact word-bank label above the word list and return adjusted list top."""
    heading_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.36 * visual_scale) * scale)
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
    return y_hi + heading_h + int(40 * scale)


def _draw_fun_fact_label(
    draw: ImageDraw.ImageDraw,
    *,
    left_hi: int,
    top_hi: int,
    scale: int,
    theme: ThemeConfig,
    visual_scale: float,
) -> tuple[int, int]:
    """Draw a small in-card fun-fact chip that does not invade the body text."""
    fact_label = "FUN FACT"
    label_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.42 * visual_scale) * scale)
    label_w, label_h = text_size(draw, fact_label, label_font)
    pad_x = int(18 * scale)
    pad_y = int(7 * scale)
    chip_left = left_hi + int(18 * scale)
    chip_top = top_hi + int(12 * scale)
    chip_right = chip_left + label_w + 2 * pad_x
    chip_bottom = chip_top + label_h + 2 * pad_y
    rounded_rectangle(
        draw,
        (chip_left, chip_top, chip_right, chip_bottom),
        radius=(chip_bottom - chip_top) // 2,
        fill=theme.fact_header_fill,
        outline=None,
        width=0,
    )
    _draw_centered_text_in_box(
        draw,
        fact_label,
        label_font,
        center_x=(chip_left + chip_right) / 2,
        center_y=(chip_top + chip_bottom) / 2,
        fill=theme.fact_header_text,
    )
    return chip_right, chip_bottom


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
    visual_scale = _format_visual_scale(layout)
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

    separator_y_hi = title_plan.y_after_title_hi + int(18 * scale)
    y_cursor_hi = _draw_title_separator(
        draw,
        content_left_hi=content_left_hi,
        content_right_hi=content_right_hi,
        y_hi=separator_y_hi,
        scale=scale,
        theme=theme,
    ) + max(int(0.35 * title_plan.title_to_fact_gap_hi), int(18 * scale))

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
        box_top_hi = y_cursor_hi + int(10 * scale)
        chip_reserved_hi = int(50 * visual_scale * scale)
        text_block_hi = fact_plan.rendered_line_count * fact_plan.line_height_hi
        box_height_hi = chip_reserved_hi + text_block_hi + int(32 * scale)
        box_bottom_hi = box_top_hi + max(box_height_hi, int(108 * scale))

        card_radius = int(theme.fact_card_radius_px * scale)
        rounded_rectangle(
            draw,
            (int(left_hi), int(box_top_hi), int(right_hi), int(box_bottom_hi)),
            radius=card_radius,
            fill=theme.fact_card_fill,
            outline=theme.fact_card_border,
            width=max(1, int(theme.fact_card_border_width_px * scale)),
        )

        _label_right_hi, label_bottom_hi = _draw_fun_fact_label(
            draw,
            left_hi=int(left_hi),
            top_hi=int(box_top_hi),
            scale=scale,
            theme=theme,
            visual_scale=visual_scale,
        )

        text_x_hi = left_hi + fact_plan.inner_horizontal_pad_hi
        text_y_hi = label_bottom_hi + int(12 * scale)
        for line in fact_plan.rendered_lines or []:
            draw.text((text_x_hi, text_y_hi), line, font=fact_plan.text_font, fill=text_color)
            text_y_hi += fact_plan.line_height_hi
        y_cursor_hi = box_bottom_hi + fact_plan.after_gap_hi

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    content_width_hi = content_right_hi - content_left_hi
    grid_ratio = 0.85 if visual_scale <= 1.02 else 0.875
    grid_width_target_hi = int(content_width_hi * grid_ratio)
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

    base_gap_hi = int(54 * scale)
    gap_pill_to_words_hi = int(50 * scale)
    words_area_height_hi = int(900 * visual_scale * scale)
    words_bottom_hi = safe_bottom_hi - int(8 * scale)
    words_top_hi = max(0, words_bottom_hi - words_area_height_hi)

    pill_box_h = 0
    pill_y = grid_bottom_hi + base_gap_hi
    if solution_page_number is not None:
        pill_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.75 * visual_scale) * scale)
        pill_text = f"Solution on page {solution_page_number}"
        tw_pill, th_pill = text_size(draw, pill_text, pill_font)
        pad_h = int(15 * scale)
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
        visual_scale=visual_scale,
    )
    words_top_hi = min(max(heading_bottom_hi + int(6 * scale), words_top_hi), words_bottom_hi)

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
