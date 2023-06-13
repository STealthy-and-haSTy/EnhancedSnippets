import sublime

from collections import namedtuple
import re

from EnhancedSnippets import frontmatter


## ----------------------------------------------------------------------------


# This named tuple is used to represent an enhanced snippet that we've loaded
# in. This contains information on the snippet as a whole, and also includes
# the core snippet properties, the resource it was loaded from, the package
# it's contained inside of, the list of variables that need to be expanded and
# the numeric field list.
Snippet = namedtuple('Snippet', [
    'trigger', 'description', 'content', 'variables', 'fields', 'options',
    'scope', 'glob', 'resource', 'package'
])

# The regex that matches a variable in a snippet; this doesn't validate that
# the variable is fully valid, only that it appears to be a variable name.
_var_regex = re.compile(r"(?:^|[^\\])\$\{?(\w+)")

# The regex that matches a numeric field in a snippet; validate that the field
# is fully valid, only that it appears to be a numeric field.
_field_regex = re.compile(r"(?:^|[^\\])\$\{?(\d+)")


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


def debug(message, *args, status=False, dialog=False):
    """
    Generate a debug log; this is functionally identical to the log method
    except that it will only generate output if debugging is turned on.
    """
    from ..src.core import es_setting
    if es_setting('debug'):
        log(message, *args, status=status, dialog=dialog)


## ----------------------------------------------------------------------------


def _yaml_field_options(raw):
    """
    Given the raw options value from the frontmatter section of a yaml
    formatted snippet, return back an appropriate options object to be used as
    a part of the snippet expansion.

    This can handle getting None as an argument, in which case it is assumed
    that there are no options.

    This expects a form like:

    options:
      - field: 1
        placeholder: 'text goes here'
        values:
          - 'value 1'
          - text: 'value 2'
            details: 'the details on this item'

    The items specified in the values array can be either single strings, or
    objects that provide text and optional details. Items that are just strings
    are inferred t be objects that contain text but no details.

    When provided, the details are used in the panel to describe the item when
    the list is offered. It is valid to provide no details.
    """
    raw = raw or []
    result = {}

    for option in raw:
        # Pull out the values that we will be needing
        field = option.get('field')
        placeholder = option.get('placeholder')
        values = option.get('values', [])

        # If any are None, that indicates that this value is not valid.
        if None in (field, placeholder, values):
            raise ValueError(f'Invalid option: {option}')

        # The items in the values list can either be strings, or objects that
        # have a required 'text' key and an optional 'details' key. Iterate
        # through the list and convert to the object format.
        #
        # FINESSE: This should also verify that the values are correctly
        #          formatted.
        values = [{"text": t} if isinstance(t, str) else t for t in values]

        # Put the placeholder into the first position, and then add the field
        # to the result.
        values.insert(0, placeholder or f'Value for field {field}')
        result[str(field)] = values

    return result


## ----------------------------------------------------------------------------


