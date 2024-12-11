from ..translator import Translator
from ..nodes.expression import BinaryOperationNode, UnaryOperationNode
from ..tokenizer.symbols import (PlusToken, MinusToken, DivideToken, SignedDivideToken, ModuloToken, Token,
                                StarToken, BinaryNotToken, LogicalNotToken, IsEqualToken,
                                BinaryAndToken, BinaryOrToken, BinaryXorToken, BinaryRotateRightToken,
                                BinaryShiftLeftToken, BinaryShiftRightToken, LessThanToken, GreaterThanToken,
                                IsLtEqToken, IsGtEqToken, IsNotEqualToken, SignedIsLtEqToken, SignedIsGtEqToken,
                                SignedGreaterThanToken, SignedLessThanToken)
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

        # if sizeof(self.node.left.node_type) == 1:
        #     self.assemble("mov", ["ah", "0"])
        # if sizeof(self.node.right.node_type) == 1:
        #     self.assemble("mov", ["bh", "0"])

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

        elif SignedGreaterThanToken.match(self.node.token):  # Greater than: ax +> bx
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])

            self.assemble("mov", ["cl", "6"])
            self.assemble("shr", ["ax", "cl"])
            self.assemble("and", ["al", "1"])
            self.assemble("mov", ["dl", "al"])

            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("and", ["ax", "1"])

            self.assemble("or", ["al", "dl"])
            self.assemble("xor", ["ax", "1"])

        elif SignedLessThanToken.match(self.node.token):  # Less than: ax <+ bx 
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("mov", ["cl", "7"])  # CF
            self.assemble("shr", ["al", "cl"])
            self.assemble("and", ["ax", "1"])

        elif SignedIsGtEqToken.match(self.node.token):  # Greater or equal: ax ~> bx
            # works 100 % for ints
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("mov", ["cl", "7"])  # CF
            self.assemble("shr", ["al", "cl"])
            self.assemble("and", ["ax", "1"])
            self.assemble("xor", ["ax", "1"])  # Invert CF for signed comparison

        elif SignedIsLtEqToken.match(self.node.token):  # Less or equal: ax <~ bx
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])

            self.assemble("mov", ["cl", "6"])
            self.assemble("shr", ["ax", "cl"])
            self.assemble("and", ["al", "1"])
            self.assemble("mov", ["dl", "al"])

            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("and", ["ax", "1"])

            self.assemble("or", ["al", "dl"])

        ################################################## unsigned comparison follows

        elif GreaterThanToken.match(self.node.token):  # Greater than: ax > bx
            assert False, "Unsigned GTEQ not implemented yet"
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("mov", ["cl", "7"])  # CF (Carry Flag)
            self.assemble("shr", ["al", "cl"])
            self.assemble("and", ["al", "1"])
            #self.assemble("xor", ["al", "1"])  # CF inverted for unsigned greater than
            self.assemble("mov", ["ah", "0"])

        elif LessThanToken.match(self.node.token):  # Less than: ax < bx 
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("mov", ["cl", "7"])  # CF (Carry Flag)
            self.assemble("shr", ["al", "cl"])
            self.assemble("and", ["al", "1"])
            self.assemble("mov", ["ah", "0"])

        elif IsGtEqToken.match(self.node.token):  # Greater or equal: ax >= bx
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("mov", ["cl", "7"])  # CF (Carry Flag)
            self.assemble("shr", ["al", "cl"])
            self.assemble("and", ["al", "1"])
            self.assemble("xor", ["al", "1"])  # CF inverted for unsigned greater than
            self.assemble("mov", ["ah", "0"])

        elif IsLtEqToken.match(self.node.token):  # Less or equal: ax <= bx
            assert False, "Template only, unsigned IsLtEqToken not implemented yet"
            self.assemble("cmp", ["ax", "bx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("mov", ["cl", "6"])  # SF
            self.assemble("shr", ["al", "cl"])
            self.assemble("and", ["ax", "1"])
            self.assemble("xor", ["ax", "1"])  # Invert SF for signed comparison


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


        elif DivideToken.match(self.node.token):
            if self.node.left.node_type is Int:
                self.assemble("mov", ["dx", "0"])
                self.assemble("div", ["bx"])
            else:
                self.assemble("div", ["bl"])
                self.assemble("xor", ["ah", "ah"])
    
        elif SignedDivideToken.match(self.node.token):
            #raise NotImplementedError("Template only, unsigned division not implemented yet", self.node.token.line)
            if self.node.left.node_type is Int:
                self.assemble("cwd")
                self.assemble("idiv", ["bx"])
            else:
                self.assemble("div", ["bl"])
                self.assemble("xor", ["ah", "ah"])

        elif ModuloToken.match(self.node.token):
            if self.node.left.node_type is Int:
                self.assemble("mov", ["dx", "0"])
                self.assemble("div", ["bx"])
                self.assemble("mov", ["ax", "dx"])
            else:
                self.assemble("div", ["bl"])
                self.assemble("xor", ["ah", "ah"]) 

        else:
            raise NotImplementedError(f"Operation {self.node.token.string} not implemented yet for i8086", self.node.token.line)

        self.assemble("push", ["ax"])


class UnaryOperationTranslator(Translator):

    node_type = UnaryOperationNode

    def make(self) -> None:
        self.node: UnaryOperationNode

        if self.node.operand is Double:
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



