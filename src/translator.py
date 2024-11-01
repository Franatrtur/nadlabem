import tokenizer
import parser

#TODO: ensure last instruction is hlt

def translate(code: str, devmode: bool = False) -> str:

    #split by lines
    string_lines: list[str] = code.split("\n")

    #map string lines to semantic lines
    lines: list[tokenizer.Line] = [tokenizer.tokenize(line, number) for number, line in enumerate(string_lines)]

    if(devmode):
        print("Tokenized:", [line.__str__() for line in lines] )

    #parse a the semantic tree
    root = parser.parse(lines)
    
    if(devmode):
        print("Parsed:", root)

    translated = root.translate()
    
    if(devmode):
        print("Translated:", translated)

    #translate
    return "\n".join(translated)