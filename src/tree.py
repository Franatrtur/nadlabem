

class Node:
    def __init__(self, parent, root, value):
        self.root: Tree = root
        self.parent: Tree = parent
        self.value = value


class Tree:
    def __init__(self, parent, root):
        self.root: Tree = root
        self.parent: Tree = parent
        self.children: list[Tree | Node] = []