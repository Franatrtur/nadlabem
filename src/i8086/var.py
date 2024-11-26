from ..translator import Translator
from ..nodes.statement import VariableDeclarationNode

class VariableDeclarationTranslator(Translator):

    node_type = VariableDeclarationNode

    def make(self) -> None:
        self.node: VariableDeclarationNode

        self.program.global_variable(self.node)
        self.add(self.node.expression_value)
        
        self.assemble("pop", ["ax"], mapping=True)
        self.assemble("mov", [f"[{self.node.token.string}]", "ax"])
        #TODO: works only for ints rn

        

