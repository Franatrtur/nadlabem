
from .i8086.translators import TRANSLATORS as I8086
from .translator import Translator

TARGETS: dict[str, list[Type[Translator]]]  = {
    "i8086": I8086
}

