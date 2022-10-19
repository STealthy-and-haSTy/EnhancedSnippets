import sublime


## ----------------------------------------------------------------------------


class EnhancementManager():
    """
    Instances of this class are responsible for keeping track of the classes
    that give us our enhanced snippet variables.
    """
    _extensions = {}


    def add(self, extensionClass):
        """
        Add an instance of the given class (which should be a subclass of the
        EnhancedSnippetBase parent class) to the list snippet variable extension
        objects that are used to expand out our variables.
        """
        self._extensions[extensionClass.__name__] = extensionClass()


    def get(self, ):
        """
        Get the list of currently known snippet variable extension classes.
        """
        return self._extensions.values()


    def get_snippet_enhancements(self, trigger, content):
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
            for enhancer in self.get():
                if enhancer.is_applicable(content):
                    classes.append(enhancer)

        return classes


## ----------------------------------------------------------------------------


# Instantiate our single instance
enhancements = EnhancementManager()