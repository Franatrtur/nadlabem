
class Tree:
    def __init__(self, parent: "Tree", root: "Tree"):
        self.root: Tree = root
        self.parent: Tree = parent
        self.children: list[Tree | Node] = []

    def add_child(self, child: "Tree"):
        self.children.append(child)

    def __str__(self):
        return f"{self.__class__.__name__}(\"{[child.__str__() for child in self.children]}\")"