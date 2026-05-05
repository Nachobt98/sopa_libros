from wordsearch.text_normalization import (
    normalize_word_for_grid,
    normalize_words_for_grid,
    strip_accents,
)


def test_strip_accents_preserves_base_letters():
    assert strip_accents("Atlántico") == "Atlantico"
    assert strip_accents("Café") == "Cafe"


def test_normalize_word_for_grid_removes_spaces_punctuation_and_numbers():
    assert normalize_word_for_grid("Garrett Morgan") == "GARRETTMORGAN"
    assert normalize_word_for_grid("Traffic Light") == "TRAFFICLIGHT"
    assert normalize_word_for_grid("Ge'ez") == "GEEZ"
    assert normalize_word_for_grid("Act 1965") == "ACT"


def test_normalize_word_for_grid_removes_accents_and_uppercases():
    assert normalize_word_for_grid("atlántico") == "ATLANTICO"
    assert normalize_word_for_grid("São Tomé") == "SAOTOME"


def test_normalize_word_for_grid_handles_none_as_empty_string():
    assert normalize_word_for_grid(None) == ""


def test_normalize_words_for_grid_preserves_order():
    words = ["Café", "Traffic Light", "Ge'ez"]
    assert normalize_words_for_grid(words) == ["CAFE", "TRAFFICLIGHT", "GEEZ"]
