"""The wake engine — one implementation, six configurations.

Extracted 2026-11-03 (dmitri) from six `local_tick.py` files that had drifted apart over five
weeks. The count that made it unavoidable: 4,529 lines across six files, one of them tested, and
the drift was not cosmetic. Three of the six still told the model "THE FIRST LINE OF THIS REPORT IS
SENT TO LINDSAY AS A TEXT MESSAGE" four weeks after the human retired per-wake texts; five of the
six carried the same `run_id`-before-assignment bug in the low-battery guard and the sixth did not;
one had a check the others lacked (a LAND line naming a path that is not in the run's own diff).
None of that is visible from any one copy.

This file is copied **byte for byte** into each `~/LLM/<bot>-bot/` directory beside a small
`local_tick.py` that configures it, and `tests/test_wake_engine_one_implementation.py` fails if the
copies ever differ. Identity is still derived from the directory the file sits in, so a copy cannot
lie about who it is.

What a body may configure: which engine (`standard` — wake, work, land — or `handoff` — Tarik's
Codex queue), which provider keys its worker may carry, and any extra environment names its
provider needs. Everything else is here.
"""
import datetime
import fcntl
import importlib.util
import json
import logging
import math
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import threading
import tempfile
import time
import urllib.request          # 2026-11-07 (Desi): `load_handoff_queue` has fetched the Codex
                               # queue through urllib.request since 2026-10-16 and never imported
                               # it. Tarik's engine is the only one configured to call it, so the
                               # only seat that could notice is the one that could not: every wake
                               # from 2026-10-19 to 2026-11-07 raised NameError inside a try whose
                               # handler returns 'skipped_handoff_unavailable' — a skip, which is
                               # the normal status of an idle handoff seat, so nothing alarmed.
import uuid
import zlib

log = logging.getLogger(__name__)

# The key variable each provider reads, from `~/.config/goose/config.yaml` and the custom-provider
# declarations beside it. A provider that is not here carries no key of its own into a wake.
PROVIDER_KEYS = {
    'anthropic': 'ANTHROPIC_API_KEY',
    'openai': 'OPENAI_API_KEY',
    'google': 'GOOGLE_API_KEY',
    'openrouter': 'OPENROUTER_API_KEY',
    'custom_deepseek': 'DEEPSEEK_API_KEY',
    'custom_alibaba': 'DASHSCOPE_API_KEY',
}


class Config:
    """What one body may decide about its engine. Everything else is shared.

    2026-11-03: this exists because six files that were meant to be copies were not, and nothing
    could tell a deliberate difference from a forgotten one. A difference that is not in here is
    drift, and the drift test says so.
    """

    def __init__(self, engine='standard', providers=(), extra_env=()):
        if engine not in ('standard', 'handoff'):
            raise ValueError('unknown engine %r' % (engine,))
        self.engine = engine
        # A callable, because one seat's provider is a switch read from its environment at the
        # moment of the wake (Gwen: DashScope or OpenRouter), not a constant in a file.
        self.providers = providers if callable(providers) else tuple(providers)
        self.extra_env = tuple(extra_env)

    def provider_list(self):
        return tuple(self.providers() if callable(self.providers) else self.providers)


CONFIG = Config()

# Which amigo is this? Derived from this file's own directory, never written into the prompt by
# hand. 2026-09-27: claude-bot and tarik-bot both opened every wake with "You are Desi, the
# DeepSeek participant" — this harness was copied from desi-bot on 09-26 and the identity string
# was not localized — so two of the four bots spent their wakes believing they were someone else,
# and a wake that runs under the wrong name writes the wrong name into the record. Deriving it
# means a copy of this file into another bot directory cannot lie about who it is.
# The seat, lower case, from the same directory. Used where the engine names the body to itself:
# `--queue <amigo>`, `to-do-lists/<amigo>.md`.
AMIGO = Path(__file__).resolve().parent.name.split('-')[0]
# 2026-11-03, on unification: this table was four entries long and defaulted to "Desi", so the
# copy that went into dmitri-bot and gwen-bot — the two seats added after it was written — would
# have opened every wake as Desi. The default was the bug: a name nobody recognises is safer than
# another person's name, because the first is visible in the first line of the prompt and the
# second is not. All six, keyed on the bare seat, with a neutral fallback.
AMIGO_IDENTITY = {
    'desi': 'Desi, the DeepSeek participant',
    'dmitri': 'Dmitri, the DeepSeek participant',
    'claude': 'Claude, the Anthropic participant',
    'gemini': 'Gemini, the Google participant',
    'tarik': 'Tarik, the OpenAI participant',
    'gwen': 'Gwen, the Qwen participant',
}.get(AMIGO, 'an amigo of the LLM Symposium')


# One trace per wake, loaded from the file beside this one like record.py beside bot.py
# (2026-11-03). Loaded by path rather than by name: inserting this directory into sys.path would
# change what every later `import` in this process resolves to — measured, it turned a test's
# missing lander into a real one that ran the suite — and a diagnostic must not have side effects.
try:
    import importlib.util as _importlib_util
    _heartbeat_spec = _importlib_util.spec_from_file_location(
        'wake_heartbeat', str(Path(__file__).resolve().parent / 'wake_heartbeat.py'))
    _heartbeat_module = _importlib_util.module_from_spec(_heartbeat_spec)
    _heartbeat_spec.loader.exec_module(_heartbeat_module)
    _record_wake_outcome = _heartbeat_module.record_outcome
except Exception as _heartbeat_err:                        # noqa: BLE001
    _record_wake_outcome = None
    log.error('wake_heartbeat.py is not importable (%s) — every wake this file runs will leave '
              'no trace, and a report that counts runs will read that as idleness', _heartbeat_err)


def save_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp-' + uuid.uuid4().hex)
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    os.replace(str(temporary), str(path))



def land_claimed(report_text):
    """The paths a report says it changed, from its `LAND:` line.

    Added 2026-09-18, after a run of the 09-18 13:19 wake asked to land ten paths and had
    produced seven. Three of them — including the write-up of its own verification — did not
    exist anywhere, and nothing said so: delivery delivered what was there and silently omitted
    the rest. A report that names a file it did not write is the same shape as the relay's
    work-log, the tick's report and the pre-fix LAND line: a claim whose return path is never
    checked. So the claim is now parsed and compared against what git actually sees.
    """
    out, seen_marker = [], False
    for line in report_text.splitlines():
        text = line.strip().lstrip('-* ').strip()
        if text.upper().startswith('LAND:'):
            seen_marker = True
            text = text[5:].strip()
        elif seen_marker:
            # continuation lines: a wrapped list, or a bare path with nothing else in it
            if not text or (':' in text and not text.startswith(('docs/', 'research/', 'channels/',
                                                               'scripts/', 'tests/', 'agenda/',
                                                               'to-do-lists/', 'discussions/',
                                                               'governance/', 'works/', 'news/',
                                                               'outreach/', 'insights/'))):
                break
        else:
            continue
        for piece in text.split(','):
            # A LAND line may separate paths with spaces instead of commas — the 09-19 09:31 run
            # wrote six paths that way and was recorded as one path containing all six, which then
            # reported all six as missing from main after they had been landed. Split on both.
            for token in piece.split():
                token = token.strip().strip('`').strip()
                if token and ('/' in token or token.endswith('.md')):
                    out.append(token)
    return out


def expand_land_claims(claimed, changed):
    """A LAND line that names a directory has named no delivery. Replace it with the run's own diff.

    Added 2026-11-11, from a measured case rather than a theory. Three runs in two days wrote
    `LAND: channels/ledger-verdicts/` — a directory, not the two files under it:
    gemini-bot 20261110T131526Z-61c082dd (cut off; its three changed paths exist only in that
    run's changes.patch, and its two verdicts never reached main), gemini-bot
    20261110T171543Z-2a288583 (the same two ids again, nothing on disk), and my own
    20261111T130044Z-9fe1b78a, which the wake summary named as `CLAIMED, NOT IN ITS DIFF:
    channels/ledger-verdicts/`.

    The directory is worse than a wrong path, because it *passes* the two checks the harness
    makes. It is in `changed` never, so it is reported as land_missing — a warning nobody acts
    on, six paths long — and it exists in the checkout, so the wake summary's "NOT IN MAIN"
    test below counts it as present while the files it stands for are absent. The run reads as
    delivered to anyone who asks the cheap question.

    So the claim is resolved against the one record the worker cannot write: its own diff. A
    directory claim becomes every changed path under it, and keeps its raw form only when the
    diff holds nothing under it — in which case it is a false claim and must stay visible as
    one. File claims pass through untouched and in order; duplicates collapse.
    """
    out = []
    for claim in claimed:
        raw = claim.strip()
        bare = raw.rstrip('/')
        if not bare:
            continue
        direct = [c for c in changed if c == bare or c == raw]
        under = [c for c in changed if c.startswith(bare + '/')]
        resolved = direct + [c for c in under if c not in direct]
        for path in (resolved or [raw]):
            if path not in out:
                out.append(path)
    return out


def worker_usage(path):
    """Token cost and whether the worker was cut off at its action cap.

    Added 2026-09-20, because both facts were knowable and neither was recorded. Measured over
    the 35 runs in the state directory: **30 of them ended on goose's own words "I've reached
    the maximum number of actions I can do without user input. Would you like me to continue?"**
    — a question put to a person who is asleep — at 680k-1.5M tokens each. A run that is cut off
    mid-artefact and a run that finishes look identical in `result.json`, and the fix for one of
    those is not the fix for the other. This makes the difference visible.
    """
    out = {'total_tokens': None, 'cut_off': False}
    try:
        text = Path(path).read_text(encoding='utf-8', errors='replace')
    except Exception:
        return out
    out['cut_off'] = 'maximum number of actions' in text
    for line in text.splitlines():
        if line.startswith('{"type":"complete"'):
            try:
                out['total_tokens'] = json.loads(line).get('total_tokens')
            except Exception:
                pass
    return out


# Paths the pipeline itself writes after a run's diff has been taken: the `tasks: file N item(s)
# from the chat` step and the record commits touch these, so a run that names one of them in its
# LAND line is not claiming work of its own. The list is a shortcut, not the definition — the
# definition of a false claim is "in the report's LAND line, not in the run's own diff"
# (added 2026-10-10, after run 20261008T003307Z-d334dbc8 reported `Registered the test in the
# workflow` with the workflow absent from its diff).
PIPELINE_WRITTEN = ('to-do-lists/', 'channels/tasks.md', 'channels/reject-queue.md',
                    'channels/items.jsonl', 'channels/conversation/', 'channels/telegram/')


