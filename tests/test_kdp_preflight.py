from pathlib import Path

from PIL import Image

from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.validation import kdp
from wordsearch.validation.kdp import build_kdp_preflight_report, write_kdp_preflight_report


def create_sample_png(path: Path, size: tuple[int, int] = (PAGE_W_PX, PAGE_H_PX)) -> str:
    image = Image.new("RGB", size, (255, 255, 255))
    image.save(path)
    return str(path)


def create_sample_pdf(path: Path) -> str:
    path.write_bytes(b"%PDF-1.4\n% baseline test pdf\n")
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
    pdf_path = create_sample_pdf(tmp_path / "book.pdf")
    content_img = create_sample_png(tmp_path / "content.png")
    solution_img = create_sample_png(tmp_path / "solution.png")

    report = build_kdp_preflight_report(
        pdf_path=pdf_path,
        output_dir=str(tmp_path),
        content_image_paths=[content_img],
        solution_image_paths=[solution_img],
    )

    assert report.expected_page_count == 3
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
    assert '"passed": true' in written.read_text(encoding="utf-8")
