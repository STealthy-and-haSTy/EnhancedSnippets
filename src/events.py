import sublime
import sublime_plugin


from ..lib import manager


## ----------------------------------------------------------------------------


# Our injected completions use this kind information to mark themselves in the
# autocomplete panel; since we're effectively going to duplicate any snippets
# that contain dates, this will help disambiguate them for people.
RES_KIND_ENHANCED_SNIPPET = (sublime.KIND_ID_COLOR_BLUISH, "s", "Snippet [Enhanced]")


## ----------------------------------------------------------------------------


def _create_completions(snippet_list):
    """
    Given a list of objects that represent possible completions, expand them
    out into full blown completion items and return back a new list that
    contains them.
    """
    completions = []

    # for each of the items in the input list, create a new completion item
    # and insert it into the completions array.
    for snippet in snippet_list:
        trigger = snippet.trigger
        description = snippet.description
        content = snippet.content
        enhancers = snippet.enhancers


        # Construct the arguments that are going to be passed to the snippet
        # command when the completion invokes.
        #
        # As we loop through, we adjust the content that is passed to
        # subsequent handlers, since we may need to rewrite the snippet content
        # in order to implement some variables.
        snippet_args = dict()
        for enhancement in enhancers:
            new_vars, content = enhancement.variables(content)
            snippet_args.update(new_vars)

        # Include the adjusted content into the arguments so that we can
        # expand it.
        snippet_args['contents'] = content.lstrip()

        completions.append(sublime.CompletionItem.command_completion(
            trigger=trigger,
            command='insert_snippet',
            args=snippet_args,
            annotation=f"{description}",
            kind=RES_KIND_ENHANCED_SNIPPET,
            details='Enhanced snippet'))

    return completions


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

        snippets = manager.match_view(view, locations)
        return _create_completions(snippets)


    def on_post_save(self, view):
        # TODO: This should be rooted in the packages folder
        if view.file_name().endswith('.sublime-snippet'):
            sublime.run_command('enhanced_snippet_refresh_cache')


## ----------------------------------------------------------------------------