def recent_runs(state_dir, limit=6):
    """The newest runs, their status, their delivery claim, and whether it reached main.

    The clock wakes six times a day with the same to-do list. Each wake re-derives the state of
    the world with its own shell calls, and none of them can see the sibling run from four hours
    ago that already did the work and left it on a branch. So this summarises them cheaply and
    the instruction hands the summary over: N unlanded runs, the newest one's paths, and which
    of those paths are absent from main.
    """
    rows = []
    runs = Path(state_dir) / 'runs'
    if not runs.is_dir():
        return rows
    for run_dir in sorted((p for p in runs.iterdir() if p.is_dir()), reverse=True)[:limit]:
        result_path = run_dir / 'result.json'
        if not result_path.is_file():
            continue
        try:
            r = json.loads(result_path.read_text(encoding='utf-8'))
        except Exception:
            continue
        report = ''
        claimed = None
        try:
            raw = (run_dir / 'report.txt').read_text(encoding='utf-8')
            report = (raw.splitlines() or [''])[0][:160]
            # Re-derive the claim from the report rather than trusting the recorded copy: the
            # record is a snapshot of the parser of its day, and the parser has been wrong once
            # (a space-separated LAND line was stored as a single path containing six).
            claimed = land_claimed(raw)
        except Exception:
            claimed = r.get('land_claimed')
        # Why the lander refused this run, if it did. It is written *after* the run ends, so a run
        # could not read its own refusal — and until 2026-10-10 nothing else read it either: 22 runs
        # sat with a refusal on disk that no later wake was ever shown (13 of them still applicable).
        refused = ''
        try:
            refused = ' '.join((run_dir / 'landing_failed.txt').read_text(
                encoding='utf-8').split())[:180]
        except Exception:
            refused = ''
        rows.append({
            'run_id': r.get('run_id', run_dir.name),
            'status': r.get('status', '?'),
            'cut_off': bool(r.get('cut_off')),
            'land_claimed': claimed or [],
            'land_missing': r.get('land_missing') or [],
            'changed_paths': r.get('changed_paths') or [],
            'refused': refused,
            'first_line': report,
        })
    return rows


# 2026-11-13 — ROWS THAT NAME A SEAT, PULLED INSIDE THE WINDOW.
#
# The ledger is handed to every wake truncated to its first 10,000 characters, because 123 open rows
# in 185,622 characters cannot ride in every prompt. The truncation is *positional*, and measured
# today that costs exactly the rows nobody could answer: the founder's vehicle-pool proposal begins at
# character 129,396, so the ratification row ("All six: ratify or amend the pool") and the answer owed
# by one seat had never been in any wake's context between 2026-11-01 and today. The seat that owed it
# had the row transcribed into her own to-do list by hand — which is a fix that expires with the next
# row, and it was not there for the seat that filed the proposal.
#
# This is the same defect `tests/test_wake_context_caps.py` found in the agenda on 2026-10-17: a wake
# told to act on a list the window does not contain. The answer there was not a bigger window; it was
# to put the list where the window falls. Same answer here: pull out the rows that name you, wherever
# they sit, and leave the long tail truncated.
#
# Bounded on three axes so a verbose seat cannot crowd out the rest of the prompt: count, per-row
# length, and total. Every cut says so in the delivered text, because a row that arrives silently
# half-read is worse than one that announces itself as cut.
OPEN_ROW_NAMED_CAP = 5
OPEN_ROW_COHORT_CAP = 4
OPEN_ROW_CHARS = 400
OPEN_ROW_BUDGET = 3500
COHORT_CUES = ('all six', 'all amig', 'the cohort', 'every amigo', 'any amigo')

COHORT_HEADER = ('=== OPEN ROWS THAT ASK THE WHOLE COHORT ===\n'
                 'Pulled from anywhere in channels/tasks.md, because the copy above stops at 10,000 '
                 'characters. These name every amigo; if you have not answered one, answer it this '
                 'run. Answering is maintenance, not a rep (to-do-lists/README.md rule 8): it does '
                 'not replace your one deliverable, and it does not wait behind your queue — a vote '
                 'the cohort is blocked on is not a task in front of you, it is a hole in the room.')
NAMED_HEADER = ('=== OPEN ROWS THAT NAME YOU ===\n'
                'Also pulled from past the truncation point. These are yours to answer; a row that '
                'names you and someone else is a row the two of you settle between you.')


def _ledger_blocks(text):
    """`- [ ] ...` rows plus their indented continuation lines, in file order."""
    blocks, cur = [], None
    for line in text.splitlines():
        if line.startswith('- [ ]'):
            if cur:
                blocks.append(cur)
            cur = [line]
        elif line.startswith('- [') or not line[:1].isspace():
            if cur:
                blocks.append(cur)
            cur = None
        elif cur is not None:
            cur.append(line)
    if cur:
        blocks.append(cur)
    return ['\n'.join(b).strip() for b in blocks if '\n'.join(b).strip()]


