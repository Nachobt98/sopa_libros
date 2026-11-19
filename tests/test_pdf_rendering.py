from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

from wordsearch.config.formats import FORMAT_PRESETS
from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.rendering.pdf import generate_pdf


def create_sample_png(path: Path, color: tuple[int, int, int]) -> str:
    image = Image.new("RGB", (PAGE_W_PX, PAGE_H_PX), color)
    image.save(path)
    return str(path)


def assert_valid_pdf(path: Path) -> None:
    assert path.exists()
    assert path.stat().st_size > 0
    assert path.read_bytes().startswith(b"%PDF")


def test_generate_pdf_creates_valid_pdf_from_images(tmp_path):
    puzzle_img = create_sample_png(tmp_path / "puzzle.png", (255, 255, 255))
    solution_img = create_sample_png(tmp_path / "solution.png", (240, 240, 240))
    pdf_path = tmp_path / "book.pdf"

    returned_path = generate_pdf(
        [puzzle_img],
        [solution_img],
        outname=str(pdf_path),
    )

    assert returned_path == str(pdf_path)
    assert_valid_pdf(pdf_path)


def test_generate_pdf_accepts_multiple_puzzle_and_solution_images(tmp_path):
    puzzle_imgs = [
        create_sample_png(tmp_path / "puzzle_1.png", (255, 255, 255)),
        create_sample_png(tmp_path / "puzzle_2.png", (245, 245, 245)),
    ]
    solution_imgs = [
        create_sample_png(tmp_path / "solution_1.png", (235, 235, 235)),
        create_sample_png(tmp_path / "solution_2.png", (225, 225, 225)),
    ]
    pdf_path = tmp_path / "multi_page_book.pdf"

    returned_path = generate_pdf(
        puzzle_imgs,
        solution_imgs,
        outname=str(pdf_path),
    )

    assert returned_path == str(pdf_path)
    assert_valid_pdf(pdf_path)


def test_generate_pdf_writes_basic_metadata(tmp_path):
    puzzle_img = create_sample_png(tmp_path / "puzzle.png", (255, 255, 255))
    solution_img = create_sample_png(tmp_path / "solution.png", (240, 240, 240))
    pdf_path = tmp_path / "metadata_book.pdf"

    generate_pdf(
        [puzzle_img],
        [solution_img],
        outname=str(pdf_path),
        metadata={
            "title": "Metadata Book",
            "author": "Author Name",
            "subject": "Puzzle Book",
            "keywords": "word search, KDP",
            "creator": "sopa-libros",
        },
    )

    assert_valid_pdf(pdf_path)
    metadata = PdfReader(str(pdf_path)).metadata
    assert metadata["/Title"] == "Metadata Book"
    assert metadata["/Author"] == "Author Name"
    assert metadata["/Subject"] == "Puzzle Book"
    assert metadata["/Keywords"] == "word search, KDP"
    assert metadata["/Creator"] == "sopa-libros"


@pytest.mark.parametrize("preset", FORMAT_PRESETS.values(), ids=FORMAT_PRESETS.keys())
@pytest.mark.parametrize("page_count,gutter", [(4, 27), (150, 27), (151, 36), (300, 36), (301, 45), (500, 45), (501, 54), (700, 54), (701, 63)])
def test_no_bleed_preserves_design_inside_mirrored_margins(tmp_path, preset, page_count, gutter):
    layout = preset.to_layout_config()
    image_path = tmp_path / "edge_to_edge.png"
    Image.new("RGB", (8, 8), "red").save(image_path)
    pdf_path = generate_pdf(
        [str(image_path)] * (page_count - 2),
        [str(image_path)],
        outname=str(tmp_path / "no_bleed.pdf"),
        background_path=str(image_path),
        layout=layout,
    )
    reader = PdfReader(pdf_path)
    width, height = layout.trim_width_in * 72, layout.trim_height_in * 72
    assert len(reader.pages) == page_count
    for number, page in enumerate(reader.pages, start=1):
        assert float(page.mediabox.width) == width
        assert float(page.mediabox.height) == height
        operations = page.get_contents().operations
        rectangles = [list(map(float, args)) for args, op in operations if op == b"re"]
        assert len(rectangles) == 1
        left, bottom, printed_width, printed_height = rectangles[0]
        right = width - left - printed_width
        assert left == pytest.approx(gutter if number % 2 else 18, abs=0.001)
        assert right == pytest.approx(18 if number % 2 else gutter, abs=0.001)
        assert bottom >= 18
        assert height - bottom - printed_height >= 18 - 0.001
        operators = [op for _, op in operations]
        clip_index = operators.index(b"W*")
        image_index = operators.index(b"Do")
        assert clip_index < image_index
        # Uniform scaling preserves square cells. The original printed area
        # maps exactly onto the clip, so none of the existing design is lost.
        transforms = [list(map(float, args)) for args, op in operations if op == b"cm"]
        w, skew_y, skew_x, h, x, y = transforms[-1]
        sx, sy = w / width, h / height
        assert sx == pytest.approx(sy, abs=0.000001)
        assert skew_y == skew_x == 0
        assert x + 18 * sx == pytest.approx(left, abs=0.001)
        assert y + 18 * sy == pytest.approx(bottom, abs=0.001)
        assert (width - 36) * sx == pytest.approx(printed_width, abs=0.001)
        assert (height - 36) * sy == pytest.approx(printed_height, abs=0.001)
        # Both drawImage's and our own saved states are restored before text.
        assert operators[image_index + 1:image_index + 3] == [b"Q", b"Q"]
