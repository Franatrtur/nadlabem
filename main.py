# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import argparse
from pathlib import Path
#import translator

from src.config import TranslationConfig
from src.translator import NadLabemTranslator, TARGETS


parser = argparse.ArgumentParser()
parser.add_argument("file", help="The input file name")
parser.add_argument("-p", "--processor", "--target", help="Choose Processor target (default=i8080)", default="i8080")

parser.add_argument("-dev", "--devmode", action="store_true", help="Developper mode flag")
parser.add_argument("-nomap", "--nomapping", action="store_true", help="Dont generate mapping comments flag")
parser.add_argument("-nocom", "--nocomments", action="store_true", help="Erase any comments flag")
parser.add_argument("-novb", "--noverbose", action="store_true", help="Dont generate generation info output")

parser.add_argument("-out", "--output", help="Output file destination (default=prints to console)", default=None)
parser.add_argument("-tab", "--tabspaces", help="Tab space amount  (default=8)", default=8)
args = parser.parse_args()

#TODO: add auto-spacing with TABS

def main() -> None:
    
    with open(args.file, 'r') as file:
        code = file.read()

        if args.processor not in TARGETS:
            raise ValueError(f"Unknown processor {args.processor}")

        config = TranslationConfig(
            target_cpu=args.processor,
            generate_mapping=not args.nomapping,
            erase_comments=args.nocomments,
            devmode=args.devmode,
            tabspaces=int(args.tabspaces),
            verbose=not args.noverbose
        )

        if config.verbose:
            with open("logo.txt", "r") as file:
                print("\033[96m" + file.read() + '\033[0m')

        translator = NadLabemTranslator(
            config=config
        )

        if config.verbose:
            print(config)
            print()

        output = translator.translate(code)

        if args.output:

            if Path(args.output).exists():
                overwrite = input(f"\nFile {args.output} already exists, do you wanna overwrite it? (y/n): ")
                if overwrite.lower() != "y":
                    exit()

            if config.verbose:
                print()
                print("\33[44m", f"Saved to file: {args.output}", '\033[0m')

            with open(args.output, 'w') as output_file:
                output_file.write(output)

        else:
            if config.verbose:
                print()
                print("\33[44m", "OUTPUT:", '\033[0m')
            print(output)


if __name__ == "__main__":
    main()