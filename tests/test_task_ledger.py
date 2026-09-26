#!/usr/bin/env python3
"""Tests for channels/task_ledger.py — the identity rule for commons task-ledger entries.

The defect these pin (measured 2026-09-25): `file_tasks` in the Telegram bot appends a line to
channels/tasks.md on every turn that mentions a topic and never checks whether the line is
already there, so one request was filed nine times and another four times. The bot's own copy
cannot be tested or landed from this checkout, so this suite pins the canonical rule the bot is
meant to call. No network, no repo writes.
"""
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from channels import task_ledger as tl  # noqa: E402

PROVENANCE = " — *(filed from Telegram)*"


def test_item_recognition():
    assert tl.is_item("- [ ] a task")
    assert tl.is_item("- [x] a done task")
    assert tl.is_item("  - [ ] indented")
    assert not tl.is_item("*Active task routing ledger*")
    assert not tl.is_item("plain prose")
    assert tl.item_body("- [x] **Desi:** fix X") == "**Desi:** fix X"
    assert tl.is_checked("- [x] done")
    assert not tl.is_checked("- [ ] open")


def test_provenance_and_markdown_are_not_identity():
    a = "- [ ] **Desi:** fix the ORS calculator" + PROVENANCE
    b = "- [ ] Desi: fix the ORS calculator *Done 2026-09-17 (Gemini)*"
    assert tl.similarity(tl.item_body(a), tl.item_body(b)) == 1.0


def test_identical_refilings_are_duplicates():
    """The measured case: nine copies of one request."""
    item = "Telegram image intake, all five doors" + PROVENANCE
    lines = [f"- [ ] {item}"] * 9
    assert tl.similarity(item, item) == 1.0
    assert len(tl.new_items([item], lines)) == 0


def test_new_items_filters_existing_and_self_dedupes():
    existing = ["- [x] **Desi:** fix the ORS calculator" + PROVENANCE]
    batch = ["**Desi:** fix the ORS calculator" + PROVENANCE,   # already filed
             "Build second rover kit",                          # new
             "Build second rover kit"]                          # repeated in the same batch
    kept = tl.new_items(batch, existing)
    assert kept == ["Build second rover kit"], kept


def test_distinct_items_are_not_merged():
    a = "correct the sodium figure: 2.5 g salt per litre is about 43 mmol/L"
    b = "correct the sodium figure: 5.0 g salt per litre is about 86 mmol/L"
    assert not tl.is_duplicate(a, [f"- [ ] {b}"])


def test_dedupe_keeps_first_position_longer_text_and_ors_the_checkbox():
    lines = [
        "# Commons tasks",
        "",
        "- [ ] **Lindsay, one photo:** send an image" + PROVENANCE,
        "- [x] **Lindsay, one photo:** send an image to any of the five bots and confirm the"
        " reply describes what is in it" + PROVENANCE,
        "",
        "## Open Risks",
    ]
    out, merged = tl.dedupe_lines(lines)
    assert len(merged) == 1, merged
    assert sum(1 for ln in out if tl.is_item(ln)) == 1
    survivor = next(ln for ln in out if tl.is_item(ln))
    assert survivor.startswith("- [ ] "), survivor           # checkbox AND'd: never look done
    assert "confirm the reply describes what is in it" in survivor   # longer text kept
    assert out.index(survivor) == 2                            # first position kept
    assert out[-1] == "## Open Risks"                          # non-entries untouched
    # Idempotent: running it again is a no-op.
    out2, merged2 = tl.dedupe_lines(out)
    assert merged2 == []
    assert out2 == out


def test_near_miss_is_reported_not_merged():
    """Two items can read alike and be two tasks. Only the report says so."""
    lines = [
        "- [ ] install the new pi card and verify the camera works end to end",
        "- [ ] install the new pi card and verify the camera works again",
    ]
    score = tl.similarity(tl.item_body(lines[0]), tl.item_body(lines[1]))
    assert tl.NEAR_MISS_FLOOR <= score < tl.NEAR_DUPLICATE, score
    out, merged = tl.dedupe_lines(lines)
    assert merged == []
    assert out == lines
    pairs = tl.duplicate_pairs(lines)
    assert len(pairs) == 1 and pairs[0]["score"] == score and pairs[0]["same"] is False


def test_check_and_apply_on_a_temp_file():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "tasks.md"
        p.write_text(
            "# Commons tasks\n\n## Filed\n"
            "- [ ] **Desi:** file each inbound message verbatim before replying\n"
            "- [ ] **Desi:** file each inbound message verbatim before replying"
            + PROVENANCE + "\n",
            encoding="utf-8")
        report = tl.check_file(p)
        assert len(report["same"]) == 1 and report["near"] == []
        assert report["items"] == 2
        assert tl.apply_file(p) == 1
        assert tl.check_file(p)["same"] == []
        assert p.read_text(encoding="utf-8").count("file each inbound message") == 1


def test_live_ledger_has_no_exact_duplicates():
    """Regression guard on the real file: a refiling must never reach the human's ledger."""
    report = tl.check_file(REPO_ROOT / tl.LEDGER_REL)
    assert "error" not in report, report
    assert report["same"] == [], report["same"]


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
