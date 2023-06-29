import sublime
import sublime_plugin

from .core import es_setting, es_syntax
from ..lib import SnippetManager, snippet_expansion_args
from ..lib import clear_snippet_info, handle_snippet_field_move


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
        completion = {
            'trigger': snippet.trigger,
            'command': 'insert_enhanced_snippet',
            'args': { 'name': snippet.resource },
            'annotation': f"{snippet.description}",
            'kind': RES_KIND_ENHANCED_SNIPPET,
        }

        if es_setting('use_details'):
            completion['details'] = 'Enhanced Snippet'

        completions.append(sublime.CompletionItem.command_completion(**completion))

    return completions


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
    to find those which apply to the current situation.

    We also respond to save events on files that look like active snippet
    resources so that we can reload the files that they contain.
    We also respond to events that tell us that we should refresh the list of
    snippets.

    In addition to the above, this also drives the process by which we track
    the navigation between fields in special snippets to be able to prompt the
    user for a multiple choice field option for some fields.

    When a multiple choice snippet expands, the command that handles it will
    set up tracking information that allows us to handle the next_field and
    prev_field commands to know where in the snippet we are, so we can act
    accordingly.

    We track when non-special snippets are (or might be) expanding and delete
    any tracking information we might be storing for them so that we don't take
    actions at the wrong time.
    """
    def _native_snippet_expand_starting(self, command, args):
        """
        Given a command name and (possible) argument dictionary, return an
        indication of whether this means that a snippet expansion is starting
        or not.
        """
        # These commands are a definite snippet expansion starting
        if command in ('expand_snippet', 'commit_completion'):
            return True

        # This command MIGHT be starting an auto complete, so long as it has
        # arguments; with no arguments it just summons the panel. With args it
        # might start an expansion, or it might just insert some text; we don't
        # really care either way for our purposes.
        if command == 'auto_complete' and len(args or {}):
            return True


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
        if is_enhanced_snippet(view.file_name()):
            view.assign_syntax(es_syntax('EnhancedSnippet'))


    def on_post_save(self, view):
        # Any time a saved file represents a snippet resource, reload that
        # snippet. We also check to see what the content of the file looks like
        # and make sure the correct syntax is applied.
        res_name = is_enhanced_snippet(view.file_name())
        if res_name:
            def reload_snippet():
                SnippetManager.instance.reload_snippet(res_name)
                syntax = es_syntax('EnhancedSnippet')
                if view.settings().get("syntax") != syntax:
                    view.assign_syntax(syntax)

            sublime.set_timeout(reload_snippet, 100)


    def on_text_command(self, view, command, args):
        # Check the current command to see if it's indicating that a snippet
        # is about to expand; if so, then we know we should stop listening to
        # other special commands in that view.
        if self._native_snippet_expand_starting(command, args):
            clear_snippet_info(view)

        if command == 'next_field':
            handle_snippet_field_move(view, 1)

        if command == 'prev_field':
            handle_snippet_field_move(view, -1)


## ----------------------------------------------------------------------------
