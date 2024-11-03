from ..tokenizer import Token, Line
from ..lexer import Lexer
from .variable import VariableLexer
from .ignore import AssemblyInstructionLexer as Assembly

def jump_var1_eq_var2(var1_label: str, var2_label: str, jump_to_label: str, parent: Lexer, negation: bool = False) -> list[str]:
    return (
        Assembly.create(parent, "LDA", [var1_label]).translate(mapping=True) +
        Assembly.create(parent, "MOV", ["B", "A"]).translate(mapping=False) +
        Assembly.create(parent, "LDA", [var2_label]).translate(mapping=False) +
        Assembly.create(parent, "CMP", ["B"]).translate(mapping=False) +
        Assembly.create(parent, 'JNZ' if negation else 'JZ', [jump_to_label]).translate(mapping=True)
    )
    # f"{spacing}LDA {self.var1_label} {self.map_comment}",
    # f"{spacing}MOV B,A",
    # f"{spacing}LDA {self.var2_label}",
    # f"{spacing}CMP B",
    # f"{spacing}{('JNZ' if self.negation else 'JZ')} {if_branch_target.label}"
