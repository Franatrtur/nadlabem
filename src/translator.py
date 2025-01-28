from .nodes.node import AbstractSyntaxTreeNode as ASTNode, ProgramNode
from .tree import Node
from .tokenizer import Line
from typing import Type
from .errors import NotImplementedError
from .config import CompilationConfig


class Assembly:

    def __init__(self, config: CompilationConfig, operation: str = "", arguments: list[str] = [], label: str = "", mapping: str = ""):
        self.operation: str | None = operation
        self.arguments: list[str] = arguments
        self.label: str | None = label
        self.mapping: str = mapping
        self.config: CompilationConfig = config
        self.line_break: bool = False
        self.assembled: bool = False

    def __str__(self):
        superlabel: str = ""

        if self.label is None:
            init = " " * self.config.tabspaces
        elif self.operation is None:
            init = self.label + ":"
        elif len(self.label) < self.config.tabspaces:
            init = self.label + " " * (self.config.tabspaces - len(self.label))
        else:
            superlabel = self.label + ":\n"
            init = " " * self.config.tabspaces

        arg_sep = "" if not self.arguments else " " + (" " * (4 - len(self.operation)))
        
        op = self.operation if self.operation is not None else ""
        line_string = f"{init}{op}{arg_sep}{', '.join(map(str, self.arguments))}"
            
        mapstr = ""

        if self.mapping and not self.config.erase_comments:
            mapstr = " " + (" " * (4 * self.config.tabspaces - len(line_string)) + f";{self.mapping}")

        ending = "\n" if self.line_break and self.config.generate_mapping else ""

        return superlabel + line_string + mapstr + ending


class SpecialInstruction(Assembly):

    def __init__(self, config: CompilationConfig, string: str):
        super().__init__(config)
        self.assembled = False
        self.string = string
    
    def __str__(self):
        return self.string + ("\n" if self.line_break else "")


class Translator(Node):

    node_type: Type[ASTNode]

    def __init__(self, parent: "Translator", node: ASTNode):
        super().__init__(parent)
        self.node = node
        if self.node is not None:
            self.node.translator = self
        self.program: ProgramTranslator = self.root
        self.result: list[Assembly] = []
        self.make()

    def make(self) -> None:
        for child in self.node.children:
            self.add(child)

    def blank_line(self) -> None:
        if self.result:
            self.result[-1].line_break = True

    def add(self, node: ASTNode) -> None:
        translator_type: Type[Translator] = self.program.select_translator(node)
        self.result.extend(translator_type(self, node).translate())

    def assemble(self, operation: str = "", arguments: list[str] = [], label: str | None = None, mapping: bool = True) -> None:

        map_content = ""
        map_target: Line = self.node.token.line if self.node.token is not None else None
        if mapping and map_target is not None and map_target not in self.program.mapped and not self.config.erase_comments:
            self.program.mapped.add(map_target)
            map_content = map_target.string + f" ({map_target.location}:{map_target.number})" if self.config.generate_mapping else map_target.comment

        instruction = Assembly(self.config, operation, arguments, label, map_content)
        instruction.assembled = True
        self.result.append(instruction)

    def special(self, string: str) -> None:
        self.result.append(SpecialInstruction(self.config, string))

    def translate(self) -> list[Assembly]:
        return self.result

    
class ProgramTranslator(Translator):

    def __init__(self, compiler: "Compiler"):
        self.config = compiler.config
        self.root = self
        self.parent = None
        self.program = self
        
        self.mapped: set[Line] = set()
        self.compiler: "Compiler" = compiler
        self.translators: list[Type[Translator]] = compiler.target.translators

        self.node: ProgramNode = compiler.tree
        self.result: list[str] = []
        self.node.translator = self

        self.make()

    def select_translator(self, node: ASTNode) -> Type[Translator]:
        for translator_type in self.translators:
            if isinstance(node, translator_type.node_type):
                return translator_type
        raise NotImplementedError(f"No translator found for {node.__class__.__name__} in target {self.config.target}", line=node.token.line)