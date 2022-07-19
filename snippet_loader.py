import sublime
import sublime_plugin

from datetime import datetime
import xml.etree.ElementTree as ElementTree


## ----------------------------------------------------------------------------


# Our injected completions use this kind information to mark themselves in the
# autocomplete panel; since we're effectively going to duplicate any snippets
# that contain dates, this will help disambiguate them for people.
RES_KIND_ENHANCED_SNIPPET = (sublime.KIND_ID_COLOR_BLUISH, "s", "Snippet [Enhanced]")

# An object that represents a list of snippets that we want to inject into the
# autocompletion system.
#
# In this dictionary the keys are scopes and the values of those keys are
# arrays of completion items that apply in those scopes.
_snippet_list = {}


## ----------------------------------------------------------------------------


def plugin_loaded():
    """
    Trigger a snippet list refresh every time the plugin loads.
    """
    sublime.run_command('enhanced_snippet_refresh_cache')


def get_snippet_completion(snippet_resource, snippet_list):
    """
    Given a package resource name for a snippet, load and parse it to see if it
    contains a snippet that we want to be able to handle.

    If it does, then add it to the provided snippet list, keying it by the
    scope in the snippet (if any) for quick lookup later.
    """
    try:
        # Load the contents of the snippet as a string, then try to parse it
        xml = sublime.load_resource(snippet_resource)
        root = ElementTree.fromstring(xml)

        # Look up the nodes in the XML for the trigger, description, scope and
        # contents; this gets us the nodes, which might be None if there is no
        # appropriate tag in the snippet.
        trigger = root.find('tabTrigger')
        description = root.find('description')
        content = root.find('content')
        scope = root.find('scope')

        # Pull out the text for everything in the ugliest possible way;
        # anything for which there is no tag is an empty string
        trigger = '' if trigger is None else trigger.text
        description = '' if description is None else description.text
        content = '' if content is None else content.text
        scope = '' if scope is None else scope.text

        # If there is no tab trigger, or the content doesn't include the
        # special date trigger, we don't care about this snippet.
        if '' in (trigger, content) or content.find('${DATE}') == -1:
            return

        # Get the array into which we're going to insert our completion handler;
        # this might be a new one if there's not already one in the object.
        items = snippet_list.get(scope, None)
        if items is None:
            items = []
            snippet_list[scope] = items

        # Return the scope to which this snippet applies (which can be the
        # empty string to imply everywhere) and a completion item that will
        # insert the snippet, expanding out the date.
        items.append(sublime.CompletionItem.command_completion(
            trigger=trigger,
            command='insert_snippet',
            args={
                'contents': content.lstrip(),
                'DATE': datetime.today().strftime('%x')
            },
            annotation=f"{description} [Enhanced]",
            kind=RES_KIND_ENHANCED_SNIPPET,
            details='Enhanced snippet'))

    except Exception as err:
        print(f"Error loading snippet: {err}")


def refresh_snippet_cache(snippet_list):
    """
    Find all of the sublime-snippet files that exist across all known packages
    and load them into memory, cacheing any that contain the special date field
    that we want to be able to insert.

    Snippets with no tab triggers or for which there is no date field are
    ignored.

    The return is a dict that is keyed by scope and whose values are the
    snippets that apply to those scopes.
    """
    resources = sublime.find_resources('*.sublime-snippet')
    for entry in resources:
        get_snippet_completion(entry, snippet_list)


## ----------------------------------------------------------------------------


class EnhancedSnippetRefreshCacheCommand(sublime_plugin.ApplicationCommand):
    """
    When invoked, this drops the currently cached version of all snippets and
    re-loads them.

    This is implicitly triggered every time the package loads, but can also be
    used manually as well as desired.
    """
    def run(self):
        print('***REFRESHING SNIPPET CACHE***')
        _snippet_list.clear()
        refresh_snippet_cache(_snippet_list)


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
        for scope,snippets in _snippet_list.items():
            if all([view.match_selector(pt, scope) for pt in locations]):
                completions.extend(snippets)

        return completions

    def on_post_save(self, view):
        if view.file_name().endswith('.sublime-snippet'):
            sublime.run_command('enhanced_snippet_refresh_cache')


## ----------------------------------------------------------------------------
