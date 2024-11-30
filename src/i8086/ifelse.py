from ..translator import Translator
from ..nodes.statement import IfNode

class IfTranslator(Translator):

    node_type = IfNode

    def make(self) -> None:
        self.node: IfNode
    
        #TODO: put all this code in if not isinstance(self.node.condition, LogicalNode):
        # but if it IS a logical node, we can map the jump command based on the operator (==, <, >, >=, ...)
        self.add(self.node.condition)
        self.assemble("pop", ["ax"])

        out_label: str = self.node.scope.generate_id("ifout")
        else_label: str = self.node.scope.generate_id("else")

        if self.node.else_body is None:
            self.assemble("jz", [out_label])
            self.add(self.node.body)
            self.assemble("nop", label=out_label)
        else:
            self.assemble("jz", [else_label])
            self.add(self.node.body)
            self.assemble("jmp", [out_label])
            self.assemble("nop", label=else_label)
            self.add(self.node.else_body)
            self.assemble("nop", label=out_label)