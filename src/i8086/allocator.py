from .sizeof import sizeof
from ..nodes.statement import VariableDeclarationNode, ArgumentDeclarationNode, FunctionDefinitonNode
from ..nodes.scope import Context, Symbol
from ..translator import Translator
from ..nodes.types import Array, Int, VariableType
from ..errors import NotImplementedError
from typing import Literal

class StackFrame:

    frames: dict[Context, "StackFrame"] = {}
    
    def __init__(self, context: Context):
        self.context: Context = context
        self.variables: list[Variable] = []
        self.var_size: int = 0
        self.arg_size: int = 0
        StackFrame.frames[context] = self

        if not context.is_root:
            self.allocate()
        else:
            self.declare()

    def declare(self):
        self.variables = [Variable(symbol, offset=None) for name, symbol in self.context.symbols.items() if isinstance(symbol.node, VariableDeclarationNode)]

    def allocate(self):
        
        arg_offset: int = -6
        var_offset: int = 2

        if not self.context.is_root:

            fn_node: FunctionDefinitonNode = self.context.node

            for name, symbol in self.context.symbols.items():

                if isinstance(symbol.node, VariableDeclarationNode):

                    variable = Variable(symbol, var_offset)
                    var_offset += sizeof(symbol.node.node_type.expression_type)
                    self.variables.append(variable)
        
            for arg_node in fn_node.arguments:

                variable = Variable(symbol, arg_offset)
                arg_offset -= sizeof(symbol.node.node_type.expression_type)


class Variable:

    variables: dict[Symbol, "Variable"] = {}

    def __init__(self, symbol: Symbol, offset: int | None):
        self.symbol: Symbol = symbol
        self.frame = StackFrame.frames[symbol.scope]
        Variable.variables[symbol] = self

        #the amount of bytes taken in memory
        self.offset: int | None = offset
        self.size: int | None = self.symbol.node.node_type.size if isinstance(self.symbol.node.node_type, Array) else None
        self.bytes: int = sizeof(self.symbol.node.node_type)
        self.is_global: bool = self.symbol.scope.is_root
        self.is_reference: bool = self.symbol.node.node_type.is_reference
        self.init_value: str | None = "?" if self.bytes <= 2 else None

    def declare(self, translator: Translator) -> None:
        if self.is_global:
            if self.init_value is not None and self.bytes == 2:
                translator.assemble("dw", [self.init_value], label=self.symbol.name)
            elif self.init_value is not None:
                translator.assemble("db", [self.init_value], label=self.symbol.name)
            else:
                translator.assemble("resb", [self.bytes], label=self.symbol.name)

    def _shifted(self, source: str, offset: int, onebyte: bool | None = None, sized: bool = True) -> str:
        onebyte = onebyte if onebyte is not None else self.bytes == 1
        prefix = ("byte" if onebyte else "word") if sized else ""
        return prefix + "[" + source + (((" + " if self.offset > 0 else " - ") + offset) if offset else "") + "]"

    def load(self, translator: Translator, index_offset: int = 0, target_register: Literal["a", "b", "c", "d"] = "a") -> None:
        register = target_register + ("l" if self.bytes == 1 else "x")

        if self.is_global and not self.is_reference:
            translator.assemble("mov", [register, self._shifted(self.symbol.name, index_offset)])

        elif self.is_global and self.is_reference:
            translator.assemble("mov", ["ax", f"[{self.symbol.name}]"])
            translator.assemble("mov", [register, self._shifted("ax", index_offset)])

        elif not self.is_global and not self.is_reference:
            translator.assemble("mov", [register, self._shifted("bp", self.offset + index_offset)])

        elif not self.is_global and self.is_reference:
            translator.assemble("mov", ["ax", self._shifted("bp", self.offset, onebyte=False)])
            translator.assemble("mov", [register, self._shifted("ax", index_offset)])


    def load_pointer(self, translator: Translator, index_offset: int = 0, target_register: Literal["a", "b", "c", "d"] = "a"):
        register = target_register + "ax"
        if self.is_global:
            translator.assemble("lea", [register, self._shifted(self.symbol.name, index_offset, sized=False)])
        else:
            translator.assemble("lea", [register, self._shifted("bp", self.offset + index_offset, sized=False)])


    def store(self, translator: Translator, index_offset: int = 0, source_register: Literal["a", "b", "c", "d"] = "a"):
        register = source_register + ("l" if self.bytes == 1 else "x")

        if self.is_global and not self.is_reference:
            translator.assemble("mov", [self._shifted(self.symbol.name, index_offset), register])

        elif self.is_global and self.is_reference:
            translator.assemble("mov", ["ax", f"[{self.symbol.name}]"])
            translator.assemble("mov", [self._shifted("ax", index_offset), register])

        elif not self.is_global and not self.is_reference:
            translator.assemble("mov", [self._shifted("bp", self.offset + index_offset), register])

        elif not self.is_global and self.is_reference:
            translator.assemble("mov", ["ax", self._shifted("bp", self.offset)])
            translator.assemble("mov", [self._shifted("ax", index_offset), register])





class Allocator:
    """Allocates memory fixend and on stack - determines offsets for local variables and assigns global ones"""

    def __init__(self, program: "ProgramTranslator"):
        self.program: "ProgramTranslator" = program

    def allocate(self) -> StackFrame:
        return self.allocate_variables(self.program.node.context)

    # recursive
    def allocate_variables(self, context: Context) -> StackFrame:

        for child in context.children:
            self.allocate_variables(child)

        return StackFrame(context)