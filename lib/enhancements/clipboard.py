import sublime

from .base import EnhancedSnippetBase


## ----------------------------------------------------------------------------


class InsertClipboardSnippet(EnhancedSnippetBase):
    """
    This snippet enhancement class provides the ability to expand out variables
    that contain the current clipboard text; if there is no text currently in
    the clipboard (i.e. it is an empty string), this does not contribute a
    variable.
    """
    def variable_name(self):
        return 'CLIPBOARD'


    def variables(self, content):
        """
        The only variable that we support is a CLIPBOARD, which inserts the
        current clipboard contents into the snippet, but only if there is
        actually any clipboard text.
        """
        text = sublime.get_clipboard()
        return {
            'CLIPBOARD': text if text != '' else None
        }, content


## ----------------------------------------------------------------------------
