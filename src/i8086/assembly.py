from .program import ProgramTranslator
from ..translator import Translator
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from ..nodes.statement import AssemblyNode
from ..errors import NotImplementedError
from ..tokenizer.symbols import HashToken

class AssemblyTranslator(Translator):

    node_type = AssemblyNode

    def make(self) -> None:
        self.node: AssemblyNode

        # if the command starts with a space its unlabeled instruction # hlt
        # otherwise treat it as #label hlt

        instruction = "#".join(self.node.token.line.string.split("#")[1:])

        label = None
        cmd = instruction[1:]

        if instruction[0] != " ":
            label = instruction.split(" ")[0]
            cmd = " ".join(instruction.split(" ")[1:])

        self.assemble(cmd, [], mapping=False, label=label)


