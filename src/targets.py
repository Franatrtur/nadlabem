
from .i8086.translators import TRANSLATORS as I8086_TRANSLATORS, ENTRY_POINT as I8086_ENTRY_POINT
from .translator import Translator, ProgramTranslator
from typing import Type


class CompilationTarget:

    def __init__(self,
            name: str,
            translators: list[Type[Translator]],
            entry_point: Type[ProgramTranslator]):

        self.name = name
        self.translators: list[Type[Translator]] = translators
        self.entry_point: Type[ProgramTranslator] = entry_point


TARGETS: dict[str, CompilationTarget] = {
    "i8086": CompilationTarget("i8086", I8086_TRANSLATORS, I8086_ENTRY_POINT)
}