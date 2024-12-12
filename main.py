#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys, os

from src.config import CompilationConfig
from src.compiler import Compiler, CompilationTarget


parser = argparse.ArgumentParser()
parser.add_argument("file", help="The input file name")
parser.add_argument("-cpu", "--target", "--processor", help="Choose Processor target (default=i8086)", default="i8086")

parser.add_argument("-lax", "--forgive", "--nostrict", action="store_true", help="Reduce strictness when verifying the program")
parser.add_argument("-nomap", "--nomapping", action="store_true", help="Dont generate mapping comments flag")
parser.add_argument("-nocom", "--nocomments", action="store_true", help="Erase all comments flag")
parser.add_argument("-novb", "--noverbose", action="store_true", help="Dont generate generation info output")

parser.add_argument("-out", "--output", help="Output file destination (default=same file.asm)", default=None)
parser.add_argument("-p", "--print", action="store_true", help="Print to console instead of writing to file", default=None)
parser.add_argument("-dev", "--devmode", action="store_true", help="Developper mode flag")
parser.add_argument("-tab", "--tabspaces", help="Tab space amount (default=8)", default=8)
args = parser.parse_args()

def replace_file_extension(path: str, new_extension: str) -> str:
    # Ensure the new extension starts with a dot
    if not new_extension.startswith("."):
        new_extension = f".{new_extension}"
    
    # Split the file name and replace its extension
    base, _ = os.path.splitext(path)
    return f"{base}{new_extension}"

def main() -> None:
    if not args.devmode:
        sys.tracebacklimit = 0

    file_path = Path(args.file)
    if not file_path.is_file():
        raise ValueError(f"The input file {file_path} does not exist!")

    with file_path.open() as file:
        code = file.read()

        if args.target not in CompilationTarget.targets:
            raise ValueError(f"Unknown target processor {args.target}!")

        config = CompilationConfig(
            location = Path(file_path),
            target = args.target,
            strict = not args.forgive,
            generate_mapping = not args.nomapping,
            erase_comments = args.nocomments,
            tabspaces = int(args.tabspaces),
            verbose = not args.noverbose
        )

        if config.verbose:
            with open("logo.txt", "r") as file:
                print("\033[96m" + file.read() + '\033[0m')

        translator = Compiler(config)

        if config.verbose:
            print(config)
            print()
        
        output = translator.compile(code)

        if config.verbose and args.devmode:
            print(translator.tree)

        if config.verbose and not config.strict and translator.warnings:
            print("\33[44m", "WARNINGS:", '\033[0m')
            for warning in translator.warnings:
                print(warning)
            print()

        if not args.print:
            out = args.output if args.output else replace_file_extension(file_path, ".asm")

            if Path(out).exists() and config.verbose and args.output:
                overwrite = input(f"\nFile {out} already exists, do you wanna overwrite it? (y/n): ")
                if overwrite.lower() != "y":
                    print()
                    print("\33[44m", "ABORTED", '\033[0m')
                    exit()

            if config.verbose:
                print()
                print("\33[44m", f"Saved to file: {out}", '\033[0m')

            with open(out, 'w') as output_file:
                output_file.write(output)

        else:
            if config.verbose:
                print()
                print("\33[44m", "OUTPUT:", '\033[0m')
            print(output)


if __name__ == "__main__":
    main()