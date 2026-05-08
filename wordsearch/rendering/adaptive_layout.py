"""Editorial layout planning helpers shared by rendering and render-quality checks.

The functions in this module are deliberately conservative. They only make small,
deterministic adjustments that mimic common manual layout fixes: slightly reduce a
crowded title, give long facts a little more breathing room, or tighten a dense
word list before raising review warnings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from PIL import ImageDraw, ImageFont

from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_PATH_BOLD,
    FONT_TITLE,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.rendering.common import load_font, text_size, wrap_text


TITLE_FONT_SCALES: tuple[float, ...] = (1.0, 0.96, 0.92, 0.88, 0.86)
TITLE_DENSE_LINE_LIMIT = 3
TITLE_DEFAULT_GAP_PX = 80
TITLE_DENSE_GAP_PX = 62
TITLE_VERY_DENSE_GAP_PX = 52

FACT_TEXT_FONT_SCALES: tuple[float, ...] = (0.50, 0.47, 0.44)
FACT_DEFAULT_AFTER_GAP_PX = 50
FACT_TIGHT_AFTER_GAP_PX = 38
FACT_LABEL_SCALE = 0.90
FACT_INNER_PAD_X_PX = 18
FACT_HEADER_PAD_Y_PX = 8
FACT_TEXT_PAD_Y_PX = 10
FACT_MIN_GRID_GAP_PX = 30

WORD_LIST_FONT_SCALES: tuple[float, ...] = (0.60, 0.57, 0.54, 0.51)
WORD_LIST_INNER_MARGIN_PX = 35
WORD_LIST_WIDTH_FIT_RATIO = 0.92
WORD_LIST_MIN_COLUMNS = 2
WORD_LIST_MAX_COLUMNS = 6


@dataclass(frozen=True)
class TitleLayoutPlan:
    font: ImageFont.FreeTypeFont
    font_size_hi: int
    font_scale: float
    lines: list[str]
    line_height_hi: int
    title_to_fact_gap_hi: int
    y_after_title_hi: int


@dataclass(frozen=True)
class FactLayoutPlan:
    present: bool
    label_font: ImageFont.FreeTypeFont | None = None
    text_font: ImageFont.FreeTypeFont | None = None
    text_font_size_hi: int = 0
    text_font_scale: float = 0.0
    raw_lines: list[str] | None = None
    rendered_lines: list[str] | None = None
    max_lines_fit: int = 0
    rendered_line_count: int = 0
    line_height_hi: int = 0
    header_height_hi: int = 0
    text_pad_v_hi: int = 0
    inner_horizontal_pad_hi: int = 0
    box_height_hi: int = 0
    box_bottom_hi: int = 0
    after_gap_hi: int = 0
    truncated: bool = False
    used_ratio: float = 0.0


@dataclass(frozen=True)
class WordListLayoutPlan:
    present: bool
    words_upper: list[str]
    words_height_hi: int
    area_left_hi: int
    area_right_hi: int
    total_w_hi: int
    font: ImageFont.FreeTypeFont | None = None
    font_scale: float = 0.0
    line_height_hi: int = 0
    col_count: int = 0
    col_width_hi: float = 0.0
    max_lines_per_col: int = 0
    required_lines_per_col: int = 0
    fill_ratio: float = 0.0
    forced_layout: bool = False
    max_word_width_ratio: float = 0.0
    longest_by_width: str = ""
    font_reduced: bool = False
    uses_extra_column_capacity: bool = False


def plan_title_layout(
    *,
    draw: ImageDraw.ImageDraw,
    title_text: str,
    max_width_hi: int,
    start_y_hi: int,
    scale: int,
    base_font_size: int = TITLE_FONT_SIZE,
) -> TitleLayoutPlan:
    """Choose the least invasive title adjustment that keeps puzzle titles calm."""
    base_size_hi = int(base_font_size * scale)
    selected: tuple[float, ImageFont.FreeTypeFont, list[str]] | None = None

    for font_scale in TITLE_FONT_SCALES:
        font_size_hi = max(1, int(base_size_hi * font_scale))
        font = load_font(FONT_TITLE, font_size_hi)
        lines = wrap_text(draw, title_text, font, max_width_hi)
        if len(lines) <= TITLE_DENSE_LINE_LIMIT:
            selected = (font_scale, font, lines)
            break
        selected = (font_scale, font, lines)

    assert selected is not None
    font_scale, font, lines = selected
    line_height_hi = text_size(draw, "Ag", font)[1]
    y_after_title_hi = start_y_hi + int(len(lines) * line_height_hi * 1.05)

    if len(lines) >= 5:
        gap_px = TITLE_VERY_DENSE_GAP_PX
    elif len(lines) >= 3 or font_scale < 1.0:
        gap_px = TITLE_DENSE_GAP_PX
    else:
        gap_px = TITLE_DEFAULT_GAP_PX

    return TitleLayoutPlan(
        font=font,
        font_size_hi=font.size,
        font_scale=round(font_scale, 3),
        lines=lines,
        line_height_hi=line_height_hi,
        title_to_fact_gap_hi=int(gap_px * scale),
        y_after_title_hi=y_after_title_hi,
    )


def plan_fact_layout(
    *,
    draw: ImageDraw.ImageDraw,
    fun_fact: str | None,
    content_left_hi: int,
    content_right_hi: int,
    grid_top_base_hi: int,
    y_cursor_hi: int,
    scale: int,
) -> FactLayoutPlan:
    """Plan a fun-fact card using small font/gap adjustments before truncating."""
    if not fun_fact:
        return FactLayoutPlan(present=False)

    label_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * FACT_LABEL_SCALE) * scale)
    label_h = text_size(draw, "FUN FACT", label_font)[1]
    header_height_hi = label_h + 2 * int(FACT_HEADER_PAD_Y_PX * scale)
    text_pad_v_hi = int(FACT_TEXT_PAD_Y_PX * scale)
    inner_horizontal_pad_hi = int(FACT_INNER_PAD_X_PX * scale)
    max_text_width_hi = int((content_right_hi - content_left_hi) - 2 * inner_horizontal_pad_hi)
    min_gap_hi = int(FACT_MIN_GRID_GAP_PX * scale)

    best: FactLayoutPlan | None = None
    for font_scale in FACT_TEXT_FONT_SCALES:
        text_font_size_hi = max(1, int(WORDLIST_FONT_SIZE * font_scale) * scale)
        text_font = load_font(FONT_PATH, text_font_size_hi)
        line_height_hi = int(text_font.size * 1.10)
        min_fact_block_hi = header_height_hi + 2 * text_pad_v_hi + line_height_hi
        max_fact_height_hi = max(min_fact_block_hi, grid_top_base_hi - y_cursor_hi - min_gap_hi)
        raw_lines = wrap_text(draw, fun_fact, text_font, max_text_width_hi)
        available_text_h = max(0, max_fact_height_hi - header_height_hi - 2 * text_pad_v_hi)
        max_lines_fit = max(1, available_text_h // line_height_hi)
        rendered_lines, truncated = _truncate_lines_to_width(
            draw=draw,
            lines=raw_lines,
            max_lines_fit=max_lines_fit,
            max_width_hi=max_text_width_hi,
            font=text_font,
        )
        rendered_line_count = len(rendered_lines)
        used_ratio = rendered_line_count / max(max_lines_fit, 1)
        fact_text_height_hi = rendered_line_count * line_height_hi
        box_height_hi = header_height_hi + text_pad_v_hi + fact_text_height_hi + text_pad_v_hi
        box_bottom_hi = y_cursor_hi + box_height_hi
        after_gap_hi = int(
            (FACT_TIGHT_AFTER_GAP_PX if truncated or used_ratio >= 0.92 else FACT_DEFAULT_AFTER_GAP_PX)
            * scale
        )

        candidate = FactLayoutPlan(
            present=True,
            label_font=label_font,
            text_font=text_font,
            text_font_size_hi=text_font.size,
            text_font_scale=round(font_scale, 3),
            raw_lines=raw_lines,
            rendered_lines=rendered_lines,
            max_lines_fit=max_lines_fit,
            rendered_line_count=rendered_line_count,
            line_height_hi=line_height_hi,
            header_height_hi=header_height_hi,
            text_pad_v_hi=text_pad_v_hi,
            inner_horizontal_pad_hi=inner_horizontal_pad_hi,
            box_height_hi=box_height_hi,
            box_bottom_hi=box_bottom_hi,
            after_gap_hi=after_gap_hi,
            truncated=truncated,
            used_ratio=round(used_ratio, 3),
        )

        if best is None or _fact_candidate_score(candidate) > _fact_candidate_score(best):
            best = candidate
        if not truncated and used_ratio <= 0.90:
            return candidate

    assert best is not None
    return best


def _fact_candidate_score(plan: FactLayoutPlan) -> tuple[int, int, float]:
    not_truncated = 0 if plan.truncated else 1
    return (not_truncated, plan.rendered_line_count, plan.text_font_scale)


def _truncate_lines_to_width(
    *,
    draw: ImageDraw.ImageDraw,
    lines: Sequence[str],
    max_lines_fit: int,
    max_width_hi: int,
    font: ImageFont.FreeTypeFont,
) -> tuple[list[str], bool]:
    if len(lines) <= max_lines_fit:
        return list(lines), False

    rendered_lines = list(lines[:max_lines_fit])
    last_line = rendered_lines[-1] if rendered_lines else ""
    ellipsis = "..."
    while last_line and text_size(draw, last_line + ellipsis, font)[0] > max_width_hi:
        last_line = last_line[:-1].rstrip()

    rendered_lines[-1] = last_line + ellipsis if last_line else ellipsis
    return rendered_lines, True


def plan_word_list_layout(
    *,
    draw: ImageDraw.ImageDraw,
    words: Sequence[str],
    words_top_hi: int,
    words_bottom_hi: int,
    content_left_hi: int,
    content_right_hi: int,
    scale: int,
    font_path: str = FONT_PATH,
    wordlist_font_size: int = WORDLIST_FONT_SIZE,
) -> WordListLayoutPlan:
    """Choose word-list columns/font with predictable editorial constraints."""
    words_upper = [str(word).upper() for word in words]
    words_height_hi = max(0, words_bottom_hi - words_top_hi)
    words_inner_margin_hi = int(WORD_LIST_INNER_MARGIN_PX * scale)
    area_left_hi = content_left_hi + words_inner_margin_hi
    area_right_hi = content_right_hi - words_inner_margin_hi
    total_w_hi = area_right_hi - area_left_hi

    if not words_upper or words_height_hi <= 0 or total_w_hi <= 0:
        return WordListLayoutPlan(
            present=False,
            words_upper=words_upper,
            words_height_hi=words_height_hi,
            area_left_hi=area_left_hi,
            area_right_hi=area_right_hi,
            total_w_hi=total_w_hi,
        )

    best: WordListLayoutPlan | None = None
    for font_scale in WORD_LIST_FONT_SCALES:
        candidate = _plan_word_list_for_font(
            draw=draw,
            words_upper=words_upper,
            words_height_hi=words_height_hi,
            area_left_hi=area_left_hi,
            area_right_hi=area_right_hi,
            total_w_hi=total_w_hi,
            scale=scale,
            font_path=font_path,
            wordlist_font_size=wordlist_font_size,
            font_scale=font_scale,
        )

        if best is None or _word_list_candidate_score(candidate) > _word_list_candidate_score(best):
            best = candidate

        if (
            not candidate.forced_layout
            and candidate.fill_ratio <= 0.88
            and candidate.max_word_width_ratio <= WORD_LIST_WIDTH_FIT_RATIO
        ):
            return candidate

    assert best is not None
    return best


def _plan_word_list_for_font(
    *,
    draw: ImageDraw.ImageDraw,
    words_upper: list[str],
    words_height_hi: int,
    area_left_hi: int,
    area_right_hi: int,
    total_w_hi: int,
    scale: int,
    font_path: str,
    wordlist_font_size: int,
    font_scale: float,
) -> WordListLayoutPlan:
    font = load_font(font_path, max(1, int(wordlist_font_size * font_scale) * scale))
    line_height_hi = int(font.size * 1.12)
    max_lines_per_col = max(1, words_height_hi // line_height_hi)
    word_widths = {word: text_size(draw, word, font)[0] for word in words_upper}
    word_max_w = max(word_widths.values()) if word_widths else 0
    longest_by_width = max(word_widths, key=word_widths.get, default="")

    best_layout: tuple[int, float, bool] | None = None
    for col_count in range(WORD_LIST_MIN_COLUMNS, WORD_LIST_MAX_COLUMNS + 1):
        if col_count * max_lines_per_col < len(words_upper):
            continue
        col_w_hi = total_w_hi / col_count
        if word_max_w <= col_w_hi * WORD_LIST_WIDTH_FIT_RATIO:
            best_layout = (col_count, col_w_hi, False)
            break

    if best_layout is None:
        col_count = max(
            WORD_LIST_MIN_COLUMNS,
            min(WORD_LIST_MAX_COLUMNS, _ceil_div(len(words_upper), max_lines_per_col)),
        )
        col_w_hi = total_w_hi / col_count
        best_layout = (col_count, col_w_hi, True)

    col_count, col_w_hi, forced_layout = best_layout
    required_lines_per_col = _ceil_div(len(words_upper), col_count)
    fill_ratio = required_lines_per_col / max(max_lines_per_col, 1)
    max_word_width_ratio = word_max_w / max(col_w_hi, 1)

    return WordListLayoutPlan(
        present=True,
        words_upper=words_upper,
        words_height_hi=words_height_hi,
        area_left_hi=area_left_hi,
        area_right_hi=area_right_hi,
        total_w_hi=total_w_hi,
        font=font,
        font_scale=round(font_scale, 3),
        line_height_hi=line_height_hi,
        col_count=col_count,
        col_width_hi=col_w_hi,
        max_lines_per_col=max_lines_per_col,
        required_lines_per_col=required_lines_per_col,
        fill_ratio=round(fill_ratio, 3),
        forced_layout=forced_layout,
        max_word_width_ratio=round(max_word_width_ratio, 3),
        longest_by_width=longest_by_width,
        font_reduced=font_scale < WORD_LIST_FONT_SCALES[0],
        uses_extra_column_capacity=col_count > 5,
    )


def _word_list_candidate_score(plan: WordListLayoutPlan) -> tuple[int, int, float, float]:
    width_ok = 1 if plan.max_word_width_ratio <= WORD_LIST_WIDTH_FIT_RATIO else 0
    not_forced = 0 if plan.forced_layout else 1
    comfortable_fill = -abs(plan.fill_ratio - 0.72)
    font_size = plan.font_scale
    return (width_ok, not_forced, comfortable_fill, font_size)


def _ceil_div(value: int, divisor: int) -> int:
    return -(-value // max(divisor, 1))
