from . import tokenizer
from . import parser

#TODO: ensure last instruction is hlt

def progress_bar(iteration, total, length=40):
    percent = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r|{bar}| {percent:.2f}% Complete', end='\r')
    if iteration == total:
        print()


class NadlabemTranslator:
    
    def __init__(self,
            generate_mapping: bool = True,
            devmode: bool = False,
            erase_comments: bool = False,
            tabspaces: int = 8,
            verbose: bool = True):

        self.generate_mapping = generate_mapping
        self.erase_comments = erase_comments
        self.devmode = devmode
        self.tabspaces = tabspaces
        self.verbose = verbose

    def translate(self, code: str) -> str:

        #split by lines
        string_lines: list[str] = code.split("\n")
        self.string_lines = string_lines

        #map string lines to semantic lines
        lines: list[tokenizer.Line] = [tokenizer.tokenize(line, number+1) for number, line in enumerate(string_lines)]
        self.lines = lines

        if(self.devmode):
            print("Tokenized:", [line.__str__() for line in lines] )

        #parse a the semantic tree
        parsed_program = parser.parse(lines)
        self.parsed_program = parsed_program
        
        if(self.devmode):
            print("Parsed:", parsed_program)

        translated = parsed_program.translate()
        self.translated = translated
        
        if(self.devmode):
            print("Translated:", translated)

        #join lines
        return "\n".join(translated)