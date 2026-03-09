# editors/folder.py — structured editor for folder resource records
#
# Shows: common fields + path field with action buttons:
#   Browse | Open | Path | (full)
#
# No "Containing" button (the path IS a folder; opening it makes more sense).

import pathlib
import tkinter as tk
import tkinter.filedialog as fd
from librarian2.ui import theme
from librarian2 import dispatch as d, state as st
from librarian2.editors._common import (
    build_common_fields, apply_common_fields,
    make_button_row, add_button,
    open_with_os, copy_to_clipboard,
)


def can_handle(entry):
    """Return True if this editor can safely handle the entry.

    Refuses entries with inline locations.
    """
    for loc in entry.get('location', []):
        if 'inline' in loc:
            return False
    return True


def build_folder_editor(parent, entry, widgets):
    """Build the folder record editor inside parent."""
    frame = tk.Frame(parent, bg=theme.DARK_BG)
    frame.grid(row=0, column=0, sticky='nsew', padx=12, pady=12)
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    next_row = build_common_fields(frame, entry, widgets, row_start=0)

    # --- Path field ---
    path_str = _get_path(entry)
    path_var = tk.StringVar(value=path_str)

    tk.Label(frame, text='path:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=next_row, column=0, sticky='ne', padx=(0, 6), pady=4)

    path_entry = tk.Entry(frame, textvariable=path_var, font=theme.FONT_MONO,
                          bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                          insertbackground=theme.DARK_FG, relief='flat')
    path_entry.grid(row=next_row, column=1, sticky='ew', pady=4)

    # --- Path action buttons ---
    btn_frame = make_button_row(frame, row=next_row + 1)

    def browse():
        chosen = fd.askdirectory(title='Select Folder')
        if chosen:
            path_var.set(chosen)

    def open_folder():
        p = path_var.get()
        if p:
            open_with_os(p)

    def copy_path():
        copy_to_clipboard(frame, path_var.get())

    def copy_full_path():
        p = path_var.get()
        if p:
            copy_to_clipboard(frame, str(pathlib.Path(p).resolve()))

    add_button(btn_frame, 'Browse', browse)
    add_button(btn_frame, 'Open',   open_folder)
    add_button(btn_frame, 'Path',   copy_path)
    add_button(btn_frame, '(full)', copy_full_path)

    # --- Apply button ---
    apply_row = next_row + 2
    tk.Button(frame, text='Apply', font=theme.FONT_UI,
              bg=theme.DARK_ACCENT, fg='white', relief='flat',
              command=lambda: _apply(entry, path_var, widgets)).grid(
        row=apply_row, column=1, sticky='w', pady=(12, 0))

    frame.rowconfigure(apply_row + 1, weight=1)

    widgets['folder_path_var']   = path_var
    widgets['folder_path_entry'] = path_entry


def _apply(entry, path_var, widgets):
    original_id = entry['id']
    new_id, tags_error = apply_common_fields(entry, widgets)
    if tags_error:
        d.dispatch(d.SET_STATUS, {'msg': tags_error, 'level': 'red'})
        return
    _set_path(entry, path_var.get())
    if new_id != original_id:
        d.dispatch(d.RENAME_ENTRY, {'old_id': original_id, 'new_id': new_id, 'entry': entry})
    else:
        entry['id'] = new_id
        d.dispatch(d.UPDATE_ENTRY, entry)
    from librarian2.ui.main_window import refresh_all
    refresh_all(st.g)


def _get_path(entry):
    for loc in entry.get('location', []):
        if 'path' in loc:
            return loc['path']
    return ''


def _set_path(entry, path_str):
    for loc in entry.get('location', []):
        if 'path' in loc:
            loc['path'] = path_str
            return
    entry.setdefault('location', []).append({'path': path_str})
