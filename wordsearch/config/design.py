"""Editorial design configuration for generated KDP interiors.

This module groups layout and theme decisions into explicit immutable objects.
The default configs mirror the current renderer constants so introducing this
layer does not intentionally change the generated visual output.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any, Literal

from wordsearch.config.fonts import FONT_PATH, FONT_PATH_BOLD, FONT_TITLE
from wordsearch.config.layout import (
    BOTTOM_PX,
    DPI,
    PAGE_H_PX,
    PAGE_W_PX,
    SAFE_BOTTOM,
    SAFE_LEFT,
    SAFE_RIGHT,
    SAFE_TOP,
    TOP_PX,
    TRIM_H_IN,
    TRIM_W_IN,
)

ColorRgba = tuple[int, int, int, int]
ColorValue = ColorRgba | str
PageType = Literal["title_page", "block_cover", "puzzle", "table_of_contents", "instructions", "solutions"]
DecorationMotif = Literal[
    "star",
    "snowflake",
    "evergreen_tree",
    "bell",
    "botanical_branch",
    "holly",
    "lantern",
    "candle",
    "gift",
    "ornament",
    "flower",
    "house",
    "star_lantern",
    "globe",
    "compass",
    "geometric_ornament",
    "garland",
]
DecorationRegion = Literal["page", "separator"]
PAGE_TYPES = ("title_page", "block_cover", "puzzle", "table_of_contents", "instructions", "solutions")
DECORATION_MOTIFS = (
    "star",
    "snowflake",
    "evergreen_tree",
    "bell",
    "botanical_branch",
    "holly",
    "lantern",
    "candle",
    "gift",
    "ornament",
    "flower",
    "house",
    "star_lantern",
    "globe",
    "compass",
    "geometric_ornament",
    "garland",
)


@dataclass(frozen=True)
class DecorationPlacement:
    """A monochrome motif positioned within a normalized page region."""

    motif: DecorationMotif
    x: float
    y: float
    size_ratio: float = 0.04
    stroke_width_ratio: float = 0.035
    color: int = 72
    opacity: float = 0.72
    rotation_degrees: float = 0.0

    def __post_init__(self) -> None:
        if self.motif not in DECORATION_MOTIFS:
            raise ValueError(f"Unknown decoration motif: {self.motif}")
        values = (self.x, self.y, self.size_ratio, self.stroke_width_ratio, self.opacity, self.rotation_degrees)
        if any(
            not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
            for value in values
        ):
            raise ValueError("Decoration position, size, stroke, opacity, and rotation must be finite numbers.")
        if not 0 <= self.x <= 1 or not 0 <= self.y <= 1:
            raise ValueError("Decoration position values must be between 0 and 1.")
        if not 0 < self.size_ratio <= 0.5:
            raise ValueError("Decoration size_ratio must be greater than 0 and at most 0.5.")
        if not 0 < self.stroke_width_ratio <= 0.25:
            raise ValueError("Decoration stroke_width_ratio must be greater than 0 and at most 0.25.")
        if not isinstance(self.color, int) or isinstance(self.color, bool) or not 0 <= self.color <= 255:
            raise ValueError("Decoration color must be a grayscale value between 0 and 255.")
        if not 0 <= self.opacity <= 1:
            raise ValueError("Decoration opacity must be between 0 and 1.")


@dataclass(frozen=True)
class PageDecorationConfig:
    """Decoration settings for one page type and reserved drawing region."""

    page_type: PageType
    placements: tuple[DecorationPlacement, ...]
    enabled: bool = True
    region: DecorationRegion = "page"

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError("Decoration page 'enabled' must be a boolean.")
        if not isinstance(self.placements, tuple) or any(
            not isinstance(placement, DecorationPlacement) for placement in self.placements
        ):
            raise ValueError("Decoration page placements must be an immutable tuple of placements.")
        if self.page_type not in PAGE_TYPES:
            raise ValueError(f"Unknown decoration page type: {self.page_type}")
        if self.region not in ("page", "separator"):
            raise ValueError(f"Unknown decoration region: {self.region}")
        if self.region == "separator" and self.page_type != "puzzle":
            raise ValueError("The separator region is currently supported only for puzzle pages.")


@dataclass(frozen=True)
class DecorationConfig:
    """Immutable optional page and motif configuration."""

    enabled: bool = False
    pages: tuple[PageDecorationConfig, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError("Decoration config 'enabled' must be a boolean.")
        if not isinstance(self.pages, tuple) or any(
            not isinstance(page, PageDecorationConfig) for page in self.pages
        ):
            raise ValueError("Decoration pages must be an immutable tuple of page configs.")
        page_types = tuple(page.page_type for page in self.pages)
        if len(page_types) != len(set(page_types)):
            raise ValueError("Decoration page types must be unique.")

    def for_page(self, page_type: PageType) -> PageDecorationConfig | None:
        if not self.enabled:
            return None
        return next(
            (page for page in self.pages if page.page_type == page_type and page.enabled and page.placements),
            None,
        )

    def with_overrides(self, override: DecorationConfig) -> DecorationConfig:
        """Return this config with explicitly supplied page settings replaced."""
        if not override.enabled:
            return override
        pages = {page.page_type: page for page in self.pages}
        pages.update({page.page_type: page for page in override.pages})
        return DecorationConfig(enabled=True, pages=tuple(pages.values()))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> DecorationConfig:
        enabled = payload.get("enabled", False)
        pages_payload = payload.get("pages", [])
        if not isinstance(enabled, bool):
            raise ValueError("Decoration config 'enabled' must be a boolean.")
        if not isinstance(pages_payload, (list, tuple)):
            raise ValueError("Decoration config 'pages' must be an array.")

        pages = []
        for page_payload in pages_payload:
            if not isinstance(page_payload, dict):
                raise ValueError("Each decoration page config must be an object.")
            page_enabled = page_payload.get("enabled", True)
            placements_payload = page_payload.get("placements", [])
            if not isinstance(page_enabled, bool):
                raise ValueError("Decoration page 'enabled' must be a boolean.")
            if not isinstance(placements_payload, (list, tuple)):
                raise ValueError("Decoration page 'placements' must be an array.")

            placements = []
            for placement_payload in placements_payload:
                if not isinstance(placement_payload, dict):
                    raise ValueError("Each decoration placement must be an object.")
                try:
                    placement = DecorationPlacement(
                        motif=placement_payload["motif"],
                        x=float(placement_payload["x"]),
                        y=float(placement_payload["y"]),
                        size_ratio=float(placement_payload.get("size_ratio", 0.04)),
                        stroke_width_ratio=float(placement_payload.get("stroke_width_ratio", 0.035)),
                        color=int(placement_payload.get("color", 72)),
                        opacity=float(placement_payload.get("opacity", 0.72)),
                        rotation_degrees=float(placement_payload.get("rotation_degrees", 0.0)),
                    )
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid decoration placement: {exc}") from exc
                placements.append(placement)

            try:
                pages.append(
                    PageDecorationConfig(
                        page_type=page_payload["page_type"],
                        placements=tuple(placements),
                        enabled=page_enabled,
                        region=page_payload.get("region", "page"),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid decoration page config: {exc}") from exc

        return cls(enabled=enabled, pages=tuple(pages))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LayoutConfig:
    """Physical page and safe-area configuration."""

    name: str
    trim_width_in: float
    trim_height_in: float
    dpi: int
    page_width_px: int
    page_height_px: int
    safe_left_px: int
    safe_right_px: int
    safe_top_px: int
    safe_bottom_px: int
    top_px: int
    bottom_px: int
    default_title_area_px: int = 600
    panel_pad_x_px: int = 30
    panel_pad_top_px: int = 40
    panel_pad_bottom_px: int = 40
    panel_radius_px: int = 35
    panel_border_width_px: int = 3
    content_margin_x_px: int = 40


@dataclass(frozen=True)
class TypographyConfig:
    """Font paths and base type sizes used by the current renderer."""

    body_font_path: str
    bold_font_path: str
    title_font_path: str
    title_font_size: int = 100
    wordlist_font_size: int = 80


@dataclass(frozen=True)
class ThemeConfig:
    """Visual theme tokens for renderer defaults."""

    name: str
    background_opacity: float
    page_background_fill: ColorRgba
    panel_fill: ColorRgba
    panel_border: ColorRgba
    title_color: ColorRgba
    body_color: ColorRgba
    panel_radius_px: int
    panel_border_width_px: int
    fact_card_fill: ColorRgba
    fact_card_border: ColorRgba
    fact_header_fill: ColorRgba
    fact_header_text: ColorRgba
    fact_card_radius_px: int
    fact_card_border_width_px: int
    pill_fill: ColorRgba
    pill_border: ColorRgba
    pill_text: ColorRgba
    pill_border_width_px: int
    grid_line_color: ColorValue
    letter_color: ColorRgba
    solution_letter_color: ColorRgba
    highlight_fill: ColorRgba
    highlight_border: ColorRgba
    page_background_opacities: tuple[tuple[PageType, float], ...] = ()
    composite_page_background: bool = False
    background_grayscale: bool = False
    decorations: DecorationConfig = DecorationConfig()
    block_decorations: tuple[tuple[str, DecorationConfig], ...] = ()

    def background_opacity_for(self, page_type: PageType | None = None) -> float:
        """Return the configured opacity for a page, falling back to the theme default."""
        for configured_page_type, opacity in self.page_background_opacities:
            if configured_page_type == page_type:
                return opacity
        return self.background_opacity

    def decorations_for_block(self, block_name: str | None) -> DecorationConfig:
        """Return a case-insensitive block override or the theme's default decorations."""
        if block_name:
            normalized_name = block_name.strip().casefold()
            for configured_name, decoration_config in self.block_decorations:
                if configured_name.strip().casefold() == normalized_name:
                    return decoration_config
        return self.decorations


