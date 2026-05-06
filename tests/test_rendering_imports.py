def test_new_rendering_modules_are_importable():
    from wordsearch.rendering.backgrounds import BACKGROUND_PATH
    from wordsearch.rendering.block_cover import render_block_cover
    from wordsearch.rendering.front_matter import (
        render_instructions_page,
        render_table_of_contents,
    )
    from wordsearch.rendering.highlights import build_solution_highlight_layer
    from wordsearch.rendering.pdf import generate_pdf
    from wordsearch.rendering.puzzle_page import render_page
    from wordsearch.rendering.title_page import render_title_page
    from wordsearch.rendering.word_list import draw_word_list

    assert isinstance(BACKGROUND_PATH, str)
    assert callable(render_block_cover)
    assert callable(render_instructions_page)
    assert callable(render_table_of_contents)
    assert callable(build_solution_highlight_layer)
    assert callable(generate_pdf)
    assert callable(render_page)
    assert callable(render_title_page)
    assert callable(draw_word_list)
