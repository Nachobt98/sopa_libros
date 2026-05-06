def test_generation_orchestration_modules_are_importable():
    from wordsearch.generation.book_assembly import (
        build_toc_entries,
        render_thematic_book_images,
    )
    from wordsearch.generation.grid_batch import generate_thematic_grids
    from wordsearch.generation.thematic_pipeline import generate_thematic_book

    assert callable(build_toc_entries)
    assert callable(render_thematic_book_images)
    assert callable(generate_thematic_grids)
    assert callable(generate_thematic_book)
