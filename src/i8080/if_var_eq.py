from ..lexer import Lexer
from ..tokenizer import (Line, match_token_pattern, IfToken, OpenParenToken, NegationToken, ElseToken,
                        NameToken, IsEqualToken, IsNotEqualToken, CloseParenToken, CodeBlockBeginToken, CodeBlockEndToken)
from .variable import DefineByteLexer
from .ignore import AssemblyInstructionLexer
from .synthetic import jump_var1_eq_var2
from ..errors import SyntaxError

if_eq_pattern = [IfToken, OpenParenToken, NameToken, IsEqualToken, NameToken, CloseParenToken, CodeBlockBeginToken]
if_neq_pattern = [IfToken, OpenParenToken, NameToken, IsNotEqualToken, NameToken, CloseParenToken, CodeBlockBeginToken]

else_pattern = [CodeBlockEndToken, ElseToken, CodeBlockBeginToken]

end_pattern = [CodeBlockEndToken]


class IfVarEqLexer(Lexer):

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
            self.negation = IsNotEqualToken.match(line.tokens[3])
            self.var2_label = line.tokens[4].string
            self.stage = 1

        elif self.stage == 1:

            if match_token_pattern(line, else_pattern):
                self.stage = 2

            elif match_token_pattern(line, end_pattern):
                stack.pop()
                self.stage = 3 #done
                return True

            else:
                return False

        elif self.stage == 2:
            if match_token_pattern(line, end_pattern):
                stack.pop()
                self.stage = 3 #done
                return True
            else:
                return False

        #assert variables exist
        self.var1 = self.program.get_variable(self.var1_label, line)
        self.var2 = self.program.get_variable(self.var2_label, line)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:

        if not self.stage == 3:
            raise SyntaxError(f"Unfinished if clause, ended on stage {stage}. {self.start_line}")

        spacing = " " * self.program.config.tabspaces

        if_branch_target = AssemblyInstructionLexer.create(self, "NOP", label=self.program.generate_label("if"))
        out_target = AssemblyInstructionLexer.create(self, "NOP", label=self.program.generate_label("out"))        

        translated_if_branch: list[str] = []
        for child in self.if_branch:
            translated_if_branch.extend(child.translate())
        
        translated_else_branch: list[str] = []
        for child in self.else_branch:
            translated_else_branch.extend(child.translate())

        #stage 0
        translated_if_clause = jump_var1_eq_var2(self.var1_label, self.var2_label, if_branch_target.label, self, self.negation)

        label_spacing = self.program.config.tabspaces - len(if_branch_target.label)

        translated_if_branch.append(out_target.translate()[0])
        translated_else_branch.append(f"{spacing}JMP {out_target.label}")

        translated_if_branch.insert(0, if_branch_target.translate()[0])

        return translated_if_clause + translated_else_branch + translated_if_branch

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