import sublime


## ----------------------------------------------------------------------------


# A list of instances of all of the known classes that can potentially offer
# enhanced snippet expansion variables. The items in the list are keyed based
# on their class names.
_snippet_extensions = {}



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
    _snippet_extensions[extensionClass.__name__] = extensionClass()


def get_snippet_extensions():
    """
    Get the list of currently known snippet variable extension classes.
    """
    return _snippet_extensions.values()


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


## ----------------------------------------------------------------------------
