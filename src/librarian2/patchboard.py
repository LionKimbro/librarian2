# patchboard.py — Patchboard integration (FileTalk style)
#
# Output channel: 'selected-item'  — emits the selected registry entry
# Input channels: 'add-file', 'add-folder', 'add-url', 'add-program'
#
# The input and output payloads are symmetric: what this program emits
# can meaningfully be fed back in as input.
#
# TODO: implement FileTalk polling loop in a worker thread.

from librarian2 import state as st


def handle_emit(payload):
    """Emit the selected registry entry to the patchboard output channel.

    payload: ignored (always emits the currently selected entry)
    """
    # TODO: write entry to FileTalk output folder, channel 'selected-item'
    pass


def handle_input(payload):
    """Process an inbound patchboard message.

    payload: dict with keys 'channel' and 'data'
    Channels: 'add-file', 'add-folder', 'add-url', 'add-program'
    """
    # TODO: read from FileTalk inbox, dispatch appropriate ADD_ENTRY actions
    pass


def start_input_polling(root):
    """Start polling for inbound patchboard messages via tkinter after().

    Called once after the main window is built. Uses root.after() so
    polling runs on the GUI thread — no extra thread needed.

    root: tkinter.Tk
    """
    # TODO: implement after()-based polling loop
    pass
