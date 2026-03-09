# registry_io.py — registry file loading and saving
#
# This module is the Castle Gate for registry data.
# All external JSON is normalized here before entering the application.
# Atomic writes ensure the file is never left in a partial state.

import json
import os
import pathlib
import tempfile


def load_registry_file(path):
    """Load a registry JSON file. Returns (doc_dict, entries_dict).

    Normalizes the registry at the Castle Gate: validates top-level
    structure so the rest of the system can trust what it receives.

    path: str or pathlib.Path
    Raises: FileNotFoundError, json.JSONDecodeError, ValueError
    """
    path = pathlib.Path(path)
    text = path.read_text(encoding='utf-8')
    data = json.loads(text)

    doc     = data.get('document', {})
    entries = data.get('registry', {})

    if not isinstance(entries, dict):
        raise ValueError(
            f'registry field must be a JSON object, got {type(entries).__name__}'
        )

    return doc, entries


def save_registry_file(path, doc, entries, indent=2):
    """Save registry to path atomically (write temp + rename).

    path: str or pathlib.Path
    doc: dict — document metadata (may be empty)
    entries: dict — registry entries
    indent: int — JSON indentation level (0 = compact)
    """
    path = pathlib.Path(path)

    data = {}
    if doc:
        data['document'] = doc
    data['registry'] = entries

    indent_arg = indent if indent > 0 else None
    separators = (',', ':') if indent == 0 else None
    text = json.dumps(data, indent=indent_arg, separators=separators,
                      ensure_ascii=False) + '\n'

    dir_ = path.parent
    fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix='.tmp', text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
