# EnhancedSnippets

EnhancedSnippets is a simple package (requiring Sublime Text 4) that extends
and enhances the Snippet system in Sublime Text to include:

- Creating snippets as text files with YAML Frontmatter instead of using XML
- Allowing snippets to be available not only by `scope` but also by `glob` (i.e.
  only if the file name matches a specific format)
- Including the ability to add your own variables to snippets, such as `$DATE`
  and `$CLIPBOARD` (both included by default)
- Allow snippet fields to specify a list of options for possible values, which
  can be selected when the snippet expands.

![Demo Video](https://gist.githubusercontent.com/OdatNurd/7eb659980b758c9f9ee3b5f07b3744f1/raw/f4733df7e8bf9e0f4c865638a6edce0ca60df176/EnhancedSnippetsDemo.gif)

> :warning: At the current time, this package (and this documentation) is still
in an Alpha state; this does not mean that it's not safe but only that it is
still being developed and so some bugs may be present and new features may be
added. Please raise an issue if you run into any problems or have suggestions.

## Installation

This package is not officially a part of Package Control. The recommended (and
supported) way of installing this package is to use `Package Control: Add Repository`
from the command palette, and enter the following URL, then use
`Package Control: Install Package` and select the package from the list:

```
https://raw.githubusercontent.com/STealthy-and-haSTy/SublimePackages/master/unreleased-packages.json
```

> :exclamation: If you have already added this repository URL to access other
packages from this source, you do not need to do this again. If you're not
sure, try to install the package and see if it's visible first. Remember that
packages that are already installed will not appear in the list of available
packages to install.

## In a Nutshell

`EnhancedSnippets` adds support for a new snippet file extension, `enhanced- sublime-snippet`;
this can be in either the standard `XML` file format of regular
`sublime- snippet` files, or you can use a text file with YAML Frontmatter to
create snippets in an easier to read way. ***EnhancedSnippets will only load
and recognize files of the `enhanced-sublime-snippet` extension!***

Once created, any newly added or modified snippets will be available via
autocomplete similar to normal snippets, and they will also be added to the
command palette as well.

In addition to the properties that a normal snippet has, an enhanced snippet
has the following extra capabilities; examples of all of these are outlined in
the following section.

 - Snippets can be defined both as XML and in a plain text format with a YAML
   Frontmatter section; the extension is `enhanced-sublime-snippet` in either
   case. Syntax definitions (currently rudimentary) are available out of the
   box.
 - You can include a `<glob>` tag to constrain the snippet only to files that
   match the glob;  this can be used instead of, or in addition to, the normal
   `<scope>` tag.
 - There is an API that allows for the creation of new snippet variables; such
   variables are available any time the snippet expands, including when
   triggered via AutoComplete. Out of the box, the `$DATE`, `$CLIPBOARD` and
   `$BUZZWORD` variables are available.
 - Numeric snippet fields can optionally include a list of multiple choice
   options; while tabbing through the snippet fields, landing on a field with
   options will display a list of the available options for you to choose from


## Examples

### File Formats

The `enhanced-sublime-snippet` file can be created in the normal `XML` format
of a normal `sublime-snippet`:

```xml
<snippet>
    <description>Lorem ipsum</description>
    <content><![CDATA[Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.]]></content>
    <tabTrigger>lorem</tabTrigger>
    <scope>-source</scope>
</snippet>
```

Or, optionally, as a text file with YAML frontmatter:

```yaml
---
tabTrigger: lorem
scope: -source
description: Lorem ipsum
---
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.]
```

### Glob Extensions

Normal snippets can use the `<scope>` tag to specify a scope that they apply
to. Enhanced Snippets can also include `<glob>` (or `glob:`) to specify a
filename glob which must match the current file in order for the snippet to be
available. This can be used instead of or in addition to the normal `scope`
handling, and allows you to further constrain snippets, such as the declaration
for a unit test, which is only required in certain files.

```xml
<snippet>
    <content><![CDATA[
class ${1:classname}(unittest.TestCase):

    def test_${2:method}(self):
        # Test Body Here
        $0
]]></content>
    <tabTrigger>test</tabTrigger>
    <description>Create unit test</description>
    <scope>source.python</scope>
    <glob>test_*.py</glob>
</snippet>
```

```yaml
---
tabTrigger: test
description: Create unit test
scope: source.python
glob: test_*.py
---
class ${1:classname}(unittest.TestCase):

    def test_${2:method}(self):
        # Test Body Here
        $0
```

### New Variables

`EnhancedSnippets` allows you to declare new variables in plugin code, which
will be made available to all snippets when they expand, including not only
from the command palette or a key binding but also via the AutoComplete panel.

As an out of the box demonstration, three new variables are available in your
snippets:

1. `$DATE`, which expands out to the current date. You can specify a date format
   in the "default text" portion of the snippet variable; see the Python
   documentation on date formatting for options
2. `$CLIPBOARD`, which expands out to the text that is currently on the
   clipboard.
3. `$BUZZWORD`, which expands out to corporate lorem ipsum; You can specify how
   many sentences of ipsum are generated in the "default text" portion of the
   snippet.

Examples of `$DATE` in a snippet:
- `${DATE}` will expand out to the date with a default format
- `${DATE:%Y-%m-%d is the current date}` uses the text in the default value of
  the snippet as the format string, which can also include arbitrary text.

Examples of `$BUZZWORD` in a snippet:
- ${BUZZWORD} will expand out to a single buzzword sentence
- `${BUZZWORD:5}` will expand out to five buzzword sentences

### Snippet Options

Numeric snippet fields can be given a list of optional values. Whenever the
snippet navigation lands on a numeric field with a value, a quick panel will
open to display the list of available options. Choosing an option from the list
will insert that text and immediately jump to the next field. You can also
press `Escape` to close the panel and type your own freeform text.

How you specify the options depends on the file format that you're using:

```xml
    <tabTrigger>wind</tabTrigger>
    <description>Windstorm HTML Template</description>
    <scope>text.html - (meta.tag | meta.characer.less-than) - source.php</scope>
    <options>
        <field>
            <number>2</number>
            <placeholder>Windstorm Version Number</placeholder>
            <values>
                <string>latest</string>
                <string>0.1.9</string>
                <string>0.1.10</string>
            </values>
        </field>
    </options>
```

```yaml
---
tabTrigger: wind
scope: text.html - (meta.tag | meta.characer.less-than) - source.php
description: Windstorm HTML Template
options:
  - field: 2
    placeholder: 'Windstorm Version Number'
    values:
      - latest
      - 0.1.9
      - 0.1.10
---
```

## Adding New Variables

This is not currently fully documented, but in a nutshell, in the package in
which you would like to include variables:

- Ensure that you have a `.python-version` file in the top level of the package
  with the content `3.8`; it is untested (and likely not supported) to try and
  load extensions from the legacy plugin host.
- Include an `.enhanced-snippets` file in your package. This file specifies the
  name of a module within the package which should be loaded in order to load
  the extensions. The content of the file is either the name of a module within
  your package (e.g. `my_vars`) or nothing at all, in which case the name of
  the module is assumed to be `snippet_enhancers`.
- Ensure that your package has the appropriate module (in the examples above,
  either `my_vars.py` or `snippet_enhancers.py` in the top level of the
  package).

Every time enhancements are loaded (which, roughly speaking, is when
`EnhancedSnippets` loads, you use the `Refresh Enhancements Cache` command from
the command palette, or a new package is installed) the module declared in the
file will be loaded, and all classes in the module that are subclasses of
`EnhancedSnippetBase` are loaded and used to provide variables.

> :warning: The module is only loaded, not force reloaded; if you modify the
implementation of the plugin at runtime, it is up to you to ensure that it is
fully reloaded before you tell EnhancedSnippets to refresh the cache.

An example of a module that adds variables:

```python
import sublime
import sublime_plugin

from EnhancedSnippets.lib import EnhancedSnippetBase


class LordFokasSnippet(EnhancedSnippetBase):
    def variable_name(self):
        return 'FOKAS'

    def variables(self, content):
        return {
            'FOKAS': 'The lord of us all'
        }, content


class AxelSnippet(EnhancedSnippetBase):
    def variable_name(self):
        return 'AXEL'

    def variables(self, content):
        return {
            'AXEL': 'Has the biggest brain of us all'
        }, content

```

- `variable_name` should return the name of the variable that your extension
  supports; this is used by the package to recognize which handlers apply to
  which snippet.

- `variables` gets the snippet content and is expected to return back a list of
  variables to expand out and their values, as well as the snippet content that
  should be used during the expansion. This allows your handler to modify the
  content of the incoming snippet in case you need to use more than one variable
  as a part of your expansion.

For more details an examples, see the source code in `lib/enhancements`.