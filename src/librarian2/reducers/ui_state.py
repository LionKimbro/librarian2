# reducers/ui_state.py — editor mode and status bar state transitions

from librarian2 import state as st


def handle_set_editor_mode(payload):
    """Switch the editor between form and raw JSON mode.

    payload: 'form' or 'raw'
    """
    st.g[st.EDITOR_MODE] = payload


def handle_set_status(payload):
    """Update the status bar message and level.

    payload: dict with keys:
        'msg'   : str  — message text
        'level' : str  — 'default' | 'green' | 'blue' | 'red'  (optional)
    """
    st.g[st.STATUS_MSG]   = payload['msg']
    st.g[st.STATUS_LEVEL] = payload.get('level', 'default')
