# reducers/entry.py — entry selection and modification state transitions

from librarian2 import state as st


def handle_select_entry(payload):
    """Select an entry by ID.

    payload: str entry id, or None to clear selection
    """
    st.g[st.SELECTED_ID] = payload


def handle_add_entry(payload):
    """Add a new entry to the registry.

    payload: dict — the complete entry record (must contain 'id')
    """
    entry    = payload
    entry_id = entry['id']
    st.g[st.REG_ENTRIES][entry_id] = entry
    st.g[st.SELECTED_ID] = entry_id
    st.g[st.DIRTY]       = True
    st.g[st.STATUS_MSG]  = f'Added: {entry_id}'
    st.g[st.STATUS_LEVEL] = 'default'


def handle_update_entry(payload):
    """Merge updated fields into an existing entry.

    payload: dict — fields to update (must contain 'id')

    Safety rule: only provided keys are touched.
    Unknown fields already in the record are untouched.
    """
    entry_id = payload['id']
    existing = st.g[st.REG_ENTRIES][entry_id]
    existing.update(payload)
    st.g[st.DIRTY]        = True
    st.g[st.STATUS_MSG]   = f'Updated: {entry_id}'
    st.g[st.STATUS_LEVEL] = 'default'


def handle_rename_entry(payload):
    """Rename an entry: reindex under new_id, remove old_id.

    payload: dict with keys:
        'old_id': str — current key in REG_ENTRIES
        'new_id': str — desired new key
        'entry':  dict — the already-updated entry record

    If new_id collides with an existing entry (other than old_id),
    sets a red status message and does nothing.
    """
    old_id = payload['old_id']
    new_id = payload['new_id']
    entry  = payload['entry']

    if new_id in st.g[st.REG_ENTRIES]:
        st.g[st.STATUS_MSG]   = f'ID already exists: {new_id!r}'
        st.g[st.STATUS_LEVEL] = 'red'
        return

    entry['id'] = new_id
    del st.g[st.REG_ENTRIES][old_id]
    st.g[st.REG_ENTRIES][new_id] = entry
    st.g[st.SELECTED_ID]  = new_id
    st.g[st.DIRTY]        = True
    st.g[st.STATUS_MSG]   = f'Renamed: {old_id!r} \u2192 {new_id!r}'
    st.g[st.STATUS_LEVEL] = 'green'


def handle_raise_entry(payload):
    """Move the selected entry one position earlier in insertion order.

    payload: str — entry id to raise (ignored if already first)
    """
    _shift_entry(payload, -1)


def handle_lower_entry(payload):
    """Move the selected entry one position later in insertion order.

    payload: str — entry id to lower (ignored if already last)
    """
    _shift_entry(payload, +1)


def _shift_entry(entry_id, delta):
    entries = st.g[st.REG_ENTRIES]
    keys    = list(entries.keys())
    try:
        idx = keys.index(entry_id)
    except ValueError:
        return
    new_idx = idx + delta
    if new_idx < 0 or new_idx >= len(keys):
        return
    keys[idx], keys[new_idx] = keys[new_idx], keys[idx]
    st.g[st.REG_ENTRIES] = {k: entries[k] for k in keys}
    st.g[st.DIRTY]        = True
    st.g[st.STATUS_MSG]   = ''
    st.g[st.STATUS_LEVEL] = 'default'


def handle_delete_entry(payload):
    """Delete an entry by ID.

    payload: str — entry id to delete
    """
    entry_id = payload
    del st.g[st.REG_ENTRIES][entry_id]

    if st.g[st.SELECTED_ID] == entry_id:
        st.g[st.SELECTED_ID] = None

    st.g[st.DIRTY]        = True
    st.g[st.STATUS_MSG]   = f'Deleted: {entry_id}'
    st.g[st.STATUS_LEVEL] = 'default'
