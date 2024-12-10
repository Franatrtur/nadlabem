# __init__.py
import os
import importlib

# Automatically import each .py file in the folder (except __init__.py)
modules = [f[:-3] for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.py') and f != '__init__.py']
for module in modules:
    globals()[module] = importlib.import_module(f'.{module}', __name__)

from .tokenize import *
from .symbols import *
from .token import *