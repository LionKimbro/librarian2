# editors/url.py — structured editor for URL resource records
#
# Shows: common fields + url field with action buttons:
#   Open | URL
#   (Open = open in default browser, URL = copy url to clipboard)

import webbrowser
import tkinter as tk
from librarian2.ui import theme
from librarian2 import dispatch as d, state as st
from librarian2.editors._common import (
    build_common_fields, apply_common_fields,
    make_button_row, add_button,
    copy_to_clipboard,
)


def can_handle(entry):
    """Return True if this editor can safely handle the entry.

    Refuses entries with inline locations.
    """
    for loc in entry.get('location', []):
        if 'inline' in loc:
            return False
    return True


def build_url_editor(parent, entry, widgets):
    """Build the URL record editor inside parent."""
    frame = tk.Frame(parent, bg=theme.DARK_BG)
    frame.grid(row=0, column=0, sticky='nsew', padx=12, pady=12)
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    next_row = build_common_fields(frame, entry, widgets, row_start=0)

    # --- URL field ---
    url_str = _get_url(entry)
    url_var = tk.StringVar(value=url_str)

    tk.Label(frame, text='url:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=next_row, column=0, sticky='ne', padx=(0, 6), pady=4)

    url_entry = tk.Entry(frame, textvariable=url_var, font=theme.FONT_MONO,
                         bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                         insertbackground=theme.DARK_FG, relief='flat')
    url_entry.grid(row=next_row, column=1, sticky='ew', pady=4)

    # --- URL action buttons ---
    btn_frame = make_button_row(frame, row=next_row + 1)

    def open_url():
        u = url_var.get()
        if u:
            webbrowser.open(u)

    def copy_url():
        copy_to_clipboard(frame, url_var.get())

    add_button(btn_frame, 'Open', open_url)
    add_button(btn_frame, 'URL',  copy_url)

    # --- Apply button ---
    apply_row = next_row + 2
    tk.Button(frame, text='Apply', font=theme.FONT_UI,
              bg=theme.DARK_ACCENT, fg='white', relief='flat',
              command=lambda: _apply(entry, url_var, widgets)).grid(
        row=apply_row, column=1, sticky='w', pady=(12, 0))

    frame.rowconfigure(apply_row + 1, weight=1)

    widgets['url_var']   = url_var
    widgets['url_entry'] = url_entry


def _apply(entry, url_var, widgets):
    original_id = entry['id']
    new_id, tags_error = apply_common_fields(entry, widgets)
    if tags_error:
        d.dispatch(d.SET_STATUS, {'msg': tags_error, 'level': 'red'})
        return
    _set_url(entry, url_var.get())
    if new_id != original_id:
        d.dispatch(d.RENAME_ENTRY, {'old_id': original_id, 'new_id': new_id, 'entry': entry})
    else:
        entry['id'] = new_id
        d.dispatch(d.UPDATE_ENTRY, entry)
    from librarian2.ui.main_window import refresh_all
    refresh_all(st.g)


def _get_url(entry):
    for loc in entry.get('location', []):
        if 'url' in loc:
            return loc['url']
    return ''


def _set_url(entry, url_str):
    for loc in entry.get('location', []):
        if 'url' in loc:
            loc['url'] = url_str
            return
    entry.setdefault('location', []).append({'url': url_str})
