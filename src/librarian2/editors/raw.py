# editors/raw.py — raw JSON record editor (always-available fallback)
#
# Provides direct text editing of the registry record JSON,
# plus Copy JSON and Copy JSON (min) clipboard buttons.
# This editor is always safe to use: it cannot lose unknown fields
# because it exposes and applies the complete record JSON.

import json
import tkinter as tk
import tkinter.ttk as ttk
from librarian2.ui import theme
from librarian2 import dispatch as d
from librarian2 import state as st
from librarian2.editors._common import add_button, copy_to_clipboard


def build_raw_editor(parent, entry, widgets):
    """Build the raw JSON editor inside parent.

    parent: tkinter widget (the editor_area frame)
    entry: dict — current registry entry record
    widgets: dict — global widget registry
    """
    frame = tk.Frame(parent, bg=theme.DARK_BG)
    frame.grid(row=0, column=0, sticky='nsew')
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    # --- JSON text area ---
    text_frame = tk.Frame(frame, bg=theme.DARK_BG)
    text_frame.grid(row=0, column=0, sticky='nsew', padx=8, pady=(8, 4))

    scrollbar = ttk.Scrollbar(text_frame, orient='vertical')
    text = tk.Text(text_frame, font=theme.FONT_MONO,
                   bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                   insertbackground=theme.DARK_FG,
                   selectbackground=theme.DARK_ACCENT,
                   wrap='none',
                   yscrollcommand=scrollbar.set)
    scrollbar.configure(command=text.yview)

    text.grid(row=0, column=0, sticky='nsew')
    scrollbar.grid(row=0, column=1, sticky='ns')
    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(0, weight=1)

    text.insert('1.0', json.dumps(entry, indent=2, ensure_ascii=False))

    # --- Button row ---
    btn_frame = tk.Frame(frame, bg=theme.DARK_BG)
    btn_frame.grid(row=1, column=0, sticky='ew', padx=8, pady=(0, 8))

    def apply_changes():
        raw_text = text.get('1.0', 'end-1c')
        try:
            updated = json.loads(raw_text)
        except json.JSONDecodeError as e:
            d.dispatch(d.SET_STATUS, {'msg': f'JSON error: {e}', 'level': 'red'})
            return
        d.dispatch(d.UPDATE_ENTRY, updated)
        from librarian2.ui.main_window import refresh_all
        refresh_all(st.g)

    def copy_json():
        copy_to_clipboard(frame, json.dumps(entry, indent=2, ensure_ascii=False))

    def copy_json_min():
        copy_to_clipboard(frame, json.dumps(entry, separators=(',', ':'),
                                            ensure_ascii=False))

    add_button(btn_frame, 'Apply',     apply_changes)
    add_button(btn_frame, 'Copy JSON', copy_json)
    add_button(btn_frame, '(min)',     copy_json_min)

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    widgets['raw_editor_frame'] = frame
    widgets['raw_editor_text']  = text
    widgets['apply_fn']         = apply_changes
