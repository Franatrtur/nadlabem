from .program import ProgramTranslator
from ..translator import Translator
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from ..nodes.expression import LiteralNode

class LiteralTranslator(Translator):

    node_type = LiteralNode

    def translate(self) -> list[str]:
        self.node: LiteralNode
        return [
            f"MOV AX, {self.node.token.value}",
            f"PUSH AX"
        ]


