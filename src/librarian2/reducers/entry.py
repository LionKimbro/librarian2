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
