from ..translator import Translator
from ..nodes.statement import VariableDeclarationNode, AssignmentNode
from ..nodes.expression import VariableReferenceNode, LiteralNode
from .sizeof import sizeof
from ..nodes.types import Int, Bool, Array
from .allocator import Variable, StackFrame
from ..errors import NotImplementedError

class VariableDeclarationTranslator(Translator):

    node_type = VariableDeclarationNode

    def make(self) -> None:
        self.node: VariableDeclarationNode

        if isinstance(self.node.assignment, LiteralNode):
            pass
            
        self.add(self.node.assignment)

        variable: Variable = Variable.variables[self.node.symbol]
        self.variable: Variable = variable

        if isinstance(variable.var_type.expression_type, Array):
            raise NotImplementedError(f"Arrays not yet implemented in i8086", self.node.token.line)

        if self.node.by_reference:
            self.assemble("pop", ["ax"])
            variable.store_pointer(self, "ax")

        else:
            src_reg: str = ""
            bytelen = sizeof(self.node.node_type.expression_type)
            if bytelen == 1:
                src_reg = "al"
            elif bytelen == 2:
                src_reg = "ax"
            elif bytelen == 4:
                src_reg = "ax,dx"
                self.assemble("pop", ["dx"])
            
            self.assemble("pop", ["ax"])

            variable.store_value(translator=self, source_register=src_reg)


class AssignmentTranslator(Translator):

    node_type = AssignmentNode

    def make(self) -> None:
        self.node: AssignmentNode

        variable: Variable = Variable.variables[self.node.symbol]
        self.variable: Variable = variable

        self.add(self.node.value)

        target_index: str = ""

        if self.node.index is not None:
            self.add(self.node.index)
            target_index = "si"

        if self.node.by_reference:
            self.assemble("pop", ["ax"])
            variable.store_pointer(translator, "ax")

        else:
            src_reg: str = ""
            bytelen = sizeof(self.node.variable.node_type.expression_type)
            if bytelen == 1:
                src_reg = "al"
            elif bytelen == 2:
                src_reg = "ax"
            elif bytelen == 4:
                src_reg = "ax,dx"
                self.assemble("pop", ["dx"])

            self.assemble("pop", ["ax"])
        
        Variable.variables[self.node.variable.symbol].store_value(self, source_register=src_reg, index_register=target_index)


class VariableReferenceTranslator(Translator):

    node_type = VariableReferenceNode

    def make(self) -> None:
        self.node: VariableReferenceNode

        variable: Variable = Variable.variables[self.node.symbol]
        self.variable: Variable = variable

        index_reg: str = ""

        if self.node.index is not None:
            self.add(self.node.index)
            index_reg = "si"

        target_reg: str = ""

        bytelen = sizeof(self.node.node_type)
        if bytelen == 1:
            target_reg = "al"
        elif bytelen == 2:
            target_reg = "ax"
        elif bytelen == 4:
            target_reg = "ax,dx"

        variable.load_value(translator=self, target_register=target_reg, index_register=index_reg)
        
        self.assemble("push", ["ax"])

        if target_reg == "dx":
            self.assemble("push", ["dx"])
        



