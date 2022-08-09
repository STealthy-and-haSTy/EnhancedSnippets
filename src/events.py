import sublime
import sublime_plugin


from ..lib.utils import create_completions, get_snippet_list


## ----------------------------------------------------------------------------


class AugmentedSnippetEventListener(sublime_plugin.EventListener):
    """
    Respond to a request for completions by checking the scope of the locations
    that are provided against our list of previously loaded snippet information
    to find those which apply to the current sitaution.

    We also respond to events that tell us that we should refresh the list of
    snippets.
    """
    def on_query_completions(self, view, prefix, locations):
        # Respect the global setting that stops snippets from appearing in the
        # autocompletion panel
        if view.settings().get('auto_complete_include_snippets') == False:
            return None

        completions = []

        # Iterate over all of the scopes for which we have loaded snippets and
        # see if they apply; the scope needs to apply at every location in the
        # locations list for this view in order to be injected.
        for scope,snippets in get_snippet_list().items():
            if all([view.match_selector(pt, scope) for pt in locations]):
                completions.extend(create_completions(snippets))

        return completions

    def on_post_save(self, view):
        # TODO: This should be rooted in the packages folder
        if view.file_name().endswith('.sublime-snippet'):
            sublime.run_command('enhanced_snippet_refresh_cache')


## ----------------------------------------------------------------------------
