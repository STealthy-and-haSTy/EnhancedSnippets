import sublime

from .utils import log, debug


## ----------------------------------------------------------------------------


class SnippetSettingsListener():
    """
    Instances of this class watch the global preferences to know when settings
    are changing. Every time it notices that the contents of the
    ignored_packages setting has changed, it notifies interested parties so
    that they can take appropriate actions.
    """

    def __init__(self):
        """
        Create an instance and set up settings listening for the settings we
        care about. This will set up cache values for the settings we want to
        watch so that we can tell that they changed, and will set up the
        listener needed.
        """
        log('Listening for settings changes on ignored_packages')
        self.settings = sublime.load_settings('Preferences.sublime-settings')

        # Cache the list of currently ignored packages as a set, so that we can
        # easily determine what is being added to it or removed from it.
        self.cached_ignored = set(self.settings.get("ignored_packages", []))

        # Listen for changes in settings.
        self.settings.add_on_change('_es_set', self.__settings_update)

        # Set up a list for registered callbacks; any functions in this list
        # when the settings change in a way that we care about will be called
        # with details on the change.
        self.listeners = []


    def shutdown(self):
        """
        If there is currently a singleton instance of the class created, then
        this will remove its settings listener and get rid of that instance; in
        other cases it silently does nothing.
        """
        debug('settings listening code shutting down')
        self.settings.clear_on_change('_es_set')


    def add_listener(self, callback):
        """
        Add a listener so that when the settings monitored by the listener are
        changed, the callback provided is invoked.

        The callback will be passed two arguments, the set of packages that
        have been added and the set of packages that have been removed.
        """
        debug('new settings listener client has been added')
        self.listeners.append(callback);


    def __settings_update(self):
        """
        This triggers every time the settings change, allowing us to determine
        if settings we care about have changed or not.
        """
        new_ignored = set(self.settings.get("ignored_packages", []))
        if new_ignored == self.cached_ignored:
            return

        # Using set operations, we can determine which packages are now in the
        # list that were not before (added) and which packages used to be in
        # the list but no longer are (removed).
        removed = self.cached_ignored - new_ignored
        added = new_ignored - self.cached_ignored

        # Update our cached version of the setting now.
        self.cached_ignored = new_ignored

        log('settings change on ignored_packages detected')
        for callback in self.listeners:
            callback(added, removed)


## ----------------------------------------------------------------------------

