# ui/editor_pane.py — entry editor widget (right pane)
#
# Contains a header row (entry id label + mode toggle button) and
# an editor area that is swapped between form and raw JSON editors.

import tkinter as tk
import tkinter.ttk as ttk
from librarian2.ui import theme
from librarian2 import state as st
from librarian2 import dispatch as d


def build_editor_pane(parent, widgets):
    """Build the right pane containing the entry editor.

    parent: tkinter widget
    widgets: dict — global widget registry
    Returns: the frame widget
    """
    frame = tk.Frame(parent, bg=theme.DARK_BG)

    # --- Header row ---
    header = tk.Frame(frame, bg=theme.DARK_BG2, pady=4)
    header.grid(row=0, column=0, sticky='ew')

    id_label = tk.Label(header, text='(no entry selected)',
                        font=theme.FONT_UI, bg=theme.DARK_BG2, fg=theme.DARK_FG,
                        anchor='w')
    id_label.pack(side='left', padx=8)

    mode_btn = tk.Button(header, text='Raw JSON',
                         font=theme.FONT_UI, bg=theme.DARK_BG3, fg=theme.DARK_FG,
                         relief='flat', command=_toggle_editor_mode)
    mode_btn.pack(side='right', padx=8)

    # --- Editor area (content swapped on selection / mode change) ---
    editor_area = tk.Frame(frame, bg=theme.DARK_BG)
    editor_area.grid(row=1, column=0, sticky='nsew')

    frame.rowconfigure(1, weight=1)
    frame.columnconfigure(0, weight=1)
    editor_area.rowconfigure(0, weight=1)
    editor_area.columnconfigure(0, weight=1)

    widgets['editor_frame']    = frame
    widgets['editor_header']   = header
    widgets['editor_id_label'] = id_label
    widgets['editor_mode_btn'] = mode_btn
    widgets['editor_area']     = editor_area

    return frame


def refresh_editor(g):
    """Rebuild the editor area for the currently selected entry.

    Clears the editor area and mounts the appropriate editor widget.
    Called after any state change that could affect the editor.
    """
    widgets     = g[st.WIDGETS]
    entry_id    = g[st.SELECTED_ID]
    editor_mode = g[st.EDITOR_MODE]

    id_label = widgets.get('editor_id_label')
    if id_label:
        id_label.configure(text=entry_id or '(no entry selected)')

    mode_btn = widgets.get('editor_mode_btn')
    if mode_btn:
        mode_btn.configure(text='Form' if editor_mode == 'raw' else 'Raw JSON')

    area = widgets['editor_area']
    for child in area.winfo_children():
        child.destroy()

    if entry_id is None:
        return

    entry = g[st.REG_ENTRIES][entry_id]

    if editor_mode == 'raw':
        from librarian2.editors.raw import build_raw_editor
        build_raw_editor(area, entry, widgets)
    else:
        from librarian2.editors.selector import select_editor
        build_fn = select_editor(entry)
        build_fn(area, entry, widgets)


def _toggle_editor_mode():
    """Toggle between form and raw editor modes."""
    current  = st.g[st.EDITOR_MODE]
    new_mode = 'raw' if current == 'form' else 'form'
    d.dispatch(d.SET_EDITOR_MODE, new_mode)

    from librarian2.ui.main_window import refresh_all
    refresh_all(st.g)
