

class Tree:
    def __init__(self, parent, root):
        self.root: Tree = root
        self.parent: Tree = parent
        self.children: list[Tree | Node] = []

    def __str__(self):
        return f"{self.__class__.__name__}(\"{[child.__str__() for child in self.children]}\")"