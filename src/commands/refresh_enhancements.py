import sublime
import sublime_plugin

from ...lib import SnippetManager


## ----------------------------------------------------------------------------


class EnhancedSnippetRefreshEnhancementsCommand(sublime_plugin.ApplicationCommand):
    """
    When invoked, this drops the currently cached version of all of the
    snippet enhancements and re-loads them.
    """
    def run(self):
        SnippetManager.instance.reload_enhancements()


## ----------------------------------------------------------------------------
