"""Solution highlight rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from PIL import Image, ImageDraw

from wordsearch.domain.grid import PlacedWord


@dataclass
class SolutionHighlightLayer:
    """Transparent highlight overlay plus highlighted grid positions."""

    overlay: Image.Image
    positions: set[tuple[int, int]]


def build_solution_highlight_layer(
    *,
    placed_words: Sequence[PlacedWord] | None,
    rows: int,
    cols: int,
    grid_left_hi: int,
    grid_top_hi: int,
    cell_size_hi: int,
    page_w_hi: int,
    page_h_hi: int,
    scale: int,
    highlight_fill,
    highlight_border,
) -> SolutionHighlightLayer:
    """Build solution highlight capsules without applying them to the page."""
    highlight_positions: set[tuple[int, int]] = set()
    overlay_fill = Image.new("RGBA", (page_w_hi, page_h_hi), (0, 0, 0, 0))
    overlay_border = Image.new("RGBA", (page_w_hi, page_h_hi), (0, 0, 0, 0))
    odraw_fill = ImageDraw.Draw(overlay_fill)

    if placed_words:
        for placed_word in placed_words:
            row, col, d_row, d_col = placed_word.position
            word_len = len(placed_word.word)
            if word_len < 2:
                continue

            centers: List[Tuple[float, float]] = []
            for i in range(word_len):
                rr = row + d_row * i
                cc = col + d_col * i
                if rr < 0 or rr >= rows or cc < 0 or cc >= cols:
                    break

                x0 = grid_left_hi + cc * cell_size_hi
                y0 = grid_top_hi + rr * cell_size_hi
                cx = x0 + cell_size_hi / 2
                cy = y0 + cell_size_hi / 2
                centers.append((cx, cy))
                highlight_positions.add((rr, cc))

            if len(centers) < 2:
                continue

            p0 = centers[0]
            p1 = centers[-1]
            thickness = cell_size_hi * 0.67
            radius = thickness / 2

            odraw_fill.line(
                centers,
                fill=highlight_fill,
                width=int(thickness),
                joint="curve",
            )
            for cx, cy in (p0, p1):
                odraw_fill.ellipse(
                    (cx - radius, cy - radius, cx + radius, cy + radius),
                    fill=highlight_fill,
                )

            tmp_border = Image.new("RGBA", (page_w_hi, page_h_hi), (0, 0, 0, 0))
            bdraw = ImageDraw.Draw(tmp_border)

            outer_width = int(thickness + 8 * scale)
            inner_width = int(thickness)
            outer_radius = radius + 4 * scale
            inner_radius = radius

            bdraw.line(
                centers,
                fill=highlight_border,
                width=outer_width,
                joint="curve",
            )
            for cx, cy in (p0, p1):
                bdraw.ellipse(
                    (
                        cx - outer_radius,
                        cy - outer_radius,
                        cx + outer_radius,
                        cy + outer_radius,
                    ),
                    fill=highlight_border,
                )

            transparent = (0, 0, 0, 0)
            bdraw.line(
                centers,
                fill=transparent,
                width=inner_width,
                joint="curve",
            )
            for cx, cy in (p0, p1):
                bdraw.ellipse(
                    (
                        cx - inner_radius,
                        cy - inner_radius,
                        cx + inner_radius,
                        cy + inner_radius,
                    ),
                    fill=transparent,
                )

            overlay_border.alpha_composite(tmp_border)

    overlay = Image.new("RGBA", (page_w_hi, page_h_hi), (0, 0, 0, 0))
    overlay.alpha_composite(overlay_fill)
    overlay.alpha_composite(overlay_border)

    return SolutionHighlightLayer(
        overlay=overlay,
        positions=highlight_positions,
    )
