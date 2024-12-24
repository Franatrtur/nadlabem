from ..tree import Node
from pathlib import Path
from ..nodes.scope import Namespace, Context
from ..nodes.statement import ModuleNode
from ..tokenizer.symbols import NameToken
from ..errors import NadLabemError


class Dependency(Node):

    def __init__(self, location: Path, parent: "Dependency | None"):
        super().__init__(parent)
        self.location = location
        self.module: ModuleNode = None

    def is_upstream(self, location: Path):
        if self.location == location:
            return True
        return False if self.is_root else self.parent.is_upstream(location)

    def __str__(self):
        return f"Dependency({self.dependency.location})"
    def __repr__(self):
        return str(self)

