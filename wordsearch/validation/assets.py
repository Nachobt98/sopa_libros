"""Runtime asset and output-path validation."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from PIL import Image

from wordsearch.config.fonts import FONT_PATH, FONT_PATH_BOLD, FONT_TITLE
from wordsearch.rendering.backgrounds import BACKGROUND_PATH

FONT_EXTENSIONS = {".otf", ".ttf"}
IMAGE_EXTENSIONS = {".jpeg", ".jpg", ".png", ".webp"}


@dataclass(frozen=True)
class AssetValidationIssue:
    severity: str
    message: str
    path: str | None = None

    def format(self) -> str:
        prefix = "ERROR" if self.severity == "error" else "WARNING"
        if self.path:
            return f"[{prefix}] {self.message}: {self.path}"
        return f"[{prefix}] {self.message}"


@dataclass
class AssetValidationReport:
    issues: list[AssetValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[AssetValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[AssetValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def add_error(self, message: str, *, path: str | None = None) -> None:
        self.issues.append(AssetValidationIssue("error", message, path))

    def add_warning(self, message: str, *, path: str | None = None) -> None:
        self.issues.append(AssetValidationIssue("warning", message, path))

    def extend(self, other: "AssetValidationReport") -> None:
        self.issues.extend(other.issues)

    def print_summary(self) -> None:
        print("\n=== Informe de assets ===")
        if not self.issues:
            print("OK: assets requeridos y output verificados.")
            return

        if self.errors:
            print(f"\nERRORES BLOQUEANTES ({len(self.errors)}):")
            for issue in self.errors:
                print(f"  - {issue.format()}")
        else:
            print("\nERRORES BLOQUEANTES: ninguno.")

        if self.warnings:
            print(f"\nAVISOS NO BLOQUEANTES ({len(self.warnings)}):")
            for issue in self.warnings:
                print(f"  - {issue.format()}")
        else:
            print("\nAVISOS NO BLOQUEANTES: ninguno.")


def collect_background_paths(backgrounds: Iterable[str | None]) -> list[str]:
    """Return unique non-empty background paths preserving input order."""
    unique_paths: list[str] = []
    seen: set[str] = set()

    for background in backgrounds:
        if not background:
            continue
        if background in seen:
            continue
        seen.add(background)
        unique_paths.append(background)

    return unique_paths


def validate_generation_assets(
    *,
    output_dir: str,
    optional_backgrounds: Iterable[str | None] = (),
) -> AssetValidationReport:
    """Validate required fonts, optional backgrounds and output writability."""
    report = AssetValidationReport()

    for font_path in (FONT_PATH, FONT_PATH_BOLD, FONT_TITLE):
        _validate_required_font(font_path, report)

    backgrounds = collect_background_paths([BACKGROUND_PATH, *optional_backgrounds])
    for background_path in backgrounds:
        _validate_optional_background(background_path, report)

    report.extend(validate_output_directory(output_dir))
    return report


def validate_output_directory(output_dir: str) -> AssetValidationReport:
    """Create and verify the output directory can be written to."""
    report = AssetValidationReport()
    output_path = Path(output_dir)

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        report.add_error(f"No se pudo crear el directorio de salida ({exc})", path=str(output_path))
        return report

    if not output_path.is_dir():
        report.add_error("La ruta de salida no es un directorio", path=str(output_path))
        return report

    test_file = output_path / ".asset_write_test"
    try:
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
    except OSError as exc:
        report.add_error(f"No se pudo escribir en el directorio de salida ({exc})", path=str(output_path))

    return report


def _validate_required_font(font_path: str, report: AssetValidationReport) -> None:
    if not os.path.exists(font_path):
        report.add_error("No se encuentra una fuente requerida", path=font_path)
        return

    if Path(font_path).suffix.lower() not in FONT_EXTENSIONS:
        report.add_error("La fuente requerida no tiene extension .ttf/.otf", path=font_path)


def _validate_optional_background(background_path: str, report: AssetValidationReport) -> None:
    if not os.path.exists(background_path):
        report.add_warning("No se encuentra el fondo; se usara fondo blanco/default", path=background_path)
        return

    if Path(background_path).suffix.lower() not in IMAGE_EXTENSIONS:
        report.add_warning("El fondo no tiene una extension de imagen comun", path=background_path)

    try:
        with Image.open(background_path) as image:
            image.verify()
    except OSError as exc:
        report.add_error(f"El fondo existe pero no se pudo abrir como imagen ({exc})", path=background_path)
