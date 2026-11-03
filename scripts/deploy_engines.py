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


def restart(out=print):
    """Restart the six bots so they load what was just written."""
    for body in BODIES:
        job = "gui/%d/com.lindsay.amigo.%s" % (__import__("os").getuid(), body)
        result = subprocess.run(["launchctl", "kickstart", "-k", job],
                                capture_output=True, text=True)
        out("%-8s restart %s" % (body, "ok" if result.returncode == 0 else
                                 "failed: %s" % result.stderr.strip()))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--restart", action="store_true",
                        help="restart the six bots afterwards (they load the new code only then)")
    args = parser.parse_args(argv)
    try:
        actions = deploy(dry_run=args.dry_run)
    except (FileNotFoundError, IOError) as exc:
        print("deploy_engines: %s" % exc, file=sys.stderr)
        return 1
    if args.restart and not args.dry_run:
        restart()
    elif any(a[2] != "unchanged" for a in actions) and not args.dry_run:
        print("the bots are still running the old code — restart them, or pass --restart")
    return 0


if __name__ == "__main__":
    sys.exit(main())
