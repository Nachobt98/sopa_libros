from pathlib import Path

from PIL import Image, ImageDraw

from wordsearch.config.design import DEFAULT_THEME, KIDS_THEME, PREMIUM_NEUTRAL_THEME
from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.rendering import title_page
from wordsearch.rendering.title_page import (
    _draw_ornamental_separator,
    _draw_soft_panel,
    render_title_page,
)


def assert_valid_png(path: str | Path) -> Image.Image:
    output = Path(path)
    assert output.exists()
    assert output.stat().st_size > 0

    image = Image.open(output)
    assert image.format == "PNG"
    assert image.size == (PAGE_W_PX, PAGE_H_PX)
    return image


def test_draw_soft_panel_changes_canvas():
    image = Image.new("RGBA", (PAGE_W_PX, PAGE_H_PX), DEFAULT_THEME.page_background_fill)
    before = image.copy()
    draw = ImageDraw.Draw(image)

    _draw_soft_panel(draw, 1, theme=PREMIUM_NEUTRAL_THEME)

    assert image.tobytes() != before.tobytes()


def test_draw_ornamental_separator_changes_expected_area():
    image = Image.new("RGBA", (PAGE_W_PX, PAGE_H_PX), DEFAULT_THEME.page_background_fill)
    before = image.copy()
    draw = ImageDraw.Draw(image)

    _draw_ornamental_separator(
        draw,
        center_x=PAGE_W_PX // 2,
        y=400,
        width=320,
        scale=1,
        theme=KIDS_THEME,
    )

    assert image.tobytes() != before.tobytes()
    assert image.getpixel((PAGE_W_PX // 2, 400)) == KIDS_THEME.title_color


def test_render_title_page_creates_png_with_explicit_filename(tmp_path):
    output_file = tmp_path / "title.png"

    returned = render_title_page(
        "Visual Baseline",
        subtitle="A compact subtitle",
        filename=str(output_file),
        background_path=None,
        theme=PREMIUM_NEUTRAL_THEME,
    )

    assert returned == str(output_file)
    image = assert_valid_png(returned)
    assert len(set(image.resize((16, 16)).getdata())) > 1


def test_render_title_page_uses_default_title_for_blank_input(tmp_path):
    output_file = tmp_path / "blank_title.png"

    returned = render_title_page(
        "   ",
        filename=str(output_file),
        background_path=None,
        theme=KIDS_THEME,
    )

    image = assert_valid_png(returned)
    assert len(set(image.resize((16, 16)).getdata())) > 1


def test_render_title_page_reduces_font_for_long_titles(tmp_path):
    output_file = tmp_path / "long_title.png"
    long_title = " ".join(["Extraordinary"] * 24)

    returned = render_title_page(
        long_title,
        subtitle="A subtitle that also keeps the renderer busy",
        filename=str(output_file),
        background_path=None,
        theme=PREMIUM_NEUTRAL_THEME,
    )

    assert_valid_png(returned)


def test_render_title_page_uses_default_filename(tmp_path, monkeypatch):
    monkeypatch.setattr(title_page, "build_default_output_file", lambda name: str(tmp_path / name))

    returned = render_title_page(
        "Default Filename Book",
        filename=None,
        background_path=None,
        theme=DEFAULT_THEME,
    )

    assert Path(returned).name == "00_title_page.png"
    assert_valid_png(returned)


def test_render_title_page_with_existing_background(tmp_path):
    background_path = tmp_path / "background.png"
    output_file = tmp_path / "with_background.png"
    Image.new("RGBA", (40, 40), (20, 40, 80, 255)).save(background_path)

    returned = render_title_page(
        "Background Book",
        filename=str(output_file),
        background_path=str(background_path),
        theme=PREMIUM_NEUTRAL_THEME,
    )

    assert_valid_png(returned)
