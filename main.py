import json

import enchant
import numpy as np


def assign_sides(letter_string):
    letters_assigned = {}
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


def find_words(letter_side):
    with open('words_dictionary.json') as json_file:
        dictionary = json.load(json_file)

    with open('filter.json') as file:
        bad_words = json.load(file)

    d = enchant.Dict("en_US")

    words_list = []
    prev_letter_side = 0

    for word in dictionary:
        word_ok = True
        for letter in word:
            if letter not in letter_side.keys() or (letter_side[str(letter)]
                                                    == prev_letter_side):
                word_ok = False
            else:
                prev_letter_side = letter_side[letter]
        if word_ok and (len(word) >= 4) and (word
                                             not in bad_words) and (d.check(word)):
            words_list.append(word)

    return words_list


def sort_words(words_list):
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


if __name__ == "__main__":

    print("Enter today's Letterboxed puzzle with:")
    print("(Enter the letters one side a time with no spaces)")
    print()
    letter_str = input("Letters:")

    letter_dict = assign_sides(letter_str)

    # print(letter_dict)

    all_words = find_words(letter_dict)

    print('Words:' + str(len(all_words)))

    sorted_words = sort_words(all_words)

    print(sorted_words)




