import json
from .config import CompilationConfig
from typing import Type

class Node:

    def __init__(self, parent: "Node"):
        self.parent: Node | None = parent
        self.root: Node = parent.root if parent is not None else self
        self.children: list["Node"] = []
        self.config: CompilationConfig = parent.config if parent is not None else None

    def set_parent(self, parent: "Node"):
        self.parent = parent
        self.root = parent.root
        self.config = parent.config

    def add_child(self, child: "Node"):
        self.children.append(child)
        child.set_parent(self)

    def closest_parent(self, *parent_types: Type["Node"]) -> "Node | None":
        if self.is_root or self.parent is None:
            return None
        if any(isinstance(self.parent, parent_type) for parent_type in parent_types):
            return self.parent
        return self.parent.closest_parent(*parent_types)

    @property
    def is_root(self) -> bool:
        return self is self.root or self is self.parent or (self.parent is None and self.root is None)

    def __str__(self):
        return f"{self.__class__.__name__}(\"{[child.__str__() for child in self.children]}\")"