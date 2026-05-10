"""Image provider abstraction for generated book assets."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from PIL import Image, ImageDraw

from wordsearch.asset_generation.requests import GeneratedImage, ImageGenerationRequest

LOCAL_PLACEHOLDER_PROVIDER = "local-placeholder"
AVAILABLE_IMAGE_PROVIDERS = (LOCAL_PLACEHOLDER_PROVIDER,)


class ImageProvider(Protocol):
    """Protocol implemented by generated-image providers."""

    name: str

    def generate(self, request: ImageGenerationRequest, output_path: Path) -> GeneratedImage:
        """Generate one raw image file and return its provider result."""
        ...


class LocalPlaceholderProvider:
    """Deterministic provider used for tests and provider-free local workflows."""

    name = LOCAL_PLACEHOLDER_PROVIDER

    def generate(self, request: ImageGenerationRequest, output_path: Path) -> GeneratedImage:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_editorial_placeholder(output_path, request.output_size, label=request.metadata.get("label", request.asset_id), variant=request.metadata.get("variant", "0"))
        return GeneratedImage(request=request, path=str(output_path), provider=self.name)


def get_image_provider(name: str) -> ImageProvider:
    """Return an image provider by CLI name."""
    if name == LOCAL_PLACEHOLDER_PROVIDER:
        return LocalPlaceholderProvider()
    available = ", ".join(AVAILABLE_IMAGE_PROVIDERS)
    raise ValueError(f"Unknown image provider '{name}'. Available providers: {available}")


def _write_editorial_placeholder(path: Path, size: tuple[int, int], *, label: str, variant: str) -> None:
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


def _variant_color(variant: str) -> tuple[int, int, int]:
    palettes = [
        (245, 239, 225),
        (238, 232, 218),
        (242, 236, 224),
        (235, 230, 218),
        (246, 241, 231),
    ]
    try:
        index = int(variant)
    except ValueError:
        index = sum(ord(char) for char in variant)
    return palettes[index % len(palettes)]
