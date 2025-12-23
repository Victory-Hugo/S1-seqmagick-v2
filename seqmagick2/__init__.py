from os import path


def _normalize_version(raw):
    if not raw:
        return '1.0.0'
    raw = raw.strip()
    if raw.startswith('v'):
        raw = raw[1:]
    dirty = False
    if raw.endswith('-dirty'):
        dirty = True
        raw = raw[:-6]
    parts = raw.split('-')
    local = None
    if len(parts) == 1:
        base = parts[0]
    elif len(parts) >= 3 and parts[1].isdigit() and parts[2].startswith('g'):
        base = f"{parts[0]}.post{parts[1]}"
        local = parts[2][1:]
        if len(parts) > 3:
            local = local + "." + ".".join(parts[3:])
    else:
        base = parts[0]
        local = ".".join(parts[1:])
        if local:
            base = base + ".post0"
    if dirty:
        local = (local + ".dirty") if local else "dirty"
    return f"{base}+{local}" if local else base


try:
    with open(path.join(path.dirname(__file__), 'data', 'ver')) as f:
        __version__ = _normalize_version(f.read())
except Exception:
    __version__ = '1.0.0'
