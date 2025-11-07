import json
from importlib import import_module, util
from typing import Dict, Iterable, List

import numpy as np

from solver import ChainResult, find_word_chains


_TEXTBLOB_LOADED = False
_TEXTBLOB_CLASS = None


def _get_textblob_class():
    global _TEXTBLOB_LOADED, _TEXTBLOB_CLASS
    if not _TEXTBLOB_LOADED:
        _TEXTBLOB_LOADED = True
        if util.find_spec("textblob") is None:
            _TEXTBLOB_CLASS = None
        else:
            module = import_module("textblob")
            _TEXTBLOB_CLASS = getattr(module, "TextBlob", None)
    return _TEXTBLOB_CLASS


def assign_sides(letter_string: str) -> Dict[str, int]:
    letters_assigned: Dict[str, int] = {}
    i = 0
    j = 1
    for char in letter_string:

        if i < 2:
            letters_assigned[char] = j
            i += 1
        else:
            letters_assigned[char] = j
            j += 1
            i = 0

    return letters_assigned


def find_words(letter_side: Dict[str, int]) -> List[str]:
    textblob_cls = _get_textblob_class()

    with open("words_dictionary.json") as json_file:
        dictionary = json.load(json_file)

    with open("filter.json") as file:
        bad_words = json.load(file)

    words_list: List[str] = []

    for word in dictionary:
        prev_letter_side = 0
        word_ok = True
        for letter in word:
            if letter not in letter_side.keys() or (
                letter_side[str(letter)] == prev_letter_side
            ):
                word_ok = False
                break
            else:
                prev_letter_side = letter_side[letter]
        if (
            word_ok
            and (len(word) >= 4)
            and (word not in bad_words)
            and (textblob_cls is None or textblob_cls(word).correct())
        ):
            words_list.append(word)

    return words_list


def sort_words(words_list: Iterable[str]) -> Dict[str, int]:
    unique_letters = {}

    for word in words_list:
        letter_list = list(word)
        unique_letters[word] = len(np.unique(letter_list))

    keys = list(unique_letters.keys())
    values = list(unique_letters.values())
    sorted_value_index = np.argsort(values)
    sorted_value_index = np.flipud(sorted_value_index)
    sorted_dict = {keys[i]: values[i] for i in sorted_value_index}

    return sorted_dict


def _format_chain(result: ChainResult) -> str:
    words = " -> ".join(result.words)
    coverage = f"{len(result.covered_letters)} letters"
    return f"{words} ({coverage})"


def _display_chains(chains: List[ChainResult]) -> None:
    if not chains:
        print("\nNo 2- or 3-word chains cover all puzzle letters.")
        return

    print("\nWord chains covering all letters:")
    for idx, chain in enumerate(chains, start=1):
        print(f"  {idx}. {_format_chain(chain)}")


def main() -> None:
    print("Enter today's Letterboxed puzzle with:")
    print("(Enter the letters one side a time with no spaces)")
    print()
    letter_str = input("Letters:")

    letter_dict = assign_sides(letter_str)

    all_words = find_words(letter_dict)

    print("Words:" + str(len(all_words)))

    sorted_words = sort_words(all_words)

    print(sorted_words)

    # Build the graph and search for 2-3 word chains that cover all letters.
    chains = find_word_chains(
        all_words,
        letter_dict,
        required_letters=letter_dict.keys(),
        min_length=2,
        max_length=3,
    )
    _display_chains(chains)


if __name__ == "__main__":
    main()
