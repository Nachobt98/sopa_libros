"""Word list rendering helpers for puzzle pages."""

from __future__ import annotations

import math
from typing import Iterable, List

from PIL import ImageDraw

from wordsearch.rendering.common import load_font, text_size


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
    """Draw the lower word list in balanced columns."""
    words_height_hi = max(0, words_bottom_hi - words_top_hi)
    words_upper = [str(word).upper() for word in words]
    if not words_upper or words_height_hi <= 0:
        return

    words_inner_margin_hi = int(35 * scale)
    area_left_hi = content_left_hi + words_inner_margin_hi
    area_right_hi = content_right_hi - words_inner_margin_hi
    total_w_hi = area_right_hi - area_left_hi

    font_words_real = load_font(font_path, int(wordlist_font_size * 0.6) * scale)
    line_h_hi = int(font_words_real.size * 1.12)

    max_lines_per_col = max(1, words_height_hi // line_h_hi)
    word_max_w = max(text_size(draw, word, font_words_real)[0] for word in words_upper)

    best_layout = None
    for col_count in range(2, 6):
        if col_count * max_lines_per_col < len(words_upper):
            continue
        col_w_hi = total_w_hi / col_count
        if word_max_w <= col_w_hi * 0.92:
            best_layout = (col_count, col_w_hi)
            break

    if best_layout is None:
        col_count = max(2, min(5, math.ceil(len(words_upper) / max_lines_per_col)))
        col_w_hi = total_w_hi / col_count
        best_layout = (col_count, col_w_hi)

    col_count, col_w_hi = best_layout
    base_len = len(words_upper) // col_count
    remainder = len(words_upper) % col_count
    col_sizes = [base_len + (1 if i < remainder else 0) for i in range(col_count)]

    col_words: List[List[str]] = []
    idx_tmp = 0
    for size in col_sizes:
        col_words.append(words_upper[idx_tmp : idx_tmp + size])
        idx_tmp += size

    max_used_h = max(len(col) * line_h_hi for col in col_words) if col_words else 0
    group_y_start = words_top_hi + (words_height_hi - max_used_h) // 2

    for col_idx, col in enumerate(col_words):
        if not col:
            continue

        col_center_x = int(area_left_hi + (col_idx + 0.5) * col_w_hi)
        y_hi = int(group_y_start)

        for word_text in col:
            try:
                draw.text(
                    (col_center_x, y_hi),
                    word_text,
                    fill=text_color,
                    font=font_words_real,
                    anchor="mm",
                )
            except TypeError:
                word_w, word_h = text_size(draw, word_text, font_words_real)
                draw.text(
                    (col_center_x - word_w / 2, y_hi - word_h / 2),
                    word_text,
                    fill=text_color,
                    font=font_words_real,
                )
            y_hi += line_h_hi
