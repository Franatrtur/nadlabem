from typing import Type
from ..translator import Translator, ProgramTranslator
from ..nodes.node import AbstractSyntaxTreeNode

from .literal import LiteralTranslator
from .var import VariableDeclarationTranslator, VariableReferenceTranslator
from .operation import BinaryOperationTranslator
from .assembly import AssemblyTranslator, AssemblyExpressionTranslator
from .ifelse import IfTranslator

from .program import ProgramI8086Translator, CodeBlockTranslator


TRANSLATORS: list[Type[Translator]] = [
    LiteralTranslator,
    VariableDeclarationTranslator,
    BinaryOperationTranslator,
    VariableReferenceTranslator,
    AssemblyTranslator,
    AssemblyExpressionTranslator,
    IfTranslator,
    CodeBlockTranslator
]

ENTRY_POINT: Type[ProgramTranslator] = ProgramI8086Translator