import pytest
from PIL import Image

from wordsearch.asset_generation.manifest import AssetManifest, ManifestAsset
from wordsearch.config.design import CHRISTMAS_VINTAGE_THEME
from wordsearch.generation import book_assembly
from wordsearch.rendering import block_cover, front_matter, page_frame, puzzle_page, solution_page, title_page
from wordsearch.rendering.backgrounds import create_page_background


@pytest.mark.parametrize(
    ("page_type", "expected_gray"),
    [
        ("title_page", 102),
        ("block_cover", 166),
        ("puzzle", 225),
        ("table_of_contents", 235),
        ("instructions", 235),
        ("solutions", 255),
    ],
)
def test_christmas_vintage_background_applies_page_opacity(tmp_path, page_type, expected_gray):
    background_path = tmp_path / "background.png"
    Image.new("RGBA", (1, 1), (0, 0, 0, 255)).save(background_path)

    image = create_page_background(
        str(background_path),
        1,
        1,
        theme=CHRISTMAS_VINTAGE_THEME,
        page_type=page_type,
    )

    assert image.getpixel((0, 0)) == (expected_gray, expected_gray, expected_gray, 255)


def test_christmas_vintage_composites_transparent_background_over_page_fill(tmp_path):
    background_path = tmp_path / "transparent_background.png"
    Image.new("RGBA", (1, 1), (0, 0, 0, 128)).save(background_path)

    image = create_page_background(
        str(background_path),
        1,
        1,
        theme=CHRISTMAS_VINTAGE_THEME,
        page_type="title_page",
    )

    assert image.getpixel((0, 0)) == (179, 179, 179, 255)


def test_shared_manifest_background_is_reused_for_book_and_block_pages(tmp_path):
    shared_background = tmp_path / "christmas.png"
    manifest = AssetManifest(
        book_title="Christmas Around the World",
        theme_id="christmas-vintage",
        assets={
            "book_default_background": ManifestAsset(
                type="background",
                path=str(shared_background),
            )
        },
    )

    assert book_assembly._global_background(manifest) == str(shared_background)
    assert book_assembly._block_background(manifest, "Christmas Traditions", None) == str(shared_background)
    assert book_assembly._block_cover_background(manifest, "Christmas Traditions", None) == str(shared_background)


def test_renderers_select_page_specific_background_opacity(monkeypatch, tmp_path):
    page_types = []

    shared_background = str(tmp_path / "shared.png")

    def fake_background(path, width_px, height_px, *, theme, page_type):
        assert path == shared_background
        page_types.append(page_type)
        return Image.new("RGBA", (width_px, height_px), theme.page_background_fill)

    def fake_save(image, filename, **kwargs):
        assert image.mode == "RGBA"
        assert "output_width_px" in kwargs
        return filename

    monkeypatch.setattr(page_frame, "create_page_background", fake_background)
    monkeypatch.setattr(front_matter, "create_page_background", fake_background)
    for renderer in (title_page, front_matter, block_cover, puzzle_page, solution_page):
        monkeypatch.setattr(renderer, "save_page", fake_save)

    title_page.render_title_page(
        "Christmas Around the World",
        filename=str(tmp_path / "title.png"),
        background_path=shared_background,
        theme=CHRISTMAS_VINTAGE_THEME,
    )
    front_matter.render_table_of_contents(
        [("Solutions", 12, True)],
        output_dir=str(tmp_path),
        background_path=shared_background,
        theme=CHRISTMAS_VINTAGE_THEME,
    )
    front_matter.render_instructions_page(
        "Christmas Around the World",
        filename=str(tmp_path / "instructions.png"),
        background_path=shared_background,
        theme=CHRISTMAS_VINTAGE_THEME,
    )
    block_cover.render_block_cover(
        "Christmas Traditions",
        1,
        filename=str(tmp_path / "block.png"),
        background_path=shared_background,
        theme=CHRISTMAS_VINTAGE_THEME,
    )
    grid = [list("CATDOG"), list("AAAAAA"), list("BBBBBB"), list("CCCCCC"), list("DDDDDD"), list("EEEEEE")]
    puzzle_page.render_page(
        grid,
        ["CAT"],
        1,
        filename=str(tmp_path / "puzzle.png"),
        background_path=shared_background,
        theme=CHRISTMAS_VINTAGE_THEME,
    )
    solution_page.render_solution_page(
        grid,
        ["CAT"],
        1,
        filename=str(tmp_path / "solution.png"),
        background_path=shared_background,
        theme=CHRISTMAS_VINTAGE_THEME,
    )

    assert page_types == [
        "title_page",
        "table_of_contents",
        "instructions",
        "block_cover",
        "puzzle",
        "solutions",
    ]
