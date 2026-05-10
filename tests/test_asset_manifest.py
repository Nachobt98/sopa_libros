import json

from wordsearch.asset_generation.manifest import AssetManifest, BlockAssetSet, ManifestAsset, empty_asset_manifest


def test_asset_manifest_round_trips_json(tmp_path):
    manifest = AssetManifest(
        book_title="Ancient Egypt Word Search",
        theme_id="ancient_egypt_generated",
        style="premium-historical",
        assets={
            "book_default_background": ManifestAsset(
                type="background",
                path="assets/generated/egypt/default.png",
                prompt="papyrus texture",
                provider="mock",
            ),
        },
        blocks={
            "gods_and_mythology": BlockAssetSet(
                background="assets/generated/egypt/gods_bg.png",
                cover_background="assets/generated/egypt/gods_cover.png",
                motif="assets/generated/egypt/gods_motif.png",
            )
        },
        warnings=["manual review recommended"],
    )

    manifest_path = tmp_path / "asset_manifest.json"
    saved_path = manifest.save(manifest_path)
    loaded = AssetManifest.load(saved_path)

    assert loaded.book_title == "Ancient Egypt Word Search"
    assert loaded.theme_id == "ancient_egypt_generated"
    assert loaded.style == "premium-historical"
    assert loaded.resolve_asset_path("book_default_background") == "assets/generated/egypt/default.png"
    assert loaded.assets_for_block("Gods and Mythology").motif == "assets/generated/egypt/gods_motif.png"
    assert loaded.warnings == ["manual review recommended"]
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["assets"]["book_default_background"]["provider"] == "mock"


def test_asset_manifest_resolves_block_backgrounds_with_fallbacks():
    manifest = AssetManifest(
        book_title="Book",
        theme_id="theme",
        assets={"book_default_background": ManifestAsset(type="background", path="global.png")},
        blocks={"civil_rights": BlockAssetSet(background="civil.png", cover_background="civil_cover.png")},
    )

    assert manifest.background_for_block("Civil Rights", fallback="declared.png") == "civil.png"
    assert manifest.cover_background_for_block("Civil Rights", fallback="declared.png") == "civil_cover.png"
    assert manifest.background_for_block("Unknown Block", fallback="declared.png") == "global.png"
    assert manifest.cover_background_for_block("Unknown Block", fallback="declared.png") == "global.png"


def test_empty_asset_manifest_is_explicit_default_contract():
    manifest = empty_asset_manifest("Book")

    assert manifest.book_title == "Book"
    assert manifest.theme_id == "none"
    assert manifest.background_for_block("Any", fallback="declared.png") == "declared.png"
    assert manifest.cover_background_for_block("Any", fallback="declared.png") == "declared.png"
    assert manifest.to_report_dict()["asset_count"] == 0
