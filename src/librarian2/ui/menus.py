# ui/menus.py — menu bar construction
#
# Underline values set throughout so Alt+key navigation works.
# Accelerator strings are for display only; real bindings are in main_window.py.

import pathlib
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
from librarian2 import dispatch as d
from librarian2 import state as st


def build_menu_bar(root, widgets):
    """Build and attach the full menu bar to root.

    root: tkinter.Tk
    widgets: dict — global widget registry
    """
    menubar = tk.Menu(root, tearoff=False)
    root.configure(menu=menubar)

    file_menu  = _build_file_menu(menubar, root)
    entry_menu = _build_entry_menu(menubar)
    view_menu  = _build_view_menu(menubar)

    widgets['menubar']     = menubar
    widgets['file_menu']   = file_menu
    widgets['entry_menu']  = entry_menu
    widgets['view_menu']   = view_menu


def _build_file_menu(menubar, root):
    m = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label='File', menu=m, underline=0)

    m.add_command(label='Open Registry...', underline=0,
                  accelerator='Ctrl+O',
                  command=cmd_open_registry)
    m.add_command(label='Save',             underline=0,
                  accelerator='Ctrl+S',
                  command=lambda: d.dispatch(d.SAVE_REGISTRY))
    m.add_separator()
    m.add_command(label='Quit',             underline=0,
                  accelerator='Ctrl+Q',
                  command=root.destroy)
    return m


def _build_entry_menu(menubar):
    m = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label='Entry', menu=m, underline=0)

    m.add_command(label='Apply',         underline=0,
                  accelerator='Ctrl+Enter',
                  command=cmd_apply)
    m.add_separator()
    m.add_command(label='Add File...',    underline=4, command=lambda: cmd_add_entry('file'))
    m.add_command(label='Add Folder...', underline=4, command=lambda: cmd_add_entry('folder'))
    m.add_command(label='Add URL...',    underline=4, command=lambda: cmd_add_entry('url'))
    m.add_command(label='Add Program...', underline=4, command=lambda: cmd_add_entry('program'))
    m.add_separator()
    m.add_command(label='Raise Entry',   underline=0,
                  accelerator='Ctrl+Up',
                  command=cmd_raise_entry)
    m.add_command(label='Lower Entry',   underline=0,
                  accelerator='Ctrl+Down',
                  command=cmd_lower_entry)
    m.add_separator()
    m.add_command(label='Delete Entry',  underline=0,
                  accelerator='Delete',
                  command=cmd_delete_selected)
    m.add_separator()
    m.add_command(label='Emit to Patchboard', underline=0,
                  command=lambda: d.dispatch(d.PATCHBOARD_EMIT))
    return m


def _build_view_menu(menubar):
    m = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label='View', menu=m, underline=0)

    m.add_command(label='Form Editor',     underline=0,
                  accelerator='Ctrl+J',
                  command=lambda: _set_editor_mode('form'))
    m.add_command(label='Raw JSON Editor', underline=0,
                  accelerator='Ctrl+J',
                  command=lambda: _set_editor_mode('raw'))
    return m


# --- Command implementations ---

def cmd_apply():
    """Invoke the active editor's apply function, if one is mounted."""
    fn = st.g[st.WIDGETS].get('apply_fn')
    if fn:
        fn()


def cmd_open_registry():
    """Prompt for a registry file and load it."""
    path = fd.askopenfilename(
        title='Open Registry',
        filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
    )
    if path:
        d.dispatch(d.LOAD_REGISTRY, path)
        _refresh_all()


def cmd_add_entry(base_type):
    """Open the appropriate dialog to add a new entry.

    base_type: 'file' | 'folder' | 'url' | 'program'
    """
    if base_type == 'file':
        path = fd.askopenfilename(title='Add File')
        if not path:
            return
        entry = _build_file_entry(pathlib.Path(path))

    elif base_type == 'folder':
        path = fd.askdirectory(title='Add Folder')
        if not path:
            return
        entry = _build_folder_entry(pathlib.Path(path))

    elif base_type == 'url':
        url = sd.askstring('Add URL', 'URL:')
        if not url:
            return
        entry = _build_url_entry(url)

    elif base_type == 'program':
        path = fd.askopenfilename(title='Add Program')
        if not path:
            return
        entry = _build_program_entry(pathlib.Path(path))

    else:
        return

    d.dispatch(d.ADD_ENTRY, entry)
    _refresh_all()


def _unique_id(stem):
    """Return stem if not already in the registry, otherwise stem-2, stem-3, ..."""
    entries = st.g[st.REG_ENTRIES]
    if stem not in entries:
        return stem
    n = 2
    while f'{stem}-{n}' in entries:
        n += 1
    return f'{stem}-{n}'


def _base_id(path):
    """Derive a registry id from a filesystem path."""
    return _unique_id(path.stem.lower().replace(' ', '-') or 'entry')


def _build_file_entry(path):
    fmt = path.suffix.lstrip('.').lower() or None
    logical = {'base': 'file'}
    if fmt:
        logical['format'] = fmt
    return {
        'id':       _base_id(path),
        'purpose':  '',
        'location': [{'path': str(path)}],
        'type':     {'logical': logical},
    }


def _build_folder_entry(path):
    entry = {
        'id':       _unique_id(path.name.lower().replace(' ', '-') or 'folder'),
        'purpose':  '',
        'location': [{'path': str(path)}],
        'type':     {'logical': {'base': 'folder'}},
    }
    return entry


def _build_url_entry(url):
    # Derive an id from the hostname
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname or 'url'
        stem = host.removeprefix('www.')
    except Exception:
        stem = 'url'
    entry = {
        'id':       _unique_id(stem),
        'purpose':  '',
        'location': [{'url': url}],
        'type':     {'logical': {'base': 'url', 'protocol': url.split('://')[0]}},
    }
    return entry


def _build_program_entry(path):
    entry = {
        'id':       _base_id(path),
        'purpose':  '',
        'location': [{'path': str(path)}],
        'type':     {'logical': {'base': 'program'}},
    }
    return entry


def cmd_raise_entry():
    """Move the selected entry one position earlier in the index."""
    entry_id = st.g[st.SELECTED_ID]
    if entry_id is None:
        return
    d.dispatch(d.RAISE_ENTRY, entry_id)
    _refresh_all()


def cmd_lower_entry():
    """Move the selected entry one position later in the index."""
    entry_id = st.g[st.SELECTED_ID]
    if entry_id is None:
        return
    d.dispatch(d.LOWER_ENTRY, entry_id)
    _refresh_all()


def cmd_delete_selected():
    """Delete the currently selected entry after user confirmation."""
    entry_id = st.g[st.SELECTED_ID]
    if entry_id is None:
        return
    if mb.askyesno('Delete Entry', f'Delete entry {entry_id!r}?'):
        d.dispatch(d.DELETE_ENTRY, entry_id)
        _refresh_all()


def _set_editor_mode(mode):
    d.dispatch(d.SET_EDITOR_MODE, mode)
    _refresh_all()


def _refresh_all():
    from librarian2.ui.main_window import refresh_all
    refresh_all(st.g)
