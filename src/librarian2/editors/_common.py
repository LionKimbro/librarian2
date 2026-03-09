# editors/_common.py — shared widget builders used by structured editors
#
# All structured editors (file, folder, url, json_file) share:
#   - common metadata fields: id, title, tags, purpose
#   - OS integration helpers: open with OS, copy to clipboard
#
# Safety rule: apply_common_fields only touches 'id', 'title', 'tags', 'purpose'.
# All other fields in the entry are left untouched.

import re
import subprocess
import sys
import tkinter as tk
import tkinter.ttk as ttk
from librarian2.ui import theme
from librarian2 import state as st

NOT_USED = '<NOT-USED>'

_TAG_RE = re.compile(r'^[a-zA-Z0-9_]+$')


def build_common_fields(frame, entry, widgets, row_start=0):
    """Build id, title, tags, and purpose input fields.

    Field order: id, title, tags, purpose.
    Stores created widgets and StringVars in the widgets dict.

    frame: tkinter widget (parent frame, using grid layout)
    entry: dict — current registry entry record
    widgets: dict — global widget registry
    row_start: int — first grid row to use
    Returns: next available grid row number
    """
    # --- id ---
    tk.Label(frame, text='id:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=row_start, column=0, sticky='ne', padx=(0, 6), pady=4)

    id_var = tk.StringVar(value=entry.get('id', ''))
    id_entry = tk.Entry(frame, textvariable=id_var, font=theme.FONT_MONO,
                        bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                        insertbackground=theme.DARK_FG, relief='flat')
    id_entry.grid(row=row_start, column=1, sticky='ew', pady=4, columnspan=2)

    # --- title ---
    tk.Label(frame, text='title:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=row_start + 1, column=0, sticky='ne', padx=(0, 6), pady=4)

    title_var = tk.StringVar(value=entry.get('title', ''))
    title_entry = tk.Entry(frame, textvariable=title_var, font=theme.FONT_MONO,
                           bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                           insertbackground=theme.DARK_FG, relief='flat')
    title_entry.grid(row=row_start + 1, column=1, sticky='ew', pady=4, columnspan=2)

    # --- tags ---
    tk.Label(frame, text='tags:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=row_start + 2, column=0, sticky='ne', padx=(0, 6), pady=4)

    tags_str = ' '.join(entry.get('tags') or [])
    tags_var = tk.StringVar(value=tags_str)
    tags_entry = tk.Entry(frame, textvariable=tags_var, font=theme.FONT_MONO,
                          bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                          insertbackground=theme.DARK_FG, relief='flat')
    tags_entry.grid(row=row_start + 2, column=1, sticky='ew', pady=4, columnspan=2)

    # --- purpose ---
    tk.Label(frame, text='purpose:', font=theme.FONT_UI,
             bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).grid(
        row=row_start + 3, column=0, sticky='ne', padx=(0, 6), pady=4)

    purpose_text = tk.Text(frame, height=5, font=theme.FONT_MONO,
                           bg=theme.DARK_INPUT_BG, fg=theme.DARK_FG,
                           insertbackground=theme.DARK_FG, relief='flat',
                           wrap='word')
    purpose_text.insert('1.0', entry.get('purpose', ''))
    purpose_text.grid(row=row_start + 3, column=1, sticky='ew', pady=4, columnspan=2)

    frame.columnconfigure(1, weight=1)

    widgets['common_id_var']        = id_var
    widgets['common_title_var']     = title_var
    widgets['common_tags_var']      = tags_var
    widgets['common_purpose_text']  = purpose_text
    widgets['common_id_entry']      = id_entry
    widgets['common_title_entry']   = title_entry
    widgets['common_tags_entry']    = tags_entry

    return row_start + 4


def apply_common_fields(entry, widgets):
    """Write title, tags, and purpose from widgets into entry. Also reads the id field.

    Validates tags against ^[a-zA-Z0-9_]+$. Writes all fields that are valid.
    Does NOT write 'id' to the entry — the caller receives new_id and decides
    whether to dispatch UPDATE_ENTRY or RENAME_ENTRY.

    Returns: (new_id, tags_error)
        new_id:     str — value from the id widget (may differ from entry['id'])
        tags_error: str or None — error message if a tag is invalid, else None
    """
    new_id = widgets['common_id_var'].get().strip()

    entry['title']   = widgets['common_title_var'].get()
    entry['purpose'] = widgets['common_purpose_text'].get('1.0', 'end-1c')

    tags_raw = widgets['common_tags_var'].get()
    tokens   = tags_raw.split()

    bad = [t for t in tokens if not _TAG_RE.match(t)]
    if bad:
        return new_id, f"Invalid tag(s): {', '.join(bad)}  (allowed: letters, digits, _)"

    if tokens:
        entry['tags'] = tokens
    elif 'tags' in entry:
        # Cleared — remove the field entirely rather than leaving an empty list
        del entry['tags']

    return new_id, None


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


# ---------------------------------------------------------------------------
# Type combobox fields  (logical.format, logical.encoding, semantic.base)
# ---------------------------------------------------------------------------

def _collect_type_values(axis, field):
    """Return sorted unique values of type[axis][field] across all registry entries."""
    seen = set()
    for entry in st.g[st.REG_ENTRIES].values():
        val = entry.get('type', {}).get(axis, {}).get(field)
        if val:
            seen.add(val)
    return sorted(seen)


def _merge_suggestions(base_list, extra):
    """Append any extra values not already in base_list. Preserves base order."""
    result  = list(base_list)
    present = set(base_list)
    for v in extra:
        if v not in present:
            result.append(v)
            present.add(v)
    return result


def build_type_fields(frame, entry, widgets, row_start,
                      format_opts=None, encoding_opts=None, semantic_opts=None):
    """Build comboboxes for logical.format, logical.encoding, and semantic.base.

    All active comboboxes are placed on a single row, packed left with their
    inline labels. Pass None for any axis to omit it entirely.
    Scans the registry to include any values already in use as extra suggestions.
    Stores vars/widgets in the widgets dict.
    Returns: next available grid row (row_start + 1 if any field is shown, else row_start).
    """
    logical  = entry.get('type', {}).get('logical', {})
    semantic = entry.get('type', {}).get('semantic', {})

    fields = []
    if format_opts is not None:
        fields.append(('format:', logical.get('format'), format_opts,
                        _collect_type_values('logical', 'format'),
                        'type_format_var', 'type_format_cb'))
    if encoding_opts is not None:
        fields.append(('encoding:', logical.get('encoding'), encoding_opts,
                        _collect_type_values('logical', 'encoding'),
                        'type_encoding_var', 'type_encoding_cb'))
    if semantic_opts is not None:
        fields.append(('semantic:', semantic.get('base'), semantic_opts,
                        _collect_type_values('semantic', 'base'),
                        'type_semantic_var', 'type_semantic_cb'))

    if not fields:
        return row_start

    row_frame = tk.Frame(frame, bg=theme.DARK_BG)
    row_frame.grid(row=row_start, column=0, columnspan=2, sticky='w', pady=4)

    for label_text, current_val, base_opts, extra_vals, var_key, cb_key in fields:
        current = current_val or NOT_USED
        values  = _merge_suggestions(base_opts, extra_vals)
        if current not in values:
            values.insert(1, current)
        var = tk.StringVar(value=current)
        tk.Label(row_frame, text=label_text, font=theme.FONT_UI,
                 bg=theme.DARK_BG, fg=theme.DARK_FG_DIM).pack(side='left', padx=(8, 2))
        cb = ttk.Combobox(row_frame, textvariable=var, values=values,
                          font=theme.FONT_MONO, width=12)
        cb.pack(side='left', padx=(0, 4))
        widgets[var_key] = var
        widgets[cb_key]  = cb

    return row_start + 1


def apply_type_fields(entry, widgets):
    """Write combobox values for logical.format, logical.encoding, semantic.base into entry.

    <NOT-USED> or blank → removes the key.
    Cleans up empty logical / semantic / type dicts after writing so no
    spurious empty objects are left in the record.
    """
    # Get or create the sub-dicts; we clean up empties at the end
    type_d   = entry.setdefault('type', {})
    logical  = type_d.setdefault('logical', {})
    semantic = type_d.setdefault('semantic', {})

    for field, wkey in [('format', 'type_format_var'), ('encoding', 'type_encoding_var')]:
        var = widgets.get(wkey)
        if var is None:
            continue
        val = var.get().strip()
        if val and val != NOT_USED:
            logical[field] = val
        else:
            logical.pop(field, None)

    var = widgets.get('type_semantic_var')
    if var is not None:
        val = var.get().strip()
        if val and val != NOT_USED:
            semantic['base'] = val
        else:
            semantic.pop('base', None)

    # Clean up empty containers (but never touch keys we don't manage, like logical.base)
    if not logical:
        type_d.pop('logical', None)
    if not semantic:
        type_d.pop('semantic', None)
    if not type_d:
        entry.pop('type', None)
