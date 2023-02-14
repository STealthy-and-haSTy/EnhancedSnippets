import sublime

import os
import functools
from fnmatch import fnmatch

from .utils import log, debug, load_snippet


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

    This class is treated as a singleton; all of the useful methods are class
    methods that track the internal instance so you don't have to.
    """
    instance = None
    pending_write = 0

    def __init__(self, listener, enhancements):
        if SnippetManager.instance is not None:
            return

        SnippetManager.instance = self
        self.enhancements = enhancements

        # Start with our data structures empty.
        self.discard_all(quiet=True)

        # Listen for settings changing, so we know when we need to drop or scan
        # for snippets.
        listener.add_listener(lambda a,r: self._settings_change(a, r))

        # Now that setup is complete, scan for all enhanched snippets across
        # all packages.
        self.scan()


    def _settings_change(self, added, removed):
        """
        This gets invoked whenever the list of ignored packages changes, to
        tell us which packages were added to the setting and which were removed
        from it.
        """
        debug(f"ignored packages => added: {str(added)} removed: {str(removed)}")

        def perform_package_reload():
            for pkg in added:
                self.discard_pkg(pkg)
                self.enhancements.discard_from_package(pkg)

            for pkg in removed:
                self.scan_pkg(pkg)
                self.enhancements.scan_for_enhancements(pkg)

        # Defer the reload operation briefly to give the file catalog a chance
        # to update; otherwise we won't be able to find the key file in
        # packages that contain enhancements (when adding).
        sublime.set_timeout(perform_package_reload, 1000)


    def rewrite_commands_file(self):
        """
        When invoked, this will schedule a generation of a sublime-commands
        file that will contain calls to our enhanced snippet insertion command
        for each of the currently known enhanced snippets.

        This uses a debounce so that if it is called multiple times in quick
        sucession the write will only happen once.
        """
        self.pending_write += 1
        sublime.set_timeout_async(functools.partial(self.__generate_commands_file), 500)


    def __generate_commands_file(self):
        """
        Iterates over all of the currently known and loaded snippets and
        generates out a sublime-commands file that contains an entry for them.

        This uses a debounce and should not be called directly; use the
        rewrite_commands_file() function instead to schedule the write.
        """
        self.pending_write -= 1
        if self.pending_write != 0:
            return

        def prepare(snippet):
            # The title is either the description or, if there is not one,
            # the name of the file without an extension.
            title = snippet.description
            if not title:
                # This is always safe because package resources are always
                # posix paths, and they will always have an extension.
                title = snippet.resource.split('/')[-1].split('.')[0]

            return {
                'caption': f'Snippet: {title}',
                'command': 'insert_enhanced_snippet',
                'args': {
                    'name': snippet.resource
                }
            }

        # Create the JSON structure of the sublime-commands file from the list
        # of snippets that are currently loaded; If that is empty, then we can
        # just leave.
        data = [prepare(snippet) for snippet in self._res_list.values()]
        if not data:
            return

        # Get our package name, then use it to construct a filename at which
        # to store our commands file.
        pkg_name = __name__.split('.')[0]
        file_folder = os.path.join(sublime.cache_path(), pkg_name)
        filename = os.path.join(file_folder, 'UserSnippets.sublime-commands')

        # Ensure that the folder we're about to put a file in exists;
        # potentially on an initial install the plugin will load prior to the
        # cache folder being set up to store the syntax cache, in which case
        # the below would fail.
        os.makedirs(file_folder, mode=0o777, exist_ok=True)

        debug(f'Writing {len(data)} entries to {filename}')
        with open(filename, 'wt') as file:
            file.write(sublime.encode_value(data, True))


    def discard_all(self, quiet=False):
        """
        Completely discard all known snippets from all of the internal lists;
        this puts everything into a completely clean state.
        """
        if not quiet:
            debug(f'discarding all snippets')

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
        discarded = 0
        for snippet in [s for s in items if s.resource in self._res_list]:
            discarded += 1
            debug(f'discarding: {snippet.resource}')

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

        # If we discarded any snippets, recreate the commands file so that
        # they will no longer be presented.
        if discarded:
            self.rewrite_commands_file()


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
        log(f"discarding all snippets matching '{selector}'")

        result = []
        for scope, snippets in self._scope_list.items():
            if sublime.score_selector(scope, selector):
                result.extend(snippets)

        self._discard_snippet_list(result)


    def discard_pkg(self, pkg_name, quiet=False):
        """
        Given a package name, remove from all of our internal lists all
        snippets contributed by that package.
        """
        if not quiet:
            log(f"discarding all snippets in package '{pkg_name}'")

        self._discard_snippet_list(self._pkg_list.get(pkg_name, []))


    def reload_snippet(self, res_name):
        """
        Given a snippet resource file, drop any version of that snippet that
        we might have, then check to see if that is an enhanced snippet and
        if so update the lists.

        This can be used to both add a brand new snippet as well as to update
        an existing one.
        """
        self.discard_snippet(res_name)
        self._load_snippet(res_name)

        # Since we reloaded a snippet, regenerate the commands file so that
        # any details changes that might be externally visible will take
        # effect.
        self.rewrite_commands_file()


    def snippet_for_resource(self, res_name):
        """
        Given the name of a snippet resource, return back the snippet object
        that is associated with it, or None if there is no such snippet known.
        """
        return self._res_list.get(res_name, None)


    def __scan_snippets(self, prefix=''):
        """
        Find and scan all snippets that are known to the package system and
        whose resource names start with the prefix given. Each found snippet is
        loaded and, if it is enhanced, returned back for us to add to the
        manager.
        """
        # Scan over all snippets, load them, and for any that return a Snippet
        # instance, add them to the appropriate lists.
        res = sublime.find_resources('*.enhanced-sublime-snippet')
        for entry in [r for r in res if r.startswith(prefix)]:
            self._load_snippet(entry)

        # After a full scan, regenerate the commands file to ensure that all
        # snippets that were found as a part of the scan are updated.
        self.rewrite_commands_file()


    def reload_enhancements(self):
        """
        Ask the snippet enhancements module to force scan and reload all of
        the modules that provide enhancements.
        """
        self.enhancements.scan_for_enhancements()


    def scan(self):
        """
        Discard all of our lists of snippets and do a complete and total rescan
        of the entire package ecosytem.
        """
        log('scanning for enhanced snippets across all packages')
        self.discard_all(quiet=True)
        self.__scan_snippets()


    def scan_pkg(self, pkg_name):
        """
        Given the name of a package, discard all of the snippets that are known
        to be in that package (from all of the internal lists), and then do a
        fresh scan of snippets that exist in that path and re-add them.
        """
        log(f"scanning for enhanced snippets in package '{pkg_name}'")
        self.discard_pkg(pkg_name, quiet=True)
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


    def glob_match(self, view, snippet):
        """
        Given a view and a snippet, return True or False to indicate whether
        the name of this file matches the snippet glob.

        Snippet with no glob always match; if there is a glob, then the file
        must match, which means that views with no filename can't possibly be
        a match.
        """
        if snippet.glob == '':
            return True

        if view.file_name() is None:
            return False

        return fnmatch(view.file_name(), snippet.glob)


    def scope_match(self, view, locations, snippet):
        """
        Given a view, locations in the view, and a snippet, return True or
        False to indicate whether this snippet applies to this scope.

        Snippets with no scope always match; if there is a scope then it must
        match every location in the view in order for this to be a match.
        """
        if snippet.scope == '':
            return True

        return all([view.match_selector(pt, snippet.scope) for pt in locations])


    def snippet_applies(self, snippet, view, locations):
        """
        Given a snippet, a view, and locations within that view, return back
        an indication of whether this snippet applies to this particular view
        or not.
        """
        return (self.glob_match(view, snippet) and
                self.scope_match(view, locations, snippet))


    def get_variable_classes(self, field_names):
        """
        Given an array of field names, return back an array of all of the
        class instances that can be used to expand out those variables at
        runtime.
        """
        return self.enhancements.get_variable_classes(field_names)


    def match_view(self, view, locations):
        """
        Given a view and a list of locations, return back all snippets that
        match the scope in the current view at the given locations; this list
        may be empty.

        In order to be returned back, the scope of a snippet must match at all
        of the positions in the locations list.
        """
        result = []

        # Grab the filename for this view (if any) and then iterate over all
        # snippets to find the ones that match in the current situation, whicn
        # is a combination of glob and scope.
        filename = view.file_name() or ''
        for snippet in self._res_list.values():
            if self.snippet_applies(snippet, view, locations):
                result.append(snippet)

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
            # Try to load in the snippet resource; this can be in one of two
            # different formats
            snippet = load_snippet(res_name, is_resource=True)

            # Link the snippet into our tables, then return
            debug(f'adding snippet: {snippet.resource}')
            self._res_list[snippet.resource] = snippet
            _get_list(self._scope_list, snippet.scope).append(snippet)
            _get_list(self._pkg_list, snippet.package).append(snippet)

            return snippet

        except Exception as err:
            log(f"Error loading snippet: {err}")


## ----------------------------------------------------------------------------