def open_rows_for(amigo, text, head=10000):
    """Open ledger rows that ask the cohort, and open rows that name `amigo`, wherever they sit.

    Two lists, capped separately, because one must not be able to starve the other: a seat with
    fourteen rows naming it would otherwise never be handed the cohort row it owes a vote on, which
    is the exact failure this was written to fix. Newest first — the ledger grows at the end, so the
    end is where the rows the truncation cuts away live — and every cut announces itself, because a
    row delivered silently half-read is worse than one that says it was cut. Word-boundary matching,
    not substring: "desire" is not Desi, and a filter that cannot tell the difference would hand her
    the founder's sentences about controlling his money.
    """
    name = re.compile(r'\b%s\b' % re.escape(amigo.lower()))
    visible = text[:head]
    blocks = [b for b in _ledger_blocks(text) if b not in visible]

    def clip(row):
        if len(row) > OPEN_ROW_CHARS:
            return row[:OPEN_ROW_CHARS].rstrip() + ' [cut — read channels/tasks.md for the rest]'
        return row

    cohort, named = [], []
    for row in reversed(blocks):
        low = row.lower()
        if any(cue in low for cue in COHORT_CUES):
            cohort.append(clip(row))
        elif name.search(low):
            named.append(clip(row))

    def fit(rows, cap, budget):
        out, used, dropped = [], 0, 0
        for row in rows:
            if len(out) >= cap or used + len(row) > budget:
                dropped += 1
                continue
            out.append(row)
            used += len(row)
        return out, dropped

    cohort_keep, cohort_dropped = fit(cohort, OPEN_ROW_COHORT_CAP, OPEN_ROW_BUDGET // 2)
    named_keep, named_dropped = fit(named, OPEN_ROW_NAMED_CAP, OPEN_ROW_BUDGET // 2)
    return {'cohort': cohort_keep, 'named': named_keep,
            'dropped': cohort_dropped + named_dropped}


# 2026-11-13 — WHAT IS DUE, ADDED TO THE BLOCK THE WAKE OPENS WITH.
#
# The founder asked on 2026-11-11 for creative work to repeat and for a monthly scan for medical
# opportunities, and then asked the question that made this necessary: if repeats are not on
# anybody's calendar, how does a body keep looking? Measured that day: the machinery to declare a
# repeat already existed (to-do-lists/README.md rule 4, probes/recurrence_projection.py,
# scripts/todo_due.py) and NOT ONE list used it — and nothing ran todo_due either, so a marker
# would have been decoration. This is the third time in three weeks the commons built a mechanism
# and left it unwired (the reading quota lived in a script nobody ran; the whole-repo review was
# a document nobody rewrote). The rule that keeps winning: put the number where the wake reads it.
#
# So the wake block now opens with what is due for THIS seat: repeats expanded to their next
# instance, overdue first, then today, then the next fortnight. Bounded to DUE_SHOWN rows and
# DUE_CHARS characters, and it says when it has cut something.
DUE_DAYS = 14
DUE_SHOWN = 8
DUE_CHARS = 2200
DUE_ITEM = re.compile(r'^- \[ \] (\d{4})-(\d{2})-(\d{2}) — (.*)$')
DUE_CONT = re.compile(r'^\s{2,}(\S.*)$')


def due_items(todo_text, today=None, repo=None):
    """(date, kind, text, repeat) for every item in one to-do list, repeats expanded once.

    kind is 'overdue' / 'today' / 'soon' / None. A repeating item's date is its NEXT instance on
    or after today, not the date it was written — that is the whole point of the marker.
    """
    today = today or datetime.date.today()
    items = []
    cur = None
    for line in todo_text.splitlines():
        m = DUE_ITEM.match(line.rstrip())
        if m:
            y, mo, d, text = m.groups()
            cur = {'date': datetime.date(int(y), int(mo), int(d)), 'text': text.strip(),
                   'repeat': None}
            items.append(cur)
            continue
        if cur is not None:
            c = DUE_CONT.match(line.rstrip())
            if c:
                if c.group(1).strip().lower().startswith('repeat:'):
                    cur['repeat'] = c.group(1).split(':', 1)[1].strip()
                continue
            if not line.strip():
                cur = None
    out = []
    for it in items:
        when, note = it['date'], ''
        if it['repeat']:
            when, note = _next_instance(it['repeat'], it['date'], today, repo)
            if when is None:
                out.append((None, 'unreadable-rule', it['text'], it['repeat'], note))
                continue
        days = (when - today).days
        kind = 'overdue' if days < 0 else ('today' if days == 0 else
                                           ('soon' if days <= DUE_DAYS else None))
        out.append((when, kind, it['text'], it['repeat'], note))
    out.sort(key=lambda r: (r[0] is None, r[0] or today))
    return out


def _next_instance(rule, start, today, repo=None):
    """Next occurrence on/after today, using the commons' own RRULE engine if it is importable.

    A rule the engine does not support is reported as unreadable rather than quietly treated as a
    one-off: `validate_rrule` takes the *parsed* spec, not the raw string, and skipping that step
    is how an unreadable rule would otherwise read as an overdue item dated in the past.
    """
    probes = str(Path(repo or '.').resolve() / 'probes')
    if probes not in sys.path:
        sys.path.insert(0, probes)
    try:
        from recurrence_projection import (expand_rrule, parse_rrule, validate_rrule,
                                           UnsupportedRRULEError)
    except Exception as exc:                       # engine absent
        return start, '(repeat not expanded: %s)' % type(exc).__name__
    try:
        validate_rrule(parse_rrule(rule))
        occ, _truncated = expand_rrule(rule, start, horizon_days=400, limit=600)
    except UnsupportedRRULEError:
        return None, '(unreadable repeat rule: %s)' % rule
    except Exception as exc:
        return start, '(repeat not expanded: %s)' % type(exc).__name__
    for d in occ:
        if d >= today:
            return d, '(next of repeat %s)' % rule
    return None, '(no occurrence inside the horizon)'


def due_block(repo, amigo=None):
    """The 'what is due' block for this seat, or a one-line statement that nothing is."""
    amigo = amigo or AMIGO
    todo = Path(repo) / 'to-do-lists' / (amigo + '.md')
    if not todo.is_file():
        return ''
    try:
        text = todo.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''
    rows = due_items(text, repo=repo)
    live = [r for r in rows if r[1] in ('overdue', 'today', 'soon')]
    repeats = [r for r in rows if r[3]]
    head = ('=== WHAT IS DUE (from to-do-lists/%s.md, repeats expanded to their next instance) ==='
            % amigo)
    if not live and not repeats:
        return (head + '\nNothing is dated today, overdue, or due in the next %d days. Nothing on '
                'your list repeats; if it should, say so in the same line as the item: '
                '`repeat: FREQ=MONTHLY;INTERVAL=1`.' % DUE_DAYS)
    if not live:
        nxt = ['- %s  next  %s%s' % (w.isoformat(), title[:200],
                                     ('  ' + note) if note else '')
               for w, kind, title, repeat, note in repeats if w is not None]
        return (head + '\nNothing is overdue or due in the next %d days. Repeating items, next '
                'instance:\n' % DUE_DAYS + '\n'.join(nxt[:DUE_SHOWN]))
    body, used, cut = [], 0, 0
    for when, kind, title, repeat, note in live:
        if when is None:
            line = '- UNREADABLE REPEAT — %s (%s)' % (title[:180], note)
        else:
            label = {'overdue': 'OVERDUE %dd' % (datetime.date.today() - when).days,
                     'today': 'DUE TODAY', 'soon': 'in %dd' % (when - datetime.date.today()).days}[kind]
            line = '- %s  %s  %s%s' % (when.isoformat(), label, title[:220],
                                       ('  ' + note) if note else '')
        if len(body) >= DUE_SHOWN or used + len(line) > DUE_CHARS:
            cut += 1
            continue
        body.append(line)
        used += len(line)
    tail = ('\n[%d more due item(s) did not fit; to-do-lists/%s.md has them all]' % (cut, amigo)
            if cut else '')
    return (head + '\nAn overdue dated item is a promise you made to yourself or to the human; '
            'doing it, moving its date with a reason, or deleting it with a reason are all '
            'answers. Leaving it untouched is not.\n' + '\n'.join(body) + tail)


def orientation(repo, state_dir, limit=6, todo_chars=6000):
    """The context every wake used to spend its first actions hunting for.

    Nothing here is new information; all of it is on disk in the checkout the run already has.
    That is the problem. A run with a 25-action budget spent 25-30 shell calls reading the
    agenda, the to-do list and git log, and then ran out of actions before it finished its own
    artefact — which is why five consecutive wakes screened the same condition and none of them
    delivered a write-up. Handing the text over costs one file read in Python and buys back the
    turns that were being spent on reconnaissance.
    """
    lines = []
    try:
        due = due_block(repo)
        if due:
            lines.append(due)
    except Exception as exc:                      # a broken block must not lose the whole wake
        lines.append('=== WHAT IS DUE ===\nunavailable this run (%s: %s); '
                     'run `python3 scripts/todo_due.py` by hand.'
                     % (type(exc).__name__, exc))
    todo = Path(repo) / 'to-do-lists' / (AMIGO + '.md')
    if todo.is_file():
        text = todo.read_text(encoding='utf-8', errors='replace').strip()
        if len(text) > todo_chars:
            text = text[:todo_chars].rstrip() + '\n[truncated here — read the file for the rest]'
        lines.append('=== YOUR TO-DO LIST (to-do-lists/' + AMIGO + '.md, verbatim) ===\n' + text)
    agenda = Path(repo) / 'agenda' / 'README.md'
    if not agenda.is_file():
        agenda = Path(repo) / 'channels' / 'agenda.md'
    if agenda.is_file():
        text = agenda.read_text(encoding='utf-8', errors='replace').strip()
        header = 'agenda/README.md' if (Path(repo) / 'agenda' / 'README.md').is_file() else 'channels/agenda.md'
        lines.append(f'=== THE AGENDA INDEX ({header}) ===\n' + text[:3500])
    tasks = Path(repo) / 'channels' / 'tasks.md'
    if tasks.is_file():
        text = tasks.read_text(encoding='utf-8', errors='replace').strip()
        lines.append('=== THE COMMONS TASK LEDGER (channels/tasks.md) ===\n' + text[:10000])
        for_you = open_rows_for(AMIGO, text)
        for key, header in (('cohort', COHORT_HEADER), ('named', NAMED_HEADER)):
            if for_you[key]:
                lines.append(header + '\n\n' + '\n\n'.join(for_you[key]))
        if for_you['dropped']:
            lines.append('[%d more open rows name you or the cohort and did not fit here; '
                         'channels/tasks.md has them in full]' % for_you['dropped'])
    decisions = Path(repo) / 'channels' / 'open-decisions.md'
    if decisions.is_file():
        text = decisions.read_text(encoding='utf-8', errors='replace').strip()
        lines.append('=== OPEN DECISIONS THAT NEED AN AMIGO (channels/open-decisions.md) ===\n'
                     'These are decisions the cuatro amigos must answer. A blank name has not answered. '
                     'If you are named below and have not answered, answer it in that file as part of '
                     'this run.\n' + text[:8000])
    rows = recent_runs(state_dir, limit=limit)
    if rows:
        out = ['=== THE LAST %d WAKES AND WHERE THEIR WORK WENT ===' % len(rows),
               'A path in a run\'s LAND line that is absent from this checkout exists only on a '
               'review branch, so no later wake has been able to build on it. Do not redo that '
               'work from nothing; say what should happen to it.']
        for r in rows:
            absent = [p for p in r['land_claimed'] if not (Path(repo) / p).exists()]
            line = '- %s  status=%s%s  claimed=%d path(s)' % (
                r['run_id'], r['status'], '  CUT OFF AT ITS ACTION CAP' if r['cut_off'] else '',
                len(r['land_claimed']))
            if absent:
                line += '  NOT IN MAIN: %s' % ', '.join(absent[:6])
            elif r['land_claimed']:
                line += '  (every claimed path is in main)'
            # A path can be in main and still not be this run's work: the 2026-10-10 case named a
            # tracked file it never touched, so "the file exists" proved nothing. Compare the claim
            # against the run's own diff — the one record the worker cannot write.
            claimed_only = [p for p in r['land_claimed']
                            if p not in r.get('changed_paths', [])
                            and not p.startswith(PIPELINE_WRITTEN)]
            if claimed_only:
                line += ('  CLAIMED, NOT IN ITS DIFF: %s (verify before trusting the report: either '
                         'another step wrote it, or the run reported work it did not do)'
                         % ', '.join(claimed_only[:6]))
            if r.get('refused'):
                line += '  LANDING REFUSED: %s' % r['refused']
            out.append(line)
            if r['first_line']:
                out.append('    its own first line: %s' % r['first_line'])
        lines.append('\n'.join(out))
    return '\n\n'.join(lines) + '\n' if lines else ''


def unlanded(state_dir, repo, limit=8):
    """Paths recent runs claimed to land that are absent from main, as (run_id, path).

    `result.json` is a snapshot: it records a status at the moment a run ends and never revisits
    it, so counting `awaiting_review` rows cannot tell you whether that work is still missing.
    Counting against main can. On 2026-09-20 this returned nothing across 21 `awaiting_review`
    runs, which is how the day's "the unlanded pile is 21 deep" was corrected.
    """
    out = []
    for row in recent_runs(state_dir, limit=limit):
        for path in row['land_claimed']:
            if not (Path(repo) / path).exists():
                out.append((row['run_id'], path))
    return out


RECOVERY_MAX_AGE = 24 * 3600


def unfinished_verdicts(state_dir, now=None, max_age=RECOVERY_MAX_AGE):
    """Runs that reached a verdict and whose lander never recorded one, oldest first.

    Measured 2026-11-03: 73 of 954 `awaiting_review` runs have no `land` field at all. The worker
    finished, `result.json` was written, the lander started, and the process ended — a restart, a
    sleeping machine, a kill. Nothing revisits `result.json`, so the work sits in `changes.patch`
    looking, from the daily report, exactly like work that was never done.

    A run is included only if it could still be landed with a straight face: a verdict
    (`awaiting_review`), no `land` key, a `changes.patch` to apply, and younger than `max_age` — past
    a day the diff is against a main that has moved and re-applying it is likelier to be wrong than
    useful.
    """
    out = []
    now = time.time() if now is None else float(now)
    root = Path(state_dir) / 'runs'
    try:
        runs = sorted(root.glob('*'))
    except OSError:
        return out
    for run in runs:
        result_path = run / 'result.json'
        try:
            result = json.loads(result_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if not isinstance(result, dict) or result.get('status') != 'awaiting_review':
            continue
        if 'land' in result:
            continue
        if not (run / 'changes.patch').is_file():
            continue
        try:
            age = now - result_path.stat().st_mtime
        except OSError:
            continue
        if age > max_age:
            continue
        out.append((run, result))
    out.sort(key=lambda pair: pair[0].name)
    return out


def finish_unlanded(state_dir, now=None, max_age=RECOVERY_MAX_AGE, lander=None):
    """Land the oldest verdict a previous wake failed to finish. One per wake, never raises.

    The lander runs the repository's own suite, so this costs the wake a couple of minutes of wall
    clock before it clones — which is why it is one run, not a drain, and why it happens before the
    battery guard would have stopped real work (a recovered landing is cheap; a model session is not).

    Returns {'run_id', 'land'} or None. An exception here must not cost the wake it precedes: the
    work being recovered is already lost once.
    """
    try:
        pending = unfinished_verdicts(state_dir, now=now, max_age=max_age)
        if not pending:
            return None
        run, result = pending[0]
        if lander is None:
            import land_runs
            lander = land_runs.land
        outcome = lander(run, dry_run=False)
        result['land'] = outcome
        result['land_recovered_by'] = 'wake_engine.finish_unlanded'
        save_json(run / 'result.json', result)
        log.info('recovered an unfinished verdict: run %s landing: %s', run.name, outcome)
        return {'run_id': run.name, 'land': outcome}
    except BaseException as exc:                          # noqa: BLE001
        log.warning('could not finish an unfinished verdict: %s', type(exc).__name__)
        return None


def prune_old_runs(state_dir, keep=3):
    """Drop the redundant checkout from runs older than the newest `keep`.

    Measured 2026-09-17: 18 runs held 1.3 GB, because every run keeps a whole
    checkout of the commons — ~75 MB each, six wakes a day, about 450 MB a day
    added to the machine that also holds the credentials and the private memory.
    Nothing is lost by dropping the checkout: the deliverable was always the
    small files beside it — report.txt (what the run said it did),
    changes.patch (the full diff, new files included), result.json (its status),
    instructions.md (what it was told). The checkout is only needed while the
    run's draft is still being landed, which is why the newest `keep` stay whole.
    """
    runs = sorted((Path(state_dir) / 'runs').glob('*'), key=lambda p: p.name, reverse=True)
    freed = 0
    for run in runs[keep:]:
        repo = run / 'repo'
        if repo.is_dir():
            size = sum(f.stat().st_size for f in repo.rglob('*') if f.is_file())
            shutil.rmtree(repo, ignore_errors=True)
            freed += size
        transcript = run / 'worker.jsonl'
        if transcript.is_file() and not (run / 'worker.jsonl.gz').exists():
            import gzip
            with gzip.open(str(transcript) + '.gz', 'wb') as dst, open(transcript, 'rb') as src:
                shutil.copyfileobj(src, dst)
            transcript.unlink()
    if freed:
        logging.getLogger(__name__).info('pruned %d older run checkouts, %.1f MB freed',
                                         max(0, len(runs) - keep), freed / 1e6)


class PeriodicWorker:
    """Poll a deadline independently of chat/mail, once per interval at most.

    Persist the start time before calling the worker: failures/crashes cannot
    cause rapid paid retries. First start waits a full interval. A restart keeps
    the previous deadline. A stopped/restarted process releases flock in the OS.
    """
    def __init__(self, interval_seconds, state_dir, callback, clock=time.time, stop=None):
        if not math.isfinite(interval_seconds) or interval_seconds <= 0:
            raise ValueError('interval must be finite and positive')
        self.interval = interval_seconds
        self.root = Path(state_dir)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.callback = callback
        self.clock = clock
        self.stop = stop or threading.Event()
        self.thread = None

    def poll(self):
        with (self.root / 'timer.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return 'busy'
            path = self.root / 'timer.json'
            now = self.clock()
            if not path.exists():
                save_json(path, {'last_attempt': now})
                return 'initialized'
            state = json.loads(path.read_text(encoding='utf-8'))
            last = float(state['last_attempt'])
            if not math.isfinite(last):
                raise ValueError('invalid persisted timer timestamp')
            if now < last:
                # Clock moved backward: wait a full interval, no catch-up storm.
                save_json(path, {'last_attempt': now})
                return 'clock_reset'
            if now - last < self.interval:
                return 'waiting'
            if now - last > self.interval + 300:
                # The machine was suspended (lid closed, or asleep): several clocks are overdue at
                # once. Wait a stable per-clock offset so they do not all start together. The
                # deadline is already stamped below, so this can never turn into a retry storm.
                self.stop.wait(_spread_offset(self.root))
            save_json(path, {'last_attempt': now})
            self.callback()
            return 'ran'

    def run_forever(self):
        log.info('independent tick clock started (interval=%ss)', self.interval)
        while not self.stop.is_set():
            try:
                self.poll()
            except Exception as exc:
                log.warning('tick clock failed: %s', type(exc).__name__)
            self.stop.wait(min(30.0, self.interval))

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return self.thread
        self.thread = threading.Thread(target=self.run_forever, name=AMIGO + '-idle-clock',
                                       daemon=True)
        self.thread.start()
        return self.thread



def battery_state():
    """(on_battery, percent, watts) from pmset/ioreg. No sudo. Never raises.

    Added 2026-09-25 because the human wants to work unplugged with the lid closed (in the car,
    in the recliner, at the rover table) and asked the only question that matters for that
    decision: how fast does the battery actually go? Answering it needs watts, not a guess.
    """
    try:
        out = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True,
                             timeout=10).stdout
        on_battery = 'Battery Power' in out
        m = re.search(r'(\d+)%', out)
        pct = int(m.group(1)) if m else 100
    except Exception:
        return (False, 100, None)
    watts = None
    if on_battery:
        try:
            reg = subprocess.run(['ioreg', '-rn', 'AppleSmartBattery'], capture_output=True,
                                 text=True, timeout=10).stdout
            a = re.search(r'"Amperage" = (-?\d+)', reg)
            v = re.search(r'"Voltage" = (\d+)', reg)
            if a and v:
                watts = abs(int(a.group(1))) * int(v.group(1)) / 1e6
        except Exception:
            watts = None
    return (on_battery, pct, watts)


def runtime_left(percent, watts):
    """Rough hours left at the present draw, from this machine's own capacity."""
    try:
        reg = subprocess.run(['ioreg', '-rn', 'AppleSmartBattery'], capture_output=True,
                             text=True, timeout=10).stdout
        cap = re.search(r'"AppleRawMaxCapacity" = (\d+)', reg)
        volt = re.search(r'"Voltage" = (\d+)', reg)
        if not (cap and volt) or not watts:
            return None
        wh = int(cap.group(1)) * int(volt.group(1)) / 1e6
        return (wh * percent / 100.0) / watts
    except Exception:
        return None

def _spread_offset(root, span=600):
    """A stable per-clock delay in [0, span), so clocks do not all fire at the same moment.

    Added 2026-09-25, after the human asked whether closing the lid stops the work. It does end
    the work while the machine is suspended — and when it wakes, `poll` sees every overdue clock
    at once and fires them all inside the same half-minute: up to four wake sessions starting
    together, each spending money, three of them finding the repository already being written to.
    The offset is derived from the clock's own state directory rather than coordinated, because
    the clocks cannot talk to each other; it only applies after a long overdue gap, so ordinary
    ticking is unaffected.
    """
    return zlib.crc32(str(root).encode('utf-8')) % span

def execute(argv, cwd, logfile, env, timeout):
    with Path(logfile).open('w', encoding='utf-8') as output:
        process = subprocess.Popen(argv, cwd=str(cwd), env=env, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return 124


# 2026-10-06 — the human's request: stop sending him a report of what each wake did. What the wakes
# did now reaches him counted, once a day, in `scripts/daily_report.py` (backed by the item ledger
# `channels/item_ledger.py`). The summary below is still composed and written into the run
# directory, so nothing is lost from the record; it just stops arriving as six texts a day. A wake
# that has something he needs still reaches him: that path is `scripts/tell_human.py`, which is
# untouched by this flag, and REQUESTs go through it. Flip this to True to restore the old behaviour.
WAKE_SUMMARY_NOTIFY = False


def worker_env(tag=None, providers=None, extra_env=None):
    """The environment a wake's model session runs in.

    One allow-list, and it is the whole boundary for a model session that can run commands:
    nothing arrives from the parent shell except these names, so a Telegram token or another
    body's mail password cannot leak into the worker.

    2026-11-03: this lived inline in `run_session`, which meant the only way to check it was to
    read it — and nobody did, for four days, while Gwen's DashScope key was mapped to a name her
    provider never asks for and every one of her wakes died with HTTP 401. Then it was six copies.
    Now it is one, and the provider key each body carries comes from `Config.providers` rather
    than from a name typed into the file.
    """
    tag = tag or AMIGO.upper()
    providers = tuple(providers if providers is not None else CONFIG.provider_list())
    extra_env = tuple(extra_env if extra_env is not None else CONFIG.extra_env)
    allowed = ['HOME', 'PATH', 'LANG', 'LC_ALL', 'TMPDIR', 'SSL_CERT_FILE']
    for provider in providers:
        name = PROVIDER_KEYS.get(provider)
        if name:
            allowed += [name, name + '_' + tag]
    allowed += ['SYMPOSIUM_MAIL_USER_' + tag, 'SYMPOSIUM_MAIL_APP_PASSWORD_' + tag]
    allowed += list(extra_env)
    env = {k: os.environ[k] for k in allowed if k in os.environ}
    # A suffixed key is this body's own key; goose reads the plain name, so map it for the child.
    # The suffixed name is kept as well because a custom provider may declare exactly that name
    # (`custom_alibaba.json` asks for `DASHSCOPE_API_KEY_GWEN`).
    for provider in providers:
        name = PROVIDER_KEYS.get(provider)
        if not name:
            continue
        suffixed = os.environ.get(name + '_' + tag)
        if suffixed:
            env[name] = suffixed
            env[name + '_' + tag] = suffixed
    # No model call for auto-naming; the session is named explicitly from its run id.
    env['GOOSE_DISABLE_SESSION_NAMING'] = 'true'
    return env


def run_session(config, goose_bin, source_repo, state_dir, provider, model, *args, **kwargs):
    """Run one wake of the configured kind, then leave one trace of it.

    `_run_standard` wakes, works in a private checkout and lands its diff; `_run_handoff` claims
    one Codex handoff, performs it and publishes the result. Both return the same shape of result,
    and every exit — including an exception raised outside the engine's own try — leaves
    `tick-state/last-wake.json` (channels/wake_heartbeat.py), because a wake that declines to
    start writes no run directory and a report that counts runs reads that as idleness.
    """
    engine = _run_handoff if config.engine == 'handoff' else _run_standard
    try:
        result = engine(config, goose_bin, source_repo, state_dir, provider, model, *args, **kwargs)
    except BaseException as exc:                           # noqa: BLE001
        if _record_wake_outcome is None:
            log.error('a wake raised %s and left no trace: wake_heartbeat.py is not importable',
                      type(exc).__name__)
        else:
            _record_wake_outcome(state_dir, {'status': 'harness_failed',
                                             'error': type(exc).__name__})
        raise
    if _record_wake_outcome is None:
        log.error('a wake finished (%s) and left no trace: wake_heartbeat.py is not importable',
                  result.get('status'))
    else:
        _record_wake_outcome(state_dir, result)
    return result


def _run_standard(config, goose_bin, source_repo, state_dir, provider, model, notify=None,
                 timeout=600, max_turns=25, executor=execute):
    """Return a result only from THIS successful run, never an old shared file.

    No automatic push or merge. New checkout and logs remain under state_dir for
    review. No mutation of the shared checkout/index. The worker still runs under
    the host user's OS identity: a checkout boundary is not security containment.
    """

    # Do not start a long agentic wake on a battery that is already low: a wake runs for up to ten
    # minutes with the CPU busy, and the human accepted the risk of an unplugged, lid-closed machine
    # but not of work still running when the power goes. Telegram replies are unaffected — those are
    # one short call, and reaching Dawn from the Pixel is the thing he wants to keep working.
    # 2026-11-03: `run_id` is named in the skip result below and was assigned after
    # this guard, so the guard raised NameError instead of skipping — in the one
    # condition it exists for (unplugged, under 20%), which no test had produced.
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    _on_batt, _pct, _watts = battery_state()
    if _on_batt and _pct < 20:
        log.info('wake skipped: on battery at %d%% (work stops before the machine does)', _pct)
        return {'run_id': run_id, 'status': 'skipped_low_battery', 'on_battery_percent': _pct,
                'workspace': None, 'changed_paths': [], 'land_claimed': []}
    # 2026-11-03: 73 runs reached a verdict and died inside the lander. Nothing revisits
    # `result.json`, so their diffs sat in changes.patch looking like work nobody did. Finish ONE
    # of them before starting new work — oldest first, younger than a day, never a drain: a wake
    # that spent its whole slot re-landing is a wake that did nothing today either.
    finish_unlanded(state_dir)
    root = Path(state_dir)
    run_dir = root / 'runs' / run_id
    run_dir.mkdir(parents=True, mode=0o700)
    repo = run_dir / 'repo'
    # Don't pass Telegram credentials or inherited Git overrides to the worker.
    # This amigo's OWN mail pair IS passed (2026-10-04): the wake may send as itself.
    env = worker_env()
    result = {'run_id': run_id, 'provider': provider, 'model': model,
              'workspace': str(repo), 'status': 'starting'}
    try:
        subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', '--single-branch',
                        str(source_repo), str(repo)], check=True, capture_output=True,
                       env=env, timeout=60)
        # The clone has committed source only, never another amigo's in-progress edits.
        subprocess.run(['git', '-C', str(repo), 'remote', 'remove', 'origin'],
                       check=True, capture_output=True, env=env, timeout=10)
        base = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], env=env, text=True).strip()
        report = run_dir / 'report.txt'
        instruction = run_dir / 'instructions.md'
        orient = orientation(repo, state_dir)
        missing = unlanded(state_dir, repo)
        if missing:
            # The gap the item called "failure telemetry" was never an instrument problem: the
            # record was there and nothing read it. This reads it, once per wake, and names the
            # work rather than the run that produced it.
            log.warning('%d path(s) claimed by recent runs are not in main: %s', len(missing),
                        ', '.join('%s (%s)' % (p, r) for r, p in missing[:5]))
        instruction.write_text(
            f'You are {AMIGO_IDENTITY} in the LLM Symposium. This is a local '
            'clock-triggered work session; no person sent a message. Whatever you change is landed '
            'on main automatically once the repository\'s tests show no new failures — you do not publish it '
            'and you do not need to ask for delivery. '
            'ORIENTATION IS DONE FOR YOU (added 2026-09-20): your to-do list, the agenda index, the '
            'commons task ledger (channels/tasks.md — where work raised in the human\'s chat with an '
            'amigo now lands, since that channel can talk but cannot write) and a summary of the '
            'last few wakes are copied at the end of this file, and the paths that never reached '
            'main are named there. Read that instead of re-deriving the state of the world with '
            'shell calls. '
            'UNLANDED IS NOT MISSING (added 2026-09-23, after a measured loop): a path named as '
            'never having reached main is a DELIVERY state, not work to be done again. Ten of the '
            'previous twenty wakes spent their whole budget recomputing work that already exists on '
            'a review branch — the vulvodynia screen was written, recovered and re-landed four '
            'times — because each wake read the same missing-path list and redid it. Do not '
            'recompute, re-verify or re-derive a path on that list. If it needs a reviewer, say so '
            'in one line and choose different work. '
            'ROTATE THE SUBJECT (same date): say in the first line of your report which area this '
            'wake is in, and name what the last two wakes were in. Do not spend a third consecutive '
            'wake in the same area unless the reason is on the record — a reviewer is needed, or the '
            'previous wake was cut off mid-artefact. If the top of your to-do list is blocked on '
            'someone else, that is exactly when to take the second item, or something not on the '
            'list at all. '
            'TAKE THE LIST IN TURN (added 2026-09-25, from the human\'s 09-24 conversation with '
            'Gemini): do not skip items and do not re-order them to suit your preference. The order '
            'is the decision; if an item looks wrong, do it, or move it with the reason on the '
            'record. '
            'A REVIEW CAN BE THE WHOLE WAKE (this paragraph used to say the opposite; withdrawn '
            '2026-10-21 because the old rule and the review rule contradicted each other, and a wake '
            'that believed the old one did its review and then treated the wake as unfinished). The '
            'September rule was "a critique is not the turn\'s payload — the wake has to leave an '
            'artifact behind". That is now false as written. A review that ENDS WITH A VERDICT '
            'RECORDED IN THE LEDGER — accomplished, postponed or rejected, with its reason — is a '
            'finished wake, and it may be the whole of it. Do the review first, record the verdict '
            'second, write the prose third, and only then, if you have turns left, do anything else. '
            'A review you opened and did not record leaves nothing. What survives from the old rule: '
            'commentary that changes no record and closes no item finishes nothing — writing about '
            'someone else\'s work is not reviewing it. '
            'THE REJECT QUEUE, IN FULL (rewritten 2026-09-25 from the human\'s own words, after he '
            'corrected a one-line version of this rule as an oversimplification): if you can do the '
            'next to-do item, do it. If you cannot, put it on channels/reject-queue.md — and that '
            'does not count as work. Review EVERY item already on that queue, every wake: if you can '
            'do one, do it and take it off the queue (that counts as work); if you cannot, add a line '
            'saying you looked and cannot, with a reason (that does not count as work). When all four '
            'of us have said we cannot, the item becomes a request for the human\'s judgement and '
            'the request is marked in the file. Desi\'s sweep does the counting, never you: do not '
            'decide that you are the fourth, and do not notify him about the queue yourself. '
            'REVIEW FIRST, AND KEEP GOING (rewritten 2026-10-22: one review per wake never drained '
            'anything). Before you add anything to the repository, open `python3 channels/item_ledger.py '
            '--queue <your name>` and clear as many of those items as your turns allow, writing the '
            'verdict the moment you reach it and never at the end of the wake - a wake cut off at its '
            'cap keeps only what it has already written. Then `--reading-queue <your name>`: the same '
            'job on work that is already in the repository and was closed by the landing machine '
            'without anyone reading it. On 22 October there were 252 of those and no queue contained '
            'them at all, which is why reading "one item from your queue" could be obeyed perfectly '
            'forever and never touch them. About twenty-three pieces of work arrive each day and one or '
            'two are read by a model; that ratio is the whole problem. A wake whose entire content is '
            'two verdicts, and no artifact, is a good wake. '
            'YOUR REVIEW QUEUE, AND THE EXIT RULE (rewritten 2026-10-09, after the human asked what '
            'our assignment algorithm was and the honest answer was: there is none — so nothing was '
            'ever addressed to anybody by name, and W could not drain no matter how much anyone '
            'wanted to work. His rule is now the rule: (a) if one amigo is plainly best suited, '
            'assign that amigo and write one line saying why; (b) otherwise draw at random among the '
            'least expensive, and the draw is frozen to the item. Two things are absolute: the author '
            'is never the reviewer, and the draw does not re-roll. '
            'Start with `python3 channels/item_ledger.py --queue ' + AMIGO + '` — the waiting items that carry '
            'YOUR name, never one you wrote. Do not drift to the oldest item in the pile. If your '
            'queue is empty, check `python3 channels/item_ledger.py --holes`: items waiting with no '
            'name on them are the failure, not the backlog, and naming them is the work — `--draw` '
            'names all of them by the cheap-and-random rule, `--assign <id> --to <amigo> --reason '
            '"why"` when one is plainly best suited, and the reason is mandatory because a name '
            'without a reason is a mood that drifts to whoever spoke last. '
            'Then work your queue, oldest first, and judge from what is on disk — the run\'s report '
            'at ~/LLM/<its amigo>-bot/tick-state/runs/<id>/report.txt and the paths the item names — '
            'not by re-doing the work. EVERY exit leaves W into an existing queue; nothing goes into '
            'nowhere, and there is no fifth state: `--state accomplished` ONLY if you did the work '
            'yourself in this wake, with a reason that names what you did (a path or a run id) — a '
            'stamp is not a review and the human forbade exactly that; `--state postponed` with the '
            'reason that stops it, which is what puts it on the blockers list and is worth more than '
            'any count; `--state rejected` with the reason it should never be done. The reason is '
            'mandatory in all three, and it is the whole record. This is work, and it may be the '
            'whole of your wake. '
            'CHECK THE REQUEST REGISTER BEFORE THE CLOCK DOES (added 2026-10-08, after D-5): read '
            'governance/request-register.md, and for every row still `open`, ask whether it is '
            'ALREADY TRUE in the world — not whether the human remembers doing it. D-5 sat open for '
            'three days after he had finished every one of its six steps, and the automated nudge '
            'emailed him about it at 16:53 on the day it was finally closed: a clock that asks '
            'without checking nags a man about work he did before breakfast. If a request is '
            'plainly satisfied — the accounts, files, credentials or statements it asked for all '
            'exist and you can name them — close it with `python3 scripts/tell_human.py --amigo '
            + AMIGO +
            ' --close <id>`, which flips the register and tells him in one line. If any part of '
            'it cannot be checked from here, leave the row alone and say in your report what you '
            'could not check. Never close by inference: "he probably did it" is not evidence. '
            'ROTATE THE TO-DO LIST EVERY TURN (added the same day, and it is a separate rule from '
            'ROTATE THE SUBJECT above): take the next item in turn and leave the list one item '
            'further on than you found it — done, moved to the reject queue, or passed over with the '
            'reason on the record. The top of the list must not be the same item next time. '
            'Measured over 35 runs: 30 of them were cut off at goose\'s own '
            'action cap ("maximum number of actions I can do without user input") and most of their '
            'actions went on reconnaissance, which is why five consecutive wakes screened the same '
            'condition and none delivered a write-up. '
            'START WITH THE ARTEFACT, NOT WITH THE RESEARCH (same reason). Do the smallest thing '
            'that is complete — a file, a table, a number checked against its source — write it to '
            'disk, then improve it. A partial artefact on disk survives being cut off; a '
            'half-finished investigation does not. '
            'Then do the work you judge most worth doing — an agenda item, a '
            'question the commons has left open, or something you believe deserves to exist. You are '
            'NOT limited to what is itemised there: if the most valuable thing you can see is not on '
            'any list, do that instead and say why in the report. Work on anything you like. The only '
            'real limits are the ones below and your own turn and time budget. If nothing is worth '
            'doing, doing nothing is correct. '
            'This is a private checkout for review, NOT the live shared repository. Do not '
            'edit any other checkout, private chats, credentials, or bot files. Do not '
            'push, post publicly, or change account settings. Mail is allowed: you may send as yourself, from your own mailbox, with your own byline. Do not invent '
            'artifacts or mark tasks done without checking the files. Validate any change. '
            'No private Dawn/SillyTavern content is in scope.\n\n'
            'THE REPORT IS WRITTEN FIRST, NOT LAST (repaired 2026-09-15 after five wakes: the '
            'report used to be written at the end, so a run that ran out of turns or time lost '
            'everything it had done). THE FIRST LINE OF THIS REPORT IS HOW THIS WAKE\'S ITEM IS NAMED '
            'IN THE HUMAN\'S DAILY REPORT (changed 2026-10-08: wake summaries are no longer texted to '
            'him — he asked for one counted report a day instead), and he reads that and does not read the repository. Write that first line as one plain sentence, in the first person, in ordinary English: what you did, in words a non-technical person would use. No file paths, no timestamps, no status words, no method names. If you cannot say what you did in one plain sentence, that is a sign you did not really do anything. Before anything else, write one line to ' +
            str(report) + ' saying what you intend to do. After each step, replace it with what '
            'you have actually done so far. Keep it to a few plain sentences. If your turn or '
            'time budget runs out, whatever is in that file is the whole record of this run: an '
            'honest "started X, did not finish" is worth more than a missing file, because a '
            'missing file discards the run. Write it with a shell command, and update it the same '
            'way. Nothing you write here reaches the commons — this is a private checkout and nobody '
            'sees it. WRITE THE LAND LINE WITH YOUR FIRST WRITE, NOT AT THE END: if you intend to '
            'change files worth keeping, make one line of the report read `LAND: <paths>`, and keep it '
            'accurate as you go. The bot lands those paths on main once the tests show no new failures. That line carried the same defect the report had until 2026-09-15 — asked '
            'for last, in a run with a limit — and it has now cost real work: the runs of 09-16 and '
            '09-17 built a complete new Works entry, verified its data path by hand, and lost the '
            'delivery by running out of turns before naming it. A run that did work and did not land '
            'it has delivered nothing, however good the work was. DELIVERY NO LONGER DEPENDS ON THAT LINE (changed 2026-09-17): if you changed files, the bot delivers them automatically, and the LAND line is now a convenience for the reader rather than a condition. Your transcript is not the '
            'report.\n', encoding='utf-8')
        if orient:
            with open(instruction, 'a', encoding='utf-8') as fh:
                fh.write('\n\n' + orient)
        args = [str(goose_bin), 'run', '--provider', provider, '--model', model,
                '--with-builtin', 'developer', '--instructions', str(instruction),
                '--max-turns', str(max_turns), '--output-format', 'stream-json',
                # 2026-09-27: --no-session, not --name. Naming on 2026-09-20 made the wakes
                # distinguishable, but they still filled the human's chat list, and deleting them
                # by hand is a mop the next tick undoes (5 regrew within four hours). --no-session
                # records the run as a hidden session (session_type='hidden'), which the session
                # list does not show, while the run's own diagnostics read worker.jsonl (the Goose
                # stdout stream), not the session store. --name is rejected together with
                # --no-session (verified: exit 2), so it is dropped. Fix the producer, not the list.
                '--no-session']
        code = executor(args, repo, run_dir / 'worker.jsonl', env, timeout)
        result['worker_exit'] = code
        result['timed_out'] = (code == 124)
        # 2026-09-20: the cost of the wake and whether it was cut off at its action cap. Both were
        # knowable and neither was recorded, so a run that stopped mid-sentence at 900k tokens
        # looked exactly like one that finished.
        usage = worker_usage(run_dir / 'worker.jsonl')
        result['total_tokens'] = usage['total_tokens']
        result['cut_off'] = usage['cut_off']
        # Record actual file changes separately from the worker's one-sentence claim.
        subprocess.run(['git', '-C', str(repo), 'add', '-N', '.'], env=env,
                       check=True, capture_output=True, timeout=15)
        patch = subprocess.check_output(['git', '-C', str(repo), 'diff', '--no-ext-diff',
                                         '--no-textconv', '--binary', base], env=env, timeout=20)
        (run_dir / 'changes.patch').write_bytes(patch)
        result['changed_paths'] = subprocess.check_output(
            ['git', '-C', str(repo), 'diff', '--no-ext-diff', '--name-only', base],
            env=env, text=True, timeout=10).splitlines()
        # The exit code ANNOTATES; it does not decide. A run that timed out after doing real work
        # has a result, and until 2026-09-15 the code threw that result away on a non-zero exit.
        changed = result['changed_paths']
        report_text = ''
        if report.is_file() and not report.is_symlink() and report.stat().st_size <= 8192:
            report_text = report.read_text(encoding='utf-8').strip()
        if report_text and changed:
            result['status'] = 'awaiting_review'
            result['worker_report'] = report_text[:1200]
        elif report_text:
            # A report is not a deliverable. Git decides whether anything happened; a report
            # without a change is kept for review but is never announced as an outcome.
            result['status'] = 'no_work_done'
            result['worker_report'] = report_text[:1200]
        elif changed:
            # The 01:14 and 05:14 runs: real edits, no report, silently nothing. Now named.
            result['status'] = 'unreported_changes'
        elif code != 0:
            result['status'] = 'timeout' if code == 124 else 'worker_failed'
        else:
            result['status'] = 'missing_or_invalid_report'
        # 2026-09-18: check the report's own LAND claim against the diff — deliberately AFTER the
        # status chain, because the first version of this sat inside it and re-attached the
        # trailing `elif code != 0` to itself, turning every unreported-changes run into a timeout.
        # A run that names files it never wrote is how it overclaims delivery with nobody noticing.
        if report_text:
            claimed = expand_land_claims(land_claimed(report_text), changed)
            result['land_claimed'] = claimed
            result['land_missing'] = [c for c in claimed if c not in changed]
            if result['land_missing']:
                log.warning('run %s claimed to land %d path(s) it did not change: %s',
                            run_id, len(result['land_missing']), ', '.join(result['land_missing'][:6]))
        if result.get('cut_off'):
            log.warning('run %s was cut off at its action cap after %s tokens with %d changed '
                        'path(s) — the work it did not reach is not in the report',
                        run_id, result.get('total_tokens'), len(changed))
        save_json(run_dir / 'result.json', result)

        # 2026-09-25: land the work instead of parking it. The human said it plainly — "you report
        # the same work over and over, so I believe it never did get done" — and he was right by
        # construction: this clone has `origin` removed, the instruction tells the model it cannot
        # publish, and nothing ever moved the diff into the repository. Measured: of 54 runs that
        # produced a diff, 3 had landed, 3 had not, and 48 could no longer be compared; the same
        # paths were claimed by twelve, eight and eight separate wakes. Landing now happens here,
        # gated on the repository's own suite showing no NEW failures, and the outcome is recorded
        # so the note he receives can say what is actually in the repository.
        if result.get('status') == 'awaiting_review':
            try:
                import land_runs
                outcome = land_runs.land(run_dir, dry_run=False)
            except Exception as exc:  # never let bookkeeping kill a run
                outcome = 'landing_error: %s' % exc
            result['land'] = outcome
            save_json(run_dir / 'result.json', result)
            log.info('run %s landing: %s', run_id, outcome)

        if notify and WAKE_SUMMARY_NOTIFY:
            # 2026-09-17: these messages used to be status codes and file paths. He reads texts and
            # not the repository, and he said plainly that they made no sense to him. Plain English,
            # first person, no paths, no timestamps, no status words — and always say whether he
            # needs to do anything, because that is the only question he is actually asking.
            head = (report_text.splitlines() or [''])[0][:300]
            if result.get('status') == 'awaiting_review' and result.get('land') == 'landed':
                msg = f"{head}\n\nStatus: in the repository; action: none." if head else "Status: in the repository; action: none."
                notify(msg)
            elif result['status'] == 'awaiting_review':
                msg = f"{head}\n\nStatus: awaiting reviewer; action: none." if head else "Status: awaiting reviewer; action: none."
                notify(msg)
            elif result['status'] == 'unreported_changes':
                notify("Changed files without a summary report.\n\nStatus: parked, unpublished; action: none.")
            elif result['status'] in ('timeout', 'worker_failed', 'missing_or_invalid_report'):
                notify("Ran out of time or lost thread partway through.\n\nStatus: no artifact; action: none.")
            # 'no_work_done' is deliberate: the worker reported and git agrees nothing changed,
            # so there is nothing to tell him. Six wake-ups a day must not become six texts.
    except Exception as exc:
        result['status'] = 'failed'
        result['error_type'] = type(exc).__name__
        save_json(run_dir / 'result.json', result)
        log.warning('local session failed (%s), run=%s', type(exc).__name__, run_id)
    log.info('local tick result: status=%s run=%s', result['status'], run_id)
    try:
        prune_old_runs(root)
    except Exception as exc:  # pruning must never fail a run or hide its result
        log.warning('could not prune old runs: %s', type(exc).__name__)
    return result


