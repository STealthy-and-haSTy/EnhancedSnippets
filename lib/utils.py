import sublime

from collections import namedtuple
import re

from EnhancedSnippets import frontmatter
import xml.etree.ElementTree as ElementTree


## ----------------------------------------------------------------------------


# This named tuple is used to represent an enhanced snippet that we've loaded
# in. This contains information on the snippet as a whole, and also includes
# the resource it was loaded from, the package it's contained inside of, and a
# list of the enhancement classes that contribute to its expansion.
Snippet = namedtuple('Snippet', [
    'trigger', 'description', 'content', 'fields',
    'scope', 'glob', 'resource', 'package'
])

# The regex that matches a variable in a snippet; this doesn't validate that
# the variable is fully valid, only that it appears to be a variable name.
_var_regex = re.compile(r"(?:^|[^\\])\$\{?(\w+)")


## ----------------------------------------------------------------------------


def log(message, *args, status=False, dialog=False):
    """
    Simple logging method; writes to the console and optionally also the status
    message as well.
    """
    message = message % args
    print("EnhancedSnippets:", message)
    if status:
        sublime.status_message(message)
    if dialog:
        sublime.message_dialog(message)


## ----------------------------------------------------------------------------


def _do_xml_load(content):
    """
    Given the content of a resource that is expected to be a snippet, parse
    it as XML and see if it conforms to the appropriate snippet format.

    On success, a dictionary with the keys of the snippet is returned;
    otherwise the return is None
    """
    try:
        # Try to parse the content into XML, and grab out the
        root = ElementTree.fromstring(content)

        # Get the nodes for the items that we're interested in
        trigger = root.find('tabTrigger')
        description = root.find('description')
        content = root.find('content')
        scope = root.find('scope')
        glob = root.find('glob')

        return {
            'tabTrigger': '' if trigger is None else trigger.text,
            'description': '' if description is None else description.text,
            'content': '' if content is None else content.text,
            'scope': '' if scope is None else scope.text,
            'glob': '' if glob is None else glob.text,
        }

    except:
        pass


def _do_yaml_load(content):
    """
    Given the content of a resource that is expected to be a snippet, parse
    it as a text document with YAML frontmatter to see if it conforms to
    that format.

    On success, a dictionary with the keys of the snippet is returned;
    otherwise the return is None
    """
    try:
        data = frontmatter.loads(content)

        return {
            'tabTrigger': data.get('tabTrigger', ''),
            'description': data.get('description', ''),
            'content': data.content or '',
            'scope': data.get('scope', ''),
            'glob': data.get('glob', ''),
        }

    except Exception:
        pass


def load_snippet(res_or_content, is_resource=True):
    """
    Given either the resource of a snippet OR some inline snippet content,
    parse it out to obtain a Snippet instance which will be returned back.

    This will raise an exception on failure, such as being given a file that is
    not a valid snippet file.
    """
    if is_resource:
        pkg_name = res_or_content.split('/')[1]
        resource = res_or_content

        # Load the contents of the snippet as a string, then parse it
        data = sublime.load_resource(res_or_content)

        # Try and load first as XML and then YAML, since we support two
        # different formats
        raw = _do_xml_load(data) or _do_yaml_load(data)
        if raw is None:
            raise ValueError(f'{res_or_content} is not in a recognized format')
    else:
        pkg_name = ''
        resource = ''

        # If we get content, we don't need to load a file, we just have the
        # content directly, but with no other information associated with it.
        raw = {
            'tabTrigger': '',
            'description': '',
            'content': res_or_content,
            'scope': '',
            'glob': '',
        }

    # Get the list of fields from this snippet, which is a list of all
    # of the unique variable names in the snippet, including those that
    # are built in.
    result = set()
    for match in _var_regex.finditer(raw['content']):
        result.add(match.group(1))

    fields = list(result)

    # Get the package name that this resource is in and create a new
    # instance.
    return Snippet(raw['tabTrigger'], raw['description'],
        raw['content'].lstrip(), fields, raw['scope'], raw['glob'],
        resource, pkg_name)


## ----------------------------------------------------------------------------
