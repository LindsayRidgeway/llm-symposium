#!/usr/bin/env python3
"""Offline tests for the civic retention sweep (scripts/enforce_retention.py)."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import enforce_retention as er  # noqa: E402


def _with_temp_repo(fn):
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        old = (er.REPO, er.CH, er.CONV_DIR, er.DATED_DIRS,
               er.RETENTION_YEARS, er.CONVERSATION_MAX_BYTES)
        root = Path(td)
        er.REPO = root
        er.CH = root / "channels"
        er.CONV_DIR = er.CH / "conversation"
        er.DATED_DIRS = [root / "news", root / "insights", er.CH / "risk-archive"]
        er.RETENTION_YEARS = 10
        er.CONVERSATION_MAX_BYTES = 1000
        try:
            fn(root)
        finally:
            (er.REPO, er.CH, er.CONV_DIR, er.DATED_DIRS,
             er.RETENTION_YEARS, er.CONVERSATION_MAX_BYTES) = old


def test_dry_run_removes_nothing():
    def run(root):
        (root / "news").mkdir(parents=True)
        (root / "news" / "2010-01-01-old.md").write_text("x", encoding="utf-8")
        (root / "news" / "2026-09-05-new.md").write_text("x", encoding="utf-8")
        removed = er.prune_dated(dry=True)
        assert "news/2010-01-01-old.md" in removed
        # dry-run must not delete
        assert (root / "news" / "2010-01-01-old.md").exists()
        assert "news/2026-09-05-new.md" not in removed
    _with_temp_repo(run)


def test_apply_removes_old_keeps_canonical_and_recent():
    def run(root):
        (root / "news").mkdir(parents=True)
        (root / "news" / "2010-01-01-old.md").write_text("x", encoding="utf-8")
        (root / "news" / "2026-09-05-new.md").write_text("x", encoding="utf-8")
        (root / "news" / "README.md").write_text("canonical", encoding="utf-8")
        removed = er.prune_dated(dry=False)
        assert "news/2010-01-01-old.md" in removed
        assert not (root / "news" / "2010-01-01-old.md").exists()
        # recent + canonical preserved
        assert (root / "news" / "2026-09-05-new.md").exists()
        assert (root / "news" / "README.md").exists()
    _with_temp_repo(run)


def test_risk_archive_year_files_age_out():
    def run(root):
        (root / "channels" / "risk-archive").mkdir(parents=True)
        (root / "channels" / "risk-archive" / "2015.md").write_text("old", encoding="utf-8")
        (root / "channels" / "risk-archive" / "2026.md").write_text("new", encoding="utf-8")
        removed = er.prune_dated(dry=False)
        assert "channels/risk-archive/2015.md" in removed
        assert not (root / "channels" / "risk-archive" / "2015.md").exists()
        assert (root / "channels" / "risk-archive" / "2026.md").exists()
    _with_temp_repo(run)


def test_conversation_store_trimmed_to_cap():
    def run(root):
        conv = root / "channels" / "conversation"
        conv.mkdir(parents=True)
        big = "# Desi\n\n" + ("X" * 5000)
        (conv / "desi.md").write_text(big, encoding="utf-8")
        changed = er.prune_conversation(dry=False)
        assert any("channels/conversation/desi.md" in c for c in changed)
        trimmed = (conv / "desi.md").read_text(encoding="utf-8")
        assert len(trimmed) <= 1000
        assert trimmed.startswith("# Desi")  # header preserved
    _with_temp_repo(run)


def test_conversation_under_cap_untouched():
    def run(root):
        conv = root / "channels" / "conversation"
        conv.mkdir(parents=True)
        small = "# Desi\n\nshort memory"
        (conv / "desi.md").write_text(small, encoding="utf-8")
        changed = er.prune_conversation(dry=True)
        assert changed == []
    _with_temp_repo(run)
