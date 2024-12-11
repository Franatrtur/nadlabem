from ..translator import Translator
from ..nodes.expression import BinaryOperationNode, UnaryOperationNode
from ..tokenizer.symbols import (PlusToken, MinusToken, DivideToken, ModuloToken, Token,
                                StarToken, BinaryNotToken, LogicalNotToken, IsEqualToken,
                                BinaryAndToken, BinaryOrToken, BinaryXorToken, BinaryRotateRightToken,
                                BinaryShiftLeftToken, BinaryShiftRightToken, LessThanToken, GreaterThanToken,
                                IsLtEqToken, IsGtEqToken, IsNotEqualToken)
from .sizeof import sizeof
from ..nodes.types import Double, Char, Int, Bool
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

        if self.node.left.node_type is Double:
            #TODO: redirect to a different method in this if clause so we dont have clutter
            raise NotImplementedError("Double operations not implemented yet for i8086", self.node.token.line)

        self.assemble("pop", ["ax"], mapping=True)
        self.assemble("pop", ["bx"])

        if sizeof(self.node.left.node_type) == 1:
            self.assemble("mov", ["ah", "0"])
        if sizeof(self.node.right.node_type) == 1:
            self.assemble("mov", ["bh", "0"])

        if PlusToken.match(self.node.token):
            self.assemble("add", ["ax", "bx"])
    
        elif MinusToken.match(self.node.token):
            self.assemble("sub", ["ax", "bx"])

        elif StarToken.match(self.node.token):
            self.assemble("mul", ["bx"])

        elif LogicalNotToken.match(self.node.token):
            self.assemble("xor", ["ax", "1"])
    
        elif Token.any(IsEqualToken, IsNotEqualToken).match(self.node.token):
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("mov", ["cl", "6"])
            self.assemble("shr", ["ax", "cl"])
            self.assemble("and", ["ax", "1"])
            if IsNotEqualToken.match(self.node.token):
                self.assemble("xor", ["ax", "1"])  # Invert the equality
        # elif IsGreaterToken.match(self.node.token):  # Greater than: ax > bx
        #     self.assemble("cmp", ["ax", "bx"])
        #     self.assemble("pushf")
        #     self.assemble("pop", ["ax"])
        #     self.assemble("mov", ["cl", "7"])  # CF (Carry Flag)
        #     self.assemble("shr", ["al", "cl"])
        #     self.assemble("and", ["ax", "1"])
        #     self.assemble("xor", ["ax", "1"])  # Invert CF for signed comparison
        # elif IsLessToken.match(self.node.token):  # Less than: ax < bx
        #     self.assemble("cmp", ["ax", "bx"])
        #     self.assemble("pushf")
        #     self.assemble("pop", ["ax"])
        #     self.assemble("mov", ["cl", "7"])  # CF
        #     self.assemble("shr", ["al", "cl"])
        #     self.assemble("and", ["ax", "1"])
        # elif IsGreaterOrEqualToken.match(self.node.token):  # Greater or equal: ax >= bx
        #     self.assemble("cmp", ["ax", "bx"])
        #     self.assemble("pushf")
        #     self.assemble("pop", ["ax"])
        #     self.assemble("mov", ["cl", "7"])  # CF
        #     self.assemble("shr", ["al", "cl"])
        #     self.assemble("and", ["ax", "1"])
        #     self.assemble("xor", ["ax", "1"])  # Invert CF for signed comparison
        # elif IsLessOrEqualToken.match(self.node.token):  # Less or equal: ax <= bx
        #     self.assemble("cmp", ["ax", "bx"])
        #     self.assemble("pushf")
        #     self.assemble("pop", ["ax"])
        #     self.assemble("mov", ["cl", "6"])  # SF
        #     self.assemble("shr", ["al", "cl"])
        #     self.assemble("and", ["ax", "1"])
        #     self.assemble("xor", ["ax", "1"])  # Invert SF for signed comparison

        elif LessThanToken.match(self.node.token):
            self.assemble("cmp", ["ax", "bx"])


        elif BinaryAndToken.match(self.node.token):
            self.assemble("and", ["ax", "bx"])

        elif BinaryOrToken.match(self.node.token):
            self.assemble("or", ["ax", "bx"])

        elif BinaryXorToken.match(self.node.token):
            self.assemble("xor", ["ax", "bx"])

        elif BinaryRotateRightToken.match(self.node.token):
            self.assemble("mov", ["cx", "bx"])
            self.assemble("ror", ["ax" if sizeof(self.node.left.node_type) == 2 else "al", "cl"])
        
        elif BinaryShiftLeftToken.match(self.node.token):
            self.assemble("mov", ["cx", "bx"])
            self.assemble("shl", ["ax" if sizeof(self.node.left.node_type) == 2 else "al", "cl"])

        elif BinaryShiftRightToken.match(self.node.token):
            self.assemble("mov", ["cx", "bx"])
            self.assemble("shr", ["ax" if sizeof(self.node.left.node_type) == 2 else "al", "cl"])


        # elif DivideToken.match(self.node.token):
        #     self.assemble("div", ["ax", "bx"])
        #     self.assemble("push", ["ax"])

        # elif ModuloToken.match(self.node.token):
        #     self.assemble("div", ["ax", "bx"])
        #     self.assemble("push", ["dx"])

        else:
            raise NotImplementedError(f"Operation {self.node.token.string} not implemented yet for i8086", self.node.token.line)

        self.assemble("push", ["ax"])


class UnaryOperationTranslator(Translator):

    node_type = UnaryOperationNode

    def make(self) -> None:
        self.node: UnaryOperationNode

        if self.node.left.operand is Double:
            raise NotImplementedError("Double operations not implemented yet for i8086", self.node.token.line)

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



