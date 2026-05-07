"""KDP-oriented preflight checks for generated books."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from PIL import Image

from wordsearch.config.fonts import FONT_PATH, FONT_PATH_BOLD, FONT_TITLE
from wordsearch.config.layout import DPI, PAGE_H_PX, PAGE_W_PX, TRIM_H_IN, TRIM_W_IN
from wordsearch.config.paths import build_output_file

PREFLIGHT_REPORT_FILENAME = "preflight_report.json"
PREFLIGHT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class KdpPreflightIssue:
    """A preflight warning or error."""

    severity: str
    message: str
    path: str | None = None

    def format(self) -> str:
        prefix = "ERROR" if self.severity == "error" else "WARNING"
        if self.path:
            return f"[{prefix}] {self.message}: {self.path}"
        return f"[{prefix}] {self.message}"


@dataclass
class KdpPreflightReport:
    """Serializable KDP preflight report for one generated book."""

    schema_version: int
    trim_width_in: float
    trim_height_in: float
    dpi: int
    expected_page_width_px: int
    expected_page_height_px: int
    expected_page_count: int
    content_image_count: int
    solution_image_count: int
    pdf_path: str
    output_dir: str
    issues: list[KdpPreflightIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[KdpPreflightIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[KdpPreflightIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def passed(self) -> bool:
        return not self.errors

    def add_error(self, message: str, *, path: str | None = None) -> None:
        self.issues.append(KdpPreflightIssue("error", message, path))

    def add_warning(self, message: str, *, path: str | None = None) -> None:
        self.issues.append(KdpPreflightIssue("warning", message, path))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["passed"] = self.passed
        return data

    def print_summary(self) -> None:
        print("\n=== KDP preflight ===")
        print(f"Trim: {self.trim_width_in}x{self.trim_height_in} in @ {self.dpi} DPI")
        print(f"Paginas esperadas: {self.expected_page_count}")

        if not self.issues:
            print("OK: no se han detectado problemas basicos de preflight.")
            return

        if self.errors:
            print(f"\nERRORES ({len(self.errors)}):")
            for issue in self.errors:
                print(f"  - {issue.format()}")
        else:
            print("\nERRORES: ninguno.")

        if self.warnings:
            print(f"\nAVISOS ({len(self.warnings)}):")
            for issue in self.warnings:
                print(f"  - {issue.format()}")
        else:
            print("\nAVISOS: ninguno.")


def build_kdp_preflight_report(
    *,
    pdf_path: str,
    output_dir: str,
    content_image_paths: Iterable[str],
    solution_image_paths: Iterable[str],
) -> KdpPreflightReport:
    """Build a basic preflight report for a generated KDP interior."""
    content_images = list(content_image_paths)
    solution_images = list(solution_image_paths)
    report = KdpPreflightReport(
        schema_version=PREFLIGHT_SCHEMA_VERSION,
        trim_width_in=TRIM_W_IN,
        trim_height_in=TRIM_H_IN,
        dpi=DPI,
        expected_page_width_px=PAGE_W_PX,
        expected_page_height_px=PAGE_H_PX,
        expected_page_count=len(content_images) + 1 + len(solution_images),
        content_image_count=len(content_images),
        solution_image_count=len(solution_images),
        pdf_path=pdf_path,
        output_dir=output_dir,
    )

    _check_output_dir(output_dir, report)
    _check_required_fonts(report)
    _check_pdf_file(pdf_path, report)
    _check_page_images(content_images, report, label="content")
    _check_page_images(solution_images, report, label="solution")

    return report


def write_kdp_preflight_report(report: KdpPreflightReport, *, output_dir: str) -> str:
    """Write a KDP preflight report JSON and return its path."""
    report_path = build_output_file(output_dir, PREFLIGHT_REPORT_FILENAME)
    Path(report_path).write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return report_path


def _check_output_dir(output_dir: str, report: KdpPreflightReport) -> None:
    output_path = Path(output_dir)
    if not output_path.exists():
        report.add_error("No existe el directorio de salida", path=str(output_path))
        return
    if not output_path.is_dir():
        report.add_error("La ruta de salida no es un directorio", path=str(output_path))


def _check_required_fonts(report: KdpPreflightReport) -> None:
    for font_path in (FONT_PATH, FONT_PATH_BOLD, FONT_TITLE):
        if not Path(font_path).exists():
            report.add_error("No se encuentra una fuente requerida", path=font_path)


def _check_pdf_file(pdf_path: str, report: KdpPreflightReport) -> None:
    path = Path(pdf_path)
    if not path.exists():
        report.add_error("No existe el PDF final", path=str(path))
        return
    if path.stat().st_size == 0:
        report.add_error("El PDF final esta vacio", path=str(path))
        return
    if not path.read_bytes()[:4] == b"%PDF":
        report.add_error("El archivo final no parece un PDF valido", path=str(path))


def _check_page_images(
    image_paths: list[str],
    report: KdpPreflightReport,
    *,
    label: str,
) -> None:
    if not image_paths:
        report.add_warning(f"No hay imagenes de tipo {label} para revisar")
        return

    for image_path in image_paths:
        path = Path(image_path)
        if not path.exists():
            report.add_error(f"No existe una imagen {label}", path=str(path))
            continue

        try:
            with Image.open(path) as image:
                if image.size != (PAGE_W_PX, PAGE_H_PX):
                    report.add_error(
                        f"La imagen {label} no coincide con el tamano esperado "
                        f"{PAGE_W_PX}x{PAGE_H_PX}px; recibido {image.size[0]}x{image.size[1]}px",
                        path=str(path),
                    )
        except OSError as exc:
            report.add_error(f"No se pudo abrir una imagen {label} ({exc})", path=str(path))
