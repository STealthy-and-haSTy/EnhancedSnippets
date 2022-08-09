import sublime


## ----------------------------------------------------------------------------


def loaded():
    """
    Initialize plugin state.
    """
    es_setting.obj = sublime.load_settings("EnhancedSnippets.sublime-settings")
    es_setting.default = {
    }

    # Start off by refreshing the list of snippets.
    sublime.run_command('enhanced_snippet_refresh_cache')


def unloaded():
    """
    Clean up every time the plugin is unloaded.
    """
    pass


## ----------------------------------------------------------------------------


def es_setting(key):
    """
    Get an EnhancedSnippet setting from a cached settings object.
    """
    default = es_setting.default.get(key, None)
    return es_setting.obj.get(key, default)


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


## ---------------------------------------------------------------------------
