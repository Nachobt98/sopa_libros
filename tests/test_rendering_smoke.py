from pathlib import Path

from PIL import Image, ImageChops

from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.domain.grid import PlacedWord
from wordsearch.rendering.block_cover import render_block_cover
from wordsearch.rendering.puzzle_page import render_page
from wordsearch.rendering.solution_page import render_solution_page


def assert_valid_non_blank_png(path: Path) -> None:
    assert path.exists()
    assert path.stat().st_size > 0

    with Image.open(path) as image:
        assert image.format == "PNG"
        assert image.size == (PAGE_W_PX, PAGE_H_PX)
        rgba = image.convert("RGBA")
        blank = Image.new("RGBA", rgba.size, rgba.getpixel((0, 0)))
        assert ImageChops.difference(rgba, blank).getbbox() is not None


def sample_grid() -> list[list[str]]:
    return [
        list("CATDOG"),
        list("AAAAAA"),
        list("BBBBBB"),
        list("CCCCCC"),
        list("DDDDDD"),
        list("EEEEEE"),
    ]


def test_render_puzzle_page_creates_valid_png(tmp_path):
    output_path = tmp_path / "puzzle.png"

    returned_path = render_page(
        sample_grid(),
        ["CAT", "DOG", "ALPHA", "BETA"],
        1,
        filename=str(output_path),
        puzzle_title="Smoke Test Puzzle",
        fun_fact="This page is rendered by a smoke test to catch basic rendering regressions.",
        solution_page_number=12,
    )

    assert returned_path == str(output_path)
    assert_valid_non_blank_png(output_path)


def test_render_solution_page_creates_valid_png(tmp_path):
    output_path = tmp_path / "solution.png"

    returned_path = render_solution_page(
        sample_grid(),
        ["CAT", "DOG"],
        1,
        filename=str(output_path),
        placed_words=[
            PlacedWord("CAT", 0, 0, 0, 1),
            PlacedWord("DOG", 0, 3, 0, 1),
        ],
        puzzle_title="Smoke Test Puzzle",
    )

    assert returned_path == str(output_path)
    assert_valid_non_blank_png(output_path)


def test_render_block_cover_creates_valid_png(tmp_path):
    output_path = tmp_path / "block_cover.png"

    returned_path = render_block_cover(
        block_name="Smoke Test Block",
        block_index=1,
        filename=str(output_path),
        background_path=None,
    )

    assert returned_path == str(output_path)
    assert_valid_non_blank_png(output_path)
