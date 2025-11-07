from solver import ChainResult, build_transition_graph, find_word_chains


def _sample_letter_sides():
    return {
        "a": 1,
        "b": 1,
        "c": 2,
        "d": 2,
        "e": 3,
        "f": 3,
        "g": 4,
        "h": 4,
    }


def _sample_words():
    return [
        "aceg",
        "gdae",
        "ebfh",
    ]


def test_build_transition_graph_creates_expected_edges():
    letter_side = _sample_letter_sides()
    graph = build_transition_graph(_sample_words(), letter_side)

    assert graph["aceg"] == ["gdae"]
    assert graph["gdae"] == ["ebfh"]
    assert graph["ebfh"] == []


def test_find_word_chains_discovers_complete_triples():
    letter_side = _sample_letter_sides()
    words = _sample_words()

    chains = find_word_chains(
        words,
        letter_side,
        required_letters=letter_side.keys(),
        min_length=2,
        max_length=3,
    )

    assert chains
    best = chains[0]
    assert isinstance(best, ChainResult)
    assert best.words == ("aceg", "gdae", "ebfh")
    assert set(best.covered_letters) == set(letter_side.keys())


def test_find_word_chains_avoids_reusing_words():
    letter_side = _sample_letter_sides()

    chains = find_word_chains(
        _sample_words(),
        letter_side,
        required_letters=letter_side.keys(),
        min_length=2,
        max_length=3,
    )

    for result in chains:
        assert len(result.words) == len(set(result.words))
