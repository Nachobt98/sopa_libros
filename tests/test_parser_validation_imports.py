def test_new_parser_modules_are_importable():
    from wordsearch.domain.puzzle import PuzzleSpec
    from wordsearch.parsing.thematic import PuzzleParseError, parse_puzzle_file

    assert callable(PuzzleSpec)
    assert issubclass(PuzzleParseError, Exception)
    assert callable(parse_puzzle_file)


def test_new_validation_module_is_importable():
    from wordsearch.validation.thematic import (
        ThematicValidationReport,
        ValidationIssue,
        validate_thematic_specs,
    )

    assert callable(ThematicValidationReport)
    assert callable(ValidationIssue)
    assert callable(validate_thematic_specs)
