
from .i8086.translators import TRANSLATORS as I8086, ENTRY_POINT as I8086_ENTRY_POINT
from .translator import Translator, ProgramTranslator
from typing import Type

TARGETS: dict[str, list[Type[Translator]]]  = {
    "i8086": I8086
}

ENTRY_POINTS: dict[str, Type[ProgramTranslator]] = {
    "i8086": I8086_ENTRY_POINT
}