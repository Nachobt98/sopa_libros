from dataclasses import replace

import pytest
from PIL import Image, ImageChops

from wordsearch.asset_generation.manifest import AssetManifest
from wordsearch.config.design import (
    CHRISTMAS_VINTAGE_THEME,
    DECORATION_MOTIFS,
    DEFAULT_LAYOUT,
    DecorationConfig,
    DecorationPlacement,
    PageDecorationConfig,
)
from wordsearch.generation import book_assembly
from wordsearch.rendering.backgrounds import create_page_background
from wordsearch.rendering.decorations import draw_page_decorations


def _config(motif: str, *, enabled: bool = True) -> DecorationConfig:
    return DecorationConfig(
        enabled=enabled,
        pages=(
            PageDecorationConfig(
                "block_cover",
                (
                    DecorationPlacement(
                        motif=motif,
                        x=0.5,
                        y=0.5,
                        size_ratio=0.12,
                        rotation_degrees=23,
                    ),
                ),
            ),
        ),
    )


@pytest.mark.parametrize("motif", DECORATION_MOTIFS)
def test_motifs_render_deterministically_within_safe_bounds(motif):
    layout = DEFAULT_LAYOUT
    config = _config(motif)
    first = Image.new("RGBA", (layout.page_width_px, layout.page_height_px), (255, 255, 255, 255))
    second = first.copy()

    first_boxes = draw_page_decorations(first, config, "block_cover", layout)
    second_boxes = draw_page_decorations(second, config, "block_cover", layout)

    assert first_boxes == second_boxes
    assert first.tobytes() == second.tobytes()
    assert first.tobytes() != Image.new("RGBA", first.size, (255, 255, 255, 255)).tobytes()
    assert len(first_boxes) == 1
    left, top, right, bottom = first_boxes[0]
    assert layout.safe_left_px <= left < right <= layout.safe_right_px
    assert layout.safe_top_px <= top < bottom <= layout.safe_bottom_px


@pytest.mark.parametrize("scale", [1, 2, 3])
def test_decorations_scale_with_page_dimensions_and_render_scale(scale):
    ratio = 0.5
    layout = replace(
        DEFAULT_LAYOUT,
        page_width_px=int(DEFAULT_LAYOUT.page_width_px * ratio),
        page_height_px=int(DEFAULT_LAYOUT.page_height_px * ratio),
        safe_left_px=int(DEFAULT_LAYOUT.safe_left_px * ratio),
        safe_right_px=int(DEFAULT_LAYOUT.safe_right_px * ratio),
        safe_top_px=int(DEFAULT_LAYOUT.safe_top_px * ratio),
        safe_bottom_px=int(DEFAULT_LAYOUT.safe_bottom_px * ratio),
    )
    image = Image.new(
        "RGBA",
        (layout.page_width_px * scale, layout.page_height_px * scale),
        (255, 255, 255, 255),
    )
    boxes = draw_page_decorations(image, _config("snowflake"), "block_cover", layout, scale=scale)

    assert boxes[0][0] >= layout.safe_left_px * scale
    assert boxes[0][2] <= layout.safe_right_px * scale
    assert boxes[0][1] >= layout.safe_top_px * scale
    assert boxes[0][3] <= layout.safe_bottom_px * scale
    assert image.getchannel("A").getbbox() is not None
    assert ImageChops.difference(
        image.convert("RGB"),
        Image.new("RGB", image.size, (255, 255, 255)),
    ).getbbox()


def test_disabled_decorations_leave_canvas_unchanged():
    layout = DEFAULT_LAYOUT
    image = Image.new("RGBA", (layout.page_width_px, layout.page_height_px), (255, 255, 255, 255))
    original = image.tobytes()

    assert draw_page_decorations(image, _config("star", enabled=False), "block_cover", layout) == ()
    assert image.tobytes() == original
    assert CHRISTMAS_VINTAGE_THEME.decorations.for_page("solutions") is None


