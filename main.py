# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import argparse
from pathlib import Path
#import translator

from src.config import TranslationConfig
from src.translator import NadlabemTranslator, TARGETS


parser = argparse.ArgumentParser()
parser.add_argument("file", help="The input file name")
parser.add_argument("-p", "--processor", "--target", help="Choose Processor target", default="i8080")

parser.add_argument("-dev", "--devmode", action="store_true", help="Developper mode flag")
parser.add_argument("-nomap", "--nomap", action="store_true", help="Dont generate mapping comments flag")
parser.add_argument("-ncm", "--nocomments", action="store_true", help="Dont generate any comments flag")
parser.add_argument("-nv", "--noverbose", action="store_true", help="Dont generate generation info output")

parser.add_argument("-out", "--output", help="Output file destination", default=None)
parser.add_argument("-tab", "--tabspaces", help="Tab space amount", default=8)
args = parser.parse_args()

#TODO: add flags for generating comments
#TODO: add auto-spacing with TABS

def main() -> None:
    with open(args.file, 'r') as file:
        code = file.read()

        if args.processor not in TARGETS:
            raise ValueError(f"Unknown processor {args.processor}")

        translator = NadlabemTranslator(
            config = TranslationConfig(
                target_cpu=args.processor,
                generate_mapping=not args.nomap,
                erase_comments=args.nocomments,
                devmode=args.devmode,
                tabspaces=int(args.tabspaces),
                verbose=not args.noverbose
            )
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