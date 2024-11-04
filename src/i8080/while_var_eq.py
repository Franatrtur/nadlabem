from ..lexer import Lexer
from ..tokenizer import (Line, match_token_pattern, OpenParenToken, WhileToken,
                        NameToken, IsEqualToken, IsNotEqualToken, CloseParenToken, CodeBlockBeginToken, CodeBlockEndToken)
from .variable import DefineByteLexer
from .ignore import AssemblyInstructionLexer
from .synthetic import jump_var1_eq_var2
from ..errors import SyntaxError

while_eq_pattern = [WhileToken, OpenParenToken, NameToken, IsEqualToken, NameToken, CloseParenToken, CodeBlockBeginToken]
while_neq_pattern = [WhileToken, OpenParenToken, NameToken, IsNotEqualToken, NameToken, CloseParenToken, CodeBlockBeginToken]

end_pattern = [CodeBlockEndToken]


class WhileVarEqLexer(Lexer):

    def __init__(self, line: Line, parent: Lexer):
        super().__init__(line, parent)
        self.stage = 0
        #stage 0 is before "while(...){"
        #stage 1 is waiting for the  "}else{" or "}"
        #stage 2 is waiting for the else "}"
        #stage 3 is done, either from stage 1 or 2

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, while_eq_pattern) or match_token_pattern(line, while_neq_pattern)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal

        if self.stage == 0:
            self.var1_label = line.tokens[2].string
            self.negation = IsNotEqualToken.match(line.tokens[3])
            self.var2_label = line.tokens[4].string
            self.stage = 1

        elif self.stage == 1:

            if match_token_pattern(line, end_pattern):
                stack.pop()
                self.stage = 2 #done
                return True

            else:
                return False

        #assert variables exist
        self.var1 = self.program.get_variable(self.var1_label, line)
        self.var2 = self.program.get_variable(self.var2_label, line)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:

        if not self.stage == 2:
            raise SyntaxError(f"Unfinished while clause, ended on stage {stage}. {self.start_line}")

        spacing = " " * self.program.config.tabspaces

        translated_children: list[str] = []
        for child in self.children:
            translated_children.extend(child.translate())

        out_target = AssemblyInstructionLexer.create(self, "NOP", label=self.program.generate_label("wout"))
        clause_target = AssemblyInstructionLexer.create(self, "NOP", label=self.program.generate_label("whil"))

        #stage 0
        translated_jump_clause = jump_var1_eq_var2(self.var1_label, self.var2_label, out_target.label, self, not self.negation)

        translated_children.append(f"{spacing}JMP {clause_target.label}")
        translated_children.extend(out_target.translate())

        translated_jump_clause.insert(0, clause_target.translate()[0])

        return translated_jump_clause + translated_children

"""
if x == y or if x != y
---
    LDA <1>
    MOV B,A
    LDA <2>
    CMP B
    JNZ else ; or JZ
    ...
else:
    ...

if x == y {} else {} or if x != y {} else {}
---
    LDA <1>
    MOV B,A
    LDA <2>
    CMP B
    JNZ else ; or JZ 
if:
    ...
    JMP out
else:
    ...
out:
    ...

"""