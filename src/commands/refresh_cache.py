import sublime
import sublime_plugin

from ...lib import manager


## ----------------------------------------------------------------------------


class EnhancedSnippetRefreshCacheCommand(sublime_plugin.ApplicationCommand):
    """
    When invoked, this drops the currently cached version of all snippets and
    re-loads them.

    This is implicitly triggered every time the package loads, but can also be
    used manually as well as desired.
    """
    def run(self):
        manager.scan()


## ----------------------------------------------------------------------------
