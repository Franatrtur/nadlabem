from ..translator import Translator, Assembly
from ..nodes.statement import VariableDeclarationNode, AssignmentNode, IncrementalNode
from ..nodes.expression import VariableReferenceNode, LiteralNode, ArrayLiteralNode
from .sizeof import sizeof
from ..tokenizer.symbols import StringLiteralToken, NumberToken, IncrementToken, DecrementToken
from ..nodes.types import Int, Bool, Array, Double
from .allocator import Variable, StackFrame
from ..errors import NotImplementedError, NadLabemError
from .program import ProgramI8086Translator
from .literal import StringReferenceTranslator

class VariableDeclarationTranslator(Translator):

    node_type = VariableDeclarationNode

    def make_array(self, variable: Variable, array_type: Array) -> None:
        self.node: VariableDeclarationNode

        if isinstance(self.node.assignment.token, StringLiteralToken):
            vals = StringReferenceTranslator.assembly_string(self.node.assignment.token)
            lenval = len(self.node.assignment.token.bytes)
        
        else:
            self.node.assignment: ArrayLiteralNode
            vals = [val.token.value for val in self.node.assignment.elements]
            lenval = len(vals)

        elem_option = "b"
        if variable.var_type.expression_type.element_type == Int:
            elem_option = "w"
        elif variable.var_type.expression_type.element_type == Double:
            elem_option = "d"

        #TODO: handle dynamic expressions in arrays
        variable.declaration = [
            Assembly(self.config, "d"+elem_option, vals, label=variable.symbol.id)
        ]
        if lenval < variable.var_type.expression_type.size:
            variable.declaration.append(
                Assembly(self.config, "res"+elem_option, [str(variable.var_type.expression_type.size - len(vals))])
            )

        self.program: ProgramI8086Translator
        if not variable.is_static:
            self.program.declare(variable.declaration)

        if not variable.is_static:
            #use the movsb or movsw to move the goddamn data
            self.config.warn(NadLabemError("Using local arrays by value (storing on stack) is extremely inefficient", self.node.token.line))

            self.assemble("lea", ["si", f"[{variable.symbol.id}]"])
            self.assemble("lea", ["di", f"[{variable.location()}]"])

            if elem_option == "b":
                self.assemble("mov", ["cx", f"{variable.bytes}"])
                self.assemble("rep", ["movsb"])
            else:
                self.assemble("mov", ["cx", f"{variable.bytes // 2}"])
                self.assemble("rep", ["movsw"])

    def make(self) -> None:
        self.node: VariableDeclarationNode

        variable: Variable = Variable.variables[self.node.symbol]
        self.variable: Variable = variable

        if self.variable.is_static:
            self.program.variables.append(variable)

        # if isinstance(self.node.assignment, LiteralNode):
        #     pass

        if isinstance(variable.var_type.expression_type, Array) and not self.node.by_reference:
            return self.make_array(variable, variable.var_type.expression_type)

        self.add(self.node.assignment)

        if self.node.by_reference:
            self.assemble("pop", ["ax"])
            variable.store_pointer(self, "ax")

        else:
            src_reg: str = ""
            bytelen = sizeof(self.node.assignment.node_type)
            if bytelen == 1:
                src_reg = "al"
            elif bytelen == 2:
                src_reg = "ax"
            elif bytelen == 4:
                src_reg = "ax,dx"
                self.assemble("pop", ["dx"])
            
            self.assemble("pop", ["ax"])

            variable.store_value(translator=self, as_type=self.node.assignment.node_type, source_register=src_reg)


class AssignmentTranslator(Translator):

    node_type = AssignmentNode

    def make(self) -> None:
        self.node: AssignmentNode

        variable: Variable = Variable.variables[self.node.symbol]
        self.variable: Variable = variable

        target_index: str = ""

        if self.node.index is not None:
            self.add(self.node.index)
            self.assemble("pop", ["si"])
            target_index = "si"

        self.add(self.node.value)

        if self.node.by_reference:
            self.assemble("pop", ["ax"])
            variable.store_pointer(translator, "ax")

        else:
            src_reg: str = ""
            bytelen = sizeof(self.node.value.node_type)
            if bytelen == 1:
                src_reg = "al"
            elif bytelen == 2:
                src_reg = "ax"
            elif bytelen == 4:
                src_reg = "ax,dx"
                self.assemble("pop", ["dx"])

            self.assemble("pop", ["ax"])
        
        Variable.variables[self.node.variable.symbol].store_value(self, as_type=self.node.value.node_type, source_register=src_reg, index_register=target_index)


class VariableReferenceTranslator(Translator):

    node_type = VariableReferenceNode

    def make(self) -> None:
        self.node: VariableReferenceNode

        variable: Variable = Variable.variables[self.node.symbol]
        self.variable: Variable = variable

        index_reg: str = ""

        if self.node.index is not None:
            self.add(self.node.index)
            self.assemble("pop", ["si"])
            index_reg = "si"

        target_reg: str = ""

        bytelen = sizeof(self.node.node_type)
        
        if bytelen == 1:
            target_reg = "al"
        elif bytelen == 2:
            target_reg = "ax"
            if index_reg:
                self.assemble("shl", ["si", "1"])
        elif bytelen == 4:
            target_reg = "ax,dx"
            if index_reg:
                self.assemble("shl", ["si", "1"])
                self.assemble("shl", ["si", "1"])

        if self.node.dereference:
            variable.load_dereference(translator=self, as_type=self.node.node_type, target_register="bx", index_register=index_reg)

        elif self.node.pointer:
            variable.load_pointer(translator=self, target_register=target_reg, index_register=index_reg)
        
        else:
            variable.load_value(translator=self, as_type=self.node.node_type, target_register=target_reg, index_register=index_reg)
            
        self.assemble("push", ["ax"])

        if "dx" in target_reg:
            self.assemble("push", ["dx"])
        


class IncrementalTranslator(Translator):

    node_type = IncrementalNode

    def make(self) -> None:
        self.node: IncrementalNode

        variable: Variable = Variable.variables[self.node.symbol]
        self.variable: Variable = variable

        if variable.var_type.expression_type is Double:
            raise NotImplementedError("Incrementing type double not supported yet in i8086", self.node.token.line)

        #TODO: add support for indexes

        variable.load_pointer(self, "bx", "")

        prefix = "word" if sizeof(variable.var_type.expression_type) == 2 else "byte"

        self.assemble("inc" if IncrementToken.match(self.node.token) else "dec", [f"{prefix}[bx]"])

        #variable.store_value(self, "!! ERROR, see i8086/var.py line 195 in incremental translator !!")

        self.result[-1]


