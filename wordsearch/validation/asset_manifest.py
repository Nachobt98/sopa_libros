"""Validation for generated/reviewed asset manifests."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from wordsearch.asset_generation.manifest import AssetManifest
from wordsearch.validation.assets import AssetValidationReport, IMAGE_EXTENSIONS


def validate_asset_manifest_assets(asset_manifest: AssetManifest) -> AssetValidationReport:
    """Validate that every path declared by the manifest exists and is image-readable."""
    report = AssetValidationReport()

    for raw_path in asset_manifest.declared_asset_paths():
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
