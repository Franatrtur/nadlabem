from typing import Type
from ..translator import Translator, ProgramTranslator
from ..nodes.node import AbstractSyntaxTreeNode

from .literal import LiteralTranslator, StringReferenceTranslator
from .var import VariableDeclarationTranslator, VariableReferenceTranslator, AssignmentTranslator, IncrementalTranslator
from .operation import AdditiveTranslator, MultiplicativeTranslator, BinaryTranslator, ComparisonTranslator, UnaryOperationTranslator
from .assembly import AssemblyTranslator, AssemblyExpressionTranslator
from .ifelse import IfTranslator
from .loops import WhileTranslator, ForTranslator, PassTranslator, ContinueTranslator, BreakTranslator
from .fun import FunctionCallTranslator, FunctionCallStatementTranslator, FunctionDefinitionTranslator, ReturnTranslator
from .cast import CastTranslator

from .program import ProgramI8086Translator, CodeBlockTranslator, ModuleTranslator


TRANSLATORS: list[Type[Translator]] = [
    LiteralTranslator,
    StringReferenceTranslator,
    CastTranslator,
    VariableDeclarationTranslator,
    AdditiveTranslator,
    MultiplicativeTranslator,
    BinaryTranslator,
    ComparisonTranslator,
    UnaryOperationTranslator,
    VariableReferenceTranslator,
    IncrementalTranslator,
    AssemblyTranslator,
    AssemblyExpressionTranslator,
    IfTranslator,
    CodeBlockTranslator,
    ModuleTranslator,
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