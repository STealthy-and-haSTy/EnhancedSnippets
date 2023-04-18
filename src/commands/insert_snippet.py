import sublime
import sublime_plugin

from ...lib import log, load_snippet, SnippetManager, snippet_expansion_args
from ...lib import prepare_snippet_info, handle_snippet_field_move


## ----------------------------------------------------------------------------


# FINESSE: This should take as an argument a list of options to be used for
#          snippet options in the same format as the loader provides so that it
#          is possible to invoke a snippet with options without going through
#          the AC system.
class InsertEnhancedSnippetCommand(sublime_plugin.TextCommand):
    """
    When invoked, this drops the currently cached version of all of the
    snippet enhancements and re-loads them.
    """
    def run(self, edit, name=None, contents=None, scope='', glob='', **kwargs):
        # We must get exactly one of the two source arguments in order to
        # proceed.
        if not ((contents is None) ^ (name is None)):
            return log("insert_enhanced_snippet should be given exactly one of 'name' or 'contents'")

        # Get the snippet to expand; this could be from the named file or it
        # could be raw content. If the snippet is not enhanced snippet, this
        # will load it and return the content back for us.
        snippet = self._get_snippet(name, contents, scope, glob)
        if snippet is None:
            return log(f"insert_enhanced_snippet was unable to find/load '{name}'")

        # Pull out the list of numeric fields and the options for them that we
        # should apply and store them into the view.
        prepare_snippet_info(self.view, snippet.fields, snippet.options)

        # Expand it out now.
        snippet_args = snippet_expansion_args(snippet, SnippetManager.instance, kwargs)
        self.view.run_command('insert_snippet', snippet_args)

        # Handle the case where a snippet field might be expanding out, in case
        # it has options to prompt for.
        handle_snippet_field_move(self.view, 0)


    def _get_snippet(self, name, contents, scope, glob):
        """
        Given either the name of a snippet file OR the contents, scope and
        glob strings, return back a snippet instance that represents the
        snippet in question.

        The name provided can be an enhanced snippet or even a regular snippet
        as desired.

        If the arguments do not represent a valid snippet, returns None
        """
        if contents is not None:
            return load_snippet(contents, scope, glob, is_resource=False)
        else:
            # Try to find the snippet as an enhanced snippet; the manager knows
            # about all of them
            snippet =  SnippetManager.instance.snippet_for_resource(name)
            if snippet is None:
                # If this is a normal snippet, try to directly load it so we
                # can expand it.
                if name.endswith('.sublime-snippet'):
                    snippet = load_snippet(name, is_resource=True)

            return snippet


    def is_enabled(self, contents=None, name=None, scope='', glob='', **kwargs):
        """
        Only enable the command if the arguments represent a snippet that
        applies in the current situation.

        This will take either the provided scope and glob into account, or the
        items from the value loaded from the named snippet, depending on the
        arguments.
        """
        snippet = self._get_snippet(name, contents, scope, glob)
        if snippet:
            locations = [region.b for region in self.view.sel()]
            return SnippetManager.instance.snippet_applies(snippet, self.view, locations)

        return False


## ----------------------------------------------------------------------------
