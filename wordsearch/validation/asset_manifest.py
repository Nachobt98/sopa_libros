"""Validation for generated/reviewed asset manifests."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from wordsearch.asset_generation.manifest import AssetManifest
from wordsearch.validation.assets import AssetValidationReport, IMAGE_EXTENSIONS


def _manifest_declared_paths(asset_manifest: AssetManifest) -> list[str]:
    paths: list[str] = [asset.path for asset in asset_manifest.assets.values()]
    for block_assets in asset_manifest.blocks.values():
        paths.extend([block_assets.background, block_assets.cover_background, block_assets.motif])
    return [path for path in paths if path]


def validate_asset_manifest_assets(asset_manifest: AssetManifest) -> AssetValidationReport:
    """Validate that every path declared by the manifest exists and is image-readable."""
    report = AssetValidationReport()
    seen: set[str] = set()

    for raw_path in _manifest_declared_paths(asset_manifest):
        if raw_path in seen:
            continue
        seen.add(raw_path)
        _validate_manifest_image(raw_path, report)

    return report


def _validate_manifest_image(raw_path: str, report: AssetValidationReport) -> None:
    image_path = Path(raw_path)
    if not image_path.exists():
        report.add_error("El manifest declara un asset que no existe", path=str(image_path))
        return

    if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
        report.add_error("El manifest declara un asset sin extension de imagen soportada", path=str(image_path))
        return

    try:
        with Image.open(image_path) as image:
            image.verify()
    except OSError as exc:
        report.add_error(f"El manifest declara un asset que no se pudo abrir como imagen ({exc})", path=str(image_path))
