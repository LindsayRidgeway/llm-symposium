#!/usr/bin/env python3
"""wake_heartbeat — the trace a wake leaves when it does not run a model at all.

Written 2026-11-03 (dmitri), after the human said he could not understand the paragraph that
described this hole. He was right: it was described in six zeros.

`run_session` returns a status for every way a wake can end, and until now only some of those ways
wrote anything. A real run leaves `tick-state/runs/<id>/result.json`; a wake that declines to start
writes nothing at all. Tarik's engine returns `skipped_no_pending_handoff` when his Codex handoff
queue is empty — no run directory, no log line — so in the daily report his row was six zeros for
fifteen days, and "nothing was queued for him" was printed in exactly the same characters as "his
engine is broken".

That is not a missing feature, it is a wrong instrument: the report counts run directories, which
measure work started, and reads them as work attempted. An engine that never starts looks idle.

So: every exit from a wake records one line here. One file, overwritten, never appended — a wake
that skips every 24 minutes must not fill a disk to say so.

    tick-state/last-wake.json
    {"at": 1793723400.5, "utc": "2026-11-03T16:50:00Z", "amigo": "tarik",
     "status": "skipped_no_pending_handoff", "run_id": "20261103T165000Z-1a2b3c4d",
     "detail": "", "trace_written_by": "wake_heartbeat"}

`status` is exactly the status `run_session` returned; this module never invents one. `detail` is a
short machine string (a lander verdict's first token, an exception's class name), never prose: the
heartbeat is a counter, and the record of what a wake did belongs in the run directory or the
report.
"""
import datetime
import json
import os
import tempfile
from pathlib import Path

HEARTBEAT_NAME = 'last-wake.json'
MAX_DETAIL = 200


def amigo_of(state_dir):
    """Which seat this state directory belongs to.

    `~/LLM/tarik-bot/tick-state` -> "tarik". Derived from the path rather than passed in, because
    the six engines are six copies of one file and a name that has to be typed in each of them is
    a name that will be wrong in one of them.
    """
    name = Path(state_dir).resolve().parent.name
    return name[:-4] if name.endswith('-bot') else (name or 'unknown')


def _detail(result):
    """A short machine string: why this ending, not what the wake was about."""
    for key in ('error', 'land', 'worker_exit', 'on_battery_percent', 'handoff_id'):
        value = result.get(key)
        if value in (None, ''):
            continue
        text = str(value).split(':')[0].strip()
        return text[:MAX_DETAIL]
    return ''


def record_outcome(state_dir, result, amigo=None, now=None):
    """Write tick-state/last-wake.json from one run_session result. Never raises.

    Returns the path written, or None if it could not be written. A heartbeat that can break a
    wake would be worse than none: this is called on the way out of every attempt, including the
    ones that already failed.
    """
    try:
        if not isinstance(result, dict):
            result = {'status': 'unrecorded_result'}
        stamp = float(now) if now is not None else datetime.datetime.now(
            datetime.timezone.utc).timestamp()
        payload = {
            'at': stamp,
            'utc': datetime.datetime.fromtimestamp(stamp, datetime.timezone.utc)
                   .strftime('%Y-%m-%dT%H:%M:%SZ'),
            'amigo': amigo or amigo_of(state_dir),
            'status': str(result.get('status') or 'unknown'),
            'run_id': str(result.get('run_id') or ''),
            'detail': _detail(result),
            'trace_written_by': 'wake_heartbeat',
        }
        root = Path(state_dir)
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = root / HEARTBEAT_NAME
        # Same-directory temporary then rename: a reader must never see half a heartbeat, and the
        # report reads this file while wakes are writing it.
        fd, tmp = tempfile.mkstemp(dir=str(root), prefix='.last-wake.', suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                json.dump(payload, fh, ensure_ascii=False)
            os.replace(tmp, path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        return path
    except Exception:                                      # noqa: BLE001
        return None


def last_outcome(state_dir):
    """The last heartbeat for this seat, or None. Never raises."""
    try:
        return json.loads((Path(state_dir) / HEARTBEAT_NAME).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
