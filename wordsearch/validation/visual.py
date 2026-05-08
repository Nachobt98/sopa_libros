"""Lightweight visual regression helpers for generated page images."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageStat

from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX
from wordsearch.config.paths import build_output_file

VISUAL_REGRESSION_REPORT_FILENAME = "visual_regression_report.json"
VISUAL_REGRESSION_SCHEMA_VERSION = 1
DEFAULT_FINGERPRINT_SIZE = 12


@dataclass(frozen=True)
class VisualFingerprint:
    """Small deterministic fingerprint for a rendered PNG page."""

    path: str
    width: int
    height: int
    average_luma: float
    luma_stddev: float
    difference_hash: str


@dataclass(frozen=True)
class VisualRegressionReport:
    """Serializable report containing fingerprints for visual comparison."""

    schema_version: int
    expected_width: int
    expected_height: int
    fingerprint_size: int
    fingerprints: list[VisualFingerprint]

    def to_dict(self) -> dict:
        return asdict(self)


def build_visual_regression_report(
    image_paths: Iterable[str],
    *,
    fingerprint_size: int = DEFAULT_FINGERPRINT_SIZE,
) -> VisualRegressionReport:
    """Build perceptual fingerprints for the provided rendered image paths."""
    fingerprints = [
        fingerprint_image(path, fingerprint_size=fingerprint_size)
        for path in image_paths
    ]
    return VisualRegressionReport(
        schema_version=VISUAL_REGRESSION_SCHEMA_VERSION,
        expected_width=PAGE_W_PX,
        expected_height=PAGE_H_PX,
        fingerprint_size=fingerprint_size,
        fingerprints=fingerprints,
    )


def write_visual_regression_report(report: VisualRegressionReport, *, output_dir: str) -> str:
    """Write a visual regression fingerprint report JSON and return its path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    report_path = build_output_file(output_dir, VISUAL_REGRESSION_REPORT_FILENAME)
    Path(report_path).write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return report_path


def fingerprint_image(path: str, *, fingerprint_size: int = DEFAULT_FINGERPRINT_SIZE) -> VisualFingerprint:
    """Return a small visual fingerprint for one rendered page image."""
    image_path = Path(path)
    with Image.open(image_path) as image:
        rgba = image.convert("RGBA")
        gray = rgba.convert("L")
        stat = ImageStat.Stat(gray)
        width, height = rgba.size
        return VisualFingerprint(
            path=str(image_path),
            width=width,
            height=height,
            average_luma=round(float(stat.mean[0]), 3),
            luma_stddev=round(float(stat.stddev[0]), 3),
            difference_hash=_difference_hash(gray, fingerprint_size=fingerprint_size),
        )


def _difference_hash(gray_image: Image.Image, *, fingerprint_size: int) -> str:
    """Compute a compact horizontal difference hash for a grayscale image."""
    if fingerprint_size <= 0:
        raise ValueError("fingerprint_size must be positive")

    resized = gray_image.resize((fingerprint_size + 1, fingerprint_size), Image.Resampling.LANCZOS)
    pixels = list(resized.getdata())
    bits: list[str] = []
    row_width = fingerprint_size + 1

    for y in range(fingerprint_size):
        row_start = y * row_width
        for x in range(fingerprint_size):
            left = pixels[row_start + x]
            right = pixels[row_start + x + 1]
            bits.append("1" if left > right else "0")

    value = int("".join(bits), 2) if bits else 0
    hex_width = max(1, (len(bits) + 3) // 4)
    return f"{value:0{hex_width}x}"
