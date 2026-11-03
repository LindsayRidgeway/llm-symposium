#!/usr/bin/env python3
"""deploy_engines.py — make the six bot directories equal to the commons, on purpose.

Written 2026-11-03 (dmitri), immediately after extracting the wake engine into
`channels/wake_engine.py`. The extraction removed the six implementations and left one question
unanswered: how does a change in the commons become a change in six directories? Until now the
answer was "a person, by hand, six times" — which is exactly how the six copies drifted in the first
place, and how every fix to them has needed a manual session.

This script is that answer, and nothing more: it copies the shared modules from `channels/` into
each `~/LLM/<bot>-bot/`, verifies the md5 of every copy, and says what changed. It does not run the
tests (the drift tests do that), it does not invent files, and it does not restart anything unless
asked — a restart interrupts whatever the bot is doing, and that is a decision, not a side effect.

    python3 scripts/deploy_engines.py            # copy and verify
    python3 scripts/deploy_engines.py --dry-run  # say what would change
    python3 scripts/deploy_engines.py --restart  # copy, verify, then restart the six bots

Exit status: 0 when every copy matches the canonical file, 1 when it does not (including when a bot
directory is missing — a deploy that silently skips a body is how one body ends up a month behind).
"""
import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path

COMMONS = Path(__file__).resolve().parent.parent
BOTS_ROOT = COMMONS.parent
SHARED = ("wake_engine.py", "wake_heartbeat.py", "record.py", "record_push.py")

# The six seats, in the order the commons lists them. A bot directory that is not here is not
# deployed to at all: the list is the same one the drift tests use, and a body added without adding
# it here would be a body nobody deploys to.
BODIES = ("desi", "dmitri", "claude", "gemini", "tarik", "gwen")