# ---------------------------------------------------------------------------------------------
# Tarik's engine: one claimed Codex handoff at a time (his seat is a queue, not a to-do list).
# Moved here 2026-11-03 so the six bodies run one engine; `Config(engine='handoff')` selects it.
# ---------------------------------------------------------------------------------------------
HANDOFF_PATH = 'channels/tarik-goose-handoff.json'
HANDOFF_URL = 'https://raw.githubusercontent.com/LindsayRidgeway/llm-symposium/main/' + HANDOFF_PATH


def load_handoff_queue(opener=None):
    """Fresh public queue only. No cached or broad-work fallback is permitted."""
    request = urllib.request.Request(HANDOFF_URL + '?wake=' + uuid.uuid4().hex,
                                     headers={'Cache-Control': 'no-cache'})
    with (opener or urllib.request.urlopen)(request, timeout=10) as response:
        raw = response.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError('handoff queue too large')
    return json.loads(raw.decode('utf-8'))


def oldest_pending_handoff(queue):
    """Validate the whole queue before allowing one oldest pending Codex task."""
    if not isinstance(queue, dict) or type(queue.get('version')) is not int or queue['version'] != 1:
        raise ValueError('invalid handoff version')
    tasks = queue.get('tasks')
    if not isinstance(tasks, list) or len(tasks) > 100:
        raise ValueError('invalid handoff tasks')
    required = {'id', 'status', 'title', 'reason_for_goose', 'instructions',
                'expected_result', 'created_utc', 'source'}
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or not required.issubset(task):
            raise ValueError('invalid handoff task')
        if any(not isinstance(task[key], str) or not task[key].strip() or len(task[key]) > 20000
               for key in required):
            raise ValueError('invalid handoff field')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', task['id']) or task['id'] in seen:
            raise ValueError('invalid handoff id')
        seen.add(task['id'])
        if task['status'] not in ('pending', 'in_progress', 'completed', 'blocked', 'uncertain') or task['source'] != 'codex':
            raise ValueError('invalid handoff status or source')
        if 'allowed_targets' in task and (not isinstance(task['allowed_targets'], list) or
                any(not isinstance(target, str) or not target.strip() for target in task['allowed_targets'])):
            raise ValueError('invalid allowed targets')
        if any(key in task and not isinstance(task[key], dict) for key in ('claim', 'result')):
            raise ValueError('invalid handoff metadata')
        created = datetime.datetime.fromisoformat(task['created_utc'].replace('Z', '+00:00'))
        if created.tzinfo is None or created.utcoffset() != datetime.timedelta(0):
            raise ValueError('handoff creation must be UTC')
    pending = [task for task in tasks if task['status'] == 'pending']
    return min(pending, key=lambda task: (
        datetime.datetime.fromisoformat(task['created_utc'].replace('Z', '+00:00')), task['id'])) if pending else None


