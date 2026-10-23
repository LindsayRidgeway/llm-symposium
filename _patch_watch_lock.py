#!/usr/bin/env python3
"""One-off: ledger_watch takes the shared-checkout lock for the parts that write."""
import pathlib

P = pathlib.Path("/Users/lindsayridgeway/LLM/llm-symposium/scripts/ledger_watch.py")
t = P.read_text(encoding="utf-8")

old_import = """sys.path.insert(0, str(REPO / "channels"))
import item_ledger as il  # noqa: E402
"""
new_import = """sys.path.insert(0, str(REPO / "channels"))
import item_ledger as il  # noqa: E402
from record_push import shared_checkout_lock  # noqa: E402
"""
assert t.count(old_import) == 1
t = t.replace(old_import, new_import)

old_sync = '''    # 1. bring the checkout up to date; a failure here is reported, not fatal
    sync_note = ""
    if not args.dry_run:
        pull = git("pull", "--rebase", "--autostash", "--quiet")
        if pull.returncode != 0:
            sync_note = "checkout could not be synced (conflict); measured what is here"

    # 2. repair
    recovered: list[str] = []
    counts = {"collected": 0, "reconciled": 0, "paths": 0}
    if not args.dry_run:
        recovered = recover_verdicts(now - dt.timedelta(days=args.days), apply=True)
        counts = filed_and_reconciled(apply=True)
    else:
        recovered = [r + " [would recover]" for r in
                     recover_verdicts(now - dt.timedelta(days=args.days), apply=False)]
    repairs = {**counts, "recovered": recovered}
'''
new_sync = '''    # 1-2. bring the checkout up to date, then repair. Both write into the shared checkout, and
    # so does every landing in every body (land_runs.py holds `.git/symposium-land.lock` for the
    # length of a landing, test suite included). Until 2026-10-23 this pull ran unlocked, which is
    # how a rebase here and a landing there produced the conflicted trees of 2026-10-22.
    sync_note = ""
    recovered: list[str] = []
    counts = {"collected": 0, "reconciled": 0, "paths": 0}
    if not args.dry_run:
        with shared_checkout_lock(REPO, timeout=900) as held:
            if not held:
                sync_note = ("another body held the shared checkout for 15 minutes; measured "
                             "without syncing or repairing")
            else:
                pull = git("pull", "--rebase", "--autostash", "--quiet")
                if pull.returncode != 0:
                    sync_note = "checkout could not be synced (conflict); measured what is here"
                recovered = recover_verdicts(now - dt.timedelta(days=args.days), apply=True)
                counts = filed_and_reconciled(apply=True)
    else:
        recovered = [r + " [would recover]" for r in
                     recover_verdicts(now - dt.timedelta(days=args.days), apply=False)]
    repairs = {**counts, "recovered": recovered}
'''
assert t.count(old_sync) == 1
t = t.replace(old_sync, new_sync)

old_commit = """        if not args.no_send:
            print("\\nledger_watch: " + telegram(text, dry=False))
        commit_and_push(m)
"""
new_commit = """        if not args.no_send:
            print("\\nledger_watch: " + telegram(text, dry=False))
        with shared_checkout_lock(REPO, timeout=900) as held:
            if held:
                commit_and_push(m)
            else:
                print("ledger_watch: shared checkout busy; the repair is on disk and will go up "
                      "with the next run")
"""
assert t.count(old_commit) == 1
t = t.replace(old_commit, new_commit)

P.write_text(t, encoding="utf-8")
print("patched", P)
