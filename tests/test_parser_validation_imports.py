def test_new_parser_modules_are_importable():
    from wordsearch.domain.puzzle import PuzzleSpec
    from wordsearch.parsing.thematic import PuzzleParseError, parse_puzzle_file

    assert callable(PuzzleSpec)
    assert issubclass(PuzzleParseError, Exception)
    assert callable(parse_puzzle_file)


def test_legacy_parser_imports_still_work():
    from wordsearch.domain.puzzle import PuzzleSpec
    from wordsearch.parsing.thematic import PuzzleParseError, parse_puzzle_file
    from wordsearch.puzzle_parser import PuzzleParseError as legacy_parse_error
    from wordsearch.puzzle_parser import PuzzleSpec as legacy_puzzle_spec
    from wordsearch.puzzle_parser import parse_puzzle_file as legacy_parse_puzzle_file

    assert legacy_puzzle_spec is PuzzleSpec
    assert legacy_parse_error is PuzzleParseError
    assert legacy_parse_puzzle_file is parse_puzzle_file


def test_new_validation_module_is_importable():
    from wordsearch.validation.thematic import (
        ThematicValidationReport,
        ValidationIssue,
        validate_thematic_specs,
    )

    assert callable(ThematicValidationReport)
    assert callable(ValidationIssue)
    assert callable(validate_thematic_specs)


def test_legacy_validation_imports_still_work():
    from wordsearch.thematic_validation import (
        ThematicValidationReport as legacy_report,
    )
    from wordsearch.thematic_validation import ValidationIssue as legacy_issue
    from wordsearch.thematic_validation import validate_thematic_specs as legacy_validate
    from wordsearch.validation.thematic import (
        ThematicValidationReport,
        ValidationIssue,
        validate_thematic_specs,
    )

    assert legacy_report is ThematicValidationReport
    assert legacy_issue is ValidationIssue
    assert legacy_validate is validate_thematic_specs