DEFAULT_LAYOUT = LayoutConfig(
    name="kdp-6x9-no-bleed",
    trim_width_in=TRIM_W_IN,
    trim_height_in=TRIM_H_IN,
    dpi=DPI,
    page_width_px=PAGE_W_PX,
    page_height_px=PAGE_H_PX,
    safe_left_px=SAFE_LEFT,
    safe_right_px=SAFE_RIGHT,
    safe_top_px=SAFE_TOP,
    safe_bottom_px=SAFE_BOTTOM,
    top_px=TOP_PX,
    bottom_px=BOTTOM_PX,
)

DEFAULT_TYPOGRAPHY = TypographyConfig(
    body_font_path=FONT_PATH,
    bold_font_path=FONT_PATH_BOLD,
    title_font_path=FONT_TITLE,
)

DEFAULT_THEME = ThemeConfig(
    name="current-default",
    background_opacity=0.7,
    page_background_fill=(255, 255, 255, 255),
    panel_fill=(255, 255, 255, 150),
    panel_border=(0, 0, 0, 60),
    title_color=(0, 0, 0, 255),
    body_color=(0, 0, 0, 255),
    panel_radius_px=DEFAULT_LAYOUT.panel_radius_px,
    panel_border_width_px=DEFAULT_LAYOUT.panel_border_width_px,
    fact_card_fill=(245, 245, 245, 245),
    fact_card_border=(170, 170, 170, 255),
    fact_header_fill=(30, 30, 30, 255),
    fact_header_text=(255, 255, 255, 255),
    fact_card_radius_px=18,
    fact_card_border_width_px=2,
    pill_fill=(230, 230, 230, 255),
    pill_border=(120, 120, 120, 255),
    pill_text=(0, 0, 0, 255),
    pill_border_width_px=2,
    grid_line_color="#444444",
    letter_color=(0, 0, 0, 255),
    solution_letter_color=(0, 0, 0, 255),
    highlight_fill=(243, 226, 200, 230),
    highlight_border=(0, 0, 0, 255),
)

