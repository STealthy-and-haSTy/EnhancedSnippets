import sublime
import sublime_plugin

import os

from ..core import es_syntax
from Default.new_templates import reformat


## ----------------------------------------------------------------------------


class NewEnhancedSnippetCommand(sublime_plugin.WindowCommand):
    """
    Create a new empty enhanced snippet template, set to store data into an
    appropriate default location for user created snippets.
    """
    def run(self):
        view = self.window.new_file(syntax=es_syntax('EnhancedSnippet'))
        view.settings().set('default_dir', os.path.join(sublime.packages_path(), 'User'))
        view.settings().set('default_extension', 'enhanced-sublime-snippet')

        template = reformat(
            """
            ---
            # Optional: Set a tabTrigger to define how to trigger the snippet
            #tabTrigger: "hello"
            # Optional: Set a scope to limit where the snippet will trigger
            #scope: "source.python"
            # Optional: Set a filename glob to limit where the snippet will trigger
            #glob: "test_*.py"
            # Optional: Set a description for what this snippet does
            #description: "insert sample text"
            options:
              - field: 2
                placeholder: "possible values for field 2"
                values:
                  - "an enhanced snippet"
                  - text: "a second optional value"
                    details: "the second value in the list"
            ---
            Hello, \\${1:this} is \\${2:placeholder}.
            """)
        view.run_command("insert_snippet", {"contents": template})



## ----------------------------------------------------------------------------
