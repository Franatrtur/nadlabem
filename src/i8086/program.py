from ..translator import Translator, ProgramTranslator, Assembly
from .sizeof import sizeof
from ..nodes.statement import VariableDeclarationNode, CodeBlockNode, FunctionDefinitonNode, ModuleNode
from .allocator import Allocator, Variable
import re
from ..ui import progress_bar
from .optimize import Optimizer


class CodeBlockTranslator(Translator):

    node_type = CodeBlockNode

    def make(self):
        for child in self.node.children:
            self.add(child)
            if not self.config.erase_comments and self.config.generate_mapping:
                self.blank_line()


class ModuleTranslator(CodeBlockTranslator):
    node_type = ModuleNode


class ProgramI8086Translator(ProgramTranslator):

    def make(self):
        # decide offset for all local vars on stack
        self.frame = Allocator(self).allocate()
        self.variables: list[Variable] = []
        self.declarations: list[list[Assembly]] = []
        self.macros: dict[str, list[Assembly]] = {}

        data_segment = "heap" if self.config.generate_mapping else "data"   # cheeky

        self.special("cpu 8086")
        self.special("segment code")

        self.assemble("mov", ["bx", data_segment], label="..start")   # start of execution
        self.assemble("mov", ["ds", "bx"])                      # data segment init
        self.assemble("mov", ["es", "bx"])                      # text segment init
        self.assemble("mov", ["bx", "stack"])                   
        self.assemble("mov", ["ss", "bx"])                      # stack segment init
        self.assemble("mov", ["sp", "dno"])                     # stack pointer init
        self.assemble("mov", ["bp", "sp"])                      # base pointer init, set to stack pointer

        self.program_begin: int = len(self.result)

        self.blank_line()

        children_done = 0

        #TODO: in nodes, add global function registration
        # and rework function translation so the translator in-place translates to nothing
        # but here we will call it in the second loop
        # ahead fn registration is so that we know how many there are for the progress bar

        for child in self.node.children:
            if not isinstance(child, FunctionDefinitonNode):
                self.add(child)
                children_done += 1
                if self.compiler.config.verbose:
                    progress_bar("Translating", children_done, len(self.node.children))

        self.special("exit:")
        self.assemble("hlt", label="ok")
        self.assemble("hlt", label="error")

        self.blank_line()

        for child in self.node.children:
            if isinstance(child, FunctionDefinitonNode):
                self.blank_line()
                self.add(child)
                children_done += 1
                if self.compiler.config.verbose:
                    progress_bar("Translating", children_done, len(self.node.children))

        self.program_end: int = len(self.result)

        for macro in self.macros.values():
            self.result.extend(macro)

        self.assemble("mov", ["ax", "1"], label="true")
        self.assemble("or", ["ax", "ax"])
        self.assemble("ret")
        self.assemble("mov", ["ax", "0"], label="false")
        self.assemble("or", ["ax", "ax"])
        self.assemble("ret")
        
        self.blank_line()

        self.special(f"segment {data_segment}")
        
        self.assemble("resw", ["1024"], label="stack")
        self.assemble("db", ["?"], label="dno")

        self.blank_line()

        for variable in self.variables:
            if not variable.declaration in self.declarations:
                self.declare(variable.declaration)

        for declaration in self.declarations:
            self.result.extend(declaration)

        self.optimize()

    
    def declare(self, variable_declaration: list[Assembly]) -> None:
        self.declarations.append(variable_declaration)

    def activate(self, tag: str, macro: list[Assembly]) -> str:
        if tag not in self.macros:
            label = self.node.context.generate_id(tag)
            macro[0].label = label
            self.macros[tag] = macro
            return label
        else:
            return self.macros[tag][0].label

    def optimize(self) -> None:
        self.result = Optimizer(self.config, self.result, self.program_begin, self.program_end).optimize()