PREMIUM_NEUTRAL_THEME = ThemeConfig(
    name="premium-neutral",
    background_opacity=0.42,
    page_background_fill=(247, 241, 229, 255),
    panel_fill=(255, 251, 242, 232),
    panel_border=(106, 84, 58, 150),
    title_color=(54, 43, 30, 255),
    body_color=(59, 48, 35, 255),
    panel_radius_px=34,
    panel_border_width_px=4,
    fact_card_fill=(253, 246, 235, 250),
    fact_card_border=(151, 119, 78, 190),
    fact_header_fill=(92, 70, 44, 255),
    fact_header_text=(255, 247, 232, 255),
    fact_card_radius_px=22,
    fact_card_border_width_px=3,
    pill_fill=(238, 221, 195, 255),
    pill_border=(137, 101, 60, 220),
    pill_text=(69, 50, 29, 255),
    pill_border_width_px=3,
    grid_line_color=(116, 93, 64, 255),
    letter_color=(48, 38, 27, 255),
    solution_letter_color=(36, 29, 21, 255),
    highlight_fill=(215, 169, 98, 138),
    highlight_border=(101, 72, 38, 235),
)

BOLD_MODERN_THEME = ThemeConfig(
    name="bold-modern",
    background_opacity=0.22,
    page_background_fill=(241, 245, 249, 255),
    panel_fill=(255, 255, 255, 238),
    panel_border=(15, 23, 42, 215),
    title_color=(2, 6, 23, 255),
    body_color=(15, 23, 42, 255),
    panel_radius_px=18,
    panel_border_width_px=6,
    fact_card_fill=(226, 232, 240, 255),
    fact_card_border=(15, 23, 42, 230),
    fact_header_fill=(15, 23, 42, 255),
    fact_header_text=(248, 250, 252, 255),
    fact_card_radius_px=14,
    fact_card_border_width_px=4,
    pill_fill=(219, 234, 254, 255),
    pill_border=(29, 78, 216, 245),
    pill_text=(30, 64, 175, 255),
    pill_border_width_px=4,
    grid_line_color=(30, 41, 59, 255),
    letter_color=(2, 6, 23, 255),
    solution_letter_color=(2, 6, 23, 255),
    highlight_fill=(96, 165, 250, 115),
    highlight_border=(29, 78, 216, 245),
)

