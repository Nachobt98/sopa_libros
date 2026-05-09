"""PDF assembly from rendered puzzle and solution page images."""

from pathlib import Path
from typing import Mapping

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from wordsearch.config.design import DEFAULT_LAYOUT, LayoutConfig
from wordsearch.config.paths import resolve_pdf_output_path
from wordsearch.rendering.backgrounds import BACKGROUND_PATH

PdfMetadata = Mapping[str, str | None]


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
    pdf_path = resolve_pdf_output_path(outname)
    c = canvas.Canvas(pdf_path, pagesize=(layout.trim_width_in * inch, layout.trim_height_in * inch))
    _apply_pdf_metadata(c, metadata)

    page_num = 1
    for img in puzzle_imgs:
        c.drawImage(img, 0, 0, width=layout.trim_width_in * inch, height=layout.trim_height_in * inch)
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(layout.trim_width_in * inch / 2, 0.35 * inch, str(page_num))
        c.showPage()
        page_num += 1

    bg_path = background_path or BACKGROUND_PATH
    if bg_path and Path(bg_path).exists():
        c.drawImage(bg_path, 0, 0, width=layout.trim_width_in * inch, height=layout.trim_height_in * inch, mask="auto")

    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(layout.trim_width_in * inch / 2, layout.trim_height_in * inch / 2, "SOLUTIONS")
    c.setFont("Helvetica", 10)
    c.drawCentredString(layout.trim_width_in * inch / 2, 0.35 * inch, str(page_num))
    c.showPage()
    page_num += 1

    for img in solution_imgs:
        c.drawImage(img, 0, 0, width=layout.trim_width_in * inch, height=layout.trim_height_in * inch)
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(layout.trim_width_in * inch / 2, 0.35 * inch, str(page_num))
        c.showPage()
        page_num += 1

    c.save()
    return pdf_path
