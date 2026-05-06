def test_legacy_grid_generation_imports_still_work():
    from wordsearch.grid_generation import generate_word_search_grid, place_words_on_grid

    assert callable(generate_word_search_grid)
    assert callable(place_words_on_grid)


def test_new_grid_generation_module_is_importable():
    from wordsearch.generation.grid import generate_word_search_grid, place_words_on_grid

    assert callable(generate_word_search_grid)
    assert callable(place_words_on_grid)
