import importlib.machinery
import types
from pathlib import Path

_file = Path(__file__).resolve().parent.parent / 'notething.pyw'
_loader = importlib.machinery.SourceFileLoader('notething_pyw', str(_file))
_module = types.ModuleType(_loader.name)
_loader.exec_module(_module)

Notepad = _module.Notepad

__all__ = ['Notepad']
