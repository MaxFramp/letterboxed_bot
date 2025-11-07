"""Utilities for building letterboxed word chains.

This module complements the existing CLI by providing helpers to build a
transition graph from candidate words and discover chains of two or three
words that cover all puzzle letters.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Set, Tuple


@dataclass(frozen=True)
class ChainResult:
    """Represents a discovered chain of words.

    Attributes
    ----------
    words:
        Ordered tuple of words forming the chain.
    covered_letters:
        Sorted tuple of the distinct letters covered by the chain.
    missing_letters:
        Sorted tuple of required letters that are not covered. For the chains
        returned by :func:`find_word_chains` this will be empty because only
        complete solutions are reported, but keeping the attribute makes the
        structure extensible for future use.
    coverage_ratio:
        Fraction of required letters covered by the chain. Complete solutions
        have a value of ``1.0``.
    """

    words: Tuple[str, ...]
    covered_letters: Tuple[str, ...]
    missing_letters: Tuple[str, ...]
    coverage_ratio: float


def _transition_is_valid(
    first: str, second: str, letter_side: Dict[str, int]
) -> bool:
    """Return ``True`` when ``second`` can follow ``first``.

    The two words can be chained when the last letter of ``first`` matches the
    first letter of ``second`` and the resulting combined sequence of letters
    still respects the Letter Boxed rule of not reusing the same side
    consecutively.
    """

    if not first or not second:
        return False

    if first[-1] != second[0]:
        return False

    # The final letter of ``first`` becomes the previous letter for the rest of
    # ``second``. We only need to check the transition between that letter and
    # the remainder of ``second`` because words produced by ``find_words`` are
    # already internally valid.
    prev_side = letter_side.get(first[-1])
    if prev_side is None:
        return False

    for letter in second[1:]:
        side = letter_side.get(letter)
        if side is None:
            return False
        if side == prev_side:
            return False
        prev_side = side

    return True


def build_transition_graph(
    words: Iterable[str], letter_side: Dict[str, int]
) -> Dict[str, List[str]]:
    """Return adjacency lists describing valid word transitions.

    Parameters
    ----------
    words:
        Iterable of candidate words.
    letter_side:
        Mapping from letters to their corresponding puzzle side.
    """

    start_map: Dict[str, List[str]] = defaultdict(list)
    sanitized_words: List[str] = []

    for word in words:
        if not word:
            continue

        # Skip words that contain characters outside of the puzzle definition.
        if any(letter not in letter_side for letter in word):
            continue

        sanitized_words.append(word)
        start_map[word[0]].append(word)

    adjacency: Dict[str, List[str]] = {word: [] for word in sanitized_words}

    for word in sanitized_words:
        followers = []
        for candidate in start_map.get(word[-1], []):
            if candidate == word:
                continue
            if _transition_is_valid(word, candidate, letter_side):
                followers.append(candidate)
        adjacency[word] = followers

    return adjacency


def find_word_chains(
    words: Sequence[str],
    letter_side: Dict[str, int],
    *,
    required_letters: Iterable[str] | None = None,
    min_length: int = 2,
    max_length: int = 3,
) -> List[ChainResult]:
    """Find word chains that cover all required letters.

    The search explores depth-first all valid paths of length ``min_length`` to
    ``max_length`` and records the ones that cover each required letter at least
    once.
    """

    if min_length < 1:
        raise ValueError("min_length must be at least 1")
    if max_length < min_length:
        raise ValueError("max_length must be >= min_length")

    graph = build_transition_graph(words, letter_side)
    required: Set[str] = (
        set(required_letters) if required_letters is not None else set(letter_side)
    )

    results: Dict[Tuple[str, ...], ChainResult] = {}

    for start_word in graph:
        stack: List[Tuple[str, Tuple[str, ...], Set[str]]] = [
            (start_word, (start_word,), set(start_word))
        ]

        while stack:
            current_word, path, coverage = stack.pop()

            if len(path) >= min_length and required.issubset(coverage):
                covered_letters = tuple(sorted(coverage))
                missing_letters = tuple(sorted(required - coverage))
                ratio = len(coverage & required) / len(required) if required else 1.0
                result = ChainResult(path, covered_letters, missing_letters, ratio)
                results.setdefault(path, result)

            if len(path) == max_length:
                continue

            for next_word in graph[current_word]:
                if next_word in path:
                    continue
                new_path = path + (next_word,)
                new_coverage = coverage | set(next_word)
                stack.append((next_word, new_path, new_coverage))

    ordered_results = sorted(
        results.values(), key=lambda res: (len(res.words), res.words)
    )

    return ordered_results

