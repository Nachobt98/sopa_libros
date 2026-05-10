import pytest
from PIL import Image

from wordsearch.asset_generation.providers import (
    LOCAL_PLACEHOLDER_PROVIDER,
    LocalPlaceholderProvider,
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
        get_image_provider("openai")


def test_image_generation_request_to_dict_serializes_output_size():
    payload = make_request().to_dict()

    assert payload["asset_id"] == "book_default_background"
    assert payload["output_size"] == [64, 80]
