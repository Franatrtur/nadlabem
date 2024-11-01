from . import tokenizer
from . import parser
from .config import TranslationConfig

#TODO: ensure last instruction is hlt

def progress_bar(iteration, total, length=40):
    percent = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r|{bar}| {percent:.2f}% Complete', end='\r')
    if iteration == total:
        print()


class NadlabemTranslator:
    
    def __init__(self, config: TranslationConfig):
        self.config = config

    def translate(self, code: str) -> str:

        #split by lines
        string_lines: list[str] = code.split("\n")
        self.string_lines = string_lines

        #map string lines to semantic lines
        lines: list[tokenizer.Line] = [tokenizer.tokenize(line, number+1) for number, line in enumerate(string_lines)]
        self.lines = lines

        if(self.config.devmode):
            print("Tokenized:", [line.__str__() for line in lines])

        #parse a the semantic tree
        parsed_program = parser.parse(lines, self.config)
        self.parsed_program = parsed_program
        
        if(self.config.devmode):
            print("Parsed:", parsed_program)

        translated = parsed_program.translate()
        self.translated = translated
        
        if(self.config.devmode):
            print("Translated:", translated)

        #join lines
        return "\n".join(translated)