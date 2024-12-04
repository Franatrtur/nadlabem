from ..translator import Translator
from ..nodes.statement import WhileNode, ForNode, PassNode
from ..tokenizer.symbols import DoToken, WhileToken

class WhileTranslator(Translator):

    node_type = WhileNode

    def make(self) -> None:
        self.node: WhileNode
    
        #TODO: put all this code in if not isinstance(self.node.condition, LogicalNode):
        # but if it IS a logical node, we can map the jump command based on the operator (==, <, >, >=, ...)
        loop_label: str = self.node.scope.generate_id("while")
        out_label: str = self.node.scope.generate_id("wout")
        self.assemble("nop", label=loop_label)

        if WhileToken.match(self.node.token):
            self.add(self.node.condition)
            self.assemble("pop", ["ax"])
            self.assemble("jz", [out_label])

        self.add(self.node.body)

        if DoToken.match(self.node.token):
            self.add(self.node.condition)
            self.assemble("pop", ["ax"])
            self.assemble("jnz", [out_label])
        
        self.assemble("jmp", [loop_label])
        self.assemble("nop", label=out_label)


class ForTranslator(Translator):

    node_type = ForNode

    def make(self) -> None:
        self.node: ForNode

        loop_label: str = self.node.scope.generate_id("for")
        out_label: str = self.node.scope.generate_id("fout")

        self.add(self.node.initialization)

        self.assemble("nop", label=loop_label)

        self.add(self.node.condition)

        self.assemble("pop", ["ax"])
        self.assemble("jz", [out_label])

        self.add(self.node.body)
        
        self.assemble("jmp", [loop_label])
        self.assemble("nop", label=out_label)


class PassTranslator(Translator):
    node_type = PassNode
    def make(self) -> None:
        self.node: PassNode
        self.assemble("nop")