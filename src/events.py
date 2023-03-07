import sublime
import sublime_plugin

from .core import es_setting
from ..lib import SnippetManager, snippet_expansion_args


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
        fields = snippet.fields

        # Get the arguments required to expand this
        snippet_args = snippet_expansion_args(snippet, SnippetManager.instance, {})

        completion = {
            'trigger': trigger,
            'command': 'insert_snippet',
            'args': snippet_args,
            'annotation': f"{description}",
            'kind': RES_KIND_ENHANCED_SNIPPET,
        }

        if es_setting('use_details'):
            completion['details'] = 'Enhanced Snippet'

        completions.append(sublime.CompletionItem.command_completion(**completion))

    return completions


def _is_yaml_snippet(view):
    """
    Checks to see if the content of a view that represents an enhanced snippet
    appears to be the YAML variety, and returns True or False accordingly.
    """
    return view.substr(sublime.Region(0, 3)) == '---'


def is_enhanced_snippet(name):
    """
    Checks to see if a filename looks like a snippet, which means that it has
    a filename that matches and that it's rooted in the packages folder.

    When this is the case, a version of the filename that is a package resource
    is returned; otherwise none is returned.
    """
    spp = sublime.packages_path()
    if name and name.startswith(spp) and name.endswith('.enhanced-sublime-snippet'):
        return f'Packages/{name[len(spp)+1:]}'

    return None


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

        snippets = SnippetManager.instance.match_view(view, locations)
        return _create_completions(snippets)


    def on_load(self, view):
        # When a file loads, if it's an enhanced snippet and the first three
        # characters are the start of a frontmatter, then assign the alternate
        # syntax to it.
        res_name = is_enhanced_snippet(view.file_name())
        if res_name and _is_yaml_snippet(view):
            view.assign_syntax('Packages/EnhancedSnippets/resources/syntax/EnhancedSnippet (YAML).sublime-syntax')


    def on_post_save(self, view):
        # Any time a saved file represents a snippet resource, reload that
        # snippet. We also check to see what the content of the file looks like
        # and make sure the correct syntax is applied.
        #
        # TODO: The syntax application is ham-handed; it should only happen in
        #       cases it needs to (like if that is not already the syntax).
        res_name = is_enhanced_snippet(view.file_name())
        if res_name:
            SnippetManager.instance.reload_snippet(res_name)
            if _is_yaml_snippet(view):
                view.assign_syntax('Packages/EnhancedSnippets/resources/syntax/EnhancedSnippet (YAML).sublime-syntax')
            else:
                view.assign_syntax('Packages/EnhancedSnippets/resources/syntax/EnhancedSnippet (XML).sublime-syntax')


## ----------------------------------------------------------------------------
