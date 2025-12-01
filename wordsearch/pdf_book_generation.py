"""
Generación del PDF final a partir de las imágenes de puzzles y soluciones.
Incluye: portada, paginación, separación de secciones, etc.
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from wordsearch.constants_and_layout import TRIM_W_IN, TRIM_H_IN
from wordsearch.image_rendering import BACKGROUND_PATH

def generate_pdf(puzzle_imgs, solution_imgs, outname="wordsearch_book_kdp.pdf", background_path=None):
    # Se asume que las imágenes ya están generadas y listas
    # El output_dir debe estar incluido en outname si se quiere ruta completa
    if os.path.dirname(outname):
        pdf_path = outname
    else:
        pdf_path = os.path.join("output_puzzles_kdp", outname)
    c = canvas.Canvas(pdf_path, pagesize=(TRIM_W_IN*inch, TRIM_H_IN*inch))

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
            height=TRIM_H_IN * inch
        )
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(
            TRIM_W_IN * inch / 2,
            0.35 * inch,
            str(page_num)
        )
        c.showPage()
        page_num += 1

    # ---------------------------
    # PORTADA DE SOLUCIONES (con fondo)
    # ---------------------------
    bg_path = background_path or BACKGROUND_PATH
    if bg_path and os.path.exists(bg_path):
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
        "SOLUTIONS"
    )
    c.setFont("Helvetica", 10)
    c.drawCentredString(
        TRIM_W_IN * inch / 2,
        0.35 * inch,
        str(page_num)
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
            height=TRIM_H_IN * inch
        )
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(
            TRIM_W_IN * inch / 2,
            0.35 * inch,
            str(page_num)
        )
        c.showPage()
        page_num += 1

    c.save()
    return pdf_path
