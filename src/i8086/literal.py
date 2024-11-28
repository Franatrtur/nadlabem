from .program import ProgramTranslator
from ..translator import Translator
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from ..nodes.expression import LiteralNode
from .sizeof import sizeof
from ..errors import NotImplementedError
from ..tokenizer.symbols import StringLiteralToken, NumberToken, BoolLiteralToken, CharLiteralToken

class LiteralTranslator(Translator):

    node_type = LiteralNode

    def make(self) -> None:
        self.node: LiteralNode

        register = "ax"

        if NumberToken.match(self.node.token):
            self.assemble("mov", [register, self.node.token.value])

        elif StringLiteralToken.match(self.node.token):
            raise NotImplementedError("String literals are not supported as part of an expression in i8086.", self.node.token.line)

        elif CharLiteralToken.match(self.node.token):
            self.assemble("mov", [register, self.node.token.value])

        elif BoolLiteralToken.match(self.node.token):
            self.assemble("mov", [register, "1" if self.node.token.value else "0"])

        self.assemble("push", ["ax"])


