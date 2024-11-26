from ..translator import Translator


class Segment:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.lines: list[str] = []


class ProgramTranslator(Translator):

    def __init__(self, node: ProgramNode):
        super().__init__(None, node)
        self.config = node.config
        self.root = self
        self.parent = None
        self.program = self
        self.mapped: set[Line] = set()

        self.code = Segment("code")
        self.data = Segment("data")
        self.stack_size: int = 0
        self.node: ProgramNode

    def translate(self):
        part1 = "\n".split("""cpu 8086
segment	code
..start	mov bx  , data
	mov ds , bx
	mov bx , stack
	mov ss,bx
	mov sp,dno""")

    part1.extend(super().translate())

    part1.extend("""segment	stack
        resb 16
    dno:	db ?""")

    return part1