from .program import ProgramTranslator
from ..translator import Translator
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from ..nodes.expression import LiteralNode

class LiteralTranslator(Translator):

    node_type = LiteralNode

    def make(self) -> None:
        self.node: LiteralNode
        self.assemble("mov", ["ax", self.node.token.value], mapping=True)
        self.assemble("push", ["ax"])


