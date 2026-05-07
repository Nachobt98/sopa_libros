from pathlib import Path

from PIL import Image

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
