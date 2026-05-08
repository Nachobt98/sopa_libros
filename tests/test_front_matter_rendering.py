from pathlib import Path

from PIL import Image

from wordsearch.config.design import DEFAULT_THEME, KIDS_THEME, PREMIUM_NEUTRAL_THEME
from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.rendering import front_matter
from wordsearch.rendering.front_matter import (
    _draw_main_panel,
    _make_background,
    _measure_instruction_block_height,
    render_instructions_page,
    render_table_of_contents,
)
from wordsearch.rendering.common import load_font
from wordsearch.config.fonts import FONT_PATH, FONT_PATH_BOLD


def assert_valid_png(path: str | Path) -> Image.Image:
    output = Path(path)
    assert output.exists()
    assert output.stat().st_size > 0

    image = Image.open(output)
    assert image.format == "PNG"
    assert image.size == (PAGE_W_PX, PAGE_H_PX)
    return image


def test_make_background_uses_theme_fill_when_background_is_missing():
    image = _make_background("missing-background.png", 1, theme=KIDS_THEME)

    assert image.size == (PAGE_W_PX, PAGE_H_PX)
    assert image.getpixel((0, 0)) == KIDS_THEME.page_background_fill


def test_make_background_applies_theme_opacity_to_existing_background(tmp_path):
    background_path = tmp_path / "bg.png"
    Image.new("RGBA", (10, 10), (10, 20, 30, 200)).save(background_path)

    image = _make_background(str(background_path), 1, theme=PREMIUM_NEUTRAL_THEME)

    assert image.size == (PAGE_W_PX, PAGE_H_PX)
    assert image.getpixel((0, 0))[3] == int(200 * PREMIUM_NEUTRAL_THEME.background_opacity)


def test_draw_main_panel_returns_expected_bounds_and_changes_canvas():
    image = Image.new("RGBA", (PAGE_W_PX, PAGE_H_PX), DEFAULT_THEME.page_background_fill)
    before = image.copy()
    draw = Image.Draw.Draw(image) if hasattr(Image, "Draw") else None
    # Pillow exposes ImageDraw as a separate module in normal runtime; import locally
    # to keep this assertion independent from renderer internals.
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    bounds = _draw_main_panel(draw, 1, theme=PREMIUM_NEUTRAL_THEME)

    assert bounds == (110, 105, PAGE_W_PX - 110, PAGE_H_PX - 150)
    assert image.tobytes() != before.tobytes()


def test_measure_instruction_block_height_increases_with_wrapped_content():
    image = Image.new("RGBA", (PAGE_W_PX, PAGE_H_PX), DEFAULT_THEME.page_background_fill)
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    number_font = load_font(FONT_PATH_BOLD, 24)
    body_font = load_font(FONT_PATH, 22)

    short_height = _measure_instruction_block_height(
        draw,
        ["Short instruction."],
        number_font,
        body_font,
        max_text_width=500,
        row_gap=20,
    )
    wrapped_height = _measure_instruction_block_height(
        draw,
        ["This instruction is intentionally long enough to wrap across several rendered lines."],
        number_font,
        body_font,
        max_text_width=120,
        row_gap=20,
    )

    assert short_height > 0
    assert wrapped_height > short_height


def test_render_table_of_contents_creates_png_with_theme_and_solutions_separator(tmp_path):
    output_files = render_table_of_contents(
        [
            ("Foundations", 4, True),
            ("Arts and Literature", 12, True),
            ("Solutions", 32, True),
        ],
        output_dir=str(tmp_path),
        background_path=None,
        theme=PREMIUM_NEUTRAL_THEME,
    )

    assert len(output_files) == 1
    image = assert_valid_png(output_files[0])
    assert len(set(image.resize((16, 16)).getdata())) > 1


def test_render_instructions_page_creates_png_with_default_filename(tmp_path, monkeypatch):
    monkeypatch.setattr(front_matter, "build_default_output_file", lambda name: str(tmp_path / name))

    output_file = render_instructions_page(
        "Book Title",
        filename=None,
        background_path=None,
        theme=KIDS_THEME,
    )

    image = assert_valid_png(output_file)
    assert Path(output_file).name == "02_instructions.png"
    assert len(set(image.resize((16, 16)).getdata())) > 1


def test_render_instructions_page_uses_explicit_filename(tmp_path):
    output_file = tmp_path / "custom_instructions.png"

    returned = render_instructions_page(
        "Book Title",
        filename=str(output_file),
        background_path=None,
        theme=PREMIUM_NEUTRAL_THEME,
    )

    assert returned == str(output_file)
    assert_valid_png(returned)
