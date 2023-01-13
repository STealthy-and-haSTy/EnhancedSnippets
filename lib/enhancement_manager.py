import sublime

import sys
import importlib

from .enhancements import install_builtin_enhancements, EnhancedSnippetBase
from .utils import log

from importlib import import_module


## ----------------------------------------------------------------------------


# When scans happen looking for enhancements, a package resource of this name
# is searched for; any package that contains one is scanned for enhancement
# classes.
_ENHANCEMENT_TRIGGER_FILE = '.enhanced-snippets'

# Any module that declares that it has snippet expansions in it must contain a
# module that tells us what module to get the enhancements in that package
# from. To do that, the trigger file's first line should be the name of the
# module to load. If that file is empty, then this is the default module name
# to use instead.
#
# Regardless of the module, if the enhancement loader notices that this module
# has been loaded before, it will cause a reload in order to make sure it's up
# to date, since the base class may have changed since it was first loaded.
_ENHANCEMENT_MODULE = 'snippet_enhancers'


## ----------------------------------------------------------------------------


class EnhancementManager():
    """
    Instances of this class are responsible for keeping track of the classes
    that give us our enhanced snippet variables.
    """
    _extensions = {}

    def __init__(self):
        self.scan_for_enhancements()


    def add(self, extensionClass):
        """
        Add an instance of the given class (which should be a subclass of the
        EnhancedSnippetBase parent class) to the list snippet variable extension
        objects that are used to expand out our variables.
        """
        self._extensions[extensionClass.__name__] = extensionClass()


    def get(self):
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


    def scan_for_enhancements(self):
        """
        Scan for all of the possible snippet enhancement plugins and install
        them. This includes installation of the enhancements that are pre
        installed as a part of this package.
        """
        self._extensions = {}
        self.__install_enhancements()


    def __add_from_package(self, pkg, res):
        try:
            log(f'Loading extensions from {pkg}')

            # Load the resource to see what module we should be importing; if
            # there is not one, assume it is named `snippet_enhancements`.
            module_name = _ENHANCEMENT_MODULE

            # Load the first line from the resource file; if it has any content
            # in it, then it is the name of the plugin that has the entry point
            # that we need.
            data = sublime.load_resource(res)
            pos = list(filter(lambda x: x > 0, [data.find(c) for c in ('\r', '\n')]))
            pos.append(len(data))

            # Create an appropriate module name to use
            module_name = f'{pkg}.{data[:min(pos)]}'

            # If this module was previously loaded before, then trigger a
            # reload so that any references it has to our code get refreshed.
            if module_name in sys.modules:
                log(f'{module_name} was loaded before; reloading')
                importlib.reload(sys.modules[module_name])

            # Get at the module that contains the enhancements, if any; this
            # could raise an exception if the module is missing.
            module = import_module(module_name)

            # Extract all subclasses of the enhancement base class and add them
            # to the list; this needs to skip over attributes that aren't
            # classes and must also skip the base class, which may also be
            # exported.
            for attr in dir(module):
                symbol = getattr(module, attr)
                if (not isinstance(symbol, type) or
                    symbol == EnhancedSnippetBase):
                    continue

                if issubclass(symbol, EnhancedSnippetBase):
                    self.add(symbol)

        except ModuleNotFoundError:
            log(f'module {module_name} does not exist; cannot load enhancements from it')

        except Exception as error:
            log(f'Unable to load enhancements from {pkg}: {str(error)}')


    def __install_enhancements(self):
        """
        Scan all existing packages to see if they contain any snippet
        enhancements; if they do, then we want to import them and apply them.
        """
        install_builtin_enhancements(self)

        # Look for all packages that advertise enhancements; each should have a
        # specific file that marks them.
        for res in sublime.find_resources('.enhanced-snippets'):
            pkg = res.split('/')[1]
            self.__add_from_package(pkg, res)


## ----------------------------------------------------------------------------
