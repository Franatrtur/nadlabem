import json

class Node:
    """AST Nodes form the parsed program Tree"""

    def __init__(self, parent: "Node" | None):
        self.parent: Node | None = parent
        self.root: Node = parent.root if parent is not None else self
        self.children: list["Node"] = []

    def add_child(self, child: "Node"):
        self.children.append(child)

    def json(self) -> str:
        return json.dumps({"children": self.children})

    def translate(self) -> list[str]:
        translated: list[str] = []
        for branch in self.children:
            translated.extend(branch.translate)
        return translated

    def __str__(self):
        return f"{self.__class__.__name__}(\"{[child.__str__() for child in self.children]}\")"