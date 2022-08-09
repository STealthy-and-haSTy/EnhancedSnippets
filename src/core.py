import sublime
import sublime_plugin

import re
from datetime import datetime

from ..lib.utils import add_snippet_extension


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


## ----------------------------------------------------------------------------


# Add our static handlers to the list of extensions.
add_snippet_extension(InsertDateSnippet)
add_snippet_extension(InsertClipboardSnippet)


## ----------------------------------------------------------------------------

