from ..translator import Translator
from ..nodes.expression import CastNode
from .sizeof import sizeof
from ..nodes.types import Int, Bool, Double, Char, Array, Pointer
from .allocator import Variable, StackFrame
from ..errors import NotImplementedError

class CastTranslator(Translator):

    node_type = CastNode

    def make(self) -> None:
        self.node: CastNode

        self.add(self.node.operand)

        result_type = self.node.result_type
        origin_type = self.node.operand.node_type
        signed = self.node.signed

        pair = (origin_type, result_type)

        if ((isinstance(result_type, Pointer) or result_type is Int) and
            (isinstance(origin_type, Pointer) or origin_type is Int)):
            pass

        elif pair in {(Char, Int), (Bool, Int)}:
            self.assemble("pop", ["ax"])
            if signed:
                self.assemble("cbw", [])
            else:
                self.assemble("mov", ["ah", "0"])
            self.assemble("push", ["ax"])

        elif pair in {(Int, Double), (Char, Double)}:
            self.assemble("pop", ["ax"])
            if origin_type is Char:
                self.assemble("mov", ["ah", "0"])
            if signed:
                if origin_type is Char:
                    self.assemble("cbw")
                self.assemble("cwd", [])
            else:
                self.assemble("mov", ["dx", "0"])
            self.assemble("push", ["ax"])
            self.assemble("push", ["dx"])

        elif pair == (Double, Int):
            self.assemble("pop", ["ax"])
            self.assemble("pop", ["dx"])
            if signed:
                self.assemble("cwd", [])
            else:
                self.assemble("mov", ["dx", "0"])
            self.assemble("push", ["ax"])

        elif pair in {(Int, Char), (Double, Char)}:
            if origin_type is Double:
                self.assemble("pop", ["dx"])
            self.assemble("pop", ["ax"])
            if not signed:
                self.assemble("mov", ["ah", "0"])
            else:
                if origin_type is Double:
                    self.assemble("cdw")
                self.assemble("cwb")
            self.assemble("push", ["ax"])

        elif result_type is Bool:
            self.assemble("pop", ["ax"])
            if origin_type is Double:
                self.assemble("pop", ["dx"])
                self.assemble("or", ["ax", "dx"])
            self.assemble("pushf")
            self.assemble("pop", ["ax"])
            self.assemble("mov", ["cl", "6"])  # zero flag
            self.assemble("shr", ["ax", "cl"])
            self.assemble("and", ["ax", "1"])
            self.assemble("xor", ["ax", "1"])
            self.assemble("push", ["ax"])
            
        else:
            raise NotImplementedError(f"Casting from {origin_type} to {result_type} is not yet implemented in i8086", self.node.token.line)
