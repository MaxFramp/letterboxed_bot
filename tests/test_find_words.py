import sys
import types
import unittest
from unittest.mock import patch

# Provide a lightweight stub for the enchant module so tests do not require the
# external C library.
enchant_stub = types.ModuleType("enchant")


class _DummyDict:
    def __init__(self, *_args, **_kwargs):
        pass

    def check(self, _word):
        return True


enchant_stub.Dict = _DummyDict
sys.modules.setdefault("enchant", enchant_stub)

import main


class FindWordsTests(unittest.TestCase):

    @patch("main.json.load")
    def test_consecutive_words_same_start_side_are_allowed(self, mock_json_load):
        # First call returns dictionary words, second call returns filter list
        mock_json_load.side_effect = [
            {"babab": True, "baba": True},
            [],
        ]

        letter_side = {"a": 1, "b": 2}

        result = main.find_words(letter_side)

        self.assertEqual({"babab", "baba"}, set(result))


if __name__ == "__main__":
    unittest.main()
