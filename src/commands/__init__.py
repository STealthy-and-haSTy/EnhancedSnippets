from ...enhanced_snippets import reload

reload("src.commands", ["refresh_cache", "refresh_enhancements",
                        "insert_snippet", "field_picker",
                        "insert_snippet_option", "insert_and_mark",
                        "new_snippet"])

from .refresh_cache import EnhancedSnippetRefreshCacheCommand
from .refresh_enhancements import EnhancedSnippetRefreshEnhancementsCommand
from .insert_snippet import InsertEnhancedSnippetCommand
from .field_picker import EnhancedSnippetFieldPickerCommand
from .insert_snippet_option import InsertEnhancedSnippetOptionCommand
from .insert_and_mark import EnhancedSnippetInsertAndMarkCommand
from .new_snippet import NewEnhancedSnippetCommand

__all__ = [
    # Utility commands
    "EnhancedSnippetRefreshCacheCommand",
    "EnhancedSnippetRefreshEnhancementsCommand",

    # Enhancement command
    "InsertEnhancedSnippetCommand",

    # The commands called by InsertEnhancedSnippetCommand (or by commands it
    # calls) that handle the actual snippet expansion
    "EnhancedSnippetFieldPickerCommand",
    "InsertEnhancedSnippetOptionCommand",
    "EnhancedSnippetInsertAndMarkCommand",

    # Utility Commands
    "NewEnhancedSnippetCommand",
]