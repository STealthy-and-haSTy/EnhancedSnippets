from ...enhanced_snippets import reload

reload("src.enhancements", ["base", "date", "clipboard"])

from ...lib.enhancement_manager import enhancements

from .base import EnhancedSnippetBase
from .date import InsertDateSnippet
from .clipboard import InsertClipboardSnippet


# Register all of the internal extensions with the system
enhancements.add(InsertDateSnippet)
enhancements.add(InsertClipboardSnippet)


__all__ = [
    # The base enhancement class from which others derive
    "EnhancedSnippetBase",

    # The known, built in enhancements
    "InsertDateSnippet",
    "InsertClipboardSnippet",
]


## ----------------------------------------------------------------------------
