import base64
import sys
from types import SimpleNamespace

import pytest
from PIL import Image

from wordsearch.asset_generation.providers import (
    LOCAL_PLACEHOLDER_PROVIDER,
    OPENAI_PROVIDER,
    LocalPlaceholderProvider,
    OpenAIImageProvider,
    _combine_prompt,
    get_image_provider,
)
from wordsearch.asset_generation.requests import ImageGenerationRequest


def make_request() -> ImageGenerationRequest:
    return ImageGenerationRequest(
        asset_id="book_default_background",
        asset_type="background",
        prompt="Prompt",
        negative_prompt="No text",
        output_size=(64, 80),
        metadata={"label": "Book", "variant": "1"},
    )


def test_local_placeholder_provider_generates_raw_png(tmp_path):
    provider = LocalPlaceholderProvider()
    output_path = tmp_path / "raw" / "asset.png"

    generated = provider.generate(make_request(), output_path)

    assert generated.provider == LOCAL_PLACEHOLDER_PROVIDER
    assert generated.path == str(output_path)
    assert generated.request.asset_id == "book_default_background"
    with Image.open(output_path) as image:
        assert image.size == (64, 80)
        assert image.mode == "RGB"


def test_get_image_provider_returns_local_placeholder_provider():
    provider = get_image_provider(LOCAL_PLACEHOLDER_PROVIDER)

    assert isinstance(provider, LocalPlaceholderProvider)


def test_get_image_provider_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unknown image provider"):
        get_image_provider("unknown")


def test_image_generation_request_to_dict_serializes_output_size():
    payload = make_request().to_dict()

    assert payload["asset_id"] == "book_default_background"
    assert payload["output_size"] == [64, 80]


def test_combine_prompt_appends_negative_prompt():
    combined = _combine_prompt(make_request())

    assert "Prompt" in combined
    assert "Avoid: No text" in combined


def test_combine_prompt_omits_empty_negative_prompt():
    request = ImageGenerationRequest(
        asset_id="asset",
        asset_type="background",
        prompt="Only positive",
        negative_prompt=None,
        output_size=(64, 80),
    )

    assert _combine_prompt(request) == "Only positive"


def test_openai_image_provider_generates_png_with_fake_client(tmp_path):
    class FakeImages:
        def __init__(self):
            self.calls = []

        def generate(self, **kwargs):
            self.calls.append(kwargs)
            png_bytes = base64.b64encode(_tiny_png_bytes()).decode("ascii")
            return SimpleNamespace(data=[SimpleNamespace(b64_json=png_bytes)])

    fake_images = FakeImages()
    fake_client = SimpleNamespace(images=fake_images)
    provider = OpenAIImageProvider(client=fake_client, model="test-model", image_size="1024x1536")
    output_path = tmp_path / "raw" / "openai.png"

    generated = provider.generate(make_request(), output_path)

    assert generated.provider == OPENAI_PROVIDER
    assert output_path.exists()
    assert fake_images.calls == [
        {
            "model": "test-model",
            "prompt": "Prompt\n\nAvoid: No text",
            "size": "1024x1536",
        }
    ]


def test_openai_image_provider_requires_b64_json(tmp_path):
    fake_client = SimpleNamespace(images=SimpleNamespace(generate=lambda **kwargs: SimpleNamespace(data=[SimpleNamespace(b64_json=None)])))
    provider = OpenAIImageProvider(client=fake_client)

    with pytest.raises(RuntimeError, match="b64_json"):
        provider.generate(make_request(), tmp_path / "raw" / "missing.png")


def test_openai_image_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        OpenAIImageProvider()


def test_openai_image_provider_reports_missing_optional_dependency(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "openai", None)

    with pytest.raises(RuntimeError, match="optional dependency"):
        OpenAIImageProvider()


def _tiny_png_bytes() -> bytes:
    import io

    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "white").save(buffer, format="PNG")
    return buffer.getvalue()
