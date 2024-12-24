import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tokenizer.tokenize import Tokenizer
from src.config import CompilationConfig

def main():
    while True:
        msg = input("Write code: ")
        print(Tokenizer.split_tokens(msg))
        print(Tokenizer(CompilationConfig()).tokenize_line(msg).tokens)

if __name__ == "__main__":
    main()
