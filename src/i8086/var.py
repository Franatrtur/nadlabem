from .program import ProgramTranslator
from ..translator import Translator
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from ..nodes.statement import VariableDeclarationNode
from ..tokenizer.symbols import NumberToken

class VariableDeclarationTranslator(Translator):

    node_type = VariableDeclarationNode

    def translate(self) -> list[str]:
        self.node: VariableDeclarationNode

        token: NumberToken = self.node.token

        return [
            "POP AX",
            f"MOV {token.value}, AX",
        ]

        

