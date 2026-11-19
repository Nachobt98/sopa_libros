"""PDF assembly from rendered puzzle and solution page images."""

from pathlib import Path
from typing import Mapping

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from wordsearch.config.design import DEFAULT_LAYOUT, LayoutConfig
from wordsearch.config.formats import KDP_MIN_OUTSIDE_MARGIN_NO_BLEED_IN, minimum_gutter_in
from wordsearch.config.paths import resolve_pdf_output_path
from wordsearch.rendering.backgrounds import BACKGROUND_PATH

PdfMetadata = Mapping[str, str | None]


def _draw_no_bleed_image(c: canvas.Canvas, image, layout: LayoutConfig, *, page_number: int, gutter_in: float, mask=None) -> None:
    """Fit the existing no-bleed design inside mirrored binding margins.

    Preserve the complete source print area (trim minus 0.25 inches on each
    edge). Scale uniformly, so grids stay square and panel outlines survive.
    Odd PDF pages bind on the left; even pages bind on the right.
    """
    width = layout.trim_width_in * inch
    height = layout.trim_height_in * inch
    margin = KDP_MIN_OUTSIDE_MARGIN_NO_BLEED_IN * inch
    gutter = gutter_in * inch
    left = gutter if page_number % 2 else margin
    print_width = width - gutter - margin
    scale = print_width / (width - 2 * margin)
    print_height = (height - 2 * margin) * scale
    bottom = (height - print_height) / 2
    c.saveState()
    clip = c.beginPath()
    clip.rect(left, bottom, print_width, print_height)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(image, left - margin * scale, bottom - margin * scale,
                width=width * scale, height=height * scale, mask=mask)
    c.restoreState()


def _apply_pdf_metadata(c: canvas.Canvas, metadata: PdfMetadata | None) -> None:
    """Apply basic document metadata when provided."""
    if not metadata:
        return

    title = metadata.get("title")
    author = metadata.get("author")
    subject = metadata.get("subject")
    keywords = metadata.get("keywords")
    creator = metadata.get("creator")

    if title:
        c.setTitle(title)
    if author:
        c.setAuthor(author)
    if subject:
        c.setSubject(subject)
    if keywords:
        c.setKeywords(keywords)
    if creator:
        c.setCreator(creator)


def generate_pdf(
    puzzle_imgs,
    solution_imgs,
    outname="wordsearch_book_kdp.pdf",
    background_path=None,
    metadata: PdfMetadata | None = None,
    layout: LayoutConfig = DEFAULT_LAYOUT,
):
    puzzle_imgs = list(puzzle_imgs)
    solution_imgs = list(solution_imgs)
    gutter = minimum_gutter_in(len(puzzle_imgs) + 1 + len(solution_imgs))
    pdf_path = resolve_pdf_output_path(outname)
    c = canvas.Canvas(pdf_path, pagesize=(layout.trim_width_in * inch, layout.trim_height_in * inch))
    _apply_pdf_metadata(c, metadata)

    page_num = 1
    for img in puzzle_imgs:
        _draw_no_bleed_image(c, img, layout, page_number=page_num, gutter_in=gutter)
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(_print_center_x(layout, page_num, gutter), 0.35 * inch, str(page_num))
        c.showPage()
        page_num += 1

    bg_path = background_path or BACKGROUND_PATH
    if bg_path and Path(bg_path).exists():
        _draw_no_bleed_image(c, bg_path, layout, page_number=page_num, gutter_in=gutter, mask="auto")

    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(_print_center_x(layout, page_num, gutter), layout.trim_height_in * inch / 2, "SOLUTIONS")
    c.setFont("Helvetica", 10)
    c.drawCentredString(_print_center_x(layout, page_num, gutter), 0.35 * inch, str(page_num))
    c.showPage()
    page_num += 1

    for img in solution_imgs:
        _draw_no_bleed_image(c, img, layout, page_number=page_num, gutter_in=gutter)
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(_print_center_x(layout, page_num, gutter), 0.35 * inch, str(page_num))
        c.showPage()
        page_num += 1

    c.save()
    return pdf_path


def _print_center_x(layout: LayoutConfig, page_number: int, gutter_in: float) -> float:
    offset = (gutter_in - KDP_MIN_OUTSIDE_MARGIN_NO_BLEED_IN) * inch / 2
    return layout.trim_width_in * inch / 2 + (offset if page_number % 2 else -offset)
