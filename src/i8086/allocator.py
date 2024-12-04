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
                #translator.assemble("dw", [self.init_value], label=self.symbol.id)
                #TODO: WTF, why does dw randomly sometimes not work???
                translator.assemble("resw", [1], label=self.symbol.id)
            elif self.init_value is not None:
                #translator.assemble("db", [self.init_value], label=self.symbol.id)
                translator.assemble("resb", [1], label=self.symbol.id)
            else:
                translator.assemble("resb", [self.bytes], label=self.symbol.id)

    def _location(self, sized: bool = True) -> str:
        source = self.symbol.id if self.is_global else "bp"
        if not sized:
            prefix = ""
        elif self.is_reference:
            prefix = "word"
        else:
            prefix = "byte" if self.bytes == 1 else "word"
        off = ((" + " if self.offset > 0 else " - ") + self.offset) if self.offset else ""
        return prefix + f"[{source}{off}]"

    def load(self, translator: Translator, src_index: str = "", target_register: Literal["a", "b", "c", "d"] = "a") -> None:
        register = target_register + ("l" if self.bytes == 1 else "x")

        if self.is_global and not self.is_reference:
            translator.assemble("mov", [register, self._location(self.symbol.id) + src_index])

        elif self.is_global and self.is_reference:
            translator.assemble("mov", ["bx", f"word[{self.symbol.id}]"])
            translator.assemble("mov", [register, "bx" + src_index])

        elif not self.is_global and not self.is_reference:
            translator.assemble("mov", [register, f"bp + {self.offset}" + src_index])

        elif not self.is_global and self.is_reference:
            translator.assemble("mov", ["bx", self._location("bp", self.offset, onebyte=False)])
            translator.assemble("mov", [register, "bx" + src_index])

    def load_pointer(self, translator: Translator, src_index: str = "", target_register: Literal["a", "b", "c", "d"] = "a"):
        register = target_register + "x"
        translator.assemble("lea", [register, self._location(sized=False) + src_index])
        

    def store(self, translator: Translator, target_index: str = "", source_register: Literal["a", "b", "c", "d"] = "a"):
        register = source_register + ("l" if self.bytes == 1 else "x")

        if not self.is_reference:
            translator.assemble("mov", [self._location(), register])

        else:
            translator.assemble("mov", ["bx", self._location()])
            translator.assemble("mov", ["[bx]" + target_index, register])

    
    def store_pointer(self, translator: Translator, source_register: Literal["a", "b", "c", "d"] = "a"):
        register = source_register + "x"
        if not self.is_reference:
            raise NadLabemError(f"Cannot overwrite pointer to non-reference variable {self.symbol.id}", self.symbol.node.token.line)

        translator.assemble("mov", [self._location(), register])



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