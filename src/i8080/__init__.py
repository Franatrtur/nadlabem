from ..lexer import Lexer

from .variable import DefineByteLexer
from .ignore import NoLexer

from .save_literal_to_var import SaveLiteralToVarLexer
from .save_var_to_var import SaveVarToVarLexer

from .add_var_to_var import AddVarToVarLexer
from .add_literal_to_var import AddLiteralToVarLexer

from .sub_literal_from_var import SubLiteralFromVarLexer
from .sub_var_from_var import SubVarFromVarLexer


#order matters as priority is used for detection
LEXERS: list[Lexer] = [
    DefineByteLexer,

    SaveLiteralToVarLexer,
    SaveVarToVarLexer,

    AddVarToVarLexer,
    AddLiteralToVarLexer,

    SubLiteralFromVarLexer,
    SubVarFromVarLexer,

    NoLexer
]


# __init__.py
import os
import importlib

# Automatically import each .py file in the folder (except __init__.py)
modules = [f[:-3] for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.py') and f != '__init__.py']
for module in modules:
    globals()[module] = importlib.import_module(f'.{module}', __name__)