KIDS_THEME = ThemeConfig(
    name="kids",
    background_opacity=0.36,
    page_background_fill=(255, 248, 220, 255),
    panel_fill=(255, 255, 255, 238),
    panel_border=(37, 99, 235, 175),
    title_color=(190, 24, 93, 255),
    body_color=(31, 41, 55, 255),
    panel_radius_px=58,
    panel_border_width_px=6,
    fact_card_fill=(255, 247, 237, 255),
    fact_card_border=(249, 115, 22, 220),
    fact_header_fill=(37, 99, 235, 255),
    fact_header_text=(255, 255, 255, 255),
    fact_card_radius_px=32,
    fact_card_border_width_px=5,
    pill_fill=(254, 240, 138, 255),
    pill_border=(234, 88, 12, 235),
    pill_text=(124, 45, 18, 255),
    pill_border_width_px=5,
    grid_line_color=(37, 99, 235, 210),
    letter_color=(17, 24, 39, 255),
    solution_letter_color=(17, 24, 39, 255),
    highlight_fill=(244, 114, 182, 120),
    highlight_border=(190, 24, 93, 235),
)


def _christmas_block_decorations(motifs: tuple[DecorationMotif, ...]) -> DecorationConfig:
    count = len(motifs)
    if not count:
        raise ValueError("Christmas block decorations must include at least one motif.")

    x_positions = tuple(0.14 + (0.72 * index / max(count - 1, 1)) for index in range(count))
    cover_placements = tuple(
        DecorationPlacement(
            motif=motif,
            x=x,
            y=y,
            size_ratio=0.048 if count > 2 else 0.054,
            stroke_width_ratio=0.028,
            color=68,
            opacity=0.68,
            rotation_degrees=180 if y > 0.5 else 0,
        )
        for y in (0.08, 0.92)
        for motif, x in zip(motifs, x_positions)
    )
    separator_motifs = (motifs[0], motifs[-1])
    puzzle_placements = tuple(
        DecorationPlacement(
            motif=motif,
            x=x,
            y=0.5,
            size_ratio=0.018,
            stroke_width_ratio=0.05,
            color=68,
            opacity=0.62,
        )
        for motif, x in zip(separator_motifs, (0.22, 0.78))
    )
    return DecorationConfig(
        enabled=True,
        pages=(
            PageDecorationConfig("block_cover", cover_placements),
            PageDecorationConfig("puzzle", puzzle_placements, region="separator"),
        ),
    )


