# dispatch.py — central action dispatcher
#
# All application state changes must go through dispatch().
# UI code calls dispatch(); reducers update g; UI refreshes from g.
#
# Usage:
#   from librarian2 import dispatch as d
#   d.dispatch(d.LOAD_REGISTRY, path)

# --- Action name constants ---

LOAD_REGISTRY    = 'load_registry'
SAVE_REGISTRY    = 'save_registry'
SELECT_ENTRY     = 'select_entry'
UPDATE_ENTRY     = 'update_entry'
ADD_ENTRY        = 'add_entry'
DELETE_ENTRY     = 'delete_entry'
RENAME_ENTRY     = 'rename_entry'
RAISE_ENTRY      = 'raise_entry'
LOWER_ENTRY      = 'lower_entry'
RUN_SCRIPT       = 'run_script'
SET_EDITOR_MODE  = 'set_editor_mode'
SET_STATUS       = 'set_status'
PATCHBOARD_EMIT  = 'patchboard_emit'
PATCHBOARD_INPUT = 'patchboard_input'

_handlers = {}  # action_name -> handler function


def dispatch(action, payload=None):
    """Dispatch an action through the reducer system.

    All application state changes must go through here.
    Raises ValueError for unknown actions.
    """
    handler = _handlers.get(action)
    if handler is None:
        raise ValueError(f'Unknown action: {action!r}')
    handler(payload)


def _register(action, fn):
    _handlers[action] = fn


def _setup():
    """Bind action names to reducer handlers. Called once at startup."""
    from librarian2.reducers import registry as reg_r
    from librarian2.reducers import entry as entry_r
    from librarian2.reducers import ui_state as ui_r
    from librarian2.reducers import script as script_r
    from librarian2 import patchboard

    _register(LOAD_REGISTRY,    reg_r.handle_load_registry)
    _register(SAVE_REGISTRY,    reg_r.handle_save_registry)
    _register(ADD_ENTRY,        entry_r.handle_add_entry)
    _register(DELETE_ENTRY,     entry_r.handle_delete_entry)
    _register(UPDATE_ENTRY,     entry_r.handle_update_entry)
    _register(RENAME_ENTRY,     entry_r.handle_rename_entry)
    _register(RAISE_ENTRY,      entry_r.handle_raise_entry)
    _register(LOWER_ENTRY,      entry_r.handle_lower_entry)
    _register(SELECT_ENTRY,     entry_r.handle_select_entry)
    _register(RUN_SCRIPT,       script_r.handle_run_script)
    _register(SET_EDITOR_MODE,  ui_r.handle_set_editor_mode)
    _register(SET_STATUS,       ui_r.handle_set_status)
    _register(PATCHBOARD_EMIT,  patchboard.handle_emit)
    _register(PATCHBOARD_INPUT, patchboard.handle_input)
