import sublime
import sublime_plugin

import re
from datetime import datetime
import xml.etree.ElementTree as ElementTree


## ----------------------------------------------------------------------------


# Our injected completions use this kind information to mark themselves in the
# autocomplete panel; since we're effectively going to duplicate any snippets
# that contain dates, this will help disambiguate them for people.
RES_KIND_ENHANCED_SNIPPET = (sublime.KIND_ID_COLOR_BLUISH, "s", "Snippet [Enhanced]")

# An object that represents a list of snippets that we want to inject into the
# autocompletion system.

# In this dictionary the keys are scopes and the values of those keys are
# arrays of dicts that have the keys ('trigger', 'description', 'content',
# 'enhancers') to represent the snippet content to be inserted.
#
# These will dynamically get converted into completion items when they are
# offered in the AC panel.
_snippet_list = {}

# A list of all of the known classes that can potentially offer enhanced
# snippet expansion variables.
_snippet_extensions = []


## ----------------------------------------------------------------------------


def plugin_loaded():
    """
    Trigger a snippet list refresh every time the plugin loads.
    """
    sublime.run_command('enhanced_snippet_refresh_cache')


def get_completion_classes(trigger, content):
    """
    Given the tab trigger for a snippet and its contents, return back a list of
    all of the known enhancement classes that apply to this particular snippet.

    This can be an empty list if none apply.
    """
    classes = []

    # We can only work with snippets that have a tab trigger since we only
    # support AC type snippets, and there's no need to waste time checking if
    # there's no body of the snippet to enhance.
    if '' not in (trigger, content):
        for enhancer in _snippet_extensions:
            if enhancer.is_applicable(content):
                classes.append(enhancer)

    return classes


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

        # Get the list of potential enhancements that we can make to this
        # snippet, which is based on the snippet content itself. If there are
        # not any, then we can just leave.
        enhancers = get_completion_classes(trigger, content)
        if not enhancers:
            return

        # Get the array into which we're going to insert our completion handler;
        # this might be a new one if there's not already one in the object.
        items = snippet_list.get(scope, None)
        if items is None:
            items = []
            snippet_list[scope] = items

        # Insert a dictionary that tells us how to create the appropriate
        # completion item when the completion fires.
        items.append({
            'trigger': trigger,
            'description': description,
            'content': content.lstrip(),
            'enhancers': enhancers
        })

    except Exception as err:
        print(f"Error loading snippet: {err}")


def create_completions(input_list):
    """
    Given a list of objects that represent possible completions, expand them
    out into full blown completion items and return back a new list that
    contains them.
    """
    completions = []

    # for each of the items in the input list, create a new completion item
    # and insert it into the completions array.
    for options in input_list:
        trigger = options["trigger"]
        description = options["description"]
        content = options["content"]
        enhancers = options["enhancers"]


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
        # print(snippet_args)

        completions.append(sublime.CompletionItem.command_completion(
            trigger=trigger,
            command='insert_snippet',
            args=snippet_args,
            annotation=f"{description} [Enhanced]",
            kind=RES_KIND_ENHANCED_SNIPPET,
            details='Enhanced snippet'))

    return completions


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
                completions.extend(create_completions(snippets))

        return completions

    def on_post_save(self, view):
        # TODO: THis should be rooted in the packages folder
        if view.file_name().endswith('.sublime-snippet'):
            sublime.run_command('enhanced_snippet_refresh_cache')


## ----------------------------------------------------------------------------


class EnhancedSnippetBase():
    """
    This is the base class for creating a new enhanced snippet expansion. As
    snippets are loaded (or reloaded), subclasses of this class are used to
    see if the content of a snippet needs any extra expansions, and if so,
    what they are.
    """
    @classmethod
    def is_applicable(cls, content):
        """
        Given the parsed content of a snippet, return a boolean indication of
        wether or not there is a variable that needs to be expanded out by this
        class or not.

        The base class implementation assumes no variables are needed.
        """
        return False

    @classmethod
    def variables(cls, content):
        """
        Given a parsed snippet body, return back a dictionary of variables and
        a (potentially modified) version of the contents of the snippet. The
        variables dictionary has keys that are the variables that need to be
        expanded, and the values are the text that will be inserted when that
        snippet expands.

        The content that is returned may or may not be modified in some fashion
        depending on wether or not this enhancement requires changes in order
        to expand out the variable properly or not.

        This will only get invoked if is_applicable() says that this class
        is supposed to contribute snippet variables.
        """
        return dict(), content


## ----------------------------------------------------------------------------


class InsertDateSnippet(EnhancedSnippetBase):
    # Look for full form date variables wherein the optional default value can
    # be a stftime format string for how to present the current date.
    _regex = re.compile(r"\${DATE(:[^}]*)?}")

    """
    This snippet enhancement class provides the ability to expand out variables
    into the current date and time.
    """
    @classmethod
    def is_applicable(cls, content):
        """
        In order for us to contribute a variable, the snippet body needs to
        want to inject a date into the snippet.
        """
        return cls._regex.search(content) is not None

    @classmethod
    def variables(cls, content):
        """
        The only variable that we support is a DATE, which inserts the current
        date into the snippet.
        """
        today = datetime.today()
        variables = {
            'DATE': today.strftime('%x')
        }

        def add_variable(match):
            fmt = match.group(1)
            var = 'DATE'
            if fmt is not None and fmt != ':':
                var = f"DATE_{len(variables)}"
                variables[var] = today.strftime(fmt[1:])


            return f'${{{var}}}'

        content = cls._regex.sub(add_variable, content)
        return variables, content

_snippet_extensions.append(InsertDateSnippet)


## ----------------------------------------------------------------------------


class InsertClipboardSnippet(EnhancedSnippetBase):
    """
    This snippet enhancement class provides the ability to expand out variables
    that contain the current clipboard text.
    """
    @classmethod
    def is_applicable(cls, content):
        """
        In order for us to contribute a variable, the snippet body needs to
        want to inject the clipboard into the snippet.
        """
        return content.find('${CLIPBOARD}') != -1

    @classmethod
    def variables(cls, content):
        """
        The only variable that we support is a CLIPBOARD, which inserts the
        current clipboard contents into the snippet.
        """
        return {
            'CLIPBOARD': sublime.get_clipboard()
        }, content

_snippet_extensions.append(InsertClipboardSnippet)


## ----------------------------------------------------------------------------
