"""
Generación del PDF final a partir de las imágenes de puzzles y soluciones.
Incluye: portada, paginación, separación de secciones, etc.
"""

from pathlib import Path
from typing import Mapping

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from wordsearch.config.layout import TRIM_H_IN, TRIM_W_IN
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
):
    # Se asume que las imágenes ya están generadas y listas
    # El output_dir debe estar incluido en outname si se quiere ruta completa
    pdf_path = resolve_pdf_output_path(outname)
    c = canvas.Canvas(pdf_path, pagesize=(TRIM_W_IN * inch, TRIM_H_IN * inch))
    _apply_pdf_metadata(c, metadata)

    page_num = 1  # contador de página

    # ---------------------------
    # PÁGINAS DE PUZZLES
    # ---------------------------
    for img in puzzle_imgs:
        c.drawImage(
            img,
            0,
            0,
            width=TRIM_W_IN * inch,
            height=TRIM_H_IN * inch,
        )
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(
            TRIM_W_IN * inch / 2,
            0.35 * inch,
            str(page_num),
        )
        c.showPage()
        page_num += 1

    # ---------------------------
    # PORTADA DE SOLUCIONES (con fondo)
    # ---------------------------
    bg_path = background_path or BACKGROUND_PATH
    if bg_path and Path(bg_path).exists():
        c.drawImage(
            bg_path,
            0,
            0,
            width=TRIM_W_IN * inch,
            height=TRIM_H_IN * inch,
            mask="auto",
        )

    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(
        TRIM_W_IN * inch / 2,
        TRIM_H_IN * inch / 2,
        "SOLUTIONS",
    )
    c.setFont("Helvetica", 10)
    c.drawCentredString(
        TRIM_W_IN * inch / 2,
        0.35 * inch,
        str(page_num),
    )
    c.showPage()
    page_num += 1

    # ---------------------------
    # PÁGINAS DE SOLUCIONES
    # ---------------------------
    for img in solution_imgs:
        c.drawImage(
            img,
            0,
            0,
            width=TRIM_W_IN * inch,
            height=TRIM_H_IN * inch,
        )
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(
            TRIM_W_IN * inch / 2,
            0.35 * inch,
            str(page_num),
        )
        c.showPage()
        page_num += 1

    c.save()
    return pdf_path
