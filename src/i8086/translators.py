from typing import Type
from ..translator import Translator, ProgramTranslator
from ..nodes.node import AbstractSyntaxTreeNode

from .literal import LiteralTranslator
from .var import VariableDeclarationTranslator, VariableReferenceTranslator
from .operation import BinaryOperationTranslator
from .assembly import AssemblyTranslator

from .program import ProgramI8086Translator


TRANSLATORS: list[Type[Translator]] = [
    LiteralTranslator,
    VariableDeclarationTranslator,
    BinaryOperationTranslator,
    VariableReferenceTranslator,
    AssemblyTranslator
]

ENTRY_POINT: Type[ProgramTranslator] = ProgramI8086Translator