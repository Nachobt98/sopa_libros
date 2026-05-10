"""Image generation request models for generated book assets."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class ImageGenerationRequest:
    """Provider-facing request for one generated visual asset."""

    asset_id: str
    asset_type: str
    prompt: str
    negative_prompt: str | None
    output_size: tuple[int, int]
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["output_size"] = list(self.output_size)
        return payload


@dataclass(frozen=True)
class GeneratedImage:
    """Result returned by an image provider before normalization."""

    request: ImageGenerationRequest
    path: str
    provider: str

    def to_dict(self) -> dict:
        return {
            "request": self.request.to_dict(),
            "path": self.path,
            "provider": self.provider,
        }
