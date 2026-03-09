# reducers/script.py — user script execution state transitions

from librarian2 import state as st
from librarian2.scripts import runner


def handle_run_script(payload):
    """Run a user script against the currently selected registry record.

    payload: str — path to the script file

    The script receives a copy of the selected record and may modify it.
    On success, the modified record is merged back via update.
    On failure, the status bar shows the error and the record is unchanged.
    """
    entry_id = st.g[st.SELECTED_ID]
    if entry_id is None:
        st.g[st.STATUS_MSG]   = 'No entry selected'
        st.g[st.STATUS_LEVEL] = 'red'
        return

    record      = dict(st.g[st.REG_ENTRIES][entry_id])  # shallow copy for script
    script_path = payload

    try:
        modified = runner.execute_script(script_path, record)
    except Exception as e:
        st.g[st.STATUS_MSG]   = f'Script error: {e}'
        st.g[st.STATUS_LEVEL] = 'red'
        return

    if modified is not None:
        st.g[st.REG_ENTRIES][entry_id] = modified
        st.g[st.DIRTY]        = True
        st.g[st.STATUS_MSG]   = f'Script applied to: {entry_id}'
        st.g[st.STATUS_LEVEL] = 'green'
