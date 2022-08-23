from ...enhanced_snippets import reload

reload("src.enhancements", ["base", "date", "clipboard"])

from ...lib.utils import add_snippet_extension, get_snippet_extensions

from .base import EnhancedSnippetBase
from .date import InsertDateSnippet
from .clipboard import InsertClipboardSnippet


# Register all of the internal extensions with the system
add_snippet_extension(InsertDateSnippet)
add_snippet_extension(InsertClipboardSnippet)


__all__ = [
    # The base enhancement class from which others derive
    "EnhancedSnippetBase",

    # The known, built in enhancements
    "InsertDateSnippet",
    "InsertClipboardSnippet",
]


## ----------------------------------------------------------------------------
