import sublime

from collections import namedtuple
import xml.etree.ElementTree as ElementTree

from .utils import log
from .enhancement_manager import enhancements


## ----------------------------------------------------------------------------


# This named tuple is used to represent an enhanced snippet that we've loaded
# in. This contains information on the snippet as a whole, and also includes
# the resource it was loaded from, the package it's contained inside of, and a
# list of the enhancement classes that contribute to its expansion.
Snippet = namedtuple('Snippet', [
    'trigger', 'description', 'content', 'enhancers',
    'scope', 'resource', 'package'
])


## ----------------------------------------------------------------------------


def _get_list(data_dict, key):
    """
    Given a data dictionary, return back the list at the given key; if there is
    no such key, a list will be added before the return.
    """
    if key not in data_dict:
        data_dict[key] = []

    return data_dict[key]


def _filter(res_name, items):
    """
    Given a list of snippets and a resource name, remove from the list any
    snippet which matches that particular resource name, returning back the
    modified list.
    """
    return list(filter(lambda snippet: snippet.resource != res_name, items))


## ----------------------------------------------------------------------------


class SnippetManager():
    """
    Instances of this class are responsible for holding onto the list of all of
    the known snippets that we're extending, and includes API methods that
    allow for querying and updating the list.
    """
    def __init__(self):
        # Start with our data structures empty.
        self.discard_all()


    def discard_all(self):
        """
        Completely discard all known snippets from all of the internal lists;
        this puts everything into a completely clean state.
        """
        log(f'discarding all snippets')

        # These lists are all dictionaries wherein the key is the important bit
        # of distinction (scope selector, package name or full resource path)
        # of snippets that we know about, and the values reprent the matching
        # data.
        #
        # In the case of the scope and package items, the values of the keys
        # are lists, but in the resource list they're single objects (the
        # snippet records) since that is a 1:1 relationship.
        self._scope_list = {}
        self._pkg_list = {}
        self._res_list = {}


    def _discard_snippet_list(self, items):
        """
        Given a list of 0 or more snippet items, remove all snippets in the
        passed in list from all of our internal lists.
        """
        for snippet in [s for s in items if s.resource in self._res_list]:
            log(f'discarding snippet from {snippet.resource}')

            res = snippet.resource
            pkg = snippet.package
            scope = snippet.scope

            # Filter the lists to not include this resource
            self._scope_list[scope] = _filter(res, self._scope_list[scope])
            self._pkg_list[pkg] = _filter(res, self._pkg_list[pkg])

            # If either list ends up empty, that list doesn't need to be in
            # the object any longer.
            if not self._scope_list[scope]:
                del self._scope_list[scope]

            if not self._pkg_list[pkg]:
                del self._pkg_list[pkg]

            # Delete the resource based item last.
            del self._res_list[res]


    def discard_snippet(self, res_name):
        """
        Given a resource name, check to see if this snippet is known to the
        system currently, and if so remove it from all of the internal lists.
        """
        snippet = self._res_list.get(res_name, None)
        self._discard_snippet_list([] if snippet is None else [snippet])


    def discard_scope(self, selector):
        """
        Given a scope selector, remove from all of our internal lists any
        snippet that matches the selector.
        """
        log(f'discarding all snippets matching {selector}')

        result = []
        for scope, snippets in self._scope_list.items():
            if sublime.score_selector(scope, selector):
                result.extend(snippets)

        self._discard_snippet_list(result)


    def discard_pkg(self, pkg_name):
        """
        Given a package name, remove from all of our internal lists all
        snippets contributed by that package.
        """
        log(f'discarding all snippets in package {pkg_name}')

        self._discard_snippet_list(self._pkg_list.get(pkg_name, []))


    def _add_snippet(self, snippet):
        """
        Given a snippet object, add it to the appropriate internal tables,
        replacing any existing item that might already exist with the same
        resource name.
        """
        log(f'adding snippet from {snippet.resource}')
        self._res_list[snippet.resource] = snippet
        _get_list(self._scope_list, snippet.scope).append(snippet)
        _get_list(self._pkg_list, snippet.package).append(snippet)


    def __scan_snippets(self, prefix=''):
        """
        Find and scan all snippets that are known to the package system and
        whose resource names start with the prefix given. Each found snippet is
        loaded and, if it is enhanced, returned back for us to add to the
        manager.
        """
        # Scan over all snippets, load them, and for any that return a Snippet
        # instance, add them to the appropriate lists.
        res = sublime.find_resources('*.sublime-snippet')
        for entry in [r for r in res if r.startswith(prefix)]:
            snippet = self._load_snippet(entry)
            if snippet:
                self._add_snippet(snippet)


    def scan(self):
        """
        Discard all of our lists of snippets and do a complete and total rescan
        of the entire package ecosytem.
        """
        self.discard_all()
        self.__scan_snippets()


    def scan_pkg(self, pkg_name):
        """
        Given the name of a package, discard all of the snippets that are known
        to be in that package (from all of the internal lists), and then do a
        fresh scan of snippets that exist in that path and re-add them.
        """
        self.discard_pkg(pkg_name)
        self.__scan_snippets(f"Packages/{pkg_name}/")


    def matching_scope(self, selector):
        """
        Given a scope selector, return back a list of all of the snippets that
        match this particular selector. This list may be empty.
        """
        result = []
        for scope, snippets in self._scope_list.items():
            if sublime.score_selector(scope, selector):
                result.append(snippets)

        return result;


    def match_view(self, view, locations):
        """
        Given a view and a list of locations, return back all snippets that
        match the scope in the current view at the given locations; this list
        may be empty.

        In order to be returned back, the scope of a snippet must match at all
        of the positions in the locations list.
        """
        result = []

        for scope, snippets in self._scope_list.items():
            if all([view.match_selector(pt, scope) for pt in locations]):
                result.extend(snippets)

        return result


    def matching_pkg(self, pkg_name):
        """
        Given a package name, return back a lsit of all of the snippets that
        are being contributed by that particular package. This list may be
        empty.
        """
        return self._pkg_list.get(pkg_name, [])


    def matching(self, res_name):
        """
        Given a resource specification, return back either the snippet record
        for the snippet matching that resource, or None if there is no such
        snippet known currently.
        """
        return self._res_list.get(res_name, None)


    def _load_snippet(self, res_name):
        """
        Given a package resource, attempt to load it as a snippet. If this
        works, we will return back a Snippet instance that wraps the data in
        this snippet; otherwise this will return None, including on errors
        (which will be logged to the console).
        """
        try:
            # Load the contents of the snippet as a string, then parse it
            xml = sublime.load_resource(res_name)
            root = ElementTree.fromstring(xml)

            # Look up the nodes for the snippet parts we're interested in;
            # these return nodes, which might be None (e.g. if there is no
            # description).
            trigger = root.find('tabTrigger')
            description = root.find('description')
            content = root.find('content')
            scope = root.find('scope')

            # Get the string content of each of the snippet parts, backfilling
            # with empty strings for any missing nodes.
            trigger = '' if trigger is None else trigger.text
            description = '' if description is None else description.text
            content = '' if content is None else content.text
            scope = '' if scope is None else scope.text

            # Get the list of potential enhancements that we can make to this
            # snippet, which is based on the snippet content itself. If there
            # are not any, then we can just leave.
            enhancers = enhancements.get_snippet_enhancements(trigger, content)
            if not enhancers:
                return None

            # Get the package name that this resource is in, and then return
            # back an appropriate instance.
            pkg_name = res_name.split('/')[1]
            return Snippet(trigger, description, content.lstrip(), enhancers,
                scope, res_name, pkg_name)

        except Exception as err:
            log(f"Error loading snippet: {err}")


## ----------------------------------------------------------------------------


# Instantiate our single instance
manager = SnippetManager()