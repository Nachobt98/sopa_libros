"""Editorial book format presets for KDP interiors."""

from __future__ import annotations

from dataclasses import dataclass

from wordsearch.config.design import LayoutConfig

KDP_BLEED_IN = 0.125
KDP_MIN_OUTSIDE_MARGIN_NO_BLEED_IN = 0.25
KDP_MIN_OUTSIDE_MARGIN_WITH_BLEED_IN = 0.375
KDP_GUTTER_24_TO_150_IN = 0.375
KDP_GUTTER_151_TO_300_IN = 0.5
KDP_GUTTER_301_TO_500_IN = 0.625


@dataclass(frozen=True)
class BookFormatPreset:
    """Physical and editorial layout preset for one book product format."""

    name: str
    label: str
    trim_width_in: float
    trim_height_in: float
    dpi: int
    bleed: bool
    inside_margin_in: float
    outside_margin_in: float
    top_margin_in: float
    bottom_margin_in: float
    editorial_inner_pad_in: float
    editorial_top_pad_in: float
    editorial_bottom_pad_in: float
    default_title_area_in: float
    panel_pad_x_in: float
    panel_pad_top_in: float
    panel_pad_bottom_in: float
    panel_radius_in: float
    panel_border_width_px: int
    content_margin_x_in: float
    recommended_grid_range: tuple[int, int]
    description: str

    @property
    def page_width_in(self) -> float:
        return self.trim_width_in + (KDP_BLEED_IN if self.bleed else 0.0)

    @property
    def page_height_in(self) -> float:
        return self.trim_height_in + (2 * KDP_BLEED_IN if self.bleed else 0.0)

    @property
    def page_width_px(self) -> int:
        return _in_to_px(self.page_width_in, self.dpi)

    @property
    def page_height_px(self) -> int:
        return _in_to_px(self.page_height_in, self.dpi)

    def to_layout_config(self) -> LayoutConfig:
        safe_left = _in_to_px(self.inside_margin_in + self.editorial_inner_pad_in, self.dpi)
        safe_right = self.page_width_px - _in_to_px(
            self.outside_margin_in + self.editorial_inner_pad_in,
            self.dpi,
        )
        safe_top = _in_to_px(self.top_margin_in + self.editorial_top_pad_in, self.dpi)
        safe_bottom = self.page_height_px - _in_to_px(
            self.bottom_margin_in + self.editorial_bottom_pad_in,
            self.dpi,
        )
        return LayoutConfig(
            name=self.name,
            trim_width_in=self.trim_width_in,
            trim_height_in=self.trim_height_in,
            dpi=self.dpi,
            page_width_px=self.page_width_px,
            page_height_px=self.page_height_px,
            safe_left_px=safe_left,
            safe_right_px=safe_right,
            safe_top_px=safe_top,
            safe_bottom_px=safe_bottom,
            top_px=_in_to_px(self.top_margin_in, self.dpi),
            bottom_px=_in_to_px(self.bottom_margin_in, self.dpi),
            default_title_area_px=_in_to_px(self.default_title_area_in, self.dpi),
            panel_pad_x_px=_in_to_px(self.panel_pad_x_in, self.dpi),
            panel_pad_top_px=_in_to_px(self.panel_pad_top_in, self.dpi),
            panel_pad_bottom_px=_in_to_px(self.panel_pad_bottom_in, self.dpi),
            panel_radius_px=_in_to_px(self.panel_radius_in, self.dpi),
            panel_border_width_px=self.panel_border_width_px,
            content_margin_x_px=_in_to_px(self.content_margin_x_in, self.dpi),
        )


def _in_to_px(value_in: float, dpi: int) -> int:
    return int(round(value_in * dpi))


TRADE_6X9_NO_BLEED = BookFormatPreset(
    name="trade-6x9",
    label="Trade paperback 6 x 9 in",
    trim_width_in=6.0,
    trim_height_in=9.0,
    dpi=300,
    bleed=False,
    inside_margin_in=KDP_GUTTER_24_TO_150_IN,
    outside_margin_in=0.34,
    top_margin_in=0.36,
    bottom_margin_in=0.42,
    editorial_inner_pad_in=0.17,
    editorial_top_pad_in=0.22,
    editorial_bottom_pad_in=0.30,
    default_title_area_in=2.0,
    panel_pad_x_in=0.10,
    panel_pad_top_in=0.13,
    panel_pad_bottom_in=0.13,
    panel_radius_in=0.12,
    panel_border_width_px=3,
    content_margin_x_in=0.13,
    recommended_grid_range=(10, 14),
    description="Compact trade format for lower print cost and premium small-paperback feel.",
)

