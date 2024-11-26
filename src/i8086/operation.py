from ..translator import Translator
from ..nodes.expression import BinaryOperationNode
from ..tokenizer.symbols import PlusToken, MinusToken, ModuloToken, StarToken
from .sizeof import sizeof
from ..errors import NotImplementedError

class BinaryOperationTranslator(Translator):

    node_type = BinaryOperationNode

    def make(self) -> None:
        self.node: BinaryOperationNode

        self.add(self.node.left)
        self.add(self.node.right)

        # A = "ax" if sizeof(self.node.left.node_type) == 2 else "al"
        # B = "bx" if sizeof(self.node.right.node_type) == 2 else "bl"
        
        self.assemble("pop", ["bx"])
        self.assemble("pop", ["ax"], mapping=True)

        if PlusToken.match(self.node.token):
            self.assemble("add", ["ax", "bx"])
        elif MinusToken.match(self.node.token):
            self.assemble("sub", ["ax", "bx"])
        elif StarToken.match(self.node.token):
            self.assemble("mul", ["ax", "bx"])
        else:
            raise NotImplementedError(f"Operation {self.node.token.string} not implemented fror i8086", self.node.token.line)

        self.assemble("push", ["ax"], mapping=True)

