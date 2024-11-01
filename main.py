import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import argparse
import translator

parser = argparse.ArgumentParser()
parser.add_argument("file", help="The input file name")
# parser.add_argument("-p", "--processor", help="Choose Processor")
parser.add_argument("-dev", "--devmode", action="store_true", help="Developper mode")
args = parser.parse_args()

#TODO: add flags for generating comments
#TODO: add auto-spacing with TABS

def main() -> None:
    with open(args.file, 'r') as file:
        output = translator.translate(file.read(), args.devmode)
        print(output)


if __name__ == "__main__":
    main()