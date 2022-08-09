import sublime


## ----------------------------------------------------------------------------


def loaded():
    """
    Trigger a snippet list refresh every time the plugin loads.
    """
    sublime.run_command('enhanced_snippet_refresh_cache')


def unloaded():
    """
    Clean up every time the plugin is unloaded.
    """
    pass


## ----------------------------------------------------------------------------