def md5(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def deploy(commons=None, bots_root=None, dry_run=False, out=print):
    """Copy the shared modules into every bot directory. Returns a list of (body, name, action)."""
    commons = Path(commons) if commons else COMMONS
    bots_root = Path(bots_root) if bots_root else BOTS_ROOT
    actions = []
    # Validate everything before writing anything: a deploy that writes four bodies and then stops
    # leaves the tree split between two versions, which is worse than not deploying at all.
    for name in SHARED:
        if not (commons / "channels" / name).is_file():
            raise FileNotFoundError("the commons has no channels/%s" % name)
    for body in BODIES:
        if not (bots_root / ("%s-bot" % body)).is_dir():
            raise FileNotFoundError("%s-bot is not a directory" % body)
    for name in SHARED:
        source = commons / "channels" / name
        wanted = md5(source)
        for body in BODIES:
            target = bots_root / ("%s-bot" % body) / name
            if target.is_file() and md5(target) == wanted:
                actions.append((body, name, "unchanged"))
                continue
            action = "added" if not target.exists() else "updated"
            if not dry_run:
                target.write_bytes(source.read_bytes())
                if md5(target) != wanted:
                    raise IOError("%s-bot/%s does not match after the copy" % (body, name))
            actions.append((body, name, action))
    for body, name, action in actions:
        if action != "unchanged":
            out("%-8s %-20s %s" % (body, name, action))
    changed = [a for a in actions if a[2] != "unchanged"]
    out("%d file(s) %s, %d already identical"
        % (len(changed), "to copy" if dry_run else "written", len(actions) - len(changed)))
    return actions


def restart(out=print, runner=None):
    """Restart the six bots so they load what was just written."""
    for body in BODIES:
        if runner is not None:
            runner(body)
            out("%-8s restart ok" % body)
            continue
        job = "gui/%d/com.lindsay.amigo.%s" % (__import__("os").getuid(), body)
        result = subprocess.run(["launchctl", "kickstart", "-k", job],
                                capture_output=True, text=True)
        out("%-8s restart %s" % (body, "ok" if result.returncode == 0 else
                                 "failed: %s" % result.stderr.strip()))


IDLE_WINDOW = 30 * 60


def in_flight(bots_root=None, commands=None, now=None):
    """Which bodies are in the middle of a wake right now, as (body, reason).

    A restart kills the worker mid-run, which leaves a verdict with no lander — the exact mess
    `finish_unlanded` was written to clean up. So the scheduled path asks first. Two signals: a run
    directory with no `result.json` and a recent timestamp, and a live process whose command line
    names this bot's tick-state. The first is cheap and catches the common case; the second catches
    a run that started more than half an hour ago and is still going (long wakes exist).
    """
    bots_root = Path(bots_root) if bots_root else BOTS_ROOT
    now = time.time() if now is None else float(now)
    busy = []
    for body in BODIES:
        runs = bots_root / ("%s-bot" % body) / "tick-state" / "runs"
        if not runs.is_dir():
            continue
        for run in runs.iterdir():
            if not run.is_dir() or (run / "result.json").is_file():
                continue
            try:
                age = now - run.stat().st_mtime
            except OSError:
                continue
            if age <= IDLE_WINDOW:
                busy.append((body, "a run started %d min ago has not finished" % (age // 60)))
                break
    if commands is None:
        commands = subprocess.run(["ps", "-Ao", "command="], capture_output=True,
                                  text=True).stdout
    known = {body for body, _ in busy}
    for body in BODIES:
        if body in known:
            continue
        if ("%s-bot/tick-state/runs/" % body) in commands:
            busy.append((body, "a worker process is still running"))
    return busy


CORE_NAME = "CORE"


def verify(commons=None, bots_root=None):
    """Would this deploy leave six working directories holding an engine that does not work?

    The schedules that this script is written for remove the person, so the two checks a person
    would make have to be here: the canonical engine imports, and every stub still refers to names
    the engine actually has. Returns a list of complaints; empty means safe to copy.
    """
    import ast
    import importlib.util
    commons = Path(commons) if commons else COMMONS
    bots_root = Path(bots_root) if bots_root else BOTS_ROOT
    engine_path = commons / "channels" / "wake_engine.py"
    spec = importlib.util.spec_from_file_location("deploy_verify_engine", str(engine_path))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except BaseException as exc:                       # noqa: BLE001
        return ["channels/wake_engine.py does not import: %s: %s" % (type(exc).__name__, exc)]
    problems = []
    for body in BODIES:
        stub = bots_root / ("%s-bot" % body) / "local_tick.py"
        try:
            tree = ast.parse(stub.read_text(encoding="utf-8"))
        except OSError:
            problems.append("%s-bot has no local_tick.py" % body)
            continue
        except SyntaxError as exc:
            problems.append("%s-bot/local_tick.py does not parse: %s" % (body, exc.msg))
            continue
        wanted = sorted({node.attr for node in ast.walk(tree)
                         if isinstance(node, ast.Attribute)
                         and isinstance(node.value, ast.Name)
                         and node.value.id == CORE_NAME})
        missing = [name for name in wanted if not hasattr(module, name)]
        if missing:
            problems.append("%s-bot/local_tick.py calls the engine for %s, which the engine no "
                            "longer has" % (body, ", ".join(missing)))
    return problems



def main(argv=None, commons=None, bots_root=None, out=print, restart_runner=None, commands=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--restart", action="store_true",
                        help="restart the six bots afterwards (they load the new code only then)")
    parser.add_argument("--verify", action="store_true",
                        help="refuse to copy an engine that does not import or a stub that calls "
                             "names it no longer has")
    parser.add_argument("--when-idle", action="store_true",
                        help="do nothing while any bot is in the middle of a wake")
    args = parser.parse_args(argv)
    commons = Path(commons) if commons else COMMONS
    bots_root = Path(bots_root) if bots_root else BOTS_ROOT
    if args.verify:
        problems = verify(commons, bots_root)
        for problem in problems:
            out("verify: %s" % problem)
        if problems:
            out("nothing was copied: %d problem(s) in the engine or the stubs" % len(problems))
            return 1
    if args.when_idle:
        busy = in_flight(bots_root, commands=commands)
        for body, reason in busy:
            out("%-8s in flight — %s" % (body, reason))
        if busy:
            out("deploy skipped: %d bot(s) in flight; nothing was written" % len(busy))
            return 0
    try:
        actions = deploy(commons, bots_root, dry_run=args.dry_run, out=out)
    except (FileNotFoundError, IOError) as exc:
        out("deploy_engines: %s" % exc)
        return 1
    changed = any(a[2] != "unchanged" for a in actions)
    if args.restart and not args.dry_run:
        if changed:
            restart(out=out, runner=restart_runner)
        else:
            out("nothing changed — the six bots were not restarted")
    elif changed and not args.dry_run:
        out("the bots are still running the old code — restart them, or pass --restart")
    return 0


if __name__ == "__main__":
    sys.exit(main())
