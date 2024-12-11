from typing import Type
from ..translator import Translator, ProgramTranslator
from ..nodes.node import AbstractSyntaxTreeNode

from .literal import LiteralTranslator, StringReferenceTranslator
from .var import VariableDeclarationTranslator, VariableReferenceTranslator, AssignmentTranslator
from .operation import BinaryOperationTranslator, UnaryOperationTranslator
from .assembly import AssemblyTranslator, AssemblyExpressionTranslator
from .ifelse import IfTranslator
from .loops import WhileTranslator, ForTranslator, PassTranslator, ContinueTranslator, BreakTranslator
from .fun import FunctionCallTranslator, FunctionCallStatementTranslator, FunctionDefinitionTranslator, ReturnTranslator
from .cast import CastTranslator

from .program import ProgramI8086Translator, CodeBlockTranslator


TRANSLATORS: list[Type[Translator]] = [
    LiteralTranslator,
    StringReferenceTranslator,
    CastTranslator,
    VariableDeclarationTranslator,
    BinaryOperationTranslator,
    UnaryOperationTranslator,
    VariableReferenceTranslator,
    AssemblyTranslator,
    AssemblyExpressionTranslator,
    IfTranslator,
    CodeBlockTranslator,
    WhileTranslator,
    ForTranslator,
    ContinueTranslator,
    BreakTranslator,
    PassTranslator,
    AssignmentTranslator,
    FunctionCallTranslator,
    FunctionCallStatementTranslator,
    FunctionDefinitionTranslator,
    ReturnTranslator,
]

ENTRY_POINT: Type[ProgramTranslator] = ProgramI8086Translator