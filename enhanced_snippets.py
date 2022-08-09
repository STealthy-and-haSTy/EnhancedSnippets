import imp
import sys


###----------------------------------------------------------------------------


def reload(prefix, modules=[""]):
    prefix = f"EnhancedSnippets.{prefix}."

    for module in modules:
        module = f"{prefix}{module}".rstrip(".")
        if module in sys.modules:
            imp.reload(sys.modules[module])


###----------------------------------------------------------------------------


reload("lib")
reload("src")

from .lib import *
from .src import *


# ###----------------------------------------------------------------------------


def plugin_loaded():
    core.loaded()


def plugin_unloaded():
    core.unloaded()


###----------------------------------------------------------------------------
