import sublime

import sys
import importlib

from collections import namedtuple
from traceback import print_tb

from .enhancements import install_builtin_enhancements, EnhancedSnippetBase
from .utils import log

from importlib import import_module


## ----------------------------------------------------------------------------


# This named tuple reprents the information for a snippet enhancement variable
# and tracks the name of the variable, the name of the module that it's defined
# in, and the instance of the class to be used during expansions.
SnippetVariable = namedtuple('SnippetVariable', [
    'name', 'module', 'instance'
])


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


# Theory:
#   - If we store enhancements with a key that includes their module and their
#     package, there is no chance of collision except when a person does
#     something dumb, and we already assume that we need to silently replace
#     due to reloading.
#
#   - If we store enhancements with a key that includes the package, we can
#     easily look them up to discard the if needed.
#
# TODO:
#   - [x] store enhancement classes as "PKG.MODULE.CLASS" instead of "CLASS"
#      - Allow clobbers silently because it must means a reload
#
#   - [ ] Store a list of variables and point it at the class that represents
#         it. If a new class uses the same variable, then display a warning and
#         clobber over. In this case
#
#   - [ ] Provide the ability to remove all enhancements based on the class.
#         It has to keep all storage up to date, including the list of variables
#         since some of the are going away.
#
#   - [ ] Tie the removal code to the setings listener, so that when a pacakge
#         goes away we can drop its stuff.
#
#  REMEMBER: Except at startup, any change to the list of extensions requires
#            that all snippets be rescanned. This probably means that for
#            ultimate coolness we need to store for each snippet the variables
#            that it requires so that we know which snippets to tweak when
#            things change.
#

class EnhancementManager():
    """
    Instances of this class are responsible for keeping track of the classes
    that give us our enhanced snippet variables. The keys are the name of the
    enhancement class as a string and the value is an instance of the class
    for use at runtime.
    """
    # In this object, the key is the name of a snippet field and the value is
    # a SnippetVariable that gives the details about that particular field.
    _fields = {}

    # In this object, the key is the fully qualified module name of the class
    # that represents a snippet variable and the value is a SnippetVariable
    # that provides details about that particular field.
    _modules = {}

    def __init__(self):
        self.scan_for_enhancements()


    def add(self, extensionClass):
        """
        Add an instance of the given class (which should be a subclass of the
        EnhancedSnippetBase parent class) to the list snippet variable extension
        objects that are used to expand out our variables.
        """
        module = f'{extensionClass.__module__}.{extensionClass.__name__}'
        try:
            instance = extensionClass()
            entry = SnippetVariable(instance.variable_name(), module, instance)

            # Check to see if this field exists in the list or not; if it does
            # it must come from the same module as this one, or we need to
            # get rid of it.
            existing = self._fields.get(entry.name)
            if existing and existing.module != entry.module:
                log(f'found reimplementation of enhancement {entry.name}')
                del self._fields[entry.name]
                del self._modules[entry.module]

            # Store the entry cross referenced by field name and by module
            # name.
            self._fields[entry.name] = entry
            self._modules[entry.module] = entry

        except Exception as error:
            log(f'Unable to load enhancements from {module}: {str(error)}')
            print_tb(error.__traceback__)


    def get_variable_classes(self, field_names):
        """
        Given an array of field names, return back an array of all of the
        class instances that can be used to expand out those variables at
        runtime.
        """
        result = []
        for field in field_names:
            value = self._fields.get(field, None)
            if value is not None:
                result.append(value.instance)

        return result


    def scan_for_enhancements(self, pkg_name=None):
        """
        Scan for all of the possible snippet enhancement plugins and install
        them, optionally constrained to only the package named. This includes
        installation of the enhancements that are pre installed as a part of
        this package, if there is no package name given.
        """
        if pkg_name is not None:
            self.discard_from_package(pkg_name)
            log(f'recanning enhancements in {pkg_name}')
        else:
            self._fields = {}
            self._modules = {}

        self.__install_enhancements(pkg_name)


    def discard_from_package(self, pkg_name):
        """
        Given the name of a package, find and remove all of the enhancement
        classes that are stored within that particular class.
        """
        log(f'discarding all loaded enhancements from {pkg_name}')

        for module in list(self._modules.keys()):
            # Is this module is from the package we're clobbering?
            if module.startswith(pkg_name):
                entry = self._modules[module]

                # Remove the entry from both tables
                del self._modules[module]
                del self._fields[entry.name]


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


    def __install_enhancements(self, pkg_name=None):
        """
        Scan all existing packages to see if they contain any snippet
        enhancements; if they do, then we want to import them and apply them.
        """
        if pkg_name is None:
            install_builtin_enhancements(self)

        # Look for all packages that advertise enhancements; each should have a
        # specific file that marks them. We want to add if it is the specific
        # package we were told is the one they're in, OR all if we were not
        # given a particular package.
        for res in sublime.find_resources('.enhanced-snippets'):
            pkg = res.split('/')[1]
            if pkg_name is None or pkg_name == pkg:
                self.__add_from_package(pkg, res)


## ----------------------------------------------------------------------------
