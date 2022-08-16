from datetime import datetime

from .base import EnhancedSnippetBase


## ----------------------------------------------------------------------------


class InsertDateSnippet(EnhancedSnippetBase):
    """
    This snippet enhancement class provides the ability to expand out variables
    into the current date and time. If a default value is provided for this
    variable, it is interpreted as a date format string.
    """
    def variable_name(self):
        return 'DATE'


    def variables(self, content):
        """
        The only variable that we support is a DATE, which inserts the current
        date into the snippet.

        This will potentially rewrite the content of the snippet and export
        many variables, one for each of the distinct date formats that were
        provided.
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

        content = self.regex.sub(add_variable, content)
        return variables, content


## ----------------------------------------------------------------------------
