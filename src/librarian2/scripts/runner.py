# scripts/runner.py — user-defined record script execution
#
# Scripts are plain Python files that receive and may modify a registry record.
# They operate on one record at a time and must not access application state.
#
# Script contract:
#   - The script is executed with a local variable D containing the record dict.
#   - The script may modify D in place.
#   - The script may reassign D to a new dict (runner picks up both cases).
#   - After execution, the resulting record is dispatched through the reducer.
#
# Example script:
#   # normalize_path.py
#   import pathlib
#   D['location'] = [{'path': str(pathlib.Path(D['location'][0]['path']).resolve())}]


def execute_script(script_path, record):
    """Execute a user script against a registry record.

    script_path: str or pathlib.Path — path to the Python script file
    record: dict — a shallow copy of the registry entry (safe to mutate)

    Returns the (possibly modified) record dict, or None if the script
    explicitly sets D = None to signal no changes.

    Raises any exception the script raises — callers should catch and report.
    """
    import pathlib

    script_path = pathlib.Path(script_path)
    source = script_path.read_text(encoding='utf-8')

    local_ns = {'D': record}
    exec(compile(source, str(script_path), 'exec'), {}, local_ns)

    return local_ns.get('D')
