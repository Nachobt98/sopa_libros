import json

from PIL import Image

from wordsearch.asset_generation.manifest import AssetManifest
from wordsearch.asset_generation.pipeline import generate_local_assets_for_book


def test_generate_local_assets_for_book_writes_manifest_prompts_and_pngs(tmp_path):
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
                "[Block]",
                "name: Gods and Mythology",
                "[/Block]",
                "[Puzzle]",
                "title: Ra",
                "fact: Another fact about Egyptian mythology.",
                "words:",
                "RA",
                "OSIRIS",
                "[/Puzzle]",
            ]
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "generated" / "egypt"

    result = generate_local_assets_for_book(
        title="Ancient Egypt Word Search",
        input_path=str(input_path),
        output_dir=output_dir,
        style="premium-historical",
        page_size=(120, 160),
    )

    assert result.output_dir == str(output_dir)
    assert result.block_count == 2
    assert result.asset_count == 5
    assert (output_dir / "asset_manifest.json").exists()
    assert (output_dir / "prompts.json").exists()

    manifest = AssetManifest.load(result.manifest_path)
    assert manifest.style == "premium-historical"
    assert manifest.resolve_asset_path("book_default_background") == str(output_dir / "processed/default_background.png")
    assert set(manifest.blocks) == {"ancient_egypt", "gods_and_mythology"}
    assert "Ancient Egypt" in manifest.assets["book_default_background"].prompt
    assert "low contrast" in manifest.assets["book_default_background"].prompt.lower()

    for asset_path in manifest.declared_asset_paths():
        with Image.open(asset_path) as image:
            assert image.size == (120, 160)

    prompt_payload = json.loads((output_dir / "prompts.json").read_text(encoding="utf-8"))
    assert prompt_payload["book_title"] == "Ancient Egypt Word Search"
    assert prompt_payload["style"] == "premium-historical"
    assert prompt_payload["visual_brief"]["subject"] == "Ancient Egypt"
    assert "readable text" in prompt_payload["assets"][0]["negative_prompt"]
    assert "Nile" in prompt_payload["assets"][0]["prompt"] or "nile" in prompt_payload["assets"][0]["prompt"]
    assert len(prompt_payload["blocks"]) == 2
    assert prompt_payload["blocks"][0]["slug"] == "ancient_egypt"
    assert prompt_payload["blocks"][0]["keywords"]
    assert "background_prompt" in prompt_payload["blocks"][0]
    assert "cover_prompt" in prompt_payload["blocks"][0]
    assert "negative_prompt" in prompt_payload["blocks"][0]


def test_generate_local_assets_for_book_handles_books_without_blocks(tmp_path):
    input_path = tmp_path / "book.txt"
    input_path.write_text(
        "\n".join(
            [
                "[Puzzle]",
                "title: No Block Puzzle",
                "fact: A short fact.",
                "words:",
                "WORD",
                "[/Puzzle]",
            ]
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "generated" / "no_blocks"

    result = generate_local_assets_for_book(
        title="No Blocks",
        input_path=str(input_path),
        output_dir=output_dir,
        page_size=(80, 100),
    )

    manifest = AssetManifest.load(result.manifest_path)
    assert result.block_count == 1
    assert set(manifest.blocks) == {"default"}
    assert manifest.background_for_block(None) == str(output_dir / "processed/default_background.png")
