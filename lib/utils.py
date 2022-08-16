import sublime

import xml.etree.ElementTree as ElementTree


## ----------------------------------------------------------------------------


# Our injected completions use this kind information to mark themselves in the
# autocomplete panel; since we're effectively going to duplicate any snippets
# that contain dates, this will help disambiguate them for people.
RES_KIND_ENHANCED_SNIPPET = (sublime.KIND_ID_COLOR_BLUISH, "s", "Snippet [Enhanced]")

# A list of instances of all of the known classes that can potentially offer
# enhanced snippet expansion variables.
_snippet_extensions = []

# An object that represents a list of snippets that we want to inject into the
# autocompletion system.
#
# In this dictionary the keys are scopes and the values of those keys are
# arrays of dicts that have the keys ('trigger', 'description', 'content',
# 'enhancers') to represent the snippet content to be inserted.
#
# These will dynamically get converted into completion items when they are
# offered in the AC panel.
_snippet_list = {}


## ----------------------------------------------------------------------------


def log(message, *args, status=False, dialog=False):
    """
    Simple logging method; writes to the console and optionally also the status
    message as well.
    """
    message = message % args
    print("EnhancedSnippets:", message)
    if status:
        sublime.status_message(message)
    if dialog:
        sublime.message_dialog(message)


def add_snippet_extension(extensionClass):
    """
    Add an instance of the given class (which should be a subclass of the
    EnhancedSnippetBase parent class) to the list snippet variable extension
    objects that are used to expand out our variables.
    """
    # TODO: This should notice if this class is in the list (by name) and
    # replace the old one with this new one
    _snippet_extensions.append(extensionClass())


def get_snippet_extensions():
    """
    Get the list of currently known snippet variable extension classes.
    """
    return _snippet_extensions


def get_snippet_list():
    """
    Get the list of currently loaded snippets; this will return every augmented
    snippet available, allowing the caller to determine on its own which ones
    are needed.
    """
    return _snippet_list


def clear_snippet_list():
    """
    Clear the list of currently loaded snippets; once this is done no more
    augmented snippets will be populated in the AC panel unless snippets are
    reloaded.
    """
    _snippet_list.clear()


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
        for enhancer in get_snippet_extensions():
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
        log(f"Error loading snippet: {err}")


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
