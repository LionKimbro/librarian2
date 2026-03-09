# ui/status_bar.py — status bar widget (bottom of main window)
#
# Shows: dirty indicator dot (red/green) + status message text.

import tkinter as tk
from librarian2.ui import theme
from librarian2 import state as st


def build_status_bar(parent, widgets):
    """Build the status bar frame. Stores widgets in the widgets dict.

    parent: tkinter widget
    widgets: dict — global widget registry
    Returns: the frame widget
    """
    frame = tk.Frame(parent, bg=theme.DARK_BG2, height=26)
    frame.grid_propagate(False)

    dirty_dot = tk.Label(frame, text='\u25cf', font=theme.FONT_UI,
                         bg=theme.DARK_BG2, fg=theme.DIRTY_GREEN)
    dirty_dot.pack(side='right', padx=(2, 8))

    status_label = tk.Label(frame, text='', font=theme.FONT_UI,
                             bg=theme.DARK_BG2, fg=theme.DARK_FG,
                             anchor='w')
    status_label.pack(side='left', fill='x', expand=True, padx=(8, 4))

    widgets['status_bar']   = frame
    widgets['dirty_dot']    = dirty_dot
    widgets['status_label'] = status_label

    return frame


def refresh_status_bar(g):
    """Refresh the status bar from current application state."""
    widgets = g[st.WIDGETS]

    dot = widgets.get('dirty_dot')
    if dot:
        dot.configure(fg=theme.DIRTY_RED if g[st.DIRTY] else theme.DIRTY_GREEN)

    label = widgets.get('status_label')
    if label:
        fg = theme.STATUS_FG.get(g[st.STATUS_LEVEL], theme.DARK_FG)
        label.configure(text=g[st.STATUS_MSG], fg=fg)
