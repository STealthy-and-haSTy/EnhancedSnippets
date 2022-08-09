import sublime

from .base import EnhancedSnippetBase


## ----------------------------------------------------------------------------


class InsertClipboardSnippet(EnhancedSnippetBase):
    """
    This snippet enhancement class provides the ability to expand out variables
    that contain the current clipboard text.
    """
    @classmethod
    def is_applicable(cls, content):
        """
        In order for us to contribute a variable, the snippet body needs to
        want to inject the clipboard into the snippet.
        """
        return content.find('${CLIPBOARD}') != -1

    @classmethod
    def variables(cls, content):
        """
        The only variable that we support is a CLIPBOARD, which inserts the
        current clipboard contents into the snippet.
        """
        return {
            'CLIPBOARD': sublime.get_clipboard()
        }, content


## ----------------------------------------------------------------------------
