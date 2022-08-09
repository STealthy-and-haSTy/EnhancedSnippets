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
