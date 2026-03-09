# patchboard.py — Patchboard integration (FileTalk file-transport profile)
#
# Component channels:
#   out: 'component-id-card'  — self-announcement at startup
#   out: 'selected-item'      — emits the selected registry entry on demand
#   in:  'add-file', 'add-folder', 'add-url', 'add-program'
#
# Transport: filesystem INCOMING / OUTBOX under .librarian2/
# Polling:   root.after() on the GUI thread, every 500 ms

import json
import pathlib
import time
import uuid

import lionscliapp as app

from librarian2 import state as st
from librarian2 import dispatch as d


CHANNELS_IN      = ['add-entry']
CHANNELS_OUT     = ['selected-item', 'component-id-card']


def _title():
    return app.ctx.get('patchboard.title') or 'Librarian2 Registry Editor'

def _poll_interval_ms():
    try:
        return int(app.ctx.get('patchboard.pollinginterval') or 500)
    except (ValueError, TypeError):
        return 500


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _inbox_path():
    return app.get_path('INBOX', 'p')

def _outbox_path():
    return app.get_path('OUTBOX', 'p')

def _ensure_dirs():
    _inbox_path().mkdir(parents=True, exist_ok=True)
    _outbox_path().mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Low-level message I/O
# ---------------------------------------------------------------------------

def _write_message(channel, signal, outbox):
    """Write a single Patchboard Core message file to outbox.

    Filename is unique per the file-transport spec (timestamp + UUID fragment).
    Written directly (no atomic rename) per spec write requirements.
    """
    msg   = {
        'channel':   channel,
        'signal':    signal,
        'timestamp': str(time.time()),
    }
    fname = f'msg_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}.json'
    (outbox / fname).write_text(
        json.dumps(msg, ensure_ascii=False),
        encoding='utf-8',
    )


# ---------------------------------------------------------------------------
# Startup: announce self
# ---------------------------------------------------------------------------

def _make_id_card():
    inbox  = _inbox_path()
    outbox = _outbox_path()
    return {
        'schema_version': 1,
        'title':          _title(),
        'inbox':          str(inbox.resolve()),
        'outbox':         str(outbox.resolve()),
        'channels': {
            'in':  CHANNELS_IN,
            'out': CHANNELS_OUT,
        },
    }


def announce_self():
    """Create transport dirs, write component-id-card.json, and self-announce.

    Called once at startup from run_editor(), before the mainloop starts.
    Writes the Component ID Card to:
      - <project-dir>/component-id-card.json  (static, for out-of-band discovery)
      - <project-dir>/OUTBOX/msg_*.json        (live announcement, channel 'component-id-card')
    """
    try:
        _ensure_dirs()
        card      = _make_id_card()
        card_path = app.get_path('component-id-card.json', 'p')
        card_path.write_text(
            json.dumps(card, indent=2, ensure_ascii=False) + '\n',
            encoding='utf-8',
        )
        _write_message('component-id-card', card, _outbox_path())
    except Exception as exc:
        # Non-fatal: patchboard is optional plumbing
        st.g[st.STATUS_MSG]   = f'Patchboard announce failed: {exc}'
        st.g[st.STATUS_LEVEL] = 'red'


# ---------------------------------------------------------------------------
# Outbound: emit selected entry
# ---------------------------------------------------------------------------

def handle_emit(payload):
    """Emit the selected registry entry to OUTBOX on channel 'selected-item'.

    payload: ignored (always emits the currently selected entry)
    """
    entry_id = st.g[st.SELECTED_ID]
    if entry_id is None:
        d.dispatch(d.SET_STATUS, {'msg': 'No entry selected to emit', 'level': 'red'})
        return
    entry = st.g[st.REG_ENTRIES].get(entry_id)
    if entry is None:
        return
    try:
        _ensure_dirs()
        _write_message('selected-item', entry, _outbox_path())
        d.dispatch(d.SET_STATUS, {'msg': f'Emitted: {entry_id}', 'level': 'green'})
    except Exception as exc:
        d.dispatch(d.SET_STATUS, {'msg': f'Emit failed: {exc}', 'level': 'red'})


# ---------------------------------------------------------------------------
# Inbound: process messages from INCOMING
# ---------------------------------------------------------------------------

def handle_input(payload):
    """Process one inbound Patchboard message dict.

    payload: dict with keys 'channel', 'signal', 'timestamp'
    Handled channels: 'add-file', 'add-folder', 'add-url', 'add-program'
    """
    channel = payload.get('channel', '')
    signal  = payload.get('signal', {})
    if channel == 'add-entry':
        _handle_add(signal)


def _handle_add(entry):
    """Add an inbound registry entry to the registry and refresh the UI."""
    if not isinstance(entry, dict) or 'id' not in entry:
        return
    d.dispatch(d.ADD_ENTRY, entry)
    from librarian2.ui.main_window import refresh_all
    refresh_all(st.g)


# ---------------------------------------------------------------------------
# Polling loop
# ---------------------------------------------------------------------------

def _poll(root):
    """One poll cycle: read all parseable .json files from INCOMING, process, delete."""
    inbox = _inbox_path()
    if inbox.is_dir():
        # Process in mtime order (best-effort; spec makes no ordering guarantee)
        files = sorted(inbox.glob('*.json'), key=lambda p: p.stat().st_mtime)
        for f in files:
            try:
                text = f.read_text(encoding='utf-8')
                msg  = json.loads(text)
            except (OSError, json.JSONDecodeError):
                continue    # incomplete write — retry next cycle per spec
            try:
                handle_input(msg)
            finally:
                try:
                    f.unlink()
                except OSError:
                    pass
    root.after(_poll_interval_ms(), lambda: _poll(root))


def start_input_polling(root):
    """Start the after()-based INCOMING polling loop.

    Called once after the main window is built. All processing happens on the
    GUI thread — no extra thread needed.
    """
    root.after(_poll_interval_ms(), lambda: _poll(root))
