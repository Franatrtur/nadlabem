from ..translator import Translator
from ..nodes.statement import FunctionDefinitonNode, FunctionCallStatementNode, ReturnNode
from ..nodes.expression import FunctionCallNode, ExpressionNode
from ..tokenizer.symbols import DoToken, WhileToken
from .allocator import Variable, StackFrame


RETURN_REGISTER = "ax"


class ReturnTranslator(Translator):

    node_type = ReturnNode

    def make(self) -> None:
        self.node: ReturnNode

        fn_translator: FunctionDefinitionTranslator = self.node.function.translator

        if self.node.value is not None:
            self.add(self.node.value)
            self.assemble("pop", [RETURN_REGISTER])

        self.assemble("jmp", [fn_translator.ret_label])


class FunctionDefinitionTranslator(Translator):

    node_type = FunctionDefinitonNode

    def make(self) -> None:
        self.node: FunctionDefinitonNode

        self.fn_label: str = self.node.symbol.id
        self.ret_label: str = self.node.scope.generate_id("rtn")

        self.frame = StackFrame.frames[self.node.context]

        self.result.append(f"{self.fn_label}:")
        self.assemble("push", ["bp"])
        self.assemble("mov", ["bp", "sp"])
        self.assemble("sub", ["sp", f"{self.frame.var_bytes}"])

        self.add(self.node.body)

        self.assemble("mov", ["sp", "bp"], label=self.ret_label)
        self.assemble("pop", ["bp"])
        self.assemble("ret", [str(self.frame.arg_bytes)])


class FunctionCallStatementTranslator(Translator):

    node_type = FunctionCallStatementNode

    def make(self) -> None:
        self.node: FunctionCallStatementNode

        for arg in reversed(self.node.arguments):
            self.add(arg)

        self.assemble("call", [self.node.symbol.id])


class FunctionCallTranslator(FunctionCallStatementTranslator):

    node_type = FunctionCallNode

    def make(self) -> None:
        self.node: FunctionCallNode

        super().make()

        self.assemble("push", [RETURN_REGISTER])