def _queue_cas(task_id, mutate, runner=None, artifact=None):
    """Queue plus optional verified result in one nonforce commit from a fresh clone."""
    runner = runner or subprocess.run
    with tempfile.TemporaryDirectory(prefix='tarik-handoff-') as temporary:
        repo = Path(temporary) / 'repo'
        def run(args):
            return runner(['git', '-C', str(repo), *args], capture_output=True, text=True,
                          check=True, timeout=60)
        runner(['git', 'clone', '--quiet', '--depth', '1', '--no-checkout',
                'https://github.com/LindsayRidgeway/llm-symposium.git', str(repo)],
               capture_output=True, text=True, check=True, timeout=60)
        run(['read-tree', 'HEAD'])  # Keep all unrelated tree entries in the queue-only commit.
        queue = json.loads(run(['show', 'HEAD:' + HANDOFF_PATH]).stdout)
        oldest_pending_handoff(queue)  # Validate before any write.
        task = next((entry for entry in queue['tasks'] if entry['id'] == task_id), None)
        if task is None:
            raise ValueError('handoff disappeared')
        mutate(queue, task)
        path = repo / HANDOFF_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        paths = [HANDOFF_PATH]
        if artifact is not None:
            validate_handoff_outcome(artifact, task)
            artifact_path = 'channels/tarik-goose-results/' + task_id + '.json'
            output = repo / artifact_path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            paths.append(artifact_path)
        run(['add', '--', *paths])
        run(['-c', 'user.name=Tarik Goose', '-c', 'user.email=tarik.s.commons@gmail.com',
             'commit', '--quiet', '-m', 'handoff(tarik): ' + task_id +
             '\n\nArchitecture: OpenAI (Tarik)', '--only', '--', *paths])
        run(['push', '--porcelain', 'origin', 'HEAD:refs/heads/main'])  # No force/retry on conflicts.
        return task


