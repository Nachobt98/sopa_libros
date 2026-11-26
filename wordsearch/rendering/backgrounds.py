"""Shared rendering background configuration."""

import os

from PIL import Image

from wordsearch.config.design import DEFAULT_THEME, PageType, ThemeConfig

BACKGROUND_PATH = "assets/world.png"


def create_page_background(
    background_path: str | None,
    width_px: int,
    height_px: int,
    *,
    theme: ThemeConfig = DEFAULT_THEME,
    page_type: PageType | None = None,
) -> Image.Image:
    """Create a page background, applying the selected theme's image opacity."""
    size = (width_px, height_px)
    bg_path = background_path or BACKGROUND_PATH

    if bg_path and os.path.exists(bg_path):
        with Image.open(bg_path) as source:
            background = source.convert("RGBA").resize(size, Image.LANCZOS)

        alpha = background.getchannel("A")
        alpha = alpha.point(lambda value: int(value * theme.background_opacity_for(page_type)))
        background.putalpha(alpha)
        if theme.composite_page_background:
            page = Image.new("RGBA", size, theme.page_background_fill)
            return Image.alpha_composite(page, background)
        return background

    return Image.new("RGBA", size, theme.page_background_fill)
