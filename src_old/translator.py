from . import tokenizer
from . import parser
from .config import TranslationConfig
from .ui import progress_bar
from .target import TARGETS


#TODO: ensure last instruction is hlt


class NadLabemTranslator:
    
    def __init__(self, config: TranslationConfig):
        self.config = config

    def translate(self, code: str) -> str:

        #split by lines
        string_lines = code.split("\n")
        self.string_lines = string_lines

        #map string lines to semantic lines
        lines: list[tokenizer.Line] = []
        for number, line in enumerate(string_lines):

            lines.append(tokenizer.tokenize(line, number+1))
            
            if self.config.verbose:
                progress_bar("Tokenizing", number+1, len(string_lines))

        self.lines = lines

        if self.config.devmode:
            print("\nTokenized:", [line.__str__() for line in lines])

        #parse a the semantic tree
        parsed_program = parser.parse(lines, self.config)
        self.parsed_program = parsed_program
        
        if self.config.devmode:
            print("\nParsed:", parsed_program)

        translated = parsed_program.translate()
        self.translated = translated
        
        if self.config.devmode:
            print("\nTranslated:", translated, "\n")

        if self.config.generate_mapping and not self.config.erase_comments:
            translated.insert(0, ";Compiled by NadLabem:")
            translated.insert(1, ";A Python-powered, dependency-free brandejs-to-assembly transpiler for the i8080 processor.")
            translated.insert(2, "")

        #remove comments
        if self.config.erase_comments:
            translated = list(map(lambda line_str: line_str.split(";")[0], translated))

        #join lines
        return "\n".join(translated)