def test_decorations_compose_with_and_without_shared_background(tmp_path):
    layout = DEFAULT_LAYOUT
    background_path = tmp_path / "shared.png"
    Image.new("RGBA", (1, 1), (200, 80, 20, 255)).save(background_path)
    config = CHRISTMAS_VINTAGE_THEME.decorations_for_block("Christmas Classics")
    region = (
        layout.safe_left_px,
        layout.safe_top_px,
        layout.safe_right_px,
        layout.safe_bottom_px,
    )

    plain = create_page_background(
        None,
        layout.page_width_px,
        layout.page_height_px,
        theme=CHRISTMAS_VINTAGE_THEME,
        page_type="puzzle",
    )
    with_background = create_page_background(
        str(background_path),
        layout.page_width_px,
        layout.page_height_px,
        theme=CHRISTMAS_VINTAGE_THEME,
        page_type="puzzle",
    )
    plain_boxes = draw_page_decorations(
        plain,
        config,
        "puzzle",
        layout,
        region_bounds=region,
    )
    background_boxes = draw_page_decorations(
        with_background,
        config,
        "puzzle",
        layout,
        region_bounds=region,
    )

    assert plain_boxes == background_boxes
    assert plain.tobytes() != with_background.tobytes()
    assert plain.getpixel((0, 0))[0] == plain.getpixel((0, 0))[1]
    assert with_background.getpixel((0, 0))[0] == with_background.getpixel((0, 0))[1]


def test_decoration_configuration_validates_and_round_trips():
    config = _config("holly")

    assert DecorationConfig.from_dict(config.to_dict()) == config
    with pytest.raises(ValueError, match="Unknown decoration motif"):
        DecorationPlacement(motif="snowman", x=0.5, y=0.5)
    with pytest.raises(ValueError, match="between 0 and 1"):
        DecorationPlacement(motif="star", x=0.5, y=0.5, opacity=1.1)
    with pytest.raises(ValueError, match="must be a boolean"):
        DecorationConfig.from_dict({"enabled": 1})
    with pytest.raises(ValueError, match="only for puzzle pages"):
        PageDecorationConfig("solutions", (), region="separator")
    with pytest.raises(ValueError, match="Invalid decoration placement"):
        DecorationConfig.from_dict(
            {
                "enabled": True,
                "pages": [
                    {
                        "page_type": "puzzle",
                        "placements": [{"motif": "star", "x": "left", "y": 0.5}],
                    }
                ],
            }
        )
    with pytest.raises(ValueError, match="must be unique"):
        DecorationConfig(
            enabled=True,
            pages=(
                PageDecorationConfig("puzzle", ()),
                PageDecorationConfig("puzzle", ()),
            ),
        )


def test_christmas_blocks_and_manifest_decoration_override():
    assert CHRISTMAS_VINTAGE_THEME.decorations_for_block("Christmas Classics").for_page("puzzle")
    assert CHRISTMAS_VINTAGE_THEME.decorations_for_block("Nordic Christmas Magic").for_page("block_cover")
    assert CHRISTMAS_VINTAGE_THEME.decorations_for_block("Global Christmas Treasures").for_page("puzzle")

    manifest = AssetManifest.from_dict(
        {
            "book_title": "Christmas Around the World",
            "theme_id": "christmas-vintage",
            "blocks": {
                "christmas_classics": {
                    "decorations": {
                        "enabled": True,
                        "pages": [
                            {
                                "page_type": "puzzle",
                                "region": "separator",
                                "placements": [
                                    {"motif": "compass", "x": 0.5, "y": 0.5},
                                ],
                            }
                        ],
                    }
                }
            },
        }
    )

    override = book_assembly._block_decorations(manifest, "Christmas Classics", CHRISTMAS_VINTAGE_THEME)
    puzzle_config = override.for_page("puzzle")
    assert puzzle_config is not None
    assert puzzle_config.placements[0].motif == "compass"
    assert override.for_page("block_cover") is not None