ACTIVITY_8_5X11_NO_BLEED = BookFormatPreset(
    name="activity-8.5x11",
    label="Activity workbook 8.5 x 11 in",
    trim_width_in=8.5,
    trim_height_in=11.0,
    dpi=300,
    bleed=False,
    inside_margin_in=KDP_GUTTER_24_TO_150_IN,
    outside_margin_in=0.38,
    top_margin_in=0.38,
    bottom_margin_in=0.46,
    editorial_inner_pad_in=0.18,
    editorial_top_pad_in=0.24,
    editorial_bottom_pad_in=0.32,
    default_title_area_in=2.28,
    panel_pad_x_in=0.11,
    panel_pad_top_in=0.14,
    panel_pad_bottom_in=0.14,
    panel_radius_in=0.13,
    panel_border_width_px=3,
    content_margin_x_in=0.16,
    recommended_grid_range=(14, 20),
    description="Large activity-book format with more breathing room for bigger grids and word lists.",
)

LARGE_PRINT_8X10_NO_BLEED = BookFormatPreset(
    name="large-print-8x10",
    label="Large-print puzzle book 8 x 10 in",
    trim_width_in=8.0,
    trim_height_in=10.0,
    dpi=300,
    bleed=False,
    inside_margin_in=KDP_GUTTER_24_TO_150_IN,
    outside_margin_in=0.40,
    top_margin_in=0.40,
    bottom_margin_in=0.48,
    editorial_inner_pad_in=0.22,
    editorial_top_pad_in=0.27,
    editorial_bottom_pad_in=0.36,
    default_title_area_in=2.20,
    panel_pad_x_in=0.12,
    panel_pad_top_in=0.15,
    panel_pad_bottom_in=0.15,
    panel_radius_in=0.14,
    panel_border_width_px=3,
    content_margin_x_in=0.18,
    recommended_grid_range=(12, 16),
    description="Roomy senior-friendly layout with extra margins and calmer density.",
)

SQUARE_8_5_NO_BLEED = BookFormatPreset(
    name="square-8.5",
    label="Square gift/activity book 8.5 x 8.5 in",
    trim_width_in=8.5,
    trim_height_in=8.5,
    dpi=300,
    bleed=False,
    inside_margin_in=KDP_GUTTER_24_TO_150_IN,
    outside_margin_in=0.38,
    top_margin_in=0.38,
    bottom_margin_in=0.44,
    editorial_inner_pad_in=0.18,
    editorial_top_pad_in=0.22,
    editorial_bottom_pad_in=0.30,
    default_title_area_in=1.88,
    panel_pad_x_in=0.11,
    panel_pad_top_in=0.13,
    panel_pad_bottom_in=0.13,
    panel_radius_in=0.13,
    panel_border_width_px=3,
    content_margin_x_in=0.16,
    recommended_grid_range=(12, 16),
    description="Square novelty format; best for giftable themed collections and moderate grids.",
)

FORMAT_PRESETS: dict[str, BookFormatPreset] = {
    preset.name: preset
    for preset in (
        TRADE_6X9_NO_BLEED,
        ACTIVITY_8_5X11_NO_BLEED,
        LARGE_PRINT_8X10_NO_BLEED,
        SQUARE_8_5_NO_BLEED,
    )
}

DEFAULT_FORMAT_NAME = TRADE_6X9_NO_BLEED.name


def format_names() -> tuple[str, ...]:
    return tuple(sorted(FORMAT_PRESETS))


def get_format_preset(name: str | None) -> BookFormatPreset:
    normalized = (name or DEFAULT_FORMAT_NAME).strip().lower()
    try:
        return FORMAT_PRESETS[normalized]
    except KeyError as exc:
        supported = ", ".join(format_names())
        raise ValueError(f"Formato no soportado: {name}. Formatos disponibles: {supported}") from exc
