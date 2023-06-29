import sublime
import sublime_plugin

import os
from re import compile

from ..core import es_syntax
from ...lib import load_legacy_snippet, SnippetHandler

from EnhancedSnippets import frontmatter


## ----------------------------------------------------------------------------


# A simple regex that can determine if a string appears to be a snippet.
_is_snippet = compile(r"\s*<snippet>")


## ----------------------------------------------------------------------------


class ConvertToEnhancedSnippetCommand(sublime_plugin.TextCommand):
    """
    If the current file is a standard Sublime Snippet file (or appears to be
    one), this command will load the file content/unsaved view data, convert
    the snippet into a YAML front matter version, and create a new buffer that
    contains the enhanced snippet version.
    """
    def run(self, edit, hide_when_disabled=True):
        view = self.view
        name = view.file_name()

        # We can only be executed if we're enabled, and we're only enabled when
        # the view is a file or is an unsaved buffer with what appearsto be a
        # snippet. So, determine which.
        is_file = bool(name is not None)
        content = name if is_file else view.substr(sublime.Region(0, len(view)))

        # Get the snippet content; if this throws an exception, this snippet
        # cannot be converted for some reason; display an error dialog and
        # leave.
        try:
            snippet = load_legacy_snippet(content, is_file=is_file)
        except Exception as error:
            return sublime.error_message(str(error))

        # Convert the content of the snippet and the metadata into the new
        # enhanced snippet format.
        post = frontmatter.Post(snippet.content, handler=SnippetHandler(),
                    tabTrigger=snippet.trigger,
                    scope=snippet.scope,
                    description=snippet.description
                )

        # Create the view that will hold the snippet data, then insert the
        # new snippet into it.
        #
        # This sets up settings to ensure that Sublime offers the appropriate
        # extension and folder by default.
        view = self.view.window().new_file(syntax=es_syntax('EnhancedSnippet'))
        view.settings().set('default_dir', os.path.join(sublime.packages_path(), 'User'))
        view.settings().set('default_extension', 'enhanced-sublime-snippet')

        view.run_command('append', {'characters': frontmatter.dumps(post)})

    def description(self, hide_when_disabled=True):
        name = self.view.file_name() or self.view.name() or "unknown"
        return f"Create enhanced snippet from '{os.path.basename(name)}'"

    def is_enabled(self, hide_when_disabled=True):
        # If there is a filename on the buffer, enable the command if this is
        # a snippet file.
        if self.view.file_name():
            return self.view.file_name().endswith('.sublime-snippet')

        # If there is no filename, this is a snippet if it appears to have
        # snippet content in it.
        return bool(_is_snippet.match(self.view.substr(sublime.Region(0, 80))))

    def is_visible(self, hide_when_disabled=True):
        if not hide_when_disabled:
            return True

        return self.is_enabled()


## ----------------------------------------------------------------------------
