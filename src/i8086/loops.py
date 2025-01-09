from ..translator import Translator
from ..nodes.statement import WhileNode, ForNode, PassNode, BreakNode, ContinueNode
from ..tokenizer.symbols import DoToken, WhileToken


#TODO: add break and continue

class WhileTranslator(Translator):

    node_type = WhileNode

    def make(self) -> None:
        self.node: WhileNode
    
        #TODO: put all this code in if not isinstance(self.node.condition, LogicalNode):
        # but if it IS a logical node, we can map the jump command based on the operator (==, <, >, >=, ...)
        loop_label: str = self.node.scope.generate_id("while")
        out_label: str = self.node.scope.generate_id("wout")
        self.assemble("nop", label=loop_label)

        self.continue_label: str = loop_label
        self.break_label: str = out_label

        if not self.node.do_loop:
            self.add(self.node.condition)
            self.assemble("pop", ["ax"])
            self.assemble("jz", [out_label])

        self.add(self.node.body)

        if self.node.do_loop:
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
        increment_label: str = self.node.scope.generate_id("finc")

        self.continue_label: str = increment_label
        self.break_label: str = out_label

        self.add(self.node.initialization)

        self.assemble("nop", label=loop_label)

        self.add(self.node.condition)

        self.assemble("pop", ["ax"])
        self.assemble("jz", [out_label])

        self.add(self.node.body)

        self.assemble("nop", label=increment_label)

        self.add(self.node.increment)
        
        self.assemble("jmp", [loop_label])
        self.assemble("nop", label=out_label)


class PassTranslator(Translator):
    node_type = PassNode
    def make(self) -> None:
        self.node: PassNode
        self.assemble("nop")


class BreakTranslator(Translator):
    
    node_type = BreakNode

    @staticmethod
    def find_loop(translator: Translator) -> WhileTranslator | ForTranslator:
        loop_for: ForTranslator = translator.closest_parent(ForTranslator)
        loop_while: WhileTranslator = translator.closest_parent(WhileTranslator)

        if not loop_for:
            return loop_while
        elif not loop_while:
            return loop_for

        elif loop_for.closest_parent(WhileTranslator) is loop_while:
            return loop_for
        else:
            return loop_while
    
    def make(self) -> None:
        self.node: BreakNode
        
        loop: WhileTranslator | ForTranslator = self.find_loop(self)

        self.assemble("jmp", [loop.break_label])


class ContinueTranslator(Translator):
    
    node_type = ContinueNode
    
    def make(self) -> None:
        self.node: ContinueNode
        
        loop: WhileTranslator | ForTranslator = BreakTranslator.find_loop(self)

        self.assemble("jmp", [loop.continue_label])