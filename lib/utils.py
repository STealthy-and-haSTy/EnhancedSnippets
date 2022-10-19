import sublime


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
