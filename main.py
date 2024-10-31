import argparse
import translator

parser = argparse.ArgumentParser()
parser.add_argument("file", help="The input file name")
# parser.add_argument("-p", "--processor", help="Choose Processor")
args = parser.parse_args()


def main() -> None:
    with open(args.file, 'r') as file:
        output = translator.translate(file.read())
        for line in output:
            print(line)


if __name__ == "__main__":
    main()