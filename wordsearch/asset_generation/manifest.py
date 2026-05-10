"""Serializable asset manifest used by generated/reviewed visual assets.

The manifest is intentionally provider-agnostic. Future AI image providers can
write it after generating and normalizing files, while the renderer only needs
to read stable local paths from it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from wordsearch.utils.slug import slugify

ASSET_MANIFEST_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ManifestAsset:
    """Single generated/reviewed visual asset reference."""

    type: str
    path: str
    prompt: str | None = None
    provider: str | None = None
    notes: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ManifestAsset":
        return cls(
            type=str(payload.get("type", "asset")),
            path=str(payload["path"]),
            prompt=payload.get("prompt"),
            provider=payload.get("provider"),
            notes=payload.get("notes"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class BlockAssetSet:
    """Assets that may override global defaults for a thematic block."""

    background: str | None = None
    cover_background: str | None = None
    motif: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BlockAssetSet":
        return cls(
            background=payload.get("background"),
            cover_background=payload.get("cover_background"),
            motif=payload.get("motif"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class AssetManifest:
    """Renderer-facing contract for generated visual assets."""

    book_title: str
    theme_id: str
    style: str | None = None
    schema_version: int = ASSET_MANIFEST_SCHEMA_VERSION
    assets: dict[str, ManifestAsset] = field(default_factory=dict)
    blocks: dict[str, BlockAssetSet] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    manifest_path: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any], *, manifest_path: str | None = None) -> "AssetManifest":
        return cls(
            schema_version=int(payload.get("schema_version", ASSET_MANIFEST_SCHEMA_VERSION)),
            book_title=str(payload.get("book_title", "")),
            theme_id=str(payload.get("theme_id", "generated-assets")),
            style=payload.get("style"),
            assets={
                str(asset_id): ManifestAsset.from_dict(asset_payload)
                for asset_id, asset_payload in payload.get("assets", {}).items()
            },
            blocks={
                str(block_slug): BlockAssetSet.from_dict(block_payload)
                for block_slug, block_payload in payload.get("blocks", {}).items()
            },
            warnings=list(payload.get("warnings", [])),
            manifest_path=manifest_path,
        )

    @classmethod
    def load(cls, path: str | Path) -> "AssetManifest":
        manifest_path = Path(path)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        return cls.from_dict(payload, manifest_path=str(manifest_path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "book_title": self.book_title,
            "theme_id": self.theme_id,
            "style": self.style,
            "assets": {asset_id: asset.to_dict() for asset_id, asset in self.assets.items()},
            "blocks": {block_slug: block_assets.to_dict() for block_slug, block_assets in self.blocks.items()},
            "warnings": self.warnings,
        }

    def save(self, path: str | Path) -> str:
        manifest_path = Path(path)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return str(manifest_path)

    def resolve_asset_path(self, asset_id: str) -> str | None:
        asset = self.assets.get(asset_id)
        return asset.path if asset else None

    def assets_for_block(self, block_name: str | None) -> BlockAssetSet:
        if not block_name:
            return BlockAssetSet()
        return self.blocks.get(slugify(block_name), BlockAssetSet())

    def background_for_block(self, block_name: str | None, fallback: str | None = None) -> str | None:
        block_assets = self.assets_for_block(block_name)
        return block_assets.background or self.resolve_asset_path("book_default_background") or fallback

    def cover_background_for_block(self, block_name: str | None, fallback: str | None = None) -> str | None:
        block_assets = self.assets_for_block(block_name)
        return block_assets.cover_background or block_assets.background or self.resolve_asset_path("book_default_background") or fallback

    def to_report_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "book_title": self.book_title,
            "theme_id": self.theme_id,
            "style": self.style,
            "asset_count": len(self.assets),
            "block_asset_count": len(self.blocks),
            "warnings": self.warnings,
            "manifest_path": self.manifest_path,
        }


def empty_asset_manifest(book_title: str, *, theme_id: str = "none") -> AssetManifest:
    """Return an explicit empty manifest for default/non-generated runs."""
    return AssetManifest(book_title=book_title, theme_id=theme_id)
