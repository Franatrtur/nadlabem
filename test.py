from src.tokenizer import tokenize, split_tokens


def test_tokenize_asm():
    with open("tests/parse.parse.asm", "r") as file:
        expected = [['x', 'db', '5'], ['y', 'DB', '32h'], [';', 'blankline', ',', 'next', 'two', 'lines', 'should', 'not', 'be', 'processed', 'as', 'there', 'is', 'no', 'content'], [';'], [], ['navesti', 'lda', 'x'], ['sta', 'x', ';', 'komentář', ',', 'utf8', 'test', ':', '👤', '😂', '🔊', '🤣'], ['HLT']]
        print([tokenize(line) for line in file])

def test_split_tokens():
    with open("tests/tokenizer.txt", "r") as file:
        print([tokenize(line).__str__() for line in file])


TESTS = [test_split_tokens]

def run_tests():
    for test in TESTS:
        test()

if __name__ == "__main__":
    run_tests()
    print("Tests done")