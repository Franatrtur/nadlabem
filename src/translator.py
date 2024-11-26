from .nodes.node import AbstractSyntaxTreeNode as ASTNode, ProgramNode
from .tree import Node
from .tokenizer import Line
from typing import Type
from .errors import NotImplementedError

class Translator(Node):

    node_type: Type[ASTNode]

    def __init__(self, parent: "Translator", node: ASTNode):
        super().__init__(parent)
        self.node = node
        self.program = self.root
        self.result: list[str] = []
        self.make()

    def make(self) -> None:
        for child in self.children:
            self.add(child)

    def add(self, node: ASTNode) -> None:
        translator: Type[Translator] = self.program.select_translator(node)
        self.extend(translator(self, lines).translate())

    def extend(self, lines: list[str]) -> None:
        self.result.extend(lines)

    def assemble(self, operation: str, arguments: list[str]) -> None:
        self.result.append(f"{operation} {', '.join(map(str, arguments))}")

    def translate(self) -> list[str]:
        return self.result

    
class ProgramTranslator(Translator):

    def __init__(self, compiler: "Compiler"):
        super().__init__(None, node)
        self.config = node.config
        self.root = self
        self.parent = None
        self.program = self
        self.mapped: set[Line] = set()
        self.node: ProgramNode = compiler.tree
        self.compiler: "Compiler" = compiler
        self.target: list[Type[Translator]] = compiler.target

    def select_translator(self, node: ASTNode) -> Type[Translator]:
        for translator in self.target:
            if translator.node_type.detects_subclass(node.__class__):
                return translator
        raise NotImplementedError(f"No translator found for {node.__class__.__name__} in target {self.config.target_cpu}", line=node.token.line)