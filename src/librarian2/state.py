# state.py — global application state bundle
#
# g is the single source of truth for all application state.
# It is mutated in place and never rebound.
# All state transitions happen through dispatch() -> reducers.

g = {}

# Keys — use these constants everywhere, never bare strings.

TK           = 'tk'           # root tkinter.Tk window
QUEUE        = 'queue'        # queue.Queue for GUI/worker thread communication

REG_DOC      = 'reg_doc'      # dict — document metadata from the registry file
REG_ENTRIES  = 'reg_entries'  # dict — {id: entry_dict} for every registry record
REG_PATH     = 'reg_path'     # pathlib.Path or None

SELECTED_ID  = 'selected_id'  # str or None — currently selected entry id

EDITOR_MODE  = 'editor_mode'  # 'form' or 'raw'

DIRTY        = 'dirty'        # bool — unsaved changes exist
STATUS_MSG   = 'status_msg'   # str — current status bar text
STATUS_LEVEL = 'status_level' # 'default' | 'green' | 'blue' | 'red'

WIDGETS      = 'widgets'      # dict — {name: widget}, global widget registry


def init_state():
    """Initialize g to a clean starting state. Called once at GUI startup."""
    g[TK]           = None
    g[QUEUE]        = None
    g[REG_DOC]      = {}
    g[REG_ENTRIES]  = {}
    g[REG_PATH]     = None
    g[SELECTED_ID]  = None
    g[EDITOR_MODE]  = 'form'
    g[DIRTY]        = False
    g[STATUS_MSG]   = ''
    g[STATUS_LEVEL] = 'default'
    g[WIDGETS]      = {}
