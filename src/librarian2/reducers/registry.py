# reducers/registry.py — load and save registry state transitions

import lionscliapp as app
from librarian2 import state as st
from librarian2 import registry_io


def handle_load_registry(payload):
    """Load a registry file into application state.

    payload: str or pathlib.Path — path to the registry file
    Clears selection and dirty flag on successful load.
    """
    import pathlib
    path = pathlib.Path(payload)
    doc, entries = registry_io.load_registry_file(path)

    st.g[st.REG_PATH]    = path
    st.g[st.REG_DOC]     = doc
    st.g[st.REG_ENTRIES] = entries
    st.g[st.SELECTED_ID] = None
    st.g[st.DIRTY]       = False
    st.g[st.STATUS_MSG]  = f'Opened: {path.name}'
    st.g[st.STATUS_LEVEL] = 'green'


def handle_save_registry(payload):
    """Save the current registry to its file.

    payload: ignored
    """
    path    = st.g[st.REG_PATH]
    doc     = st.g[st.REG_DOC]
    entries = st.g[st.REG_ENTRIES]
    indent  = int(app.ctx.get('json.indent.registry', 2))

    registry_io.save_registry_file(path, doc, entries, indent)

    st.g[st.DIRTY]        = False
    st.g[st.STATUS_MSG]   = f'Saved: {path.name}'
    st.g[st.STATUS_LEVEL] = 'green'
