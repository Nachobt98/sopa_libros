"""Word list rendering helpers for puzzle pages."""

from __future__ import annotations

from typing import Iterable, List

from PIL import ImageDraw

from wordsearch.rendering.adaptive_layout import plan_word_list_layout
from wordsearch.rendering.common import text_size


def draw_word_list(
    *,
    draw: ImageDraw.ImageDraw,
    words: Iterable[str],
    words_top_hi: int,
    words_bottom_hi: int,
    content_left_hi: int,
    content_right_hi: int,
    scale: int,
    font_path: str,
    wordlist_font_size: int,
    text_color,
) -> None:
    """Draw the lower word list in balanced, adaptive columns."""
    plan = plan_word_list_layout(
        draw=draw,
        words=list(words),
        words_top_hi=words_top_hi,
        words_bottom_hi=words_bottom_hi,
        content_left_hi=content_left_hi,
        content_right_hi=content_right_hi,
        scale=scale,
        font_path=font_path,
        wordlist_font_size=wordlist_font_size,
    )
    if not plan.present or plan.font is None:
        return

    base_len = len(plan.words_upper) // plan.col_count
    remainder = len(plan.words_upper) % plan.col_count
    col_sizes = [base_len + (1 if i < remainder else 0) for i in range(plan.col_count)]

    col_words: List[List[str]] = []
    idx_tmp = 0
    for size in col_sizes:
        col_words.append(plan.words_upper[idx_tmp : idx_tmp + size])
        idx_tmp += size

    max_used_h = max(len(col) * plan.line_height_hi for col in col_words) if col_words else 0
    group_y_start = words_top_hi + (plan.words_height_hi - max_used_h) // 2

    for col_idx, col in enumerate(col_words):
        if not col:
            continue

        col_center_x = int(plan.area_left_hi + (col_idx + 0.5) * plan.col_width_hi)
        y_hi = int(group_y_start)

        for word_text in col:
            try:
                draw.text(
                    (col_center_x, y_hi),
                    word_text,
                    fill=text_color,
                    font=plan.font,
                    anchor="mm",
                )
            except TypeError:
                word_w, word_h = text_size(draw, word_text, plan.font)
                draw.text(
                    (col_center_x - word_w / 2, y_hi - word_h / 2),
                    word_text,
                    fill=text_color,
                    font=plan.font,
                )
            y_hi += plan.line_height_hi
