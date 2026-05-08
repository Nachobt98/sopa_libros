"""Editorial render-quality checks for thematic book pages.

These checks are intentionally heuristic: they do not replace human visual
review, but they highlight pages that are likely to need manual inspection.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from PIL import Image, ImageDraw

from wordsearch.config.design import DEFAULT_THEME, ThemeConfig
from wordsearch.config.fonts import (
    FONT_PATH,
    FONT_PATH_BOLD,
    FONT_TITLE,
    title_font_size as TITLE_FONT_SIZE,
    wordlist_font_size as WORDLIST_FONT_SIZE,
)
from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.page_plan import PagePlan
from wordsearch.rendering.common import load_font, text_size, wrap_text
from wordsearch.rendering.page_frame import draw_page_frame

RENDER_QUALITY_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class RenderQualityWarning:
    """Actionable warning emitted by the render-quality analyzer."""

    severity: str
    code: str
    message: str
    page_type: str
    page_number: int | None = None
    puzzle_index: int | None = None
    title: str | None = None
    path: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RenderQualityReport:
    """Serializable render-quality summary."""

    schema_version: int
    warning_count: int
    by_severity: dict[str, int]
    by_code: dict[str, int]
    warnings: list[RenderQualityWarning]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["warnings"] = [warning.to_dict() for warning in self.warnings]
        return data

    def print_summary(self) -> None:
        print("\n=== Render quality ===")
        if not self.warnings:
            print("OK: no se han detectado warnings editoriales de render.")
            return

        print(f"Warnings: {self.warning_count}")
        for code, count in sorted(self.by_code.items()):
            print(f"  - {code}: {count}")


def build_render_quality_report(
    *,
    book_title: str,
    generated_puzzles: Sequence[GeneratedPuzzle],
    page_plan: PagePlan,
    content_image_paths: Iterable[str],
    theme: ThemeConfig = DEFAULT_THEME,
) -> RenderQualityReport:
    """Build render-quality warnings for the generated thematic book."""
    warnings: list[RenderQualityWarning] = []
    path_index = _index_content_paths(content_image_paths)
    draw = _make_measure_draw(theme)

    warnings.extend(_analyze_title_page(book_title, draw=draw, path=path_index.get("00_title_page")))
    warnings.extend(_analyze_block_covers(generated_puzzles, page_plan, draw=draw, path_index=path_index))

    for generated in generated_puzzles:
        warnings.extend(
            _analyze_puzzle_page(
                generated,
                page_plan,
                draw=draw,
                path=path_index.get(f"puzzle_{generated.spec.index + 1}"),
                theme=theme,
            )
        )

    by_severity = dict(Counter(warning.severity for warning in warnings))
    by_code = dict(Counter(warning.code for warning in warnings))
    return RenderQualityReport(
        schema_version=RENDER_QUALITY_SCHEMA_VERSION,
        warning_count=len(warnings),
        by_severity=by_severity,
        by_code=by_code,
        warnings=warnings,
    )


def _make_measure_draw(theme: ThemeConfig) -> ImageDraw.ImageDraw:
    image = Image.new("RGBA", (PAGE_W_PX * 3, PAGE_H_PX * 3), theme.page_background_fill)
    return ImageDraw.Draw(image)


def _index_content_paths(content_image_paths: Iterable[str]) -> dict[str, str]:
    indexed: dict[str, str] = {}
    for path in content_image_paths:
        stem = Path(path).stem
        indexed[stem] = path
    return indexed


def _warning(
    *,
    severity: str,
    code: str,
    message: str,
    page_type: str,
    page_number: int | None = None,
    puzzle_index: int | None = None,
    title: str | None = None,
    path: str | None = None,
    details: dict[str, Any] | None = None,
) -> RenderQualityWarning:
    return RenderQualityWarning(
        severity=severity,
        code=code,
        message=message,
        page_type=page_type,
        page_number=page_number,
        puzzle_index=puzzle_index,
        title=title,
        path=path,
        details=details or {},
    )


def _analyze_title_page(
    book_title: str,
    *,
    draw: ImageDraw.ImageDraw,
    path: str | None,
) -> list[RenderQualityWarning]:
    warnings: list[RenderQualityWarning] = []
    scale = 3
    max_width = int(PAGE_W_PX * scale * 0.70)
    title_size = int(TITLE_FONT_SIZE * 1.70) * scale
    min_title_size = int(TITLE_FONT_SIZE * 0.98) * scale
    original_size = title_size
    title = book_title.strip() or "Word Search Book"

    while title_size > min_title_size:
        title_font = load_font(FONT_TITLE, title_size)
        title_lines = wrap_text(draw, title, title_font, max_width)
        widest = max((text_size(draw, line, title_font)[0] for line in title_lines), default=0)
        if widest <= max_width and len(title_lines) <= 4:
            break
        title_size = int(title_size * 0.90)

    title_font = load_font(FONT_TITLE, title_size)
    title_lines = wrap_text(draw, title, title_font, max_width)
    font_ratio = title_size / original_size

    if len(title_lines) > 4:
        warnings.append(
            _warning(
                severity="error",
                code="TITLE_PAGE_OVERFLOW_RISK",
                message="Book title still wraps beyond the intended title-page line limit after font reduction.",
                page_type="title_page",
                page_number=1,
                title=title,
                path=path,
                details={"line_count": len(title_lines), "font_ratio": round(font_ratio, 3)},
            )
        )
    elif font_ratio < 0.72 or len(title_lines) >= 4:
        warnings.append(
            _warning(
                severity="warning",
                code="TITLE_PAGE_DENSE_TITLE",
                message="Book title fits, but it is visually dense and should be reviewed on the title page.",
                page_type="title_page",
                page_number=1,
                title=title,
                path=path,
                details={"line_count": len(title_lines), "font_ratio": round(font_ratio, 3)},
            )
        )

    return warnings


def _analyze_block_covers(
    generated_puzzles: Sequence[GeneratedPuzzle],
    page_plan: PagePlan,
    *,
    draw: ImageDraw.ImageDraw,
    path_index: dict[str, str],
) -> list[RenderQualityWarning]:
    warnings: list[RenderQualityWarning] = []
    scale = 3
    page_w_hi = PAGE_W_PX * scale
    max_text_width = page_w_hi - 2 * int(page_w_hi * 0.10)
    base_size = int(TITLE_FONT_SIZE * 1.6) * scale
    min_size = int(TITLE_FONT_SIZE * 1.0) * scale

    block_names = []
    seen = set()
    for generated in generated_puzzles:
        block_name = (generated.spec.block_name or "").strip()
        if block_name and block_name not in seen:
            seen.add(block_name)
            block_names.append(block_name)

    for block_index, block_name in enumerate(block_names, start=1):
        font_size = base_size
        while font_size > min_size:
            font_title = load_font(FONT_TITLE, font_size)
            title_lines = wrap_text(draw, block_name, font_title, max_text_width)
            widest = max((text_size(draw, line, font_title)[0] for line in title_lines), default=0)
            if widest <= max_text_width:
                break
            font_size = int(font_size * 0.9)

        font_title = load_font(FONT_TITLE, font_size)
        title_lines = wrap_text(draw, block_name, font_title, max_text_width)
        font_ratio = font_size / base_size
        path = _find_block_cover_path(path_index, block_index)
        page_number = page_plan.block_first_page.get(block_name)

        if len(title_lines) > 3 or font_ratio < 0.68:
            warnings.append(
                _warning(
                    severity="warning",
                    code="BLOCK_COVER_DENSE_TITLE",
                    message="Block cover title is dense after wrapping/font reduction and should be reviewed.",
                    page_type="block_cover",
                    page_number=page_number,
                    title=block_name,
                    path=path,
                    details={
                        "block_index": block_index,
                        "line_count": len(title_lines),
                        "font_ratio": round(font_ratio, 3),
                    },
                )
            )

    return warnings


def _find_block_cover_path(path_index: dict[str, str], block_index: int) -> str | None:
    prefix = f"block_{block_index:02d}_"
    for stem, path in path_index.items():
        if stem.startswith(prefix):
            return path
    return None


def _analyze_puzzle_page(
    generated: GeneratedPuzzle,
    page_plan: PagePlan,
    *,
    draw: ImageDraw.ImageDraw,
    path: str | None,
    theme: ThemeConfig,
) -> list[RenderQualityWarning]:
    warnings: list[RenderQualityWarning] = []
    spec = generated.spec
    page_number = page_plan.puzzle_page.get(spec.index)
    title = spec.title

    layout = _measure_puzzle_layout(generated, draw=draw, theme=theme)

    warnings.extend(
        _analyze_puzzle_title(
            layout,
            spec_index=spec.index,
            page_number=page_number,
            title=title,
            path=path,
        )
    )
    warnings.extend(
        _analyze_fun_fact(
            layout,
            spec_index=spec.index,
            page_number=page_number,
            title=title,
            path=path,
        )
    )
    warnings.extend(
        _analyze_word_list(
            layout,
            spec_index=spec.index,
            page_number=page_number,
            title=title,
            path=path,
        )
    )
    warnings.extend(
        _analyze_grid_legibility(
            layout,
            spec_index=spec.index,
            page_number=page_number,
            title=title,
            path=path,
        )
    )

    return warnings


def _measure_puzzle_layout(
    generated: GeneratedPuzzle,
    *,
    draw: ImageDraw.ImageDraw,
    theme: ThemeConfig,
) -> dict[str, Any]:
    scale = 3
    frame = draw_page_frame(draw=draw, scale=scale, theme=theme)
    spec = generated.spec
    title_text = f"{spec.index + 1}. {spec.title}" if spec.title else f"Puzzle {spec.index + 1}"

    title_font = load_font(FONT_TITLE, TITLE_FONT_SIZE * scale)
    title_max_width = int(frame.content_right_hi - frame.content_left_hi)
    title_lines = wrap_text(draw, title_text, title_font, title_max_width)
    title_line_height = text_size(draw, "Ag", title_font)[1]
    y_after_title = frame.panel_top + int(25 * scale) + int(len(title_lines) * title_line_height * 1.05)
    y_cursor_hi = y_after_title + int(80 * scale)

    fact_metrics = _measure_fact_block(
        spec.fact,
        draw=draw,
        frame=frame,
        y_cursor_hi=y_cursor_hi,
        scale=scale,
    )

    rows = len(generated.grid)
    cols = len(generated.grid[0]) if rows else 0
    content_width_hi = frame.content_right_hi - frame.content_left_hi
    grid_width_target_hi = int(content_width_hi * 0.85)
    cell_size_hi = int(grid_width_target_hi / max(cols, 1))

    word_list_metrics = _measure_word_list(
        spec.words,
        draw=draw,
        frame=frame,
        grid_rows=rows,
        grid_cols=cols,
        cell_size_hi=cell_size_hi,
        scale=scale,
    )

    return {
        "title_lines": title_lines,
        "title_text": title_text,
        "fact": fact_metrics,
        "word_list": word_list_metrics,
        "grid_rows": rows,
        "grid_cols": cols,
        "cell_size_px": round(cell_size_hi / scale, 2),
        "word_count": len(spec.words),
        "longest_word": max((str(word) for word in spec.words), key=len, default=""),
    }


def _measure_fact_block(
    fun_fact: str,
    *,
    draw: ImageDraw.ImageDraw,
    frame: Any,
    y_cursor_hi: int,
    scale: int,
) -> dict[str, Any]:
    if not fun_fact:
        return {"present": False}

    fact_label_font = load_font(FONT_PATH_BOLD, int(WORDLIST_FONT_SIZE * 0.9) * scale)
    fact_text_font_size_hi = int(WORDLIST_FONT_SIZE * 0.5) * scale
    fact_text_font = load_font(FONT_PATH, fact_text_font_size_hi)

    inner_horizontal_pad = int(18 * scale)
    max_text_width_hi = int((frame.content_right_hi - frame.content_left_hi) - 2 * inner_horizontal_pad)
    label_h = text_size(draw, "FUN FACT", fact_label_font)[1]
    header_height_hi = label_h + 2 * int(8 * scale)
    text_pad_v_hi = int(10 * scale)
    line_height_hi = int(fact_text_font.size * 1.10)
    min_gap_hi = int(30 * scale)

    min_fact_block_hi = header_height_hi + 2 * text_pad_v_hi + line_height_hi
    max_fact_height_hi = max(min_fact_block_hi, frame.grid_top_base - y_cursor_hi - min_gap_hi)
    fact_lines = wrap_text(draw, fun_fact, fact_text_font, max_text_width_hi)
    available_text_h = max(0, max_fact_height_hi - header_height_hi - 2 * text_pad_v_hi)
    max_lines_fit = max(1, available_text_h // line_height_hi)
    rendered_line_count = min(len(fact_lines), max_lines_fit)

    return {
        "present": True,
        "char_count": len(fun_fact),
        "line_count": len(fact_lines),
        "max_lines_fit": max_lines_fit,
        "rendered_line_count": rendered_line_count,
        "truncated": len(fact_lines) > max_lines_fit,
        "used_ratio": round(rendered_line_count / max(max_lines_fit, 1), 3),
    }


def _measure_word_list(
    words: Sequence[str],
    *,
    draw: ImageDraw.ImageDraw,
    frame: Any,
    grid_rows: int,
    grid_cols: int,
    cell_size_hi: int,
    scale: int,
) -> dict[str, Any]:
    words_upper = [str(word).upper() for word in words]
    if not words_upper:
        return {"present": False}

    safe_bottom_hi = frame.safe_bottom_hi
    content_left_hi = frame.content_left_hi
    content_right_hi = frame.content_right_hi
    grid_top_hi = frame.grid_top_base
    grid_bottom_hi = grid_top_hi + cell_size_hi * grid_rows
    base_gap_hi = int(60 * scale)
    gap_pill_to_words_hi = int(70 * scale)
    words_area_height_hi = int(850 * scale)
    words_bottom_hi = safe_bottom_hi - int(8 * scale)
    words_top_hi = max(0, words_bottom_hi - words_area_height_hi)

    pill_font = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.75) * scale)
    pill_text = "Solution on page 999"
    _, th_pill = text_size(draw, pill_text, pill_font)
    pad_h = int(16 * scale)
    box_h = th_pill + 2 * pad_h
    target_pill_y = words_top_hi - gap_pill_to_words_hi - box_h
    min_pill_y = grid_bottom_hi + base_gap_hi
    pill_y = max(min_pill_y, target_pill_y)
    desired_words_top_hi = pill_y + box_h + gap_pill_to_words_hi
    if desired_words_top_hi > words_top_hi:
        words_top_hi = desired_words_top_hi
    if words_top_hi > words_bottom_hi:
        words_top_hi = words_bottom_hi

    words_height_hi = max(0, words_bottom_hi - words_top_hi)
    words_inner_margin_hi = int(35 * scale)
    area_left_hi = content_left_hi + words_inner_margin_hi
    area_right_hi = content_right_hi - words_inner_margin_hi
    total_w_hi = area_right_hi - area_left_hi
    font_words_real = load_font(FONT_PATH, int(WORDLIST_FONT_SIZE * 0.6) * scale)
    line_h_hi = int(font_words_real.size * 1.12)
    max_lines_per_col = max(1, words_height_hi // line_h_hi)
    word_widths = {word: text_size(draw, word, font_words_real)[0] for word in words_upper}
    word_max_w = max(word_widths.values()) if word_widths else 0

    best_layout = None
    for col_count in range(2, 6):
        if col_count * max_lines_per_col < len(words_upper):
            continue
        col_w_hi = total_w_hi / col_count
        if word_max_w <= col_w_hi * 0.92:
            best_layout = (col_count, col_w_hi, False)
            break

    if best_layout is None:
        col_count = max(2, min(5, _ceil_div(len(words_upper), max_lines_per_col)))
        col_w_hi = total_w_hi / col_count
        best_layout = (col_count, col_w_hi, True)

    col_count, col_w_hi, forced_layout = best_layout
    required_lines_per_col = _ceil_div(len(words_upper), col_count)
    fill_ratio = required_lines_per_col / max(max_lines_per_col, 1)
    longest_by_width = max(word_widths, key=word_widths.get, default="")
    max_word_width_ratio = word_max_w / max(col_w_hi, 1)

    return {
        "present": True,
        "word_count": len(words_upper),
        "col_count": col_count,
        "max_lines_per_col": max_lines_per_col,
        "required_lines_per_col": required_lines_per_col,
        "fill_ratio": round(fill_ratio, 3),
        "forced_layout": forced_layout,
        "max_word_width_ratio": round(max_word_width_ratio, 3),
        "longest_by_width": longest_by_width,
        "words_height_px": round(words_height_hi / scale, 2),
        "grid_to_words_compacted": desired_words_top_hi > max(0, words_bottom_hi - words_area_height_hi),
        "grid_cols": grid_cols,
    }


def _ceil_div(value: int, divisor: int) -> int:
    return -(-value // max(divisor, 1))


def _analyze_puzzle_title(
    layout: dict[str, Any],
    *,
    spec_index: int,
    page_number: int | None,
    title: str,
    path: str | None,
) -> list[RenderQualityWarning]:
    line_count = len(layout["title_lines"])
    if line_count <= 3:
        return []
    return [
        _warning(
            severity="warning" if line_count == 4 else "error",
            code="PUZZLE_TITLE_DENSE",
            message="Puzzle title wraps to many lines and may crowd the fact/card area.",
            page_type="puzzle",
            page_number=page_number,
            puzzle_index=spec_index,
            title=title,
            path=path,
            details={"line_count": line_count, "title_text": layout["title_text"]},
        )
    ]


def _analyze_fun_fact(
    layout: dict[str, Any],
    *,
    spec_index: int,
    page_number: int | None,
    title: str,
    path: str | None,
) -> list[RenderQualityWarning]:
    fact = layout["fact"]
    if not fact.get("present"):
        return []

    warnings: list[RenderQualityWarning] = []
    if fact["truncated"]:
        warnings.append(
            _warning(
                severity="warning",
                code="FACT_TRUNCATED",
                message="Fun fact is expected to be truncated in the rendered card.",
                page_type="puzzle",
                page_number=page_number,
                puzzle_index=spec_index,
                title=title,
                path=path,
                details=fact,
            )
        )
    elif fact["used_ratio"] >= 0.92 and fact["line_count"] >= 3:
        warnings.append(
            _warning(
                severity="info",
                code="FACT_CARD_TIGHT",
                message="Fun fact fits but uses nearly all available card text space.",
                page_type="puzzle",
                page_number=page_number,
                puzzle_index=spec_index,
                title=title,
                path=path,
                details=fact,
            )
        )
    return warnings


def _analyze_word_list(
    layout: dict[str, Any],
    *,
    spec_index: int,
    page_number: int | None,
    title: str,
    path: str | None,
) -> list[RenderQualityWarning]:
    word_list = layout["word_list"]
    if not word_list.get("present"):
        return []

    warnings: list[RenderQualityWarning] = []
    if word_list["forced_layout"] or word_list["max_word_width_ratio"] > 0.98:
        warnings.append(
            _warning(
                severity="warning",
                code="WORD_LIST_COLUMN_OVERFLOW_RISK",
                message="At least one word is likely too wide for the computed word-list columns.",
                page_type="puzzle",
                page_number=page_number,
                puzzle_index=spec_index,
                title=title,
                path=path,
                details=word_list,
            )
        )
    elif word_list["fill_ratio"] >= 0.90 or word_list["word_count"] >= 24:
        warnings.append(
            _warning(
                severity="info",
                code="WORD_LIST_DENSE",
                message="Word list fits but is dense enough to deserve manual review.",
                page_type="puzzle",
                page_number=page_number,
                puzzle_index=spec_index,
                title=title,
                path=path,
                details=word_list,
            )
        )

    if word_list["grid_to_words_compacted"]:
        warnings.append(
            _warning(
                severity="info",
                code="GRID_WORD_LIST_SPACING_TIGHT",
                message="The lower area was compacted to keep the solution pill and word list inside safe bounds.",
                page_type="puzzle",
                page_number=page_number,
                puzzle_index=spec_index,
                title=title,
                path=path,
                details=word_list,
            )
        )

    return warnings


def _analyze_grid_legibility(
    layout: dict[str, Any],
    *,
    spec_index: int,
    page_number: int | None,
    title: str,
    path: str | None,
) -> list[RenderQualityWarning]:
    cell_size_px = layout["cell_size_px"]
    if cell_size_px >= 42:
        return []
    return [
        _warning(
            severity="warning" if cell_size_px >= 36 else "error",
            code="GRID_CELL_SMALL",
            message="Grid cells are small for print readability; review this page at actual trim size.",
            page_type="puzzle",
            page_number=page_number,
            puzzle_index=spec_index,
            title=title,
            path=path,
            details={
                "cell_size_px": cell_size_px,
                "grid_rows": layout["grid_rows"],
                "grid_cols": layout["grid_cols"],
            },
        )
    ]
