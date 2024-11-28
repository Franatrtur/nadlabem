from ..translator import Translator
from ..nodes.statement import VariableDeclarationNode
from ..nodes.expression import VariableReferenceNode
from .sizeof import sizeof
from ..nodes.types import Int, Bool, Array
from .allocator import Variable, StackFrame

class VariableDeclarationTranslator(Translator):

    node_type = VariableDeclarationNode

    def load(self, translator: Translator) -> None:
        self.assemble("push", ["ax"])

    def make(self) -> None:
        self.node: VariableDeclarationNode
    
        self.add(self.node.expression_value)
        self.assemble("pop", ["ax"])
        Variable.variables[self.node.symbol].store(translator=self, source_register="a")

        
class VariableReferenceTranslator(Translator):

    node_type = VariableReferenceNode

    def make(self) -> None:
        self.node: VariableReferenceNode

        Variable.variables[self.node.symbol].load(translator=self, target_register="a")
        self.assemble("push", ["ax"])
