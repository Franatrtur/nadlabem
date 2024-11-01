# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import argparse
from pathlib import Path
#import translator

from src.translator import NadlabemTranslator

parser = argparse.ArgumentParser()
parser.add_argument("file", help="The input file name")
# parser.add_argument("-p", "--processor", help="Choose Processor")

parser.add_argument("-dev", "--devmode", action="store_true", help="Developper mode flag")
parser.add_argument("-nomap", "--nomap", action="store_true", help="Dont generate mapping comments flag")
parser.add_argument("-ncm", "--nocomments", action="store_true", help="Dont generate any comments flag")

parser.add_argument("-out", "--output", help="Output file destination", default=None)
parser.add_argument("-tab", "--tabspaces", help="Tab space amount", default=8)
args = parser.parse_args()

#TODO: add flags for generating comments
#TODO: add auto-spacing with TABS

def main() -> None:
    with open(args.file, 'r') as file:
        code = file.read()

        translator = NadlabemTranslator(
            generate_mapping=not args.nomap,
            erase_comments=args.nocomments,
            devmode=args.devmode,
            tabspaces=int(args.tabspaces)
        )
        output = translator.translate(code)

        if args.output:

            if Path(args.output).exists():
                raise FileExistsError(f"File {args.output} already exists")

            with open(args.output, 'w') as output_file:
                output_file.write(output)

        else:
            print(output)


if __name__ == "__main__":
    main()