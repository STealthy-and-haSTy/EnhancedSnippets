import re

from ...lib import log


## ----------------------------------------------------------------------------


class EnhancedSnippetBase():
    """
    This is the base class for creating a new enhanced snippet variable. As
    snippets are loaded (or reloaded), subclasses of this class are used to see
    if the content of a snippet needs any extra variable expansions, and if so,
    what they are.
    """
    def __init__(self):
        """
        Construct an instance of this enhancement class, setting up a regular
        expression which can be used to search snippet content to see if this
        particular item applies or not.

        This will always generate a regular expression with a single capture
        group that is the (optional) default value, which can be used by the
        enhancement in any way it sees fit.
        """
        self.regex = re.compile(rf"\${{{self.variable_name()}(:[^}}]*)?}}")
        log(f"{self.__class__.__qualname__} => {self.regex.pattern}")


    def variable_name(self):
        """
        The name of the custom variable that this particular enhancement
        provides. The base class version of is_applicable() will use this to
        determine if an enhancement applies to particular snippet content or
        not.
        """
        return 'NONE'


    def is_applicable(self, content):
        """
        Given the parsed content of a snippet, return a boolean indication of
        wether or not there is a variable that needs to be expanded out by this
        class or not.

        The base class implementation does a regex search to see if the
        variable exposed by this class exists in the content or not.
        """
        return self.regex.search(content) is not None


    def variables(self, content):
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

        The base class version returns no variables and does not modify the
        snippet content.
        """
        return dict(), content


## ----------------------------------------------------------------------------
