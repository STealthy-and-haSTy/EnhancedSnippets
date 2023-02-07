import sublime

from ..lib import SnippetManager, EnhancementManager, SnippetSettingsListener


## ----------------------------------------------------------------------------


# Our instance of the object that allows us to listen for settings changes;
# this gets initialized when the plugin loads, and cleaned up when the plugin
# unloads.
_settings_listener = None


## ----------------------------------------------------------------------------


def loaded():
    """
    Initialize plugin state.
    """
    es_setting.obj = sublime.load_settings("EnhancedSnippets.sublime-settings")
    es_setting.default = {
        "use_details": True
    }

    # Create the settings listener, which will attach to the global preferences
    # and which allows interested things to know when settings are changing.
    global _settings_listener
    _settings_listener = SnippetSettingsListener()

    # Set up the list of snippet enhancers; this includes the enhancements that
    # are packed in.
    enhancements = EnhancementManager()

    # Create the singleton snippet manager class, passing to it the listener so
    # that it can set up events and the list of enhancements so that it knows
    # how to enhance snippets.
    SnippetManager(_settings_listener, enhancements)


def unloaded():
    """
    Clean up every time the plugin is unloaded.
    """
    _settings_listener.shutdown()


## ----------------------------------------------------------------------------


def es_setting(key):
    """
    Get an EnhancedSnippet setting from a cached settings object.
    """
    default = es_setting.default.get(key, None)
    return es_setting.obj.get(key, default)


## ---------------------------------------------------------------------------
