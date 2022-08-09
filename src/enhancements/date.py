import re
from datetime import datetime

from .base import EnhancedSnippetBase


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
            # TODO: This should check and see if a format is reused and if so
            # just reuse the same variable instead of making a new one for
            # each.
            fmt = match.group(1)
            var = 'DATE'
            if fmt is not None and fmt != ':':
                var = f"DATE_{len(variables)}"
                variables[var] = today.strftime(fmt[1:])

            return f'${{{var}}}'

        content = cls._regex.sub(add_variable, content)
        return variables, content


## ----------------------------------------------------------------------------
