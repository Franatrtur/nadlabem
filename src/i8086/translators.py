from .literal import LiteralTranslator
from .var import VariableDeclarationTranslator
from typing import Type
from ..translator import Translator
from ..nodes.node import AbstractSyntaxTreeNode

TRANSLATORS: list[Type[Translator]] = [
    LiteralTranslator,
    VariableDeclarationTranslator
]