_CHRISTMAS_BLOCK_MOTIFS: tuple[tuple[str, tuple[DecorationMotif, ...]], ...] = (
    ("Christmas Classics", ("bell", "holly", "star")),
    ("Western European Christmas", ("lantern", "garland", "house")),
    ("Nordic Christmas Magic", ("snowflake", "evergreen_tree")),
    ("Central and Eastern European Traditions", ("star", "geometric_ornament")),
    ("Mediterranean Christmas", ("botanical_branch", "candle", "star")),
    ("A North American Christmas", ("gift", "evergreen_tree", "ornament")),
    ("Latin American Christmas", ("star_lantern", "flower", "lantern")),
    ("Christmas Across Asia and Oceania", ("star_lantern", "botanical_branch", "flower")),
    ("Christmas in Africa and the Middle East", ("candle", "star", "geometric_ornament")),
    ("Global Christmas Treasures", ("globe", "compass", "star")),
)

CHRISTMAS_VINTAGE_THEME = ThemeConfig(
    name="christmas-vintage",
    background_opacity=0.12,
    page_background_fill=(255, 255, 255, 255),
    panel_fill=(255, 255, 255, 240),
    panel_border=(176, 176, 176, 255),
    title_color=(35, 35, 35, 255),
    body_color=(54, 54, 54, 255),
    panel_radius_px=24,
    panel_border_width_px=2,
    fact_card_fill=(248, 248, 248, 255),
    fact_card_border=(172, 172, 172, 255),
    fact_header_fill=(62, 62, 62, 255),
    fact_header_text=(255, 255, 255, 255),
    fact_card_radius_px=18,
    fact_card_border_width_px=2,
    pill_fill=(239, 239, 239, 255),
    pill_border=(155, 155, 155, 255),
    pill_text=(42, 42, 42, 255),
    pill_border_width_px=2,
    grid_line_color=(125, 125, 125, 255),
    letter_color=(28, 28, 28, 255),
    solution_letter_color=(24, 24, 24, 255),
    highlight_fill=(188, 188, 188, 90),
    highlight_border=(85, 85, 85, 230),
    page_background_opacities=(
        ("title_page", 0.60),
        ("block_cover", 0.35),
        ("puzzle", 0.12),
        ("table_of_contents", 0.08),
        ("instructions", 0.08),
        ("solutions", 0.00),
    ),
    composite_page_background=True,
    background_grayscale=True,
    decorations=_christmas_block_decorations(("star",)),
    block_decorations=tuple(
        (block_name, _christmas_block_decorations(motifs))
        for block_name, motifs in _CHRISTMAS_BLOCK_MOTIFS
    ),
)

THEME_PRESETS: dict[str, ThemeConfig] = {
    DEFAULT_THEME.name: DEFAULT_THEME,
    PREMIUM_NEUTRAL_THEME.name: PREMIUM_NEUTRAL_THEME,
    BOLD_MODERN_THEME.name: BOLD_MODERN_THEME,
    KIDS_THEME.name: KIDS_THEME,
    CHRISTMAS_VINTAGE_THEME.name: CHRISTMAS_VINTAGE_THEME,
}

DEFAULT_THEME_NAME = DEFAULT_THEME.name


def theme_names() -> tuple[str, ...]:
    """Return available theme preset names sorted for CLI/documentation use."""
    return tuple(sorted(THEME_PRESETS))


def get_theme(name: str | None) -> ThemeConfig:
    """Return a theme preset by name."""
    normalized = (name or DEFAULT_THEME_NAME).strip().lower()
    try:
        return THEME_PRESETS[normalized]
    except KeyError as exc:
        supported = ", ".join(theme_names())
        raise ValueError(f"Tema no soportado: {name}. Temas disponibles: {supported}") from exc
