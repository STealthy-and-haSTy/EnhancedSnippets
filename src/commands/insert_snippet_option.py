import sublime
import sublime_plugin

from ...lib import handle_snippet_field_move


## ----------------------------------------------------------------------------


# FINESSE: This command will allow you to trigger options for what it thinks
#          the current field is even if the snippet is not expanding since we
#          don't know how to capture all possible ways that a snippet can be
#          exited. Make sure it's not exposed.
#
# FINESSE: This should add in visible regions at the cursor positions so that
#          it is possible to know where the insert is going to happen.
class InsertEnhancedSnippetOptionCommand(sublime_plugin.TextCommand):
    """
    Given a field number in the snippet that is currently expanding, a list of
    options to pick from and the placeholder for the items, display a quick
    panel to allow the user to pick from the available options.
    """
    def run(self, edit, field, placeholder, options):
        def insert(idx):
            # Regardless of choice, remove the region markers.
            self.view.erase_regions('_es_cursors')

            if idx != -1:
                # Insert the selected text in and ensure that the text that was
                # inserted has a field based region so that we can get back to
                # it later.
                self.view.run_command('enhanced_snippet_insert_and_mark', {
                    'field': field,
                    'characters': options[idx]
                })

                # If this is not the last field, skip to the next one; because
                # we're invoking the command ourselves in response to something
                # else, the event listener won't pick it up, so handle the move
                # directly ourselves.
                if field != '0':
                    self.view.run_command('next_field')
                    handle_snippet_field_move(self.view, 1)

        # If there are any regions associated with this field, then use them to
        # replace the selection so that if the user picks an option, the value
        # that is currently in place will be replaced.
        regions = self.view.get_regions(f'_es_field_{field}')
        if regions:
            self.view.sel().clear()
            for sel in regions:
                self.view.sel().add(sel)

        # Temporarily draw some regions that say where the cursors are
        self.view.add_regions('_es_cursors', [r for r in self.view.sel()],
                              scope='comment',
                              flags=sublime.DRAW_NO_FILL|sublime.DRAW_EMPTY)

        # Show the quick panel to allow the user to pick from the options that
        # we were given.
        self.view.window().show_quick_panel(options, placeholder=placeholder,
                                            on_select=lambda idx: insert(idx))


## ----------------------------------------------------------------------------
