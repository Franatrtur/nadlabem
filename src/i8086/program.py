from ..translator import Translator, ProgramTranslator, AssemblyInstruction
from .sizeof import sizeof
from ..nodes.statement import VariableDeclarationNode, CodeBlockNode, FunctionDefinitonNode
from .allocator import Allocator, Variable
import re
from ..ui import progress_bar
from .optimize import Optimizer


class CodeBlockTranslator(Translator):

    node_type = CodeBlockNode

    def make(self):
        for child in self.node.children:
            self.blank_line()
            self.add(child)
            #self.blank_line()


class ProgramI8086Translator(ProgramTranslator):

    def make(self):
        # decide offset for all local vars on stack
        self.frame = Allocator(self).allocate()
        self.variables: list[Variable] = self.frame.variables
        self.declarations: list[list[AssemblyInstruction]] = []

        data_segment = "heap" if self.config.generate_mapping else "data"

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

        for child in self.node.children:
            if not isinstance(child, FunctionDefinitonNode):
                self.add(child)
                children_done += 1
                if self.compiler.config.verbose:
                    progress_bar("Translating", children_done, len(self.node.children))

        self.special("exit:")
        self.assemble("hlt", label=self.node.context.generate_id("ok"))
        self.assemble("hlt", label=self.node.context.generate_id("error"))


        for child in self.node.children:
            if isinstance(child, FunctionDefinitonNode):
                self.blank_line()
                self.add(child)
                children_done += 1
                if self.compiler.config.verbose:
                    progress_bar("Translating", children_done, len(self.node.children))
        
        self.blank_line()

        self.program_end: int = len(self.result)

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

    
    def declare(self, variable_declaration: list[AssemblyInstruction]) -> None:
        self.declarations.append(variable_declaration)


    def optimize(self) -> None:
        self.result = Optimizer(self.config, self.result, self.program_begin, self.program_end).optimize()


    """def optimize_old(self):
        self.result: list[str]

        code: list[str] = []

        i = 0
        while i < len(self.result):
            if self.is_instruction(i, 'push') and not self.is_instruction(i, 'pushf') and self.is_instruction(i + 1, 'pop'):
                push_reg = self.get_operand(i)
                pop_reg = self.get_operand(i + 1)

                if push_reg != pop_reg:
                    code.append(self.result[i].replace('push', 'mov').replace(push_reg, f'{pop_reg}, {push_reg}'))
                i += 2
                continue
    
            code.append(self.result[i])
            i += 1

        self.result = code


    def is_instruction(self, index: int, instruction: str) -> bool:
        return self.result[index].strip().startswith(instruction)


    def get_operand(self, index: int) -> str:
        return self.result[index].strip().split()[1]
"""