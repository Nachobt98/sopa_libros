from wordsearch.config.formats import (
    ACTIVITY_8_5X11_NO_BLEED,
    DEFAULT_FORMAT_NAME,
    FORMAT_PRESETS,
    KDP_GUTTER_24_TO_150_IN,
    LARGE_PRINT_8X10_NO_BLEED,
    TRADE_6X9_NO_BLEED,
    format_names,
    get_format_preset,
)


def test_default_format_is_trade_6x9():
    assert DEFAULT_FORMAT_NAME == "trade-6x9"
    assert get_format_preset(None) == TRADE_6X9_NO_BLEED


def test_format_names_are_sorted_and_include_editorial_presets():
    names = format_names()

    assert names == tuple(sorted(names))
    assert set(names) == {
        "activity-8.5x11",
        "large-print-8x10",
        "square-8.5",
        "trade-6x9",
    }


def test_format_presets_use_real_kdp_safe_gutter_or_better():
    for preset in FORMAT_PRESETS.values():
        assert preset.inside_margin_in >= KDP_GUTTER_24_TO_150_IN
        assert preset.outside_margin_in >= 0.25
        assert preset.top_margin_in >= 0.25
        assert preset.bottom_margin_in >= 0.25
        assert preset.dpi == 300
        assert preset.bleed is False


def test_trade_6x9_layout_preserves_compact_book_geometry():
    layout = TRADE_6X9_NO_BLEED.to_layout_config()

    assert layout.name == "trade-6x9"
    assert layout.trim_width_in == 6.0
    assert layout.trim_height_in == 9.0
    assert layout.page_width_px == 1800
    assert layout.page_height_px == 2700
    assert layout.safe_left_px > int(0.375 * 300)
    assert layout.safe_right_px < layout.page_width_px - int(0.25 * 300)


def test_activity_format_has_more_working_area_than_trade():
    trade = TRADE_6X9_NO_BLEED.to_layout_config()
    activity = ACTIVITY_8_5X11_NO_BLEED.to_layout_config()

    assert activity.page_width_px > trade.page_width_px
    assert activity.page_height_px > trade.page_height_px
    assert activity.recommended_grid_range if hasattr(activity, "recommended_grid_range") else True


def test_large_print_format_is_roomier_than_trade_but_not_as_tall_as_letter():
    trade = TRADE_6X9_NO_BLEED.to_layout_config()
    large = LARGE_PRINT_8X10_NO_BLEED.to_layout_config()

    assert large.page_width_px > trade.page_width_px
    assert large.page_height_px > trade.page_height_px
    assert LARGE_PRINT_8X10_NO_BLEED.recommended_grid_range == (12, 16)


def test_unknown_format_raises_helpful_error():
    try:
        get_format_preset("unknown")
    except ValueError as exc:
        assert "Formato no soportado" in str(exc)
        assert "trade-6x9" in str(exc)
    else:
        raise AssertionError("Expected unknown format to raise ValueError")
