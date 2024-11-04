from ..tokenizer import *
from ..lexer import Lexer, SyntheticLexer
from .variable import VariableLexer
from ..errors import ParsingError
from .ignore import AssemblyInstructionLexer as Assembly
from typing import Type

class SyntheticAssemblyLexer(SyntheticLexer):

    pattern: list[Type[Token]]

    @classmethod
    def create(cls, parent: Lexer, tokens: list[Token]) -> SyntheticLexer:
        if not match_token_pattern(tokens, cls.pattern):
            cls_names = ",".join([token_type.__name__ for token_type in cls.pattern])
            raise ParsingError(f"{cls.__name__} expected pattern [{cls_names}] but got {tokens}", parent.start_line)
        return super().create(parent)

    def assemble(self, command: str, arguments: list[str] = [], label: str | None = None):
        self.add(Assembly, command=command, arguments=arguments, label=label)

    def add(self, cls: Type[Lexer], *args, **kwargs):
        self.children.append(cls.create(parent=self, *args, **kwargs))


class LoadLexer(SyntheticAssemblyLexer):
    """Loads a value (either a variable or a number) into a register."""
    pattern = [ValueToken]

    @classmethod
    def create(cls, parent: Lexer, tokens: list[Token], register: str = "A") -> "LoadLexer":
        lexer: LoadLexer = super().create(tokens, parent)

        val1 = tokens[0]

        if NameToken.match(val1):
            var1 = parent.program.get_variable(val1, parent.start_line)
            lexer.assemble("LDA", [var1.label])

            if register != "A":
                lexer.assemble("MOV", [register, "A"])

        elif NumberLiteralToken.match(val1):
            lexer.assemble("MVI", [register, str(val1.value)])

        else:
            raise ParsingError("Loading strings is disabled in i8080", parent.start_line)
        
        return lexer


class ComparisonPartLexer(SyntheticAssemblyLexer):
    """Compares two values via CMP, uses A and B registers."""
    pattern = [ValueToken, ComparisonToken, ValueToken]

    @classmethod
    def create(cls, parent: Lexer, tokens: list[Token]) -> SyntheticLexer:
        lexer = super().create(tokens, parent)

        lexer.add(LoadLexer, tokens=[tokens[0]], register="B")
        lexer.add(LoadLexer, tokens=[tokens[2]], register="A")

        lexer.assemble("CMP", ["B"])
        
        return lexer


class JumpComparisonLexer(SyntheticAssemblyLexer):
    """Jumps to a label if the comparison is true."""
    pattern = [ValueToken, ComparisonToken, ValueToken]

    @classmethod
    def create(cls, parent: Lexer, tokens: list[Token], target_label: str) -> SyntheticLexer:
        lexer = super().create(parent)

        # assert we first create the label before we jump to it
        element = parent.program.get_by_label(target_label, parent.start_line)

        lookup: dict[str, tuple[bool, str]] = {
            "==": (False, "JZ"),
            "!=": (False, "JNZ"),
            "<": (False, "JNC"),
            ">": (False, "JC"),
            "<=": (True, "JNC"),
            ">=": (True, "JC")
        }

        swap, jump_commad = lookup[tokens[1].string]

        lexer.add(ComparisonPartLexer, tokens = tokens.reverse() if swap else tokens)
        lexer.assemble(jump_commad, [target_label])

        return lexer


class StoreFlagLexer(SyntheticAssemblyLexer):
    """Stores a flag in the A register either zero or non zero."""
    pattern = [NameToken]

    @classmethod
    def create(cls, parent: Lexer, tokens: list[Token], register: str) -> SyntheticLexer:
        lexer = super().create(tokens, parent)

        var1 = parent.program.get_variable(tokens[0], parent.start_line)


