from ..lexer import Lexer
from ..labeled import DirectiveLexer
from ..tokenizer import Line, match_token_pattern, NameToken, NumberLiteralToken, CommaToken, Token, IgnoreToken
from ..errors import SyntaxError

no_arguments = [NameToken]
no_argument_labeled = [NameToken, NameToken]
one_argument = [NameToken, Token.any(NameToken, NumberLiteralToken)]
one_argument_labeled = [NameToken, NameToken, Token.any(NameToken, NumberLiteralToken)]
two_arguments = [NameToken, Token.any(NameToken, NumberLiteralToken), CommaToken, Token.any(NameToken, NumberLiteralToken)]
two_arguments_labeled = [NameToken, NameToken, Token.any(NameToken, NumberLiteralToken), CommaToken, Token.any(NameToken, NumberLiteralToken)]

class AssemblyInstructionLexer(DirectiveLexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return any([match_token_pattern(line, pattern, ignore_subsequent_tokens=False) for pattern in [
            no_arguments, no_argument_labeled, one_argument, one_argument_labeled, two_arguments, two_arguments_labeled
        ]])

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away (1 line instruction)
        stack.pop()

        self.arguments = []
        
        self.labeled = line.string.startswith(line.tokens[0].string)

        if self.labeled:
            self.label = line.tokens[0].string
            self.command = line.tokens[1].string

        else:
            self.label = None
            self.command = line.tokens[0].string

        
        for i in range(2 if self.labeled else 1, len(line.tokens), 2):
            token = line.tokens[i]
            if IgnoreToken.match(token):
                break
            self.arguments.append(token.string)

        self.synthetic = False

        self.register()
        #ano, spapal jsem to já
        return True



class NoLexer(Lexer):

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()

        if not match_token_pattern(line, []):
            raise SyntaxError("Unexpected syntax", line)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        return [
            self.start_line.string
        ]

    @staticmethod
    def detect(line: Line) -> bool:
        return True
