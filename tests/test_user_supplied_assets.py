import json

from PIL import Image

from wordsearch.asset_generation.manifest import AssetManifest
from wordsearch.asset_generation.user_assets import USER_SUPPLIED_PROVIDER, build_user_asset_manifest_for_book


def write_thematic_book(tmp_path):
    input_path = tmp_path / "book.txt"
    input_path.write_text(
        "\n".join(
            [
                "[Block]",
                "name: Ancient Egypt",
                "[/Block]",
                "[Puzzle]",
                "title: Pharaohs",
                "fact: A short fact about Nile monuments.",
                "words:",
                "NILE",
                "PYRAMID",
                "[/Puzzle]",
            ]
        ),
        encoding="utf-8",
    )
    return input_path


def save_image(path, color):
    Image.new("RGB", (24, 18), color).save(path)


def test_build_user_asset_manifest_normalizes_images_and_records_sources(tmp_path):
    input_path = write_thematic_book(tmp_path)
    source_dir = tmp_path / "user_assets"
    source_dir.mkdir()
    save_image(source_dir / "default_background.jpg", "white")
    save_image(source_dir / "ancient_egypt_background.png", "blue")
    save_image(source_dir / "ancient_egypt_cover.jpeg", "green")
    output_dir = tmp_path / "generated" / "egypt"

    result = build_user_asset_manifest_for_book(
        title="Ancient Egypt Word Search",
        input_path=str(input_path),
        user_assets_dir=source_dir,
        output_dir=output_dir,
        style="reviewed-user-assets",
        page_size=(80, 100),
    )

    assert result.output_dir == str(output_dir)
    assert result.block_count == 1
    assert result.asset_count == 3
    assert result.warning_count == 1
    assert (output_dir / "asset_manifest.json").exists()
    assert (output_dir / "user_asset_sources.json").exists()

    manifest = AssetManifest.load(result.manifest_path)
    assert manifest.style == "reviewed-user-assets"
    assert manifest.assets["book_default_background"].provider == USER_SUPPLIED_PROVIDER
    assert manifest.resolve_asset_path("book_default_background") == str(output_dir / "processed/default_background.png")
    assert manifest.background_for_block("Ancient Egypt") == str(
        output_dir / "processed/block_01_ancient_egypt_background.png"
    )
    assert manifest.cover_background_for_block("Ancient Egypt") == str(
        output_dir / "processed/block_01_ancient_egypt_cover.png"
    )

    for asset_path in manifest.declared_asset_paths():
        with Image.open(asset_path) as image:
            assert image.size == (80, 100)

    source_map = json.loads((output_dir / "user_asset_sources.json").read_text(encoding="utf-8"))
    assert source_map["provider"] == USER_SUPPLIED_PROVIDER
    assert source_map["assets"]["book_default_background"]["source_path"] == str(source_dir / "default_background.jpg")
    assert source_map["blocks"][0]["background_source_path"] == str(source_dir / "ancient_egypt_background.png")
    assert source_map["blocks"][0]["cover_source_path"] == str(source_dir / "ancient_egypt_cover.jpeg")


def test_build_user_asset_manifest_warns_when_optional_images_are_missing(tmp_path):
    input_path = write_thematic_book(tmp_path)
    source_dir = tmp_path / "user_assets"
    source_dir.mkdir()
    save_image(source_dir / "default_background.png", "white")
    output_dir = tmp_path / "generated" / "missing"

    result = build_user_asset_manifest_for_book(
        title="Missing Block Images",
        input_path=str(input_path),
        user_assets_dir=source_dir,
        output_dir=output_dir,
        page_size=(40, 60),
    )

    manifest = AssetManifest.load(result.manifest_path)
    assert result.asset_count == 1
    assert result.warning_count == 3
    assert "ancient_egypt" not in manifest.blocks
    assert any("No block background found" in warning for warning in manifest.warnings)
    assert any("No block cover background found" in warning for warning in manifest.warnings)
