#!/usr/bin/env python3
"""Offline tests for the local retention entrypoint (scripts/retention_pass.py).

The property under test did not exist before 2026-09-26: the two GitHub workflows that used to
trim the commons were both retired on 2026-09-25, and nothing took over either pass. So these
tests pin the three things that make the replacement safe to run unattended —

  1. one command runs BOTH passes (the raw channel trim *and* the dated/conversation pass),
     because "half of the retention story restored" is the failure that is hard to notice;
  2. it is dry by default and changes nothing until `--apply`;
  3. a failure in one pass is reported and the other pass still runs — and the exit code stays 0.

Everything runs in a temp tree; no repository file is touched.
"""
import datetime as _dt
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import channels.retention as retention  # noqa: E402
import enforce_retention as er  # noqa: E402
import retention_pass  # noqa: E402


class _TempRepo:
    """Point both retention modules at a temp repository, and put them back afterwards."""

    def __enter__(self):
        self.td = tempfile.TemporaryDirectory()
        root = Path(self.td.name)
        self._old = (
            retention.REPO_ROOT, retention.RAW_DIRS, retention.RETENTION_DAYS,
            er.REPO, er.CH, er.CONV_DIR, er.DATED_DIRS, er.RETENTION_YEARS,
            er.CONVERSATION_MAX_BYTES,
        )
        retention.REPO_ROOT = root
        retention.RAW_DIRS = (
            root / "channels" / "inbound",
            root / "channels" / "telegram",
        )
        retention.RETENTION_DAYS = 14
        er.REPO = root
        er.CH = root / "channels"
        er.CONV_DIR = er.CH / "conversation"
        er.DATED_DIRS = [root / "news", er.CH / "risk-archive"]
        er.RETENTION_YEARS = 10
        er.CONVERSATION_MAX_BYTES = 1000
        self.root = root
        self._build()
        return root

    def __exit__(self, *exc):
        (retention.REPO_ROOT, retention.RAW_DIRS, retention.RETENTION_DAYS,
         er.REPO, er.CH, er.CONV_DIR, er.DATED_DIRS, er.RETENTION_YEARS,
         er.CONVERSATION_MAX_BYTES) = self._old
        self.td.cleanup()
        return False

    def _build(self):
        tg = self.root / "channels" / "telegram"
        tg.mkdir(parents=True)
        (tg / "2020-01-01-000000-inbound-1.md").write_text("# old\n", encoding="utf-8")
        today = _dt.date.today().isoformat()
        (tg / f"{today}-000000-inbound-2.md").write_text("# today\n", encoding="utf-8")
        (tg / "README.md").write_text("# not an artifact\n", encoding="utf-8")

        news = self.root / "news"
        news.mkdir(parents=True)
        (news / "2000-01-01-ancient.md").write_text("old\n", encoding="utf-8")

        conv = self.root / "channels" / "conversation"
        conv.mkdir(parents=True)
        (conv / "desi.md").write_text("HEAD\n\n" + ("x" * 5000), encoding="utf-8")


def test_dry_run_reports_both_passes_and_changes_nothing():
    with _TempRepo() as root:
        s = retention_pass.run(apply=False, raw_mod=retention, enforce_mod=er)
        assert s["errors"] == [], s["errors"]
        assert s["raw"] == ["channels/telegram/2020-01-01-000000-inbound-1.md"], s["raw"]
        assert s["dated"] == ["news/2000-01-01-ancient.md"], s["dated"]
        assert len(s["conversation"]) == 1 and "desi.md" in s["conversation"][0]
        # Nothing moved on disk.
        assert (root / "channels" / "telegram" / "2020-01-01-000000-inbound-1.md").exists()
        assert (root / "news" / "2000-01-01-ancient.md").exists()
        assert (root / "channels" / "conversation" / "desi.md").stat().st_size > 1000


def test_apply_does_both_passes():
    with _TempRepo() as root:
        s = retention_pass.run(apply=True, raw_mod=retention, enforce_mod=er)
        assert s["errors"] == [], s["errors"]
        # pass 1: the raw channel trim
        assert not (root / "channels" / "telegram" / "2020-01-01-000000-inbound-1.md").exists()
        # pass 2a: the dated horizon
        assert not (root / "news" / "2000-01-01-ancient.md").exists()
        # pass 2b: the conversation size cap
        assert (root / "channels" / "conversation" / "desi.md").stat().st_size <= 1000
        # and what should survive, survives
        assert (root / "channels" / "telegram" / "README.md").exists()
        assert len(list((root / "channels" / "telegram").glob(f"{_dt.date.today().isoformat()}*"))) == 1


def test_one_failing_pass_does_not_skip_the_other_and_never_raises():
    class _Broken:
        @staticmethod
        def prune_raw(dry=False):
            raise RuntimeError("simulated failure")

    with _TempRepo() as root:
        s = retention_pass.run(apply=True, raw_mod=_Broken(), enforce_mod=er)
        assert any("raw channel trim" in e for e in s["errors"]), s["errors"]
        # the second pass still ran even though the first blew up
        assert not (root / "news" / "2000-01-01-ancient.md").exists()
        # and the command still exits 0 — housekeeping is never fatal
        assert retention_pass.main(["--apply"], raw_mod=_Broken(), enforce_mod=er) == 0


def test_format_summary_is_plain_and_names_the_mode():
    s = {"raw": ["a.md"], "dated": [], "conversation": ["channels/conversation/desi.md (5000 -> 1000)"],
         "errors": []}
    dry = retention_pass.format_summary(s, apply=False)
    assert "DRY RUN" in dry
    assert "raw channel logs past their window: 1" in dry
    assert "conversation stores over the cap:   1" in dry
    assert "safety" not in dry.lower()  # no invented vocabulary
    applied = retention_pass.format_summary(s, apply=True)
    assert "APPLIED" in applied
    assert "nothing was changed" in dry and "nothing was changed" not in applied


def test_default_is_dry_run():
    """`main()` with no flags must not trim — the safe direction for an unattended command."""
    with _TempRepo() as root:
        rc = retention_pass.main([], raw_mod=retention, enforce_mod=er)
        assert rc == 0
        assert (root / "news" / "2000-01-01-ancient.md").exists()
        assert (root / "channels" / "telegram" / "2020-01-01-000000-inbound-1.md").exists()


def _run_all():
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