def claim_handoff(task, run_id, runner=None):
    claim = {'actor': 'tarik-goose', 'run_id': run_id,
             'claimed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'token': uuid.uuid4().hex}
    def mutate(queue, current):
        oldest = oldest_pending_handoff(queue)
        if current['status'] != 'pending' or oldest is None or oldest['id'] != task['id']:
            raise ValueError('handoff is no longer oldest pending')
        current.update(status='in_progress', claim=claim)
    return _queue_cas(task['id'], mutate, runner)


def finish_handoff(task, outcome, runner=None):
    validate_handoff_outcome(outcome, task)
    def mutate(queue, current):
        if current['status'] != 'in_progress' or current.get('claim', {}).get('token') != task['claim']['token']:
            raise ValueError('handoff claim changed')
        current.update(status=outcome['status'], result=outcome['result'])
        if outcome['status'] == 'completed':
            current['completed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return _queue_cas(task['id'], mutate, runner, artifact=outcome)


def verified_handoff_outcome(repo, task):
    path = Path(repo) / 'channels' / 'tarik-goose-results' / (task['id'] + '.json')
    if path.is_symlink() or not path.resolve().is_relative_to(Path(repo).resolve()) or \
            not path.is_file() or path.stat().st_size > 100000:
        raise ValueError('missing or oversized handoff result')
    outcome = json.loads(path.read_text(encoding='utf-8'))
    return validate_handoff_outcome(outcome, task)


def validate_handoff_outcome(outcome, task):
    if not isinstance(outcome, dict):
        raise ValueError('invalid handoff outcome')
    if outcome.get('id') != task['id'] or outcome.get('claim_token') != task['claim']['token']:
        raise ValueError('handoff result claim mismatch')
    if outcome.get('status') not in ('completed', 'blocked') or not isinstance(outcome.get('result'), dict):
        raise ValueError('invalid handoff outcome')
    serialized = json.dumps(outcome, ensure_ascii=False)
    credential_name = re.compile(r'(?:^|_)(?:API_KEY|ACCESS_TOKEN|AUTH_TOKEN|PASSWORD|TOKEN)(?:_[A-Z0-9]+)?$', re.I)
    for name, value in os.environ.items():
        if value and credential_name.search(name) and (value in serialized or
                json.dumps(value, ensure_ascii=False)[1:-1] in serialized):
            raise ValueError('handoff result contains sensitive material')
    for url in re.findall(r'''https?://[^\s<>"'\\]+''', serialized, flags=re.I):
        try:
            parsed = urllib.parse.urlsplit(url)
        except ValueError:
            raise ValueError('handoff result contains sensitive material') from None
        parameters = urllib.parse.unquote(parsed.query) + '&' + urllib.parse.unquote(parsed.fragment)
        credential_parameter = re.search(
            r'(?:^|[&;])(?:(?:[a-z0-9]+[_-])*token|api[_-]?key|password|client[_-]?secret|'
            r'secret|credential|signature|sig|auth|key|code|ticket)=', parameters, re.I)
        credential_path = re.search(
            r'/(?:reset|password[_-]?reset|reset[_-]?password|magic|magic[_-]?link|'
            r'invitation|invitations|invite)/(?:token/)?[^/]+', urllib.parse.unquote(parsed.path), re.I)
        if parsed.username is not None or parsed.password is not None or credential_parameter or credential_path:
            raise ValueError('handoff result contains sensitive material')
    checks = outcome['result'].get('checks')
    if outcome['status'] == 'completed' and (outcome.get('verified') is not True or
            not isinstance(checks, list) or not checks or
            any(not isinstance(check, (str, dict)) or not check for check in checks)):
        raise ValueError('handoff completion lacks verification evidence')
    return outcome


def handoff_instructions(task, report):
    return (
        f'You are {AMIGO_IDENTITY} in the LLM Symposium. Perform exactly the single '
        'Codex-to-Goose handoff below. This selected task is your complete work scope. '
        'Write a brief report first at ' + str(report) + ', and keep it accurate as you work. '
        'The harness already claimed this exact task in the fresh public queue; its claim token is '
        'included below. Do not change the queue yourself; the harness performs a matching-token '
        'completion update and result publication atomically from a fresh queue snapshot. '
        'Do not inspect credential files or values, or any Dawn/private conversation content. '
        'Host-local execution and editing outside this isolated checkout are allowed ONLY when the '
        'selected instructions explicitly authorize the exact paths or targets. If that scope is '
        'missing, do not guess: record the block. When allowed_targets is supplied, it is the outer '
        'limit on host modifications. No other task or independent work is authorized. '
        'The ONLY permitted public repository edit is the exact result artifact named below. '
        'Codex owns other public repository changes; do not edit public code, the queue, or other '
        'artifacts in this checkout. Extra repository edits fail closed and will not be published. '
        'Keep any LAND line limited to that result artifact. Verify any host-local '
        'change against its actual deployed result, not against a prepared patch. '
        'Write a nonsecret result artifact in this isolated repository at '
        'channels/tarik-goose-results/' + task['id'] + '.json with id, claim_token, status '
        '(completed or blocked), verified (boolean), and result (object containing a summary and '
        'checks with actual verification evidence). The report must name that artifact in LAND. '
        'Set completed only after actual result verification. If unfinished or unable to verify, '
        'set blocked with the reason in result; never claim '
        'completion from an intention, local proposal, or attempted command. Preserve every other '
        'queue item. Do not automatically '
        'retry an interrupted in_progress task. Do not send a message unless this task explicitly '
        'authorizes it. The final report must distinguish actual host changes, landed repository '
        'changes, blocked work, and uncertainty. Do not restart or stop the bot hosting this wake '
        'before the outcome and result artifact are durably published. For self-deployment, arrange '
        'an independently supervised deferred restart or report that the deployment is incomplete; '
        'a staged file or queued restart is not proof of active deployment.\n\nSELECTED HANDOFF TASK:\n' +
        json.dumps(task, ensure_ascii=False, indent=2) + '\n'
    )


def _run_handoff(config, goose_bin, source_repo, state_dir, provider, model, notify=None,
                 timeout=600, max_turns=25, executor=execute, handoff_loader=load_handoff_queue,
                 handoff_claimer=claim_handoff, handoff_finisher=finish_handoff):
    """Return a result only from THIS successful run, never an old shared file.

    Only a freshly claimed Codex handoff may run. New checkout and logs remain
    under state_dir; the result and queue transition publish atomically from a fresh clone.
    No mutation of the shared checkout/index by the harness. The worker still runs under
    the host user's OS identity: a checkout boundary is not security containment.
    """

    run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    skipped = {'run_id': run_id, 'workspace': None, 'changed_paths': [], 'land_claimed': []}
    try:
        handoff = oldest_pending_handoff(handoff_loader())
    except Exception as exc:
        log.warning('handoff refresh unavailable or invalid (%s); no work started', type(exc).__name__)
        return dict(skipped, status='skipped_handoff_unavailable')
    if handoff is None:
        return dict(skipped, status='skipped_no_pending_handoff')
    attempt = Path(state_dir) / 'handoff-attempts' / (handoff['id'] + '.json')
    if attempt.exists():
        return dict(skipped, status='skipped_handoff_already_attempted', handoff_id=handoff['id'])

    # Do not start a long agentic wake on a battery that is already low: a wake runs for up to ten
    # minutes with the CPU busy, and the human accepted the risk of an unplugged, lid-closed machine
    # but not of work still running when the power goes. Telegram replies are unaffected — those are
    # one short call, and reaching Dawn from the Pixel is the thing he wants to keep working.
    _on_batt, _pct, _watts = battery_state()
    if _on_batt and _pct < 20:
        log.info('wake skipped: on battery at %d%% (work stops before the machine does)', _pct)
        return {'run_id': run_id, 'status': 'skipped_low_battery', 'on_battery_percent': _pct,
                'workspace': None, 'changed_paths': [], 'land_claimed': []}
    try:
        handoff = handoff_claimer(handoff, run_id)
        if handoff.get('status') != 'in_progress' or not handoff.get('claim', {}).get('token'):
            raise ValueError('invalid claim receipt')
    except Exception as exc:
        log.warning('handoff claim unavailable (%s); no work started', type(exc).__name__)
        return dict(skipped, status='skipped_handoff_claim_unavailable')
    root = Path(state_dir)
    run_dir = root / 'runs' / run_id
    run_dir.mkdir(parents=True, mode=0o700)
    repo = run_dir / 'repo'
    # Don't pass Telegram credentials or inherited Git overrides to the worker.
    # This amigo's OWN mail pair IS passed (2026-10-04): the wake may send as itself.
    env = worker_env()
    result = {'run_id': run_id, 'provider': provider, 'model': model, 'handoff_id': handoff['id'],
              'workspace': str(repo), 'status': 'starting'}
    try:
        subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', '--single-branch',
                        str(source_repo), str(repo)], check=True, capture_output=True,
                       env=env, timeout=60)
        # The clone has committed source only, never another amigo's in-progress edits.
        subprocess.run(['git', '-C', str(repo), 'remote', 'remove', 'origin'],
                       check=True, capture_output=True, env=env, timeout=10)
        base = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], env=env, text=True).strip()
        report = run_dir / 'report.txt'
        instruction = run_dir / 'instructions.md'
        instruction.write_text(handoff_instructions(handoff, report), encoding='utf-8')
        attempt.parent.mkdir(parents=True, exist_ok=True)
        save_json(attempt, {'handoff_id': handoff['id'], 'run_id': run_id,
                            'claim_token': handoff['claim']['token'], 'status': 'attempting'})
        args = [str(goose_bin), 'run', '--provider', provider, '--model', model,
                '--with-builtin', 'developer', '--instructions', str(instruction),
                '--max-turns', str(max_turns), '--output-format', 'stream-json',
                # 2026-09-27: --no-session, not --name. Naming on 2026-09-20 made the wakes
                # distinguishable, but they still filled the human's chat list, and deleting them
                # by hand is a mop the next tick undoes (5 regrew within four hours). --no-session
                # records the run as a hidden session (session_type='hidden'), which the session
                # list does not show, while the run's own diagnostics read worker.jsonl (the Goose
                # stdout stream), not the session store. --name is rejected together with
                # --no-session (verified: exit 2), so it is dropped. Fix the producer, not the list.
                '--no-session']
        code = executor(args, repo, run_dir / 'worker.jsonl', env, timeout)
        result['worker_exit'] = code
        result['timed_out'] = (code == 124)
        # 2026-09-20: the cost of the wake and whether it was cut off at its action cap. Both were
        # knowable and neither was recorded, so a run that stopped mid-sentence at 900k tokens
        # looked exactly like one that finished.
        usage = worker_usage(run_dir / 'worker.jsonl')
        result['total_tokens'] = usage['total_tokens']
        result['cut_off'] = usage['cut_off']
        # Record actual file changes separately from the worker's one-sentence claim.
        subprocess.run(['git', '-C', str(repo), 'add', '-N', '.'], env=env,
                       check=True, capture_output=True, timeout=15)
        patch = subprocess.check_output(['git', '-C', str(repo), 'diff', '--no-ext-diff',
                                         '--no-textconv', '--binary', base], env=env, timeout=20)
        (run_dir / 'changes.patch').write_bytes(patch)
        result['changed_paths'] = subprocess.check_output(
            ['git', '-C', str(repo), 'diff', '--no-ext-diff', '--name-only', base],
            env=env, text=True, timeout=10).splitlines()
        # The exit code ANNOTATES; it does not decide. A run that timed out after doing real work
        # has a result, and until 2026-09-15 the code threw that result away on a non-zero exit.
        changed = result['changed_paths']
        report_text = ''
        if report.is_file() and not report.is_symlink() and report.stat().st_size <= 8192:
            report_text = report.read_text(encoding='utf-8').strip()
        if report_text and changed:
            result['status'] = 'awaiting_review'
            result['worker_report'] = report_text[:1200]
        elif report_text:
            # A report is not a deliverable. Git decides whether anything happened; a report
            # without a change is kept for review but is never announced as an outcome.
            result['status'] = 'no_work_done'
            result['worker_report'] = report_text[:1200]
        elif changed:
            # The 01:14 and 05:14 runs: real edits, no report, silently nothing. Now named.
            result['status'] = 'unreported_changes'
        elif code != 0:
            result['status'] = 'timeout' if code == 124 else 'worker_failed'
        else:
            result['status'] = 'missing_or_invalid_report'
        # 2026-09-18: check the report's own LAND claim against the diff — deliberately AFTER the
        # status chain, because the first version of this sat inside it and re-attached the
        # trailing `elif code != 0` to itself, turning every unreported-changes run into a timeout.
        # A run that names files it never wrote is how it overclaims delivery with nobody noticing.
        if report_text:
            claimed = expand_land_claims(land_claimed(report_text), changed)
            result['land_claimed'] = claimed
            result['land_missing'] = [c for c in claimed if c not in changed]
            if result['land_missing']:
                log.warning('run %s claimed to land %d path(s) it did not change: %s',
                            run_id, len(result['land_missing']), ', '.join(result['land_missing'][:6]))
        if result.get('cut_off'):
            log.warning('run %s was cut off at its action cap after %s tokens with %d changed '
                        'path(s) — the work it did not reach is not in the report',
                        run_id, result.get('total_tokens'), len(changed))
        save_json(run_dir / 'result.json', result)

        # A claim advances remote main while this worker's source checkout can remain stale.
        # Publish only the scoped result plus matching-token queue transition from a fresh CAS clone.
        # The old live-checkout lander cannot safely publish these host-local handoffs.
        try:
            expected_result = 'channels/tarik-goose-results/' + handoff['id'] + '.json'
            if code != 0 or changed != [expected_result]:
                result['unexpected_repository_paths'] = [path for path in changed if path != expected_result]
                raise ValueError('worker incomplete or unexpected repository changes')
            handoff_outcome = verified_handoff_outcome(repo, handoff)
            handoff_finisher(handoff, handoff_outcome)
            result['land'] = 'handoff_result_published'
            result['handoff_completion'] = handoff_outcome['status']
        except Exception as exc:
            result['land'] = 'handoff_result_not_published'
            result['handoff_completion'] = 'uncertain'
            result['handoff_completion_error'] = type(exc).__name__
            # Keep the remote claim in_progress. Codex must explicitly recover it; never steal/retry.
        save_json(run_dir / 'result.json', result)

        if notify and WAKE_SUMMARY_NOTIFY:
            # 2026-09-17: these messages used to be status codes and file paths. He reads texts and
            # not the repository, and he said plainly that they made no sense to him. Plain English,
            # first person, no paths, no timestamps, no status words — and always say whether he
            # needs to do anything, because that is the only question he is actually asking.
            head = (report_text.splitlines() or [''])[0][:300]
            if result.get('status') == 'awaiting_review' and result.get('land') == 'landed':
                msg = f"{head}\n\nStatus: in the repository; action: none." if head else "Status: in the repository; action: none."
                notify(msg)
            elif result['status'] == 'awaiting_review':
                msg = f"{head}\n\nStatus: awaiting reviewer; action: none." if head else "Status: awaiting reviewer; action: none."
                notify(msg)
            elif result['status'] == 'unreported_changes':
                notify("Changed files without a summary report.\n\nStatus: parked, unpublished; action: none.")
            elif result['status'] in ('timeout', 'worker_failed', 'missing_or_invalid_report'):
                notify("Ran out of time or lost thread partway through.\n\nStatus: no artifact; action: none.")
            # 'no_work_done' is deliberate: the worker reported and git agrees nothing changed,
            # so there is nothing to tell him. Six wake-ups a day must not become six texts.
    except Exception as exc:
        result['status'] = 'failed'
        result['error_type'] = type(exc).__name__
        save_json(run_dir / 'result.json', result)
        log.warning('local session failed (%s), run=%s', type(exc).__name__, run_id)
    log.info('local tick result: status=%s run=%s', result['status'], run_id)
    if attempt.exists():
        save_json(attempt, {'handoff_id': handoff['id'], 'run_id': run_id,
                            'claim_token': handoff['claim']['token'],
                            'status': result.get('handoff_completion', 'uncertain')})
    try:
        prune_old_runs(root)
    except Exception as exc:  # pruning must never fail a run or hide its result
        log.warning('could not prune old runs: %s', type(exc).__name__)
    return result
