from pathlib import Path

from PIL import Image
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX, TRIM_H_IN, TRIM_W_IN
from wordsearch.validation import kdp
from wordsearch.validation.kdp import build_kdp_preflight_report, write_kdp_preflight_report


def create_sample_png(path: Path, size: tuple[int, int] = (PAGE_W_PX, PAGE_H_PX)) -> str:
    image = Image.new("RGB", size, (255, 255, 255))
    image.save(path)
    return str(path)


def create_sample_pdf(
    path: Path,
    *,
    pages: int = 3,
    width_in: float = TRIM_W_IN,
    height_in: float = TRIM_H_IN,
    metadata: dict[str, str] | None = None,
) -> str:
    c = canvas.Canvas(str(path), pagesize=(width_in * inch, height_in * inch))
    metadata = metadata or {}
    if title := metadata.get("title"):
        c.setTitle(title)
    if author := metadata.get("author"):
        c.setAuthor(author)
    if subject := metadata.get("subject"):
        c.setSubject(subject)
    if keywords := metadata.get("keywords"):
        c.setKeywords(keywords)
    if creator := metadata.get("creator"):
        c.setCreator(creator)

    for index in range(pages):
        c.drawString(72, 72, f"Page {index + 1}")
        c.showPage()
    c.save()
    return str(path)


def patch_required_fonts(monkeypatch, tmp_path: Path) -> None:
    regular = tmp_path / "regular.ttf"
    bold = tmp_path / "bold.ttf"
    title = tmp_path / "title.ttf"
    for font_path in (regular, bold, title):
        font_path.write_text("fake font for path preflight tests", encoding="utf-8")

    monkeypatch.setattr(kdp, "FONT_PATH", str(regular))
    monkeypatch.setattr(kdp, "FONT_PATH_BOLD", str(bold))
    monkeypatch.setattr(kdp, "FONT_TITLE", str(title))


def test_build_kdp_preflight_report_passes_for_expected_files(tmp_path, monkeypatch):
    patch_required_fonts(monkeypatch, tmp_path)
    metadata = {
        "title": "Book Title",
        "subject": "Subject",
        "keywords": "word search, KDP",
        "creator": "sopa-libros",
    }
    pdf_path = create_sample_pdf(tmp_path / "book.pdf", metadata=metadata)
    content_img = create_sample_png(tmp_path / "content.png")
    solution_img = create_sample_png(tmp_path / "solution.png")

    report = build_kdp_preflight_report(
        pdf_path=pdf_path,
        output_dir=str(tmp_path),
        content_image_paths=[content_img],
        solution_image_paths=[solution_img],
        expected_pdf_metadata=metadata,
    )

    assert report.schema_version == 2
    assert report.expected_page_count == 3
    assert report.actual_page_count == 3
    assert report.actual_page_width_in == TRIM_W_IN
    assert report.actual_page_height_in == TRIM_H_IN
    assert report.actual_pdf_metadata["title"] == "Book Title"
    assert report.content_image_count == 1
    assert report.solution_image_count == 1
    assert report.passed
    assert report.errors == []


def test_build_kdp_preflight_report_flags_wrong_image_size(tmp_path, monkeypatch):
    patch_required_fonts(monkeypatch, tmp_path)
    pdf_path = create_sample_pdf(tmp_path / "book.pdf")
    content_img = create_sample_png(tmp_path / "content.png", size=(100, 100))
    solution_img = create_sample_png(tmp_path / "solution.png")

    report = build_kdp_preflight_report(
        pdf_path=pdf_path,
        output_dir=str(tmp_path),
        content_image_paths=[content_img],
        solution_image_paths=[solution_img],
    )

    assert not report.passed
    assert any("tamano esperado" in issue.message for issue in report.errors)


def test_build_kdp_preflight_report_flags_wrong_pdf_page_count(tmp_path, monkeypatch):
    patch_required_fonts(monkeypatch, tmp_path)
    pdf_path = create_sample_pdf(tmp_path / "book.pdf", pages=2)
    content_img = create_sample_png(tmp_path / "content.png")
    solution_img = create_sample_png(tmp_path / "solution.png")

    report = build_kdp_preflight_report(
        pdf_path=pdf_path,
        output_dir=str(tmp_path),
        content_image_paths=[content_img],
        solution_image_paths=[solution_img],
    )

    assert not report.passed
    assert report.actual_page_count == 2
    assert any("paginas reales" in issue.message for issue in report.errors)


def test_build_kdp_preflight_report_flags_wrong_pdf_page_size(tmp_path, monkeypatch):
    patch_required_fonts(monkeypatch, tmp_path)
    pdf_path = create_sample_pdf(tmp_path / "book.pdf", width_in=8.5, height_in=11)
    content_img = create_sample_png(tmp_path / "content.png")
    solution_img = create_sample_png(tmp_path / "solution.png")

    report = build_kdp_preflight_report(
        pdf_path=pdf_path,
        output_dir=str(tmp_path),
        content_image_paths=[content_img],
        solution_image_paths=[solution_img],
    )

    assert not report.passed
    assert report.actual_page_width_in == 8.5
    assert report.actual_page_height_in == 11
    assert any("tamano fisico" in issue.message for issue in report.errors)


def test_build_kdp_preflight_report_warns_for_metadata_mismatch(tmp_path, monkeypatch):
    patch_required_fonts(monkeypatch, tmp_path)
    pdf_path = create_sample_pdf(tmp_path / "book.pdf", metadata={"title": "Actual Title"})
    content_img = create_sample_png(tmp_path / "content.png")
    solution_img = create_sample_png(tmp_path / "solution.png")

    report = build_kdp_preflight_report(
        pdf_path=pdf_path,
        output_dir=str(tmp_path),
        content_image_paths=[content_img],
        solution_image_paths=[solution_img],
        expected_pdf_metadata={"title": "Expected Title"},
    )

    assert report.passed
    assert any("Metadata PDF inesperada" in issue.message for issue in report.warnings)


def test_build_kdp_preflight_report_warns_when_pdf_cannot_be_inspected(tmp_path, monkeypatch):
    patch_required_fonts(monkeypatch, tmp_path)
    pdf_path = tmp_path / "broken.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nnot a real pdf\n")
    content_img = create_sample_png(tmp_path / "content.png")
    solution_img = create_sample_png(tmp_path / "solution.png")

    report = build_kdp_preflight_report(
        pdf_path=str(pdf_path),
        output_dir=str(tmp_path),
        content_image_paths=[content_img],
        solution_image_paths=[solution_img],
    )

    assert report.passed
    assert any("No se pudo inspeccionar" in issue.message for issue in report.warnings)


def test_write_kdp_preflight_report_writes_json(tmp_path, monkeypatch):
    patch_required_fonts(monkeypatch, tmp_path)
    pdf_path = create_sample_pdf(tmp_path / "book.pdf")
    content_img = create_sample_png(tmp_path / "content.png")
    solution_img = create_sample_png(tmp_path / "solution.png")
    report = build_kdp_preflight_report(
        pdf_path=pdf_path,
        output_dir=str(tmp_path),
        content_image_paths=[content_img],
        solution_image_paths=[solution_img],
    )

    report_path = write_kdp_preflight_report(report, output_dir=str(tmp_path))

    written = Path(report_path)
    assert written.exists()
    written_text = written.read_text(encoding="utf-8")
    assert '"passed": true' in written_text
    assert '"actual_page_count": 3' in written_text
