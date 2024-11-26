from typing import Type
from ..translator import Translator, ProgramTranslator
from ..nodes.node import AbstractSyntaxTreeNode

from .literal import LiteralTranslator
from .var import VariableDeclarationTranslator
from .operation import BinaryOperationTranslator

from .program import ProgramI8086Translator


TRANSLATORS: list[Type[Translator]] = [
    LiteralTranslator,
    VariableDeclarationTranslator,
    BinaryOperationTranslator,
]

ENTRY_POINT: Type[ProgramTranslator] = ProgramI8086Translator