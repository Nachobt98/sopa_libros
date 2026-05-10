from PIL import Image

from wordsearch.asset_generation.manifest import AssetManifest, BlockAssetSet, ManifestAsset
from wordsearch.validation.asset_manifest import validate_asset_manifest_assets


def test_validate_asset_manifest_assets_requires_existing_files(tmp_path):
    manifest = AssetManifest(
        book_title="Book",
        theme_id="generated",
        assets={"book_default_background": ManifestAsset(type="background", path=str(tmp_path / "missing.png"))},
    )

    report = validate_asset_manifest_assets(manifest)

    assert report.has_errors is True
    assert report.errors[0].message == "El manifest declara un asset que no existe"


def test_validate_asset_manifest_assets_accepts_valid_images(tmp_path):
    global_background = tmp_path / "global.png"
    block_background = tmp_path / "block.png"
    Image.new("RGB", (10, 10), "white").save(global_background)
    Image.new("RGB", (10, 10), "white").save(block_background)
    manifest = AssetManifest(
        book_title="Book",
        theme_id="generated",
        assets={"book_default_background": ManifestAsset(type="background", path=str(global_background))},
        blocks={"block": BlockAssetSet(background=str(block_background))},
    )

    report = validate_asset_manifest_assets(manifest)

    assert report.has_errors is False
    assert report.issues == []
