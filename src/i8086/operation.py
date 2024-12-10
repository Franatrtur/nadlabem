from ..translator import Translator
from ..nodes.expression import BinaryOperationNode, UnaryOperationNode
from ..tokenizer.symbols import PlusToken, MinusToken, DivideToken, ModuloToken, StarToken, BinaryNotToken, LogicalNotToken, IsEqualToken
from .sizeof import sizeof
from .allocator import Variable
from ..errors import NotImplementedError

class BinaryOperationTranslator(Translator):

    node_type = BinaryOperationNode

    def make(self) -> None:
        self.node: BinaryOperationNode

        self.add(self.node.right)
        self.add(self.node.left)

        # A = "ax" if sizeof(self.node.left.node_type) == 2 else "al"
        # B = "bx" if sizeof(self.node.right.node_type) == 2 else "bl"
        
        self.assemble("pop", ["ax"], mapping=True)
        self.assemble("pop", ["bx"])

        if PlusToken.match(self.node.token):
            self.assemble("add", ["ax", "bx"])
            self.assemble("push", ["ax"])
    
        elif MinusToken.match(self.node.token):
            self.assemble("sub", ["ax", "bx"])
            self.assemble("push", ["ax"])

        elif StarToken.match(self.node.token):
            self.assemble("mul", ["bx"])
            self.assemble("push", ["ax"])
    
        elif IsEqualToken.match(self.node.token):
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("and", ["ax", "64"])
            self.assemble("mov", ["cl", "6"])
            self.assemble("shr", ["al", "cl"])
            self.assemble("push", ["ax"])

        # elif DivideToken.match(self.node.token):
        #     self.assemble("div", ["ax", "bx"])
        #     self.assemble("push", ["ax"])

        # elif ModuloToken.match(self.node.token):
        #     self.assemble("div", ["ax", "bx"])
        #     self.assemble("push", ["dx"])

        else:
            raise NotImplementedError(f"Operation {self.node.token.string} not implemented yet for i8086", self.node.token.line)

        # if sizeof(self.node.node_type) == 1:
        #     self.assemble("mov", ["ah", "0"])


class UnaryOperationTranslator(Translator):

    node_type = UnaryOperationNode

    def make(self) -> None:
        self.node: UnaryOperationNode

        if StarToken.match(self.node.token):
            
            Variable.variables[self.node.operand.symbol].load_pointer(translator=self, target_register="a")
            self.assemble("push", ["ax"])

        elif MinusToken.match(self.node.token):
            self.add(self.node.operand)
            #TODO: handle bytes differently than ints
            self.assemble("pop", ["ax"])
            self.assemble("neg", ["ax"])
            self.assemble("push", ["ax"])

        elif BinaryNotToken.match(self.node.token):
            self.add(self.node.operand)
            self.assemble("pop", ["ax"])
            self.assemble("not", ["ax"])
            self.assemble("push", ["ax"])

        elif LogicalNotToken.match(self.node.token):
            self.add(self.node.operand)
            self.assemble("pop", ["ax"])
            self.assemble("cmp", ["ax", "0"])
            self.assemble("sete", ["al"])
            self.assemble("push", ["ax"])

        else:
            raise NotImplementedError(f"Unary operation {self.node.token.string} not implemented yet for i8086", self.node.token.line)



