import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tokenizer.tokenize import split_tokens, tokenize_line

def main():
    while True:
        msg = input("Write code: ")
        print(split_tokens(msg))
        print(tokenize_line(msg))

if __name__ == "__main__":
    main()
