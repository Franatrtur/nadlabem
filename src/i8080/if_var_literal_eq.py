from ..lexer import Lexer
from ..tokenizer import (Line, match_token_pattern, IfToken, OpenParenToken, NegationToken, ElseToken, NumberLiteralToken,
                        NameToken, EqualsToken, CloseParenToken, CodeBlockBeginToken, CodeBlockEndToken)
from .variable import DefineByteLexer
from ..errors import SyntaxError

if_eq_pattern = [IfToken, OpenParenToken, NameToken, EqualsToken, EqualsToken, NumberLiteralToken, CloseParenToken, CodeBlockBeginToken]
if_neq_pattern = [IfToken, OpenParenToken, NameToken, NegationToken, EqualsToken, NumberLiteralToken, CloseParenToken, CodeBlockBeginToken]

else_pattern = [CodeBlockEndToken, ElseToken, CodeBlockBeginToken]

end_pattern = [CodeBlockEndToken]


class IfVarLiteralEqLexer(Lexer):

    def __init__(self, line: Line, parent: "Lexer"):
        super().__init__(line, parent)
        self.stage = 0
        #stage 0 is before "if(...){"
        #stage 1 is waiting for the  "}else{" or "}"
        #stage 2 is waiting for the else "}"
        #stage 3 is done, either from stage 1 or 2

        self.if_branch: list[Lexer] = []
        self.else_branch: list[Lexer] = []

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, if_eq_pattern) or match_token_pattern(line, if_neq_pattern)

    def add_child(self, child: Lexer):
        super().add_child(child)
        
        if self.stage == 1:
            self.if_branch.append(child)
        elif self.stage == 2:
            self.else_branch.append(child)
        else:
            raise f"Invalid branch on line {child.start_line}"

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal

        if self.stage == 0:
            self.var1_label = line.tokens[2].string
            self.negation = NegationToken.match(line.tokens[3])
            self.literal = line.tokens[5].string
            self.stage = 1

        elif self.stage == 1:

            if match_token_pattern(line, else_pattern, ignore_commented_tokens=False):
                self.stage = 2

            elif match_token_pattern(line, end_pattern, ignore_commented_tokens=False):
                stack.pop()
                self.stage = 3 #done
                return True

            else:
                return False

        elif self.stage == 2:
            if match_token_pattern(line, end_pattern, ignore_commented_tokens=False):
                stack.pop()
                self.stage = 3 #done
                return True
            else:
                return False

        #assert variables exist
        self.var1 = self.program.get_variable(self.var1_label, line)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:

        if not self.stage == 3:
            raise SyntaxError(f"Unfinished if clause, ended on stage {stage}. {self.start_line}")

        spacing = " " * self.program.config.tabspaces

        if_branch_start_label = self.program.generate_label("if")
        out_label = self.program.generate_label("out")        

        translated_if_branch: list[str] = []
        for child in self.if_branch:
            translated_if_branch.extend(child.translate())
        translated_else_branch: list[str] = []
        for child in self.else_branch:
            translated_else_branch.extend(child.translate())

        #stage 0
        translated_if_clause =  [
            f"{spacing}LDA {self.var1_label} {self.map_comment}",
            f"{spacing}MVI B,{self.literal}",
            f"{spacing}CMP B",
            f"{spacing}{('JNZ' if self.negation else 'JZ')} {if_branch_start_label}"
        ]

        label_spacing = self.program.config.tabspaces - len(if_branch_start_label)

        translated_else_branch.append(f"{spacing}JMP {out_label}")
        translated_if_branch.append(f"{self.program.justify_label(out_label, self)}NOP")

        translated_if_branch.insert(0, f"{self.program.justify_label(if_branch_start_label, self)}NOP")

        return translated_if_clause + translated_else_branch + translated_if_branch

"""
if x == 5 or if x != 5
---
    LDA <target1>
    MVI B,<8bit data>
    CMP B
    JNZ ne ; or JZ
    ...
ne:
    ...

if x == 5 {} else {} or if x != 5 {} else {}
---
    LDA <target1>
    MVI B,<8bit data>
    CMP B
    JNZ ne ; or JZ 
ano:
    ...
    JMP out
ne:
    ...
out:
    ...

"""