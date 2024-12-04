from .program import ProgramTranslator
from ..translator import Translator
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from ..nodes.statement import AssemblyNode
from ..nodes.expression import AssemblyExpressionNode
from ..errors import NotImplementedError, SyntaxError
from ..tokenizer.symbols import AtToken

class AssemblyTranslator(Translator):

    node_type = AssemblyNode

    def make(self) -> None:
        self.node: AssemblyNode

        # if the command starts with a space its unlabeled instruction  @ mov
        # otherwise treat it as labeled                                 @label mov

        instruction = "$".join(self.node.token.line.string.split("$")[1:])

        if not instruction:
            raise SyntaxError("Assembly node without instruction", self.node.token.line)

        label = None
        cmd = instruction[1:]

        if instruction[0] != " ":
            label = instruction.split(" ")[0]
            cmd = " ".join(instruction.split(" ")[1:])

        self.assemble(cmd, [], mapping=True, label=label)


class AssemblyExpressionTranslator(AssemblyTranslator):

    node_type = AssemblyExpressionNode

    def make(self) -> None:
        self.node: AssemblyExpressionNode

        onebyte = True if (self.node.assembly_expression.startswith("byte[") or
                            self.node.assembly_expression.endswith("h") or
                            self.node.assembly_expression.endswith("l")) else False

        self.assemble("mov", ["al" if onebyte else "ax", self.node.assembly_expression])
        if onebyte:
            self.assemble("mov", ["ah", "0"])
        self.assemble("push", ["ax"])
