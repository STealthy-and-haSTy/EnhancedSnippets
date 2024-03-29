import sublime
import sublime_plugin

from ...lib import SnippetManager


## ----------------------------------------------------------------------------


class EnhancedSnippetRefreshCacheCommand(sublime_plugin.ApplicationCommand):
    """
    When invoked, this drops the currently cached version of all snippets and
    re-loads them.
    """
    def run(self):
        SnippetManager.instance.scan()


## ----------------------------------------------------------------------------
