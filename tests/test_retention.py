#!/usr/bin/env python3
"""Offline tests for channel raw-artifact retention."""
import os
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import channels.retention as retention  # noqa: E402


def _with_temp_repo(fn):
    with tempfile.TemporaryDirectory() as td:
        old = (retention.REPO_ROOT, retention.RAW_DIRS, retention.RETENTION_DAYS)
        root = Path(td)
        retention.REPO_ROOT = root
        retention.RAW_DIRS = (root / "channels" / "inbound", root / "channels" / "telegram")
        retention.RETENTION_DAYS = 14
        try:
            fn(root)
        finally:
            retention.REPO_ROOT, retention.RAW_DIRS, retention.RETENTION_DAYS = old


def test_prunes_old_unmarked_raw_file_by_filename_date():
    def run(root):
        d = root / "channels" / "telegram"
        d.mkdir(parents=True)
        p = d / "2026-01-01-120000-inbound-42.md"
        p.write_text("# old\n", encoding="utf-8")
        # Recent mtime must not save an old dated artifact after Git checkout.
        os.utime(p, None)
        removed = retention.prune_raw(now=2000000000)
        assert "channels/telegram/2026-01-01-120000-inbound-42.md" in removed
        assert not p.exists()
    _with_temp_repo(run)


def test_prunes_old_unmarked_raw_file_by_mtime_when_no_date():
    def run(root):
        d = root / "channels" / "telegram"
        d.mkdir(parents=True)
        p = d / "old.md"
        p.write_text("# old\n", encoding="utf-8")
        old_time = time.time() - 30 * 86400
        os.utime(p, (old_time, old_time))
        removed = retention.prune_raw()
        assert "channels/telegram/old.md" in removed
        assert not p.exists()
    _with_temp_repo(run)


def test_keeps_old_preserved_file():
    def run(root):
        d = root / "channels" / "inbound"
        d.mkdir(parents=True)
        p = d / "2026-01-01-important.md"
        p.write_text("# important\n\nRetention: keep\n", encoding="utf-8")
        removed = retention.prune_raw(now=2000000000)
        assert removed == []
        assert p.exists()
    _with_temp_repo(run)


def test_prune_raw_can_be_asked_not_to_delete():
    def run(root):
        d = root / "channels" / "telegram"
        d.mkdir(parents=True)
        p = d / "2026-01-01-120000-inbound-42.md"
        p.write_text("# old\n", encoding="utf-8")
        removed = retention.prune_raw(apply=False)
        assert "channels/telegram/2026-01-01-120000-inbound-42.md" in removed
        assert p.exists(), "apply=False must be read-only"
    _with_temp_repo(run)


def test_cli_is_dry_run_by_default():
    """A bare `python3 channels/retention.py` must report, not delete.

    Until 2026-10-06 it deleted 259 tracked files in a checkout and printed only
    a count. The sibling sweep (scripts/enforce_retention.py) has always been
    dry-run unless --apply; this pins the same convention here.
    """
    def run(root):
        d = root / "channels" / "telegram"
        d.mkdir(parents=True)
        p = d / "2026-01-01-120000-inbound-42.md"
        p.write_text("# old\n", encoding="utf-8")
        rc = retention.main([])
        assert rc == 0
        assert p.exists(), "the CLI must not delete without --apply"
    _with_temp_repo(run)


def test_cli_apply_deletes():
    def run(root):
        d = root / "channels" / "telegram"
        d.mkdir(parents=True)
        p = d / "2026-01-01-120000-inbound-42.md"
        p.write_text("# old\n", encoding="utf-8")
        rc = retention.main(["--apply"])
        assert rc == 0
        assert not p.exists()
    _with_temp_repo(run)


def test_cli_rejects_conflicting_and_unknown_flags():
    assert retention.main(["--apply", "--dry-run"]) == 2
    assert retention.main(["--nonsense"]) == 2
    assert retention.main(["--help"]) == 0


def _run_all():
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_run_all())
