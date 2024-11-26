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
        self.node.translator = self
        self.program: ProgramTranslator = self.root
        self.result: list[str] = []
        self.make()

    def make(self) -> None:
        for child in self.node.children:
            self.add(child)

    def space(self) -> None:
        self.result.append("")

    def add(self, node: ASTNode) -> None:
        translator_type: Type[Translator] = self.program.select_translator(node)
        self.result.extend(translator_type(self, node).translate())

    def assemble(self, operation: str, arguments: list[str] = [], label: str | None = None, mapping: bool = True) -> None:
        if label is None:
            init = " " * self.config.tabspaces
        elif len(label) < self.config.tabspaces:
            init = label + " " * (self.config.tabspaces - len(label))
        else:
            self.result.append(label + ":")
            init = " " * self.config.tabspaces

        line_string = f"{init}{operation} {', '.join(map(str, arguments))}"
            
        mapstr = ""
        map_target: Line = self.node.token.line if self.node.token is not None else None
        if mapping and map_target is not None and map_target not in self.program.mapped and not self.config.erase_comments:
            self.program.mapped.add(map_target)
            mapstr = " " * (30 - len(line_string)) + ";" + (map_target.string if self.config.generate_mapping else map_target.comment)

        self.result.append(line_string + mapstr)

    def translate(self) -> list[str]:
        return self.result

    
class ProgramTranslator(Translator):

    def __init__(self, compiler: "Compiler"):
        self.config = compiler.config
        self.root = self
        self.parent = None
        self.program = self
        
        self.mapped: set[Line] = set()
        self.compiler: "Compiler" = compiler
        self.target: list[Type[Translator]] = compiler.target

        self.node: ProgramNode = compiler.tree
        self.result: list[str] = []
        self.node.translator = self

        self.make()

    def select_translator(self, node: ASTNode) -> Type[Translator]:
        for translator_type in self.target:
            if isinstance(node, translator_type.node_type):
                return translator_type
        raise NotImplementedError(f"No translator found for {node.__class__.__name__} in target {self.config.target_cpu}", line=node.token.line)

    def global_variable(self, node: ASTNode) -> None:
        pass