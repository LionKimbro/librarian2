# ui/index_pane.py — entry index widget (left pane)
#
# Shows resource IDs sorted alphabetically.
# Type indicated by unicode icon; title and tags are not shown.

import tkinter as tk
import tkinter.ttk as ttk
from librarian2.ui import theme
from librarian2 import state as st
from librarian2 import dispatch as d


def build_index_pane(parent, widgets):
    """Build the left pane showing the registry entry index.

    parent: tkinter widget
    widgets: dict — global widget registry
    Returns: the frame widget
    """
    frame = tk.Frame(parent, bg=theme.DARK_BG)

    scrollbar = ttk.Scrollbar(frame, orient='vertical')
    tree = ttk.Treeview(frame, columns=(), show='tree',
                        yscrollcommand=scrollbar.set,
                        selectmode='browse')
    scrollbar.configure(command=tree.yview)

    tree.column('#0', width=250, stretch=True)

    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar.grid(row=0, column=1, sticky='ns')

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    tree.bind('<<TreeviewSelect>>', lambda e: _on_tree_select(tree))
    tree.bind('<Delete>', lambda e: _on_delete_key())

    widgets['index_frame']  = frame
    widgets['index_tree']   = tree
    widgets['index_scroll'] = scrollbar

    return frame


def refresh_index(g):
    """Rebuild the index tree from the current registry entries in g."""
    tree     = g[st.WIDGETS]['index_tree']
    entries  = g[st.REG_ENTRIES]
    selected = g[st.SELECTED_ID]

    # Suppress selection event while rebuilding
    tree.unbind('<<TreeviewSelect>>')
    tree.delete(*tree.get_children())

    for entry_id in entries.keys():
        icon  = _icon_for_entry(entries[entry_id])
        label = f'{icon}  {entry_id}'
        tree.insert('', 'end', iid=entry_id, text=label)

    if selected and selected in entries:
        tree.selection_set(selected)
        tree.focus(selected)
        tree.see(selected)

    tree.bind('<<TreeviewSelect>>', lambda e: _on_tree_select(tree))


def _on_tree_select(tree):
    """Handle selection change in the index tree.

    Only refreshes the editor and status bar — never the index itself,
    since rebuilding the index from within a tree selection event would
    re-trigger selection_set, causing an infinite loop.
    """
    selection = tree.selection()
    entry_id  = selection[0] if selection else None
    if entry_id == st.g[st.SELECTED_ID]:
        return   # stale event queued by selection_set in refresh_index; nothing changed
    d.dispatch(d.SELECT_ENTRY, entry_id)

    from librarian2.ui.editor_pane import refresh_editor
    from librarian2.ui.status_bar  import refresh_status_bar
    refresh_editor(st.g)
    refresh_status_bar(st.g)


def _on_delete_key():
    """Handle Delete key while the index tree has focus."""
    from librarian2.ui.menus import cmd_delete_selected
    cmd_delete_selected()


def _icon_for_entry(entry):
    """Return the unicode icon for an entry's logical base type."""
    base = entry.get('type', {}).get('logical', {}).get('base', '')
    return {
        'file':    theme.ICON_FILE,
        'folder':  theme.ICON_FOLDER,
        'url':     theme.ICON_URL,
        'program': theme.ICON_PROGRAM,
    }.get(base, theme.ICON_UNKNOWN)
