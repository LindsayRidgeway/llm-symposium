#!/usr/bin/env python3
"""The ledger-row recovery must recover exactly the rows a failed landing lost, and no others.

Written 2026-10-14 (Dmitri) with `scripts/ledger_row_recovery.py`. The defect it closes was
named by run `20261013T170314Z-0838fbd7`, whose patch lost 137 ledger rows to a `git apply`
that is atomic over the whole patch: one volatile file's hunk failing discards the ledger
hunk with it.

Three things are worth guarding, and each is a way the tool could do harm rather than good:

1. **A patch for another path must contribute nothing.** The reader scopes itself to the
   `channels/items.jsonl` section, so a `+` line in a sibling file's hunk is not a ledger row.
   Getting this wrong would inject another file's lines into the register.

2. **Older must never overwrite newer.** The ledger is later-wins, so appending an *older* row
   for an `id` already present is a regression, not a recovery. Those rows must be skipped and
   named. This is the rule that keeps the remedy from becoming a second defect.

3. **It must not touch the ledger on a dry run.** A tool that edits a shared register while
   reporting what it *would* do is worse than no tool.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts import ledger_row_recovery as L  # noqa: E402


def _row(rid: str, state: str | None = None, utc: str = "") -> dict:
    r = {"id": rid, "amigo": "desi", "filed_utc": utc or "2026-01-01T00:00:00Z"}
    if state:
        r["state"] = state
    if utc:
        r["state_utc"] = utc
    return r


def _patch_for(rows: list[dict], other: list[dict] | None = None) -> str:
    """A patch shaped like the lander's: an append-at-EOF hunk for the ledger, plus another file."""
    out = ["diff --git a/channels/items.jsonl b/channels/items.jsonl",
           "index 0000000..1111111 100644", "--- a/channels/items.jsonl",
           "+++ b/channels/items.jsonl", f"@@ -1,1 +1,{1 + len(rows)} @@", " {}",]
    out += ["+" + json.dumps(r, sort_keys=True) for r in rows]
    if other:
        out += ["diff --git a/channels/other.md b/channels/other.md",
                "--- a/channels/other.md", "+++ b/channels/other.md",
                "@@ -1,1 +1,2 @@", " x"]
        out += ["+" + json.dumps(r, sort_keys=True) for r in other]
    return "\n".join(out) + "\n"


def test_reader_scopes_to_the_target_file() -> None:
    """Only the ledger section's `+` lines are rows; a sibling file's additions are not."""
    text = _patch_for([_row("A")], other=[{"id": "NOT-A-LEDGER-ROW", "amigo": "x"}])
    rows, bad = L.added_rows(text)
    assert bad == 0, bad
    assert [r["id"] for r in rows] == ["A"], rows


def test_plan_appends_missing_and_newer_skips_older() -> None:
    """A new id is recovered; an older row for a known id is skipped; a newer one is appended."""
    ledger = {"A": _row("A", "accomplished", "2026-06-01T00:00:00Z"),
              "B": _row("B", "postponed", "2026-06-01T00:00:00Z")}
    rows = [_row("A", "accomplished", "2025-12-31T00:00:00Z"),   # older -> skip, and name
            _row("B", "accomplished", "2026-07-01T00:00:00Z"),   # newer -> append
            _row("C", "rejected", "2026-07-01T00:00:00Z")]       # absent -> append
    append, current, staler = L.plan(rows, ledger)
    assert sorted(r["id"] for r in append) == ["B", "C"], append
    assert "A" in staler, staler
    assert "A" in current, current


def test_plan_last_row_for_an_id_wins() -> None:
    """Within one patch, the last line for an id wins — the ledger's own later-wins rule."""
    rows = [_row("A", "postponed", "2026-01-01T00:00:00Z"),
            _row("A", "accomplished", "2026-02-01T00:00:00Z")]
    append, _, _ = L.plan(rows, {})
    assert len(append) == 1 and append[0]["state"] == "accomplished", append


def test_dry_run_writes_nothing_and_write_appends_only_recoverable() -> None:
    """A dry run leaves the ledger byte-identical; --write appends exactly the recoverable rows."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        patch = td / "changes.patch"
        ledger = td / "items.jsonl"
        patch.write_text(_patch_for([_row("A", "accomplished", "2025-12-31T00:00:00Z"),
                                     _row("B", "accomplished", "2026-07-01T00:00:00Z"),
                                     _row("C", "rejected", "2026-07-01T00:00:00Z")]),
                         encoding="utf-8")
        ledger.write_text("\n".join(json.dumps(r, sort_keys=True) for r in
                                    [_row("A", "accomplished", "2026-06-01T00:00:00Z")]) + "\n",
                          encoding="utf-8")
        before = ledger.read_bytes()
        res = L.recover(patch=patch, ledger_path=ledger, write=False)
        assert ledger.read_bytes() == before, "dry run changed the ledger"
        assert sorted(res["recovered"]) == ["B", "C"], res
        assert res["staler_than_ledger"] == ["A"], res
        res = L.recover(patch=patch, ledger_path=ledger, write=True)
        assert res["written"] and sorted(res["recovered"]) == ["B", "C"], res
        after = L.load_rows(ledger)
        assert set(after) == {"A", "B", "C"}, after
        # later-wins, so the recovered states are the ones the ledger now reports
        assert after["B"]["state"] == "accomplished" and after["C"]["state"] == "rejected", after


def test_cli_dry_run_exit_zero_and_reports() -> None:
    """The CLI must run, report, and exit 0 without --write."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        rd = td / "20260101T000000Z-00000000"
        rd.mkdir()
        (rd / "changes.patch").write_text(_patch_for([_row("Z", "accomplished", "2026-01-01T00:00:00Z")]),
                                          encoding="utf-8")
        ledger = td / "items.jsonl"
        ledger.write_text("", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(REPO / "scripts" / "ledger_row_recovery.py"),
                               str(rd), "--ledger", str(ledger)],
                              capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        assert "missing from the ledger (recoverable): 1" in proc.stdout, proc.stdout
        assert ledger.read_text(encoding="utf-8") == "", "dry run touched the ledger"


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"ok   {t.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {t.__name__}: {exc}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
