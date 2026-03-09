# editors/_common.py — shared widget builders used by structured editors
#
# All structured editors (file, folder, url, json_file) share:
#   - common metadata fields: id, title, purpose
#   - OS integration helpers: open with OS, copy to clipboard
#
# Safety rule: _apply_common_fields only touches 'id', 'title', 'purpose'.
# All other fields in the entry are left untouched.

import subprocess
import sys
import tkinter as tk
from librarian2.ui import theme


def build_common_fields(frame, entry, widgets, row_start=0):
    """Build id, title, and purpose input fields.

    These appear at the top of every structured editor.
    Stores created widgets and StringVars in the widgets dict.

    frame: tkinter widget (parent frame, using grid layout)
    entry: dict — current registry entry record
    widgets: dict — global widget registry
    row_start: int — first grid row to use
    Returns: next available grid row number
    """
    tk.Label(frame, text='id:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=row_start, column=0, sticky='ne', padx=(0, 6), pady=4)

    id_var = tk.StringVar(value=entry.get('id', ''))
    id_entry = tk.Entry(frame, textvariable=id_var, font=theme.FONT_MONO,
                        bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                        insertbackground=theme.DARK_FG, relief='flat')
    id_entry.grid(row=row_start, column=1, sticky='ew', pady=4, columnspan=2)

    tk.Label(frame, text='title:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=row_start + 1, column=0, sticky='ne', padx=(0, 6), pady=4)

    title_var = tk.StringVar(value=entry.get('title', ''))
    title_entry = tk.Entry(frame, textvariable=title_var, font=theme.FONT_MONO,
                           bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                           insertbackground=theme.DARK_FG, relief='flat')
    title_entry.grid(row=row_start + 1, column=1, sticky='ew', pady=4, columnspan=2)

    tk.Label(frame, text='purpose:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=row_start + 2, column=0, sticky='ne', padx=(0, 6), pady=4)

    purpose_text = tk.Text(frame, height=5, font=theme.FONT_MONO,
                           bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                           insertbackground=theme.DARK_FG, relief='flat',
                           wrap='word')
    purpose_text.insert('1.0', entry.get('purpose', ''))
    purpose_text.grid(row=row_start + 2, column=1, sticky='ew', pady=4, columnspan=2)

    frame.columnconfigure(1, weight=1)

    widgets['common_id_var']      = id_var
    widgets['common_title_var']   = title_var
    widgets['common_purpose_text'] = purpose_text
    widgets['common_id_entry']    = id_entry
    widgets['common_title_entry'] = title_entry

    return row_start + 3


def apply_common_fields(entry, widgets):
    """Read id, title, purpose from widgets and merge into entry.

    Only these three fields are touched. All other entry fields are preserved.
    """
    entry['id']      = widgets['common_id_var'].get()
    entry['title']   = widgets['common_title_var'].get()
    entry['purpose'] = widgets['common_purpose_text'].get('1.0', 'end-1c')


def make_button_row(frame, row, col_start=1):
    """Create and grid a sub-frame for action buttons. Returns the frame."""
    btn_frame = tk.Frame(frame, bg=theme.DARK_BG)
    btn_frame.grid(row=row, column=col_start, sticky='w', pady=(4, 0), columnspan=2)
    return btn_frame


def add_button(btn_frame, label, command):
    """Append a flat dark-mode button to btn_frame. Returns the button."""
    btn = tk.Button(btn_frame, text=label, font=theme.FONT_UI,
                    bg=theme.DARK_BG3, fg=theme.DARK_FG,
                    relief='flat', padx=6, command=command)
    btn.pack(side='left', padx=(0, 4))
    return btn


def open_with_os(path):
    """Open path using the OS default handler."""
    if sys.platform == 'win32':
        import os
        os.startfile(str(path))
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', str(path)])
    else:
        subprocess.Popen(['xdg-open', str(path)])


def copy_to_clipboard(root, text):
    """Copy text to the system clipboard."""
    root.clipboard_clear()
    root.clipboard_append(text)
