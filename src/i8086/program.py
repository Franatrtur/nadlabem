from ..translator import Translator, ProgramTranslator
from .sizeof import sizeof
from ..nodes.statement import VariableDeclarationNode, CodeBlockNode, FunctionDefinitonNode
from .allocator import Allocator
import re


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

        self.result.extend([
            "cpu 8086",
            "segment code"
        ])
        self.assemble("mov", ["bx", "data"], label="..start")   # start of execution
        self.assemble("mov", ["ds", "bx"])                      # data segment init
        self.assemble("mov", ["bx", "stack"])                   
        self.assemble("mov", ["ss", "bx"])                      # stack segment init
        self.assemble("mov", ["sp", "dno"])                     # stack pointer init
        self.assemble("mov", ["bp", "sp"])                      # base pointer init, set to stack pointer

        self.blank_line()

        for child in self.node.children:
            if not isinstance(child, FunctionDefinitonNode):
                self.add(child)

        self.assemble("hlt")
        self.blank_line()

        for child in self.node.children:
            if isinstance(child, FunctionDefinitonNode):
                self.add(child)
        
        self.blank_line()

        self.result.append("segment data")
        
        for variable in self.frame.variables:
            variable.declare(translator=self)

        self.blank_line()

        self.result.append("segment stack")
        self.assemble("resb", ["1024"])
        self.assemble("db", ["?"], label="dno")

        self.optimize()


    def optimize(self):
        self.result: list[str]

        code: list[str] = []

        i = 0
        while i < len(self.result):
            if self.is_instruction(i, 'push') and self.is_instruction(i + 1, 'pop'):
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
