from wordsearch.domain.grid import GridGenerationResult
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.generation.difficulty import DifficultyLevel
from wordsearch.generation.grid_batch import generate_thematic_grids


def make_spec(index: int, words: list[str]) -> PuzzleSpec:
    return PuzzleSpec(
        index=index,
        title=f"Puzzle {index + 1}",
        fact="Fact",
        words=words,
        block_name="Block",
    )


def generated_signature(batch_result):
    return [
        (generated.grid, generated.placed_words)
        for generated in batch_result.generated_puzzles
    ]


def test_generate_thematic_grids_is_reproducible_with_seed():
    specs = [
        make_spec(0, ["ALPHA", "BETA", "GAMMA"]),
        make_spec(1, ["DELTA", "OMEGA", "SIGMA"]),
    ]

    first = generate_thematic_grids(
        specs,
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=12,
        seed=1234,
    )
    second = generate_thematic_grids(
        specs,
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=12,
        seed=1234,
    )

    assert not first.has_failures
    assert not second.has_failures
    assert generated_signature(first) == generated_signature(second)


def test_generate_thematic_grids_uses_single_rng_stream_for_seed(monkeypatch):
    specs = [
        make_spec(0, ["ALPHA"]),
        make_spec(1, ["BETA"]),
    ]
    rng_ids = []

    def fake_generate_word_search_grid(words, difficulty, grid_size, *, rng=None, **kwargs):
        rng_ids.append(id(rng))
        return GridGenerationResult(
            grid=[[next(iter(words))]],
            placed_words=[],
            attempts_used=1,
        )

    monkeypatch.setattr(
        "wordsearch.generation.grid_batch.generate_word_search_grid",
        fake_generate_word_search_grid,
    )

    result = generate_thematic_grids(
        specs,
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
        seed=99,
    )

    assert not result.has_failures
    assert len(rng_ids) == 2
    assert rng_ids[0] == rng_ids[1]


def test_generate_thematic_grids_uses_default_randomness_without_seed(monkeypatch):
    specs = [make_spec(0, ["ALPHA"])]
    calls = []

    def fake_generate_word_search_grid(words, difficulty, grid_size, *, rng=None, **kwargs):
        calls.append(rng)
        return GridGenerationResult(
            grid=[[next(iter(words))]],
            placed_words=[],
            attempts_used=1,
        )

    monkeypatch.setattr(
        "wordsearch.generation.grid_batch.generate_word_search_grid",
        fake_generate_word_search_grid,
    )

    result = generate_thematic_grids(
        specs,
        difficulty=DifficultyLevel.EASY,
        grid_size=8,
    )

    assert not result.has_failures
    assert calls == [None]
