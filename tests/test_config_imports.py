def test_config_modules_are_importable():
    from wordsearch.config.fonts import FONT_PATH, FONT_PATH_BOLD, FONT_TITLE
    from wordsearch.config.layout import PAGE_H_PX, PAGE_W_PX, TRIM_H_IN, TRIM_W_IN
    from wordsearch.config.paths import BASE_OUTPUT_DIR

    assert BASE_OUTPUT_DIR
    assert FONT_PATH
    assert FONT_PATH_BOLD
    assert FONT_TITLE
    assert PAGE_H_PX > 0
    assert PAGE_W_PX > 0
    assert TRIM_H_IN > 0
    assert TRIM_W_IN > 0


def test_legacy_constants_and_layout_imports_still_work():
    from wordsearch.constants_and_layout import BASE_OUTPUT_DIR, FONT_PATH, PAGE_H_PX, PAGE_W_PX

    assert BASE_OUTPUT_DIR
    assert FONT_PATH
    assert PAGE_H_PX > 0
    assert PAGE_W_PX > 0
