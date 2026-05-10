"""Local asset generation pipeline used to bootstrap theme manifests.

This is intentionally deterministic and provider-free. It creates valid,
print-sized placeholder PNGs and an asset manifest with the same contract that a
future AI provider will write after generating and normalizing images.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from wordsearch.asset_generation.manifest import AssetManifest, BlockAssetSet, ManifestAsset
from wordsearch.config.design import DEFAULT_LAYOUT
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.parsing.thematic import parse_puzzle_file
from wordsearch.utils.slug import slugify

DEFAULT_ASSET_STYLE = "mock-editorial"
DEFAULT_ASSET_ROOT = Path("assets/generated")


@dataclass(frozen=True)
class GeneratedAssetSet:
    """Result of the local asset generation bootstrap command."""

    output_dir: str
    manifest_path: str
    prompt_plan_path: str
    asset_count: int
    block_count: int


def build_default_asset_output_dir(book_title: str, root_dir: str | Path = DEFAULT_ASSET_ROOT) -> Path:
    """Return the default generated-assets directory for a book title."""
    return Path(root_dir) / slugify(book_title)


def generate_local_assets_for_book(
    *,
    title: str,
    input_path: str,
    output_dir: str | Path | None = None,
    style: str = DEFAULT_ASSET_STYLE,
    page_size: tuple[int, int] | None = None,
) -> GeneratedAssetSet:
    """Generate placeholder image assets and an asset manifest for a thematic book."""
    specs = parse_puzzle_file(input_path)
    target_dir = Path(output_dir) if output_dir else build_default_asset_output_dir(title)
    processed_dir = target_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    page_size = page_size or (DEFAULT_LAYOUT.page_width_px, DEFAULT_LAYOUT.page_height_px)
    blocks = _blocks_in_order(specs)

    default_background = processed_dir / "default_background.png"
    _write_editorial_background(default_background, page_size, label="book", variant=0)

    block_manifest: dict[str, BlockAssetSet] = {}
    prompt_plan = {
        "book_title": title,
        "style": style,
        "assets": [
            {
                "id": "book_default_background",
                "type": "background",
                "target": "book",
                "prompt": _placeholder_prompt(title=title, block_name=None, style=style, asset_kind="default background"),
            }
        ],
        "blocks": [],
    }

    for index, block_name in enumerate(blocks, start=1):
        block_slug = slugify(block_name)
        block_background = processed_dir / f"block_{index:02d}_{block_slug}_background.png"
        block_cover = processed_dir / f"block_{index:02d}_{block_slug}_cover.png"
        _write_editorial_background(block_background, page_size, label=block_name, variant=index)
        _write_editorial_background(block_cover, page_size, label=f"cover {block_name}", variant=index + 100)
        block_manifest[block_slug] = BlockAssetSet(
            background=str(block_background.relative_to(target_dir)),
            cover_background=str(block_cover.relative_to(target_dir)),
        )
        prompt_plan["blocks"].append(
            {
                "slug": block_slug,
                "name": block_name,
                "background_prompt": _placeholder_prompt(
                    title=title,
                    block_name=block_name,
                    style=style,
                    asset_kind="block puzzle background",
                ),
                "cover_prompt": _placeholder_prompt(
                    title=title,
                    block_name=block_name,
                    style=style,
                    asset_kind="block cover background",
                ),
            }
        )

    manifest = AssetManifest(
        book_title=title,
        theme_id=slugify(f"{title} {style}"),
        style=style,
        assets={
            "book_default_background": ManifestAsset(
                type="background",
                path=str(default_background.relative_to(target_dir)),
                prompt=prompt_plan["assets"][0]["prompt"],
                provider="local-placeholder",
                notes="Deterministic placeholder asset. Replace with normalized AI output later.",
            )
        },
        blocks=block_manifest,
        warnings=["Local placeholder assets generated; review/replace before production publishing."],
    )

    manifest_path = manifest.save(target_dir / "asset_manifest.json")
    prompt_plan_path = target_dir / "prompts.json"
    prompt_plan_path.write_text(_json_dumps(prompt_plan), encoding="utf-8")

    return GeneratedAssetSet(
        output_dir=str(target_dir),
        manifest_path=manifest_path,
        prompt_plan_path=str(prompt_plan_path),
        asset_count=1 + (2 * len(blocks)),
        block_count=len(blocks),
    )


def _blocks_in_order(specs: list[PuzzleSpec]) -> list[str]:
    blocks: list[str] = []
    seen: set[str] = set()
    for spec in specs:
        block_name = spec.block_name or "default"
        if block_name in seen:
            continue
        seen.add(block_name)
        blocks.append(block_name)
    return blocks


def _write_editorial_background(path: Path, size: tuple[int, int], *, label: str, variant: int) -> None:
    """Write a subtle valid PNG suitable for testing manifest-based rendering."""
    width, height = size
    base = _variant_color(variant)
    image = Image.new("RGB", size, base)
    draw = ImageDraw.Draw(image)

    line_color = tuple(max(channel - 18, 0) for channel in base)
    step = max(width // 16, 80)
    for x in range(-height, width + height, step):
        draw.line((x, 0, x + height, height), fill=line_color, width=3)

    border_color = tuple(max(channel - 42, 0) for channel in base)
    margin = _safe_margin_for_size(width, height)
    draw.rounded_rectangle(
        (margin, margin, width - margin, height - margin),
        outline=border_color,
        width=max(1, min(6, margin // 2)),
        radius=min(36, margin),
    )

    label_color = tuple(max(channel - 72, 0) for channel in base)
    label_y = max(margin, height - margin - 42)
    draw.text((margin + 8, label_y), label[:80], fill=label_color)
    image.save(path)


def _safe_margin_for_size(width: int, height: int) -> int:
    """Return a margin that cannot invert the drawable rectangle on tiny fixtures."""
    shortest_side = max(1, min(width, height))
    preferred_margin = max(shortest_side // 18, 8)
    max_margin = max(1, (shortest_side - 2) // 2)
    return min(preferred_margin, max_margin)


def _variant_color(variant: int) -> tuple[int, int, int]:
    palettes = [
        (245, 239, 225),
        (238, 232, 218),
        (242, 236, 224),
        (235, 230, 218),
        (246, 241, 231),
    ]
    return palettes[variant % len(palettes)]


def _placeholder_prompt(*, title: str, block_name: str | None, style: str, asset_kind: str) -> str:
    block_text = f" for the section '{block_name}'" if block_name else ""
    return (
        f"Create a subtle printable {asset_kind}{block_text} for a word search book titled "
        f"'{title}', style '{style}', low contrast, no readable text, no logos, clean center area."
    )


def _json_dumps(payload: dict) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
