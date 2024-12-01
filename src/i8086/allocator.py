from .sizeof import sizeof
from ..nodes.statement import VariableDeclarationNode, ArgumentDeclarationNode, FunctionDefinitonNode, StatementNode
from ..nodes.scope import Context, Symbol
from ..translator import Translator
from ..nodes.types import Array, Int, VariableType
from ..errors import NadLabemError, NotImplementedError
from typing import Literal

class StackFrame:

    frames: dict[Context, "StackFrame"] = {}
    
    def __init__(self, context: Context):
        self.context: Context = context
        self.variables: list[Variable] = []
        StackFrame.frames[context] = self

        if not context.is_root:
            self.allocate()
        else:
            self.declare()

    def declare(self):
        self.variables = [Variable(symbol, offset=None) for name, symbol in self.context.symbols.items() if isinstance(symbol.node, VariableDeclarationNode)]

    def allocate(self):
        
        self.var_bytes: int = 0     # forwards (-)
        self.arg_bytes: int = 0     # backwards (+)

        if not self.context.is_root:

            fn_node: FunctionDefinitonNode = self.context.node

            for name, symbol in self.context.symbols.items():

                if isinstance(symbol.node, VariableDeclarationNode):

                    self.var_bytes += sizeof(symbol.node.node_type.expression_type)
                    variable = Variable(symbol, -self.var_bytes)
                    self.variables.append(variable)
        
            for arg_node in fn_node.arguments:

                self.arg_bytes += 2  # we just dont care
                variable = Variable(symbol, self.arg_bytes + 2)     # ret addr + old bp = 4
                self.variables.append(variable)


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
                translator.assemble("dw", [self.init_value], label=self.symbol.id)
            elif self.init_value is not None:
                translator.assemble("db", [self.init_value], label=self.symbol.id)
            else:
                translator.assemble("resb", [self.bytes], label=self.symbol.id)

    def _shifted(self, source: str, offset: int, onebyte: bool | None = None, sized: bool = True) -> str:
        onebyte = onebyte if onebyte is not None else self.bytes == 1
        prefix = ("byte" if onebyte else "word") if sized else ""
        return prefix + "[" + source + (((" + " if self.offset > 0 else " - ") + str(offset)) if offset else "") + "]"

    def load(self, translator: Translator, index_offset: int = 0, target_register: Literal["a", "b", "c", "d"] = "a") -> None:
        register = target_register + ("l" if self.bytes == 1 else "x")

        if self.is_global and not self.is_reference:
            translator.assemble("mov", [register, self._shifted(self.symbol.id, index_offset)])

        elif self.is_global and self.is_reference:
            translator.assemble("mov", ["ax", f"word[{self.symbol.id}]"])
            translator.assemble("mov", [register, self._shifted("ax", index_offset)])

        elif not self.is_global and not self.is_reference:
            translator.assemble("mov", [register, self._shifted("bp", self.offset + index_offset)])

        elif not self.is_global and self.is_reference:
            translator.assemble("mov", ["ax", self._shifted("bp", self.offset, onebyte=False)])
            translator.assemble("mov", [register, self._shifted("ax", index_offset)])


    def load_pointer(self, translator: Translator, index_offset: int = 0, target_register: Literal["a", "b", "c", "d"] = "a"):
        register = target_register + "x"
        if self.is_global:
            translator.assemble("lea", [register, self._shifted(self.symbol.id, index_offset, sized=False)])
        else:
            translator.assemble("lea", [register, self._shifted("bp", self.offset + index_offset, sized=False)])


    def store(self, translator: Translator, index_offset: int = 0, source_register: Literal["a", "b", "c", "d"] = "a"):
        register = source_register + ("l" if self.bytes == 1 else "x")

        if self.is_global and not self.is_reference:
            translator.assemble("mov", [self._shifted(self.symbol.id, index_offset), register])

        elif self.is_global and self.is_reference:
            translator.assemble("mov", ["ax", f"[{self.symbol.id}]"])
            translator.assemble("mov", [self._shifted("ax", index_offset), register])

        elif not self.is_global and not self.is_reference:
            translator.assemble("mov", [self._shifted("bp", self.offset + index_offset), register])

        elif not self.is_global and self.is_reference:
            translator.assemble("mov", ["ax", self._shifted("bp", self.offset)])
            translator.assemble("mov", [self._shifted("ax", index_offset), register])

    
    def store_pointer(self, translator: Translator, source_register: Literal["a", "b", "c", "d"] = "a"):
        register = source_register + "x"
        if not self.is_reference:
            raise NadLabemError(f"Cannot overwrite pointer to non-reference variable {self.symbol.id}", self.symbol.node.token.line)
        
        if self.is_global:
            translator.assemble("mov", [f"[{self.symbol.id}]", register])
        else:
            translator.assemble("mov", [self._shifted("bp", self.offset), register])






class Allocator:
    """Allocates memory fixed and on stack - determines offsets for local variables and assigns global ones"""

    def __init__(self, program: "ProgramTranslator"):
        self.program: "ProgramTranslator" = program

    def allocate(self) -> StackFrame:
        return self.create_stack_frame(self.program.node.context)

    # recursive
    def create_stack_frame(self, context: Context) -> StackFrame:

        for child in context.children:
            self.create_stack_frame(child)

        return StackFrame(context)