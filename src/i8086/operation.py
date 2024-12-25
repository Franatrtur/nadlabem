from ..translator import Translator, Assembly
from ..nodes.expression import (BinaryOperationNode, UnaryOperationNode, AdditiveNode, MultiplicativeNode, BinaryNode, ComparisonNode)
from ..tokenizer.symbols import (PlusToken, MinusToken, DivideToken, SignedDivideToken, ModuloToken, Token,
                                StarToken, BinaryNotToken, LogicalNotToken, IsEqualToken,
                                BinaryAndToken, BinaryOrToken, BinaryXorToken, BinaryRotateRightToken,
                                BinaryShiftLeftToken, BinaryShiftRightToken, LessThanToken, GreaterThanToken,
                                IsLtEqToken, IsGtEqToken, IsNotEqualToken, SignedIsLtEqToken, SignedIsGtEqToken,
                                SignedGreaterThanToken, SignedLessThanToken)
from .sizeof import sizeof
from ..nodes.types import Double, Char, Int, Bool, ValueType
from .allocator import Variable
from ..errors import NotImplementedError

class BinaryOperationTranslator(Translator):

    # node_type = BinaryOperationNode

    def _load_operands(self, swap: bool = False):

        if swap:
            self.add(self.node.left)
            self.add(self.node.right)
        else:
            self.add(self.node.right)
            self.add(self.node.left)

        if self.node.left.node_type is Double:
            self.assemble("pop", ["dx"])
            self.assemble("pop", ["ax"])
            self.assemble("pop", ["cx"])
            self.assemble("pop", ["bx"])
        else:
            self.assemble("pop", ["ax"])
            self.assemble("pop", ["bx"])

    def _save_result(self):
        
        self.assemble("push", ["ax"])
        if self.node.node_type is Double:
            self.assemble("push", ["dx"])


class ComparisonTranslator(BinaryOperationTranslator):

    node_type = ComparisonNode

    def make(self) -> None:
        self.node: ComparisonNode

        equality = Token.any(IsEqualToken, IsNotEqualToken).match(self.node.token)

        signed = Token.any(SignedGreaterThanToken, SignedIsGtEqToken, SignedLessThanToken, SignedIsLtEqToken).match(self.node.token)

        swapped = not Token.any(LessThanToken, IsGtEqToken, SignedLessThanToken, SignedIsGtEqToken).match(self.node.token)

        inverted = Token.any(IsNotEqualToken, IsGtEqToken, IsLtEqToken, SignedIsGtEqToken, SignedIsLtEqToken).match(self.node.token)

        self._load_operands(swapped)

        if self.node.left.node_type is Double:
            raise NotImplementedError("Double comparison not yet implemented for i8086", self.node.token.line)

        A = "ax" if sizeof(self.node.left.node_type) == 2 else "al"
        B = "bx" if sizeof(self.node.right.node_type) == 2 else "bl"
        
        # why not all 8 possibilites of conditional jumps?
        # would pollute code with too many macros
        macro: list[Assembly] = [
            Assembly(self.config, "cmp", [A, B]),
            Assembly(self.config, "je" if equality else ("jl" if signed else "jb"), ["true"]),
            Assembly(self.config, "jmp", ["false"]),
        ]
        
        name: str = "q" if equality else ("s" if signed else "u")
        sizename: str = "b" if self.node.left.node_type is Char else "w"
        macro_label: str = self.program.activate("_" + name + sizename + "cmp", macro)

        self.assemble("call", [macro_label])

        if inverted:
            self.assemble("xor", ["ax", "1"])

        self._save_result()


class AdditiveTranslator(BinaryOperationTranslator):

    node_type = AdditiveNode

    def make(self) -> None:
        self.node: AdditiveNode
        
        self._load_operands()

        if PlusToken.match(self.node.token):
            self.assemble("add", ["ax", "bx"])
            if self.node.left.node_type is Double:
                self.assemble("adc", ["dx", "cx"])
    
        elif MinusToken.match(self.node.token):
            self.assemble("sub", ["ax", "bx"])
            if self.node.left.node_type is Double:
                raise NotImplementedError("How to do subtraction for doubles?", self.node.token.line)
        
        else:
            raise NotImplementedError(f"Operation {self.node.token.string} not implemented yet for i8086", self.node.token.line)

        self._save_result()


class BinaryTranslator(BinaryOperationTranslator):

    node_type = BinaryNode

    def make(self) -> None:
        self.node: BinaryNode
        
        self._load_operands()

        if BinaryAndToken.match(self.node.token):
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
        
        else:
            raise NotImplementedError(f"Operation {self.node.token.string} not implemented yet for i8086", self.node.token.line)

        self._save_result()


class MultiplicativeTranslator(BinaryOperationTranslator):

    node_type = MultiplicativeNode

    def make(self) -> None:
        self.node: MultiplicativeNode
        
        self._load_operands()

        if self.node.node_type is Double:
            raise NotImplementedError("Double multiplicative node ops not yet implemented for i8086", self.node.token.line)

        if StarToken.match(self.node.token):
            self.assemble("mul", ["bx"])

        elif DivideToken.match(self.node.token):
            if self.node.left.node_type is Int:
                self.assemble("mov", ["dx", "0"])
                self.assemble("div", ["bx"])
            else:
                self.assemble("div", ["bl"])
                self.assemble("xor", ["ah", "ah"])
    
        elif SignedDivideToken.match(self.node.token):
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

        self._save_result()


class UnaryOperationTranslator(Translator):

    node_type = UnaryOperationNode

    def _load_operand(self) -> None:
        self.add(self.node.operand)
        if self.node.operand.node_type is Double:
            self.assemble("pop", ["dx"])
        self.assemble("pop", ["ax"])

    def _save_operand(self) -> None:
        self.assemble("push", ["ax"])
        if self.node.operand.node_type is Double:
            self.assemble("push", ["dx"])

    def make(self) -> None:
        self.node: UnaryOperationNode

        if self.node.operand.node_type is Double:
            raise NotImplementedError("Double unary operations not implemented yet for i8086", self.node.token.line)

        self._load_operand()

        if MinusToken.match(self.node.token):
            if self.node.operand.node_type is Char:
                self.assemble("neg", ["al"])
            elif self.node.operand.node_type is Int:
                self.assemble("neg", ["ax"])
            else:
                macro: list[Assembly] = [
                    Assembly(self.config, "not", ["ax"]),
                    Assembly(self.config, "not", ["dx"]),
                    Assembly(self.config, "add", ["ax", "1"]),
                    Assembly(self.config, "adc", ["dx", "0"]),
                    Assembly(self.config, "ret")
                ]
                label = self.program.activate("_dwnot", macro)
                self.assemble("call", [label])

        elif BinaryNotToken.match(self.node.token):
            if self.node.operand.node_type is Char:
                self.assemble("not", ["al"])
            elif self.node.operand.node_type is Int:
                self.assemble("not", ["ax"])
            else:
                self.assemble("not", ["ax"])
                self.assemble("not", ["dx"])

        elif LogicalNotToken.match(self.node.token):
            self.assemble("xor", ["ax", "1"])

        else:
            raise NotImplementedError(f"Unary operation {self.node.token.string} not implemented yet for i8086", self.node.token.line)

        self._save_operand()



