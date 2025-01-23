from ..translator import Translator
from ..nodes.statement import IfNode
from ..nodes.expression import ExpressionNode
from .operation import ComparisonTranslator, ComparisonNode, BinaryOperationTranslator
from typing import Type

class ConditionalJump:

    def __init__(self, translator: Translator, condition: ExpressionNode):
        self.translator: Translator = translator
        self.condition: ExpressionNode = condition

    def jump(self, label: str, on: bool) -> None:

        if isinstance(self.condition, ComparisonNode):

            equality, signed, swap, invert = ComparisonTranslator._analyze_comparison(self.condition.token)
        
            BinaryOperationTranslator.load(
                self.translator,
                self.condition.left,
                self.condition.right,
                swap
            )

            invert = invert if on else not invert

            normal: str
            inverted: str

            if equality:
                normal, inverted = "je", "jne"
            elif signed:
                normal, inverted = "jl", "jge"
            else:
                normal, inverted = "jb", "jae"

            self.translator.assemble("cmp", ["ax", "bx"])
            self.translator.assemble(inverted if invert else normal, [label])

        else:
            self.translator.add(self.condition)
            self.translator.assemble("pop", ["ax"])
            self.translator.assemble("cmp", ["ax", "0"])
            self.translator.assemble("jnz" if on else "jz", [label])




class IfTranslator(Translator):

    node_type = IfNode

    def make(self) -> None:
        self.node: IfNode
    
        #TODO: put all this code in if not isinstance(self.node.condition, LogicalNode):
        # but if it IS a logical node, we can modify the jump command based on the operator (== je, != jne, < jl, >, >=, ...)
        # self.add(self.node.condition)
        # self.assemble("pop", ["ax"])

        conditon = ConditionalJump(self, self.node.condition)

        out_label: str = self.node.scope.generate_id("ifout")
        else_label: str = self.node.scope.generate_id("else")

        if self.node.else_body is None:
            conditon.jump(out_label, on=False)
            # self.assemble("jz", [out_label])
            self.add(self.node.body)
            self.assemble("nop", label=out_label)
        else:
            conditon.jump(else_label, on=False)
            # self.assemble("jz", [else_label])
            self.add(self.node.body)
            self.assemble("jmp", [out_label])
            self.assemble("nop", label=else_label)
            self.add(self.node.else_body)
            self.assemble("nop", label=out_label)