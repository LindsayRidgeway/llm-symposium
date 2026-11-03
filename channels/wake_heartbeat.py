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


TRANSCRIPT_TAIL = 65536
NO_REASON = ('worker_failed', 'failed')


def _transcript_error(state_dir, run_id):
    """The last error line a dying worker wrote, as one machine token.

    A worker that exits 1 because it could not reach its provider leaves `worker_exit: 1` in its
    result and the reason in `runs/<id>/worker.jsonl`. Reporting the 1 makes a network failure and a
    crash look the same, which is the defect this whole module exists to fix, one level down.
    """
    if not state_dir or not run_id:
        return ''
    path = Path(state_dir) / 'runs' / str(run_id) / 'worker.jsonl'
    try:
        with open(path, 'rb') as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            fh.seek(max(0, size - TRANSCRIPT_TAIL))
            tail = fh.read().decode('utf-8', 'replace')
    except OSError:
        return ''
    # The worker writes its failures as JSON events and, on the last line, as prose. Take the last
    # of either — whichever came last is what ended the run.
    candidate = ''
    for line in tail.splitlines():
        stripped = line.strip()
        if stripped.startswith('Error:'):
            candidate = stripped[len('Error:'):].strip()
            continue
        if '"type":"error"' not in stripped:
            continue
        try:
            event = json.loads(stripped)
        except ValueError:
            continue
        message = event.get('error') or ''
        if isinstance(message, str) and message:
            candidate = message
    return candidate.split(':')[0].split(' — ')[0].strip()[:MAX_DETAIL]


def _detail(result, state_dir=None):
    """A short machine string: why this ending, not what the wake was about."""
    status = str(result.get('status') or '')
    for key in ('error', 'land', 'on_battery_percent', 'handoff_id', 'worker_exit'):
        value = result.get(key)
        if value in (None, ''):
            continue
        if key == 'worker_exit' and status in NO_REASON:
            # "worker_failed: 1" is a code, not a reason. Look one file further before settling
            # for it — the transcript usually says what actually happened.
            reason = _transcript_error(state_dir, result.get('run_id'))
            if reason:
                return reason
        text = str(value).split(':')[0].strip()
        return text[:MAX_DETAIL]
    if status in NO_REASON:
        reason = _transcript_error(state_dir, result.get('run_id'))
        if reason:
            return reason
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
            'detail': _detail(result, state_dir),
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
