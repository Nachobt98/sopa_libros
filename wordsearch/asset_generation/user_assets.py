"""Build asset manifests from images supplied by the user."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from wordsearch.asset_generation.brief import build_book_visual_brief
from wordsearch.asset_generation.manifest import AssetManifest, BlockAssetSet, ManifestAsset
from wordsearch.asset_generation.normalizer import normalize_generated_asset
from wordsearch.asset_generation.pipeline import build_default_asset_output_dir
from wordsearch.config.design import DEFAULT_LAYOUT
from wordsearch.parsing.thematic import parse_puzzle_file
from wordsearch.utils.slug import slugify

USER_SUPPLIED_PROVIDER = "user-supplied"
SUPPORTED_USER_ASSET_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


@dataclass(frozen=True)
class UserSuppliedAssetSet:
    """Result of normalizing user assets and writing a renderer manifest."""

    output_dir: str
    manifest_path: str
    source_map_path: str
    asset_count: int
    block_count: int
    warning_count: int


def build_user_asset_manifest_for_book(
    *,
    title: str,
    input_path: str,
    user_assets_dir: str | Path,
    output_dir: str | Path | None = None,
    style: str = USER_SUPPLIED_PROVIDER,
    page_size: tuple[int, int] | None = None,
) -> UserSuppliedAssetSet:
    """Create an asset manifest from user-supplied local images.

    Expected filenames in ``user_assets_dir``:
    - book fallback: default_background.*, book_default_background.* or background.*
    - block background: <block_slug>_background.*, <block_slug>_bg.* or block_NN_<block_slug>_background.*
    - block cover: <block_slug>_cover.*, <block_slug>_cover_background.* or block_NN_<block_slug>_cover.*
    """
    source_dir = Path(user_assets_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"User assets directory not found: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"User assets path is not a directory: {source_dir}")

    specs = parse_puzzle_file(input_path)
    visual_brief = build_book_visual_brief(book_title=title, specs=specs, style=style)
    target_dir = Path(output_dir) if output_dir else build_default_asset_output_dir(title)
    processed_dir = target_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    page_size = page_size or (DEFAULT_LAYOUT.page_width_px, DEFAULT_LAYOUT.page_height_px)
    warnings = [
        "User-supplied assets should be checked for print rights, image quality, and KDP suitability before publishing."
    ]
    assets: dict[str, ManifestAsset] = {}
    block_manifest: dict[str, BlockAssetSet] = {}
    source_map: dict[str, object] = {
        "book_title": title,
        "style": style,
        "provider": USER_SUPPLIED_PROVIDER,
        "user_assets_dir": str(source_dir),
        "assets": {},
        "blocks": [],
        "warnings": warnings,
    }

    default_source = _find_first_existing(source_dir, ["default_background", "book_default_background", "background"])
    asset_count = 0
    if default_source:
        default_processed = normalize_generated_asset(default_source, processed_dir / "default_background.png", page_size)
        default_rel_path = _relative_posix(default_processed, target_dir)
        assets["book_default_background"] = ManifestAsset(
            type="background",
            path=default_rel_path,
            provider=USER_SUPPLIED_PROVIDER,
            notes=f"Normalized from user image: {default_source.name}",
        )
        source_map["assets"] = {
            "book_default_background": {
                "source_path": str(default_source),
                "processed_path": default_rel_path,
            }
        }
        asset_count += 1
    else:
        warnings.append("No default book background found. Add default_background.png/jpg/webp to provide a fallback.")

    for index, block_brief in enumerate(visual_brief.blocks, start=1):
        background_source = _find_first_existing(
            source_dir,
            [
                f"block_{index:02d}_{block_brief.slug}_background",
                f"{block_brief.slug}_background",
                f"{block_brief.slug}_bg",
            ],
        )
        cover_source = _find_first_existing(
            source_dir,
            [
                f"block_{index:02d}_{block_brief.slug}_cover",
                f"block_{index:02d}_{block_brief.slug}_cover_background",
                f"{block_brief.slug}_cover",
                f"{block_brief.slug}_cover_background",
            ],
        )

        block_entry: dict[str, object] = {"index": index, "slug": block_brief.slug, "name": block_brief.name}
        background_rel_path = None
        cover_rel_path = None

        if background_source:
            background_processed = normalize_generated_asset(
                background_source,
                processed_dir / f"block_{index:02d}_{block_brief.slug}_background.png",
                page_size,
            )
            background_rel_path = _relative_posix(background_processed, target_dir)
            block_entry["background_source_path"] = str(background_source)
            block_entry["background_processed_path"] = background_rel_path
            asset_count += 1
        else:
            warnings.append(f"No block background found for '{block_brief.name}' ({block_brief.slug}).")

        if cover_source:
            cover_processed = normalize_generated_asset(
                cover_source,
                processed_dir / f"block_{index:02d}_{block_brief.slug}_cover.png",
                page_size,
            )
            cover_rel_path = _relative_posix(cover_processed, target_dir)
            block_entry["cover_source_path"] = str(cover_source)
            block_entry["cover_processed_path"] = cover_rel_path
            asset_count += 1
        else:
            warnings.append(f"No block cover background found for '{block_brief.name}' ({block_brief.slug}).")

        if background_rel_path or cover_rel_path:
            block_manifest[block_brief.slug] = BlockAssetSet(
                background=background_rel_path,
                cover_background=cover_rel_path,
            )
        source_map["blocks"].append(block_entry)

    manifest = AssetManifest(
        book_title=title,
        theme_id=slugify(f"{title} {style} user assets"),
        style=style,
        assets=assets,
        blocks=block_manifest,
        warnings=warnings,
    )
    manifest_path = manifest.save(target_dir / "asset_manifest.json")
    source_map_path = target_dir / "user_asset_sources.json"
    source_map_path.write_text(json.dumps(source_map, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    return UserSuppliedAssetSet(
        output_dir=str(target_dir),
        manifest_path=manifest_path,
        source_map_path=str(source_map_path),
        asset_count=asset_count,
        block_count=len(visual_brief.blocks),
        warning_count=len(warnings),
    )


def _find_first_existing(directory: Path, stems: list[str]) -> Path | None:
    for stem in stems:
        for extension in SUPPORTED_USER_ASSET_EXTENSIONS:
            candidate = directory / f"{stem}{extension}"
            if candidate.exists() and candidate.is_file():
                return candidate
    return None


def _relative_posix(path: str | Path, root: str | Path) -> str:
    return Path(path).relative_to(root).as_posix()
