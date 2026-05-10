"""Normalization helpers for generated image assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


def normalize_generated_asset(raw_path: str | Path, output_path: str | Path, target_size: tuple[int, int]) -> str:
    """Normalize a raw generated image into a renderer-ready PNG.

    The first implementation intentionally stays conservative: it converts to RGB,
    resizes to the expected page size and writes a PNG to the processed folder.
    """
    raw = Path(raw_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(raw) as image:
        normalized = image.convert("RGB").resize(target_size, Image.Resampling.LANCZOS)
        normalized.save(output)
    return str(output)
