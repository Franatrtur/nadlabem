import sys
import os

from src.tokenizer import tokenize, split_tokens
from src.translator import translate


def test_tokenize_asm():
    with open("tests/parse.asm", "r") as file:
        expected = [['x', 'db', '5'], ['y', 'DB', '32h'], [';', 'blankline', ',', 'next', 'two', 'lines', 'should', 'not', 'be', 'processed', 'as', 'there', 'is', 'no', 'content'], [';'], [], ['navesti', 'lda', 'x'], ['sta', 'x', ';', 'komentář', ',', 'utf8', 'test', ':', '👤', '😂', '🔊', '🤣'], ['HLT']]
        print([tokenize(line).__str__() for line in file])


def test_split_tokens():
    with open("tests/tokenizer.txt", "r") as file:
        print([tokenize(line).__str__() for line in file])


def save_literal_to_var_test():
    with open("tests/save_literal_to_var_test.asm", "r") as file:
        print(translate(file.read()))


def save_var_to_var_test():
    with open("tests/save_var_to_var_test.asm", "r") as file:
        print(translate(file.read()))


def add_var_to_var_test():
    with open("tests/add_var_to_var_test.asm", "r") as file:
        print(translate(file.read()))


def add_literal_to_var_test():
    with open("tests/add_literal_to_var_test.asm", "r") as file:
        print(translate(file.read()))

def huge_test():
    with open("tests/huge.asm", "r") as file:
        print(translate(file.read()))


def main():
    # test_tokenize_asm()
    # test_split_tokens()
    # save_literal_to_var_test()
    # save_var_to_var_test()
    # add_var_to_var_test()
    # add_literal_to_var_test()
    huge_test()


if __name__ == "__main__":
    main()