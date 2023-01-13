from ...enhanced_snippets import reload

reload("lib.enhancements", ["base", "date", "clipboard"])

from .base import EnhancedSnippetBase
from .date import InsertDateSnippet
from .clipboard import InsertClipboardSnippet

from ..utils import log


def install_builtin_enhancements(enhancements):
    """
    This will register all of the shipped snippet enhancements with the
    enhancement manager instance provided.
    """
    log('installing built-in snippet enhancement classes')
    enhancements.add(InsertDateSnippet)
    enhancements.add(InsertClipboardSnippet)


__all__ = [
    # The base enhancement class from which others derive
    "EnhancedSnippetBase",

    # The known, built in enhancements
    "InsertDateSnippet",
    "InsertClipboardSnippet",

    # The function that initalizes enhancements for us.
    "install_builtin_enhancements",
]


## ----------------------------------------------------------------------------
