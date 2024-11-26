from ..translator import Translator, ProgramTranslator
from .sizeof import sizeof
from ..nodes.statement import VariableDeclarationNode


class ProgramI8086Translator(ProgramTranslator):
    
    def make(self):
        self.variables: dict[str, int] = {}

        self.result.extend([
            "cpu 8086",
            "segment code"
        ])
        self.assemble("mov", ["bx", "data"], label="..start")
        self.assemble("mov", ["ds", "bx"])
        self.assemble("mov", ["bx", "stack"])
        self.assemble("mov", ["ss", "bx"])
        self.assemble("mov", ["sp", "dno"])

        self.space()

        for child in self.node.children:
            self.add(child)

        self.assemble("hlt")
        self.space()
        self.result.append("segment data")
        
        for name, size in self.variables.items():
            if size <= 2:
                self.assemble("db" if size == 1 else "dw", ["?"], label=name)
            else:
                self.assemble("resb", [str(size)], label=name)

        self.space()

        self.result.append("segment stack")
        self.assemble("resb", ["16"])
        self.assemble("db", ["?"], label="dno")

    def global_variable(self, node: VariableDeclarationNode) -> None:
        name = node.name_token.string
        bytesize = sizeof(node.node_type.expression_type)
        self.variables[name] = bytesize

    # def __init__(self, compiler: "Compiler"):
    #     super().__init__(compiler)


#     def translate(self):
#         part1 = "\n".split("""cpu 8086
# segment	code
# ..start	mov bx  , data
# 	mov ds , bx
# 	mov bx , stack
# 	mov ss,bx
# 	mov sp,dno""")

#     part1.extend(super().translate())

#     part1.extend("""segment	stack
#         resb 16
#     dno:	db ?""")

#     return part1