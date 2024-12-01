from ..translator import Translator
from ..nodes.statement import VariableDeclarationNode, AssignmentNode
from ..nodes.expression import VariableReferenceNode
from .sizeof import sizeof
from ..nodes.types import Int, Bool, Array
from .allocator import Variable, StackFrame

class VariableDeclarationTranslator(Translator):

    node_type = VariableDeclarationNode

    def make(self) -> None:
        self.node: VariableDeclarationNode
    
        #TODO add init value to program variables instead if the value is a literal
        self.add(self.node.expression_value)
        self.assemble("pop", ["ax"])
        Variable.variables[self.node.symbol].store(translator=self, source_register="a")


class AssignmentTranslator(Translator):

    node_type = AssignmentNode

    def make(self) -> None:
        self.node: AssignmentNode

        #TODO: handle array access
        self.add(self.node.value)
        self.assemble("pop", ["ax"])
        Variable.variables[self.node.symbol].store(translator=self, target_register="a")


class VariableReferenceTranslator(Translator):

    node_type = VariableReferenceNode

    def make(self) -> None:
        self.node: VariableReferenceNode

        # arrays should be handled in the index array access  node translator
        Variable.variables[self.node.symbol].load(translator=self, target_register="a")
        self.assemble("push", ["ax"])
