import sublime
import sublime_plugin


## ----------------------------------------------------------------------------


class EnhancedSnippetFieldPickerCommand(sublime_plugin.TextCommand):
    """
    If the current file is actively invoking a snippet that has fields, and the
    current field has options, trigger a command that will prompt the user for
    an option and, if they pick one, insert that text.
    """
    def run(self, edit):
        # Get the current field out of the field list
        data = self.view.settings().get('_es_cache', {})
        cur_field = data["fields"][data["current_field_idx"]]

        # Get the options for this field, if any; when there are, the result is
        # an array where the first item is the placeholder and the remainder of
        # the items are the actual values; prompt with a quick panel.
        options = list(data["options"].get(cur_field, []))
        if options:
            self.view.run_command('insert_enhanced_snippet_option', {
                "field": cur_field,
                "placeholder": options[0],
                "options": options[1:]
            })

    def is_enabled(self):
        # We are only able to run if there is tracking information for the view
        # that might have some options.
        # Getting
        return self.view.settings().get('_es_cache', None) is not None


## ----------------------------------------------------------------------------
