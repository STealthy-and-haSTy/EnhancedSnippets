import sublime
import sublime_plugin

from ...lib import log, load_snippet, SnippetManager, snippet_expansion_args


## ----------------------------------------------------------------------------


class InsertEnhancedSnippetCommand(sublime_plugin.TextCommand):
    """
    When invoked, this drops the currently cached version of all of the
    snippet enhancements and re-loads them.
    """
    def run(self, edit, contents=None, name=None, **kwargs):
        # We must get exactly one of the two arguments in order to proceed.
        if not ((contents is None) ^ (name is None)):
            return log("insert_enhanced_snippet should be given exactly one of 'name' or 'contents'")

        # Alias the manager for clarity
        manager = SnippetManager.instance

        if contents is not None:
            snippet = load_snippet(contents, is_resource=False)
        else:
            # Try to find the snippet as an enhanced snippet; the manager knows
            # about all of them
            snippet =  manager.snippet_for_resource(name)
            if snippet is None:
                # If this is a normal snippet, try to directly load it so we
                # can expand it.
                if name.endswith('.sublime-snippet'):
                    snippet = load_snippet(name, is_resource=True)

        if snippet is None:
            return log(f"insert_enhanced_snippet was unable to find/load '{name}'")

        # Expand it
        snippet_args = snippet_expansion_args(snippet, manager, kwargs)
        self.view.run_command('insert_snippet', snippet_args)


## ----------------------------------------------------------------------------
