import sublime
import sublime_plugin

from ...lib import handle_snippet_field_move


## ----------------------------------------------------------------------------


class EnhancedSnippetInsertAndMarkCommand(sublime_plugin.TextCommand):
    """
    Given some text, insert that text as the "insert" command would do.

    Along with the insert, this will also add in a set of regions that mark
    all of the characters that were inserted so that they can be recalled and
    replaced later.
    """
    def run(self, edit, field, characters):
        # Store the start position and size of all selections that are
        # currently in the buffer.
        sel = [(r.begin(), r.size()) for r in self.view.sel()]

        # Insert the requested text
        self.view.run_command('insert', {'characters': characters})

        # Adjust all of the start positions that we stored to account for the
        # insertion; the originally captured points will be wrong based on the
        # difference in length between the original text and the new text.
        length = len(characters)
        start = [(s[0] + (idx * (length - s[1]))) for idx,s in enumerate(sel)]

        # Save regions for this field that track all of the text that was just
        # inserted.
        self.view.add_regions(f'_es_field_{field}',
                              [sublime.Region(s, s + length) for s in start],
                              flags=sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE)


## ----------------------------------------------------------------------------
