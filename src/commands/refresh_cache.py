import sublime
import sublime_plugin

from ...lib.utils import clear_snippet_list, refresh_snippet_cache
from ...lib.utils import get_snippet_list


## ----------------------------------------------------------------------------


class EnhancedSnippetRefreshCacheCommand(sublime_plugin.ApplicationCommand):
    """
    When invoked, this drops the currently cached version of all snippets and
    re-loads them.

    This is implicitly triggered every time the package loads, but can also be
    used manually as well as desired.
    """
    def run(self):
        clear_snippet_list()
        refresh_snippet_cache(get_snippet_list())


## ----------------------------------------------------------------------------
