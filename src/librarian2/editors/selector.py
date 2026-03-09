# editors/selector.py — choose the appropriate editor for a registry record
#
# The selector is the Castle Gate for form editors: it only returns a
# form editor if that editor can safely handle the entry. Otherwise it
# falls back to the raw JSON editor, which can always handle anything.

from librarian2.editors import raw


def select_editor(entry):
    """Return the build function for the most appropriate editor.

    Returns a callable: build_fn(parent, entry, widgets) -> None

    Selection logic based on type.logical.base (and .format for files).
    If the chosen editor reports it cannot safely handle the entry,
    the raw editor is returned instead.
    """
    logical      = entry.get('type', {}).get('logical', {})
    logical_base = logical.get('base', '')
    logical_fmt  = logical.get('format', '')

    if logical_base == 'file':
        if logical_fmt == 'json':
            from librarian2.editors import json_file
            if json_file.can_handle(entry):
                return json_file.build_json_file_editor
        else:
            from librarian2.editors import file as file_ed
            if file_ed.can_handle(entry):
                return file_ed.build_file_editor

    elif logical_base == 'folder':
        from librarian2.editors import folder
        if folder.can_handle(entry):
            return folder.build_folder_editor

    elif logical_base == 'url':
        from librarian2.editors import url
        if url.can_handle(entry):
            return url.build_url_editor

    # Program editor: reserved / not yet implemented — fall through to raw.
    return raw.build_raw_editor
