# Introduction #

EnhancedSnippets is a package for Sublime Text 4 that extends and enhances the
Snippet System in Sublime Text to include:

- A new `.enhanced-sublime-snippet` file type that is a text file with YAML
  front matter instead of an XML file
- Snippets can be made available not only by `scope` but also by `glob` (i.e.
  only if the file name matches a specific format), or optionally both at once
- The ability to add your own variables to snippets, such as `$DATE`,
  `$BUZZWORD` and `$CLIPBOARD` (all included by default)
- Snippet fields can be given a list of options, for which you will be prompted
  to select a value when the snippet expands.

![Demo Video](/_images/EnhancedSnippetsDemo.gif)

```yaml
---
tabTrigger: 'wind'
scope: 'text.html - (meta.tag | meta.character.less-than) - source.php'
description: 'Windstorm HTML Template'
options:
  - field: 2
    placeholder: 'Windstorm Version Number'
    values:
      - '0.3.8'
      - 'latest'
---
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$1</title>
</head>
<body>
  <!-- Docs: https://windstorm.axel669.net/ -->
  <script src="https://cdn.jsdelivr.net/npm/@axel669/windstorm@${2:latest}/dist/browser.js"></script>

  $0
</body>
</html>
```


# Installation #

## Package Control ##

The best way to install the package is via PackageControl, as this will take
care of ensuring that the package is kept up to date without your having to do
anything at all.

You can install via Package Control by opening the Command Palette and
selecting the command `Package Control: Install Package` and searching for
`EnhancedSnippets` in the list of packages.



## Manual Installation ##

In order to manually install the package, clone the repository into your
Sublime Text `Packages` directory. You can locate this directory by choosing
`Preferences > Browse Packages...` from the menu.

Manual installation is not recommended for most users, as in this case you are
responsible for manually keeping everything up to date. You should only use
manual installation if you have a very compelling reason to do so and are
familiar enough with the process to know how to do it properly.


# In a Nutshell #

`EnhancedSnippets` adds support for a new snippet file extension,
`enhanced-sublime-snippet`; this is a text file with YAML front matter to help
create snippets in an easier to read way. ***EnhancedSnippets will only load
and recognize files of the `enhanced-sublime-snippet` extension!***

Once created, `enhanced-sublime-snippet` files are automatically loaded when
Sublime starts, reloaded when they are changed, and will be loaded and unloaded
from third party packages as well (if that package has any defined).

Enhanced snippets will be available via autocomplete, added to the command
palette (although they will not show their tab triggers the way that a native
snippet can, currently), and can be used in key bindings and menu entries via
the `insert_enhanced_snippet` command, which is a drop in placement for the
built in `insert_snippet` command.

In addition to the properties that a normal snippet has, an enhanced snippet
has the following extra capabilities; examples of all of these are outlined in
the following section.

 - You can include a `glob` key to constrain the snippet only to files that
   match the glob;  this can be used instead of, or in addition to, the normal
   `scope` key.
 - Numeric snippet fields can optionally include a list of multiple choice
   options; while tabbing through the snippet fields, landing on a field with
   options will display a list of the available options for you to choose from
 - There is an API that allows for the creation of new snippet variables; such
   variables are available any time the snippet expands, including when
   triggered via AutoComplete. Out of the box, the `$DATE`, `$CLIPBOARD` and
   `$BUZZWORD` variables are available.


For more detailed documentation on the package, please consult the
[official documentation site](https://enhancedsnippets.odatnurd.net).