def _do_yaml_load(content):
    """
    Given the content of a resource that is expected to be a snippet, parse
    it as a text document with YAML front matter to see if it conforms to
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
            'options': _yaml_field_options(data.get('options'))
        }

    except Exception:
        pass


def _get_variables(content):
    """
    Return a list of all of the unique textual variables that are contained in
    the snippet content; the list contains both built in as well as user
    defined variables.
    """
    result = set()
    for match in _var_regex.finditer(content):
        result.add(match.group(1))

    return list(result)


def _get_fields(content):
    """
    Given the content of a snippet, return back an array of all of the numeric
    fields that are present in it, in ascending order.

    The result always has a "0" entry, and it's always at the end of the list
    returned (i.e. it is in field order for expansion, not sorted order)
    """
    result = set()
    for match in _field_regex.finditer(content):
        result.add(int(match.group(1)))

    # We always want a 0 element, but it needs to be last, so remove it from
    # the set if it happens to be present.
    if 0 in result:
        result.remove(0)

    result = sorted(result)
    result.append(0)

    return [str(field) for field in result]


def load_snippet(res_or_content, scope='', glob='', is_resource=True):
    """
    Given either the resource of a snippet OR some inline snippet content,
    parse it out to obtain a Snippet instance which will be returned back.

    This will raise an exception on failure, such as being given a file that is
    not a valid snippet file.
    """
    if is_resource:
        pkg_name = res_or_content.split('/')[1]
        resource = res_or_content

        # Load the contents of the snippet as a string, then parse it as a
        # YAML snippet.
        data = sublime.load_resource(res_or_content)
        raw = _do_yaml_load(data)
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
            'scope': scope,
            'glob': glob,
            # NOTE: This triggers for provided content; we should probably
            #       allow options to be provided this way or something so
            #       someone can trigger the command with options?
            'options': {}
        }

    # Get the list of variables and numeric fields from this snippet
    variables = _get_variables(raw['content'])
    fields = _get_fields(raw['content'])

    # Get the package name that this resource is in and create a new
    # instance.
    return Snippet(raw['tabTrigger'], raw['description'],
        raw['content'].lstrip(), variables, fields, raw['options'],
        raw['scope'], raw['glob'], resource, pkg_name)


def snippet_expansion_args(snippet, manager, extra_args):
    """
    Given a loaded snippet and a dictionary with any extra variable arguments
    that should be expanded in addition to the built in variables and those
    that are enhancements, return a dictionary which, when passed as the
    arguments to insert_snippet, which insert that snippet in with all of the
    custom variables (that are known) properly expanded out
    """
    # Get the list of classes that are used to expand out the custom
    # variables in this snippet.
    enhancers = manager.get_variable_classes(snippet.variables)

    # Construct the arguments that are going to be passed to the snippet
    # command when the completion invokes.
    #
    # As we loop through, we adjust the content that is passed to
    # subsequent handlers, since we may need to rewrite the snippet content
    # in order to implement some variables.
    snippet_args = dict(extra_args)
    content = snippet.content
    for enhancement in enhancers:
        new_vars, content = enhancement.variables(content)
        snippet_args.update(new_vars)

    # Include the adjusted content into the arguments so that we can
    # expand it.
    snippet_args['contents'] = content.lstrip()

    return snippet_args


## ----------------------------------------------------------------------------


def prepare_snippet_info(view, fields, options):
    """
    Given a view, a list of fields, and options for those fields, update the
    tracking information in the current view to know that is the snippet that
    is about to be expanded.

    fields is a list of all of the numeric fields as strings (e.g. "1", "2"")
    which must be in numeric order, except for "0", which must always be
    present and always be at the end.

    options is a dictionary whose keys are field numbers and whose values are
    arrays that list the options; the first item in the array is the
    placeholder that explains what the field is for, and the remainder of the
    items are the options to pick from.

    If this view has any tracking information for a snippet (including any
    regions from a previous call), they will be removed prior to the new data
    being set in.
    """
    clear_snippet_info(view)

    view.settings().set('_es_cache', {
        'fields': fields,
        'options': options,
        'current_field_idx': 0
    })


def clear_snippet_info(view):
    """
    Clear from the passed in view all tracking information about an enhanced
    snippet that is being expanded out.

    This will remove the tracking regions along with the setting that tracks
    the snippet details.
    """
    if view.settings().has('_es_cache'):
        fields = view.settings().get('_es_cache').get('fields', [])
        for field in fields:
            view.erase_regions(f'_es_field_{field}')

    view.settings().erase('_es_cache')


def handle_snippet_field_move(view, direction):
    """
    If this view is currently in the process of expanding a special snippet,
    then this function will jump the internal list of fields to point at the
    correct field, and update the object accordingly.

    direction can be:
        1: if we are going to the next field
       -1: if we are going to the previous field
        0: if the field is staying in the same place as it currently is

    Once the move happens, the field is checked to see if it is one of the
    ones that has a special value, and if it is, we will prompt via a quick
    panel for the text to insert.
    """
    data = view.settings().get('_es_cache', None)
    if data is None:
        return

    # TODO: This should bounds check the navigation to make sure that it is
    #       still valid; this should technically never happen because the key
    #       binding context blocks the commands, but they could be run other
    #       ways.
    #
    # Apply the direction to determine what the current field is.
    data["current_field_idx"] = data["current_field_idx"] + direction
    view.settings().set('_es_cache', data)

    # Our picker command requires the selection to be updated, and it might not
    # be if we were executed from a command, so schedule a call for the next
    # loop.
    sublime.set_timeout(lambda: view.run_command('enhanced_snippet_field_picker'))
