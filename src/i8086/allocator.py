from .sizeof import sizeof
from ..nodes.statement import VariableDeclarationNode, ArgumentDeclarationNode, FunctionDefinitonNode, StatementNode
from ..nodes.scope import Context, Symbol
from ..translator import Translator
from ..nodes.types import Array, Int, VariableType, ExpressionType, Pointer, ValueType
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

                symbol = arg_node.symbol

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
        self.var_type: VariableType = self.symbol.node.node_type
        self.bytes: int = sizeof(self.var_type)
        self.is_global: bool = self.symbol.scope.is_root
        self.is_reference: bool = self.var_type.is_reference
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

    def _location(self) -> str:
        source = self.symbol.id if self.is_global else "bp"
        off = ((" + " if self.offset > 0 else " - ") + str(abs(self.offset))) if self.offset else ""
        return source + off

    def _dereference(self, translator: Translator, as_type: ExpressionType, source: str, target_register: str, index_register: str = "") -> None:
        value_size: int = sizeof(as_type)
        index_modifier = f" + {index_register}" if index_register else ""
        if value_size == 1:
            assert target_register[0] in ["a", "b", "c", "l"] and target_register[1] in ["l", "h"], "Cannot load type 1 byte into register "+target_register
            translator.assemble("mov", [target_register[0]+"x", "0"])
            translator.assemble("mov", [target_register, f"byte[{source}{index_modifier}]"])
        elif value_size == 2:
            assert target_register in ["ax", "bx", "cx", "dx"], "Cannot load type 2 bytes into register "+target_register
            translator.assemble("mov", [target_register, f"word[{source}{index_modifier}]"])
        elif value_size == 4:
            assert target_register in ["ax,dx", "bx,cx", "si,di"], "Cannot load type 4 bytes into register/s "+target_register
            [low, high] = target_register.split(",")
            translator.assemble("mov", [low, f"word[{source}{index_modifier}]"])
            translator.assemble("mov", [high, f"word[{source}{index_modifier} + 2]"])
        else:
            raise NadLabemError(f"Cannot load type {self.var_type} as {as_type} of size {value_size} bytes into register {target_register} - too big", self.symbol.node.token.line)

    def _store(self, translator: Translator, as_type: ExpressionType, target: str, source_register: str, index_register: str = "") -> None:
        index_modifier = f" + {index_register}" if index_register else ""
        value_size: int = sizeof(as_type)
        if value_size == 1:
            assert source_register[0] in ["a", "b", "c", "l"] and source_register[1] in ["l", "h"], "Cannot store 1 byte from register "+source_register
            translator.assemble("mov", [f"byte[{target}{index_modifier}]", source_register])
        elif value_size == 2:
            assert source_register in ["ax", "bx", "cx", "dx"], "Cannot store 2 bytes from register "+source_register
            translator.assemble("mov", [f"word[{target}{index_modifier}]", source_register])
        elif value_size == 4:
            [low, high] = source_register.split(",")
            translator.assemble("mov", [f"word[{target}{index_modifier}]", low])
            translator.assemble("mov", [f"word[{target}{index_modifier} + 2]", high])
        else:
            raise NadLabemError(f"Cannot store type {self.var_type} as {as_type} of size {value_size} bytes from register {source_register} - too big", self.symbol.node.token.line)

    def load_value(self, translator: Translator, target_register: str, index_register: str = "") -> None:
        
        if self.is_reference:
            self.load_pointer(translator, "di", "")
            self._dereference(translator, self.var_type.expression_type, "di", target_register, index_register)
        else:
            self._dereference(translator, self.var_type.expression_type, self._location(), target_register, index_register)
            

    def load_pointer(self, translator: Translator, target_register: str = "bx", index_register: str = ""):
        index_modifier = f" + {index_register}" if index_register else ""
        translator.assemble("lea", [target_register, f"[{self._location()}{index_modifier}]"])

    def load_dereference(self, translator: Translator, target_register: str, index_register: str = ""):
        target_type: ValueType = self.var_type.expression_type
        if isinstance(self.var_type.expression_type, Array):
            target_type = target_type.element_type
        assert isinstance(target_type, Pointer), "Cannot dereference non-pointer variable "+self.symbol.id
        self.load_value(translator, "bx", "")
        self._dereference(translator, target_type, "bx", target_register, index_register)


    def store_pointer(self, translator: Translator, source_register: str = "bx", index_register: str = ""):
        index_modifier = f" + {index_register}" if index_register else ""
        assert self.var_type.is_reference, "Cannot store pointer to non-reference variable "+self.symbol.id
        translator.assemble("mov", [f"word[{self._location()}{index_modifier}]", source_register])
        
    def store_value(self, translator: Translator, source_register: str = "bx", index_register: str = ""):
        
        if self.is_reference:
            self.load_pointer(translator, "di", "")
            self._store(translator, self.var_type.expression_type, "di", source_register, index_register)
        else:
            self._store(translator, self.var_type.expression_type, self._location(), source_register, index_register)



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