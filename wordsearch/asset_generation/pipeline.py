"""Local asset generation pipeline used to bootstrap theme manifests.

This is intentionally deterministic and provider-free by default. It creates raw
provider images, normalizes them into renderer-ready PNGs and writes an asset
manifest with the same contract that a future AI provider will satisfy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wordsearch.asset_generation.brief import BlockVisualBrief, BookVisualBrief, build_book_visual_brief
from wordsearch.asset_generation.manifest import AssetManifest, BlockAssetSet, ManifestAsset
from wordsearch.asset_generation.normalizer import normalize_generated_asset
from wordsearch.asset_generation.providers import LOCAL_PLACEHOLDER_PROVIDER, ImageProvider, get_image_provider
from wordsearch.asset_generation.requests import GeneratedImage, ImageGenerationRequest
from wordsearch.config.design import DEFAULT_LAYOUT
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
    provider_name: str = LOCAL_PLACEHOLDER_PROVIDER,
    provider: ImageProvider | None = None,
) -> GeneratedAssetSet:
    """Generate image assets and an asset manifest for a thematic book."""
    specs = parse_puzzle_file(input_path)
    visual_brief = build_book_visual_brief(book_title=title, specs=specs, style=style)
    target_dir = Path(output_dir) if output_dir else build_default_asset_output_dir(title)
    raw_dir = target_dir / "raw"
    processed_dir = target_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    page_size = page_size or (DEFAULT_LAYOUT.page_width_px, DEFAULT_LAYOUT.page_height_px)
    image_provider = provider or get_image_provider(provider_name)
    blocks = visual_brief.blocks

    default_prompt = _book_background_prompt(visual_brief)
    default_request = ImageGenerationRequest(
        asset_id="book_default_background",
        asset_type="background",
        prompt=default_prompt,
        negative_prompt=_negative_prompt(visual_brief),
        output_size=page_size,
        metadata={"label": "book", "variant": "0"},
    )
    default_raw = _generate_raw_asset(
        provider=image_provider,
        request=default_request,
        raw_path=raw_dir / "book_default_background.png",
    )
    default_background = normalize_generated_asset(
        default_raw.path,
        processed_dir / "default_background.png",
        page_size,
    )

    block_manifest: dict[str, BlockAssetSet] = {}
    raw_assets: list[dict] = [default_raw.to_dict()]
    prompt_plan = {
        "book_title": title,
        "style": style,
        "provider": image_provider.name,
        "visual_brief": visual_brief.to_dict(),
        "assets": [
            {
                "id": default_request.asset_id,
                "type": default_request.asset_type,
                "target": "book",
                "prompt": default_request.prompt,
                "negative_prompt": default_request.negative_prompt,
                "raw_path": str(Path(default_raw.path).relative_to(target_dir)),
                "processed_path": str(Path(default_background).relative_to(target_dir)),
            }
        ],
        "blocks": [],
        "raw_assets": raw_assets,
    }

    for index, block_brief in enumerate(blocks, start=1):
        background_request = ImageGenerationRequest(
            asset_id=f"block_{index:02d}_{block_brief.slug}_background",
            asset_type="background",
            prompt=_block_background_prompt(visual_brief, block_brief),
            negative_prompt=_negative_prompt(visual_brief),
            output_size=page_size,
            metadata={"label": block_brief.name, "variant": str(index)},
        )
        cover_request = ImageGenerationRequest(
            asset_id=f"block_{index:02d}_{block_brief.slug}_cover",
            asset_type="cover_background",
            prompt=_block_cover_prompt(visual_brief, block_brief),
            negative_prompt=_negative_prompt(visual_brief),
            output_size=page_size,
            metadata={"label": f"cover {block_brief.name}", "variant": str(index + 100)},
        )

        background_raw = _generate_raw_asset(
            provider=image_provider,
            request=background_request,
            raw_path=raw_dir / f"{background_request.asset_id}.png",
        )
        cover_raw = _generate_raw_asset(
            provider=image_provider,
            request=cover_request,
            raw_path=raw_dir / f"{cover_request.asset_id}.png",
        )
        raw_assets.extend([background_raw.to_dict(), cover_raw.to_dict()])

        block_background = normalize_generated_asset(
            background_raw.path,
            processed_dir / f"block_{index:02d}_{block_brief.slug}_background.png",
            page_size,
        )
        block_cover = normalize_generated_asset(
            cover_raw.path,
            processed_dir / f"block_{index:02d}_{block_brief.slug}_cover.png",
            page_size,
        )
        block_manifest[block_brief.slug] = BlockAssetSet(
            background=str(Path(block_background).relative_to(target_dir)),
            cover_background=str(Path(block_cover).relative_to(target_dir)),
        )
        prompt_plan["blocks"].append(
            {
                "slug": block_brief.slug,
                "name": block_brief.name,
                "keywords": block_brief.keywords,
                "sample_titles": block_brief.sample_titles,
                "visual_direction": block_brief.visual_direction,
                "background_prompt": background_request.prompt,
                "cover_prompt": cover_request.prompt,
                "negative_prompt": background_request.negative_prompt,
                "background_raw_path": str(Path(background_raw.path).relative_to(target_dir)),
                "background_processed_path": str(Path(block_background).relative_to(target_dir)),
                "cover_raw_path": str(Path(cover_raw.path).relative_to(target_dir)),
                "cover_processed_path": str(Path(block_cover).relative_to(target_dir)),
            }
        )

    manifest = AssetManifest(
        book_title=title,
        theme_id=slugify(f"{title} {style}"),
        style=style,
        assets={
            "book_default_background": ManifestAsset(
                type="background",
                path=str(Path(default_background).relative_to(target_dir)),
                prompt=default_prompt,
                provider=image_provider.name,
                notes="Generated raw asset normalized into processed PNG for renderer consumption.",
            )
        },
        blocks=block_manifest,
        warnings=["Generated assets should be reviewed before production publishing."],
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


def _generate_raw_asset(
    *,
    provider: ImageProvider,
    request: ImageGenerationRequest,
    raw_path: Path,
) -> GeneratedImage:
    return provider.generate(request, raw_path)


def _book_background_prompt(visual_brief: BookVisualBrief) -> str:
    return _join_prompt_parts(
        [
            f"Subtle printable background for a word search puzzle book about {visual_brief.subject}.",
            f"Tone: {visual_brief.tone}.",
            f"Visual language: {', '.join(visual_brief.visual_keywords[:8])}.",
            f"Content keywords to inspire abstract motifs: {', '.join(visual_brief.keywords[:8])}.",
            "Portrait page, low contrast, soft paper texture, clean bright center area for a black letter grid.",
            "Suitable for KDP interior print, 300 DPI, no bleed-critical details near edges.",
        ]
    )


def _block_background_prompt(visual_brief: BookVisualBrief, block_brief: BlockVisualBrief) -> str:
    return _join_prompt_parts(
        [
            f"Subtle printable puzzle-page background for the section '{block_brief.name}' in a word search book about {visual_brief.subject}.",
            block_brief.visual_direction,
            f"Section keywords: {', '.join(block_brief.keywords[:8])}.",
            "Keep the center quiet and readable for puzzle letters; put any motifs near borders or corners.",
            "Low contrast, elegant print texture, no readable text.",
        ]
    )


def _block_cover_prompt(visual_brief: BookVisualBrief, block_brief: BlockVisualBrief) -> str:
    return _join_prompt_parts(
        [
            f"Elegant section-opener background for the section '{block_brief.name}' in a word search puzzle book about {visual_brief.subject}.",
            block_brief.visual_direction,
            f"Suggested motifs from content: {', '.join(block_brief.keywords[:8])}.",
            "Balanced empty central area for a large section title panel, refined border detail, premium educational activity-book style.",
            "Print-ready portrait background, low contrast, no readable text.",
        ]
    )


def _negative_prompt(visual_brief: BookVisualBrief) -> str:
    return ", ".join(visual_brief.avoid)


def _join_prompt_parts(parts: list[str]) -> str:
    return " ".join(part.strip() for part in parts if part and part.strip())


def _json_dumps(payload: dict) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
