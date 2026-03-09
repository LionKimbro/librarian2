# ui/main_window.py — main window construction and application entry point

import queue
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import lionscliapp as app

from librarian2 import state as st
from librarian2 import dispatch as d
from librarian2.ui import theme
from librarian2.ui.index_pane  import build_index_pane,  refresh_index
from librarian2.ui.editor_pane import build_editor_pane, refresh_editor
from librarian2.ui.status_bar  import build_status_bar,  refresh_status_bar
from librarian2.ui.menus       import build_menu_bar


def run_editor():
    """Entry point for the GUI. Called by lionscliapp after ctx is ready.

    Initializes state, wires up dispatch, builds the main window,
    optionally loads the configured registry, then enters the main loop.
    """
    st.init_state()
    d._setup()

    root = tk.Tk()
    root.title('Librarian2 Registry Editor')
    root.withdraw()                  # hide until layout is complete
    root.option_add('*tearOff', False)

    st.g[st.TK]    = root
    st.g[st.QUEUE] = queue.Queue()

    theme.apply_theme(root)
    build_main_window(root)
    bind_keys(root)

    registry_path = app.ctx.get('path.registry')
    if not (registry_path and registry_path.is_file()):
        registry_path = app.get_path('registry.json', 'p')

    if registry_path.is_file():
        d.dispatch(d.LOAD_REGISTRY, registry_path)
        refresh_all(st.g)
    else:
        # No registry yet — point state at the default path so Save works.
        st.g[st.REG_PATH] = registry_path

    root.deiconify()
    root.mainloop()


def build_main_window(root):
    """Construct the two-pane layout inside root.

    Left pane: entry index.   Right pane: entry editor.
    Status bar pinned at the bottom.
    """
    widgets = st.g[st.WIDGETS]

    root.columnconfigure(0, weight=0, minsize=270)
    root.columnconfigure(1, weight=0)     # separator
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=0)

    build_menu_bar(root, widgets)

    index_pane  = build_index_pane(root, widgets)
    separator   = ttk.Separator(root, orient='vertical')
    editor_pane = build_editor_pane(root, widgets)
    status_bar  = build_status_bar(root, widgets)

    index_pane.grid(row=0, column=0, sticky='nsew')
    separator.grid(  row=0, column=1, sticky='ns', padx=1)
    editor_pane.grid(row=0, column=2, sticky='nsew')
    status_bar.grid( row=1, column=0, columnspan=3, sticky='ew')

    widgets['separator'] = separator


def bind_keys(root):
    """Bind global keyboard shortcuts to the root window."""
    from librarian2.ui.menus import cmd_open_registry, cmd_raise_entry, cmd_lower_entry
    root.bind('<Control-o>',    lambda e: cmd_open_registry())
    root.bind('<Control-s>',    lambda e: _save())
    root.bind('<Control-q>',    lambda e: root.destroy())
    root.bind('<Control-j>',    lambda e: _toggle_editor_mode())
    root.bind('<Control-Return>', lambda e: _cmd_apply())
    root.bind('<Control-Up>',   lambda e: cmd_raise_entry())
    root.bind('<Control-Down>', lambda e: cmd_lower_entry())


def _toggle_editor_mode():
    from librarian2.ui.menus import _set_editor_mode
    new_mode = 'raw' if st.g[st.EDITOR_MODE] == 'form' else 'form'
    _set_editor_mode(new_mode)


def _cmd_apply():
    from librarian2.ui.menus import cmd_apply
    cmd_apply()


def refresh_all(g):
    """Refresh all UI components from current application state.

    Preserves keyboard focus across the rebuild: finds which widgets-dict
    key held focus before, then restores focus to the same key after.
    """
    focused_key = _focused_widget_key(g)

    refresh_index(g)
    refresh_editor(g)
    refresh_status_bar(g)

    _restore_focus(g, focused_key)


def _focused_widget_key(g):
    """Return the widgets-dict key of the currently focused widget, or None."""
    focused = g[st.TK].focus_get()
    if focused is None:
        return None
    for key, w in g[st.WIDGETS].items():
        if callable(w):
            continue
        if w is focused:
            return key
    return None


def _restore_focus(g, key):
    """Focus the widget stored under key in the widgets dict, if it still exists."""
    if not key:
        return
    w = g[st.WIDGETS].get(key)
    if w is None or callable(w):
        return
    try:
        w.focus_set()
    except Exception:
        pass


def _save():
    d.dispatch(d.SAVE_REGISTRY)
    refresh_all(st.g)
