#!/usr/bin/env python3
"""One-off: make item_ledger.append atomic against a second writer."""
import pathlib

P = pathlib.Path("/Users/lindsayridgeway/LLM/llm-symposium/channels/item_ledger.py")
t = P.read_text(encoding="utf-8")

old_append = '''def append(records: list[dict], path: Path = LEDGER) -> None:
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, sort_keys=True) + "\\n")
'''

new_append = '''@contextlib.contextmanager
def _append_lock(path: Path):
    """One appender at a time. The ledger is the commons' only write-hot file.

    Two writers appending at once cannot corrupt a row here — each write is a single small
    ``write()`` under the same append file — but the readers between them can see a half-written
    line, and `load()` skips unreadable lines, so a torn row disappears rather than failing loudly.
    Cheap to prevent: flock on a file inside .git (which can never make the tree dirty), or in the
    temp directory when this is not a checkout (a wake's clone, a test fixture).
    """
    git_dir = path.parent.parent / ".git"
    lock_dir = git_dir if git_dir.is_dir() else Path(tempfile.gettempdir())
    lock_path = lock_dir / "symposium-ledger.lock"
    try:
        fh = lock_path.open("a+")
    except OSError:
        yield                          # a lock that cannot be taken must not stop the write
        return
    try:
        deadline = time.monotonic() + 10.0
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    break              # an append is smaller than the risk of refusing it
                time.sleep(0.05)
        try:
            yield
        finally:
            try:
                fcntl.flock(fh, fcntl.LOCK_UN)
            except OSError:
                pass
    finally:
        fh.close()


def append(records: list[dict], path: Path = LEDGER) -> None:
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with _append_lock(path):
        with path.open("a", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, sort_keys=True) + "\\n")
'''
assert t.count(old_append) == 1
t = t.replace(old_append, new_append)

# imports: append the stdlib ones the lock needs next to the existing import block
lines = t.splitlines(keepends=True)
start = next(i for i, l in enumerate(lines) if l.startswith("import "))
end = start
while end < len(lines) and (lines[end].startswith("import ") or lines[end].startswith("from ")
                            or lines[end].strip() == ""):
    if lines[end].strip() == "" and end > start + 1:
        break
    end += 1
block = "".join(lines[start:end])
need = [m for m in ("import contextlib", "import fcntl", "import tempfile", "import time")
        if m + "\n" not in block]
print("existing block starts with:", block.splitlines()[:4], "| adding", need)
new_block = block
for m in reversed(need):
    new_block = m + "\n" + new_block
lines[start:end] = [new_block]
t = "".join(lines)
P.write_text(t, encoding="utf-8")
print("patched", P)
