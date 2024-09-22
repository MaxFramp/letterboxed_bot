import enchant
import json
import numpy as np


def keywithmaxval(d):
    """ a) create a list of the dict's keys and values;
         b) return the key with the max value"""
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(max(v))]


with open('words_dictionary.json') as json_file:
    dictionary = json.load(json_file)

with open('filter.json') as file:
    filter = json.load(file)

d = enchant.Dict("en_US")

# input = 'oehdlki'
# req_letter = 'd'

input = 'umtgnlihdreo'
# req_letter = 'r'
letter_side = {
    'u': 1,
    'm': 1,
    't': 1,
    'g': 2,
    'n': 2,
    'l': 2,
    'i': 3,
    'h': 3,
    'd': 3,
    'r': 4,
    'e': 4,
    'o': 4,
}
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
                                         not in filter) and (d.check(word)):
        words_list.append(word)

# for word in dictionary:
#     word_ok = True
#     for letter in word:
#         if letter not in input:
#             word_ok = False
#     if word_ok and req_letter in word and (len(word) >= 4):
#         words_list.append(word)

# and (word not in filter) and (d.check(word))

# for key in data:
#     word_ok = True
#     for letter in key:
#         if letter not in input:
#             word_ok = False
#     if word_ok and (len(key) >= 4) and (d.check(key)) and (key not in filter):
#         words_list.append(key)

hints = dict()

for word in words_list:
    hint = word[0:2]
    if str(hint) in hints.keys():
        hints[str(hint)] += 1
    else:
        hints[str(hint)] = 1

# for firsttwo, number in hints.items():
#     print(firsttwo.upper() + '-: ' + str(number))

print('Words:' + str(len(words_list)))
# print(words_list)
# print(len(words_list))
unique_letters = {}

for word in words_list:
    letter_list = list(word)

    unique_letters[word] = len(np.unique(letter_list))
    # print(str(word) + str(unique_letters[word]))

max_unique = keywithmaxval(unique_letters)
print(max_unique)

keys = list(unique_letters.keys())
values = list(unique_letters.values())
sorted_value_index = np.argsort(values)
sorted_dict = {keys[i]: values[i] for i in sorted_value_index}

print(sorted_dict)
