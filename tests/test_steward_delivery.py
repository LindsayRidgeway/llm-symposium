"""The reject queue's requests reach the human, and the file says so only when they did.

2026-11-10 (Desi). Three items had carried `steward-requested: 2026-10-15` for 26 days and
`scripts/reject_queue_sweep.py --check` reported, correctly, that no delivery was on record for any
of them. It reported it to a run's stdout. The one channel the human reads is the counted daily
report, and `scripts/daily_report.py` did not mention the queue at all — so the check could see the
gap for ever without anyone who could close it seeing the check.

Two directions are pinned here, because both can rot silently:
  * a request with no delivery record appears in the report (else the gap stays invisible);
  * the delivery line is written by a send, under the item it belongs to (else the file claims a
    message that never went).
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import reject_queue_sweep as rqs  # noqa: E402

QUEUE = """# Reject queue

## A blocked item
- raised: 2026-10-01 by desi
- blocked because: the only missing piece is a private bot file this checkout may not edit
- reviewed: desi 2026-10-15 cannot (private bot file)
- steward-requested: 2026-10-15
- steward-note: channels/steward-notes/2026-10-26-reject-queue.md
"""

QUIET = """# Reject queue

## An item nobody has asked about yet
- raised: 2026-10-01 by desi
- blocked because: still being reviewed
- reviewed: desi 2026-10-15 cannot (private bot file)
"""


def test_an_undelivered_request_is_undelivered():
    assert [i["title"] for i in rqs.undelivered(rqs.parse(QUEUE))] == ["A blocked item"]


def test_the_report_line_names_the_request_and_when_it_was_asked():
    line = rqs.undelivered_line(rqs.parse(QUEUE))
    assert "1 request" in line, line
    assert "A blocked item" in line, line
    assert "2026-10-15" in line, line


def test_an_unasked_item_produces_no_line():
    assert rqs.undelivered_line(rqs.parse(QUIET)) == ""


def test_delivery_is_recorded_and_closes_the_gap():
    with tempfile.TemporaryDirectory() as d:
        q = Path(d) / "reject-queue.md"
        q.write_text(QUEUE, encoding="utf-8")
        rqs.record_delivery(q, {"A blocked item"}, "unit test", today="2026-11-10")
        text = q.read_text(encoding="utf-8")
        assert "- steward-delivered: unit test 2026-11-10" in text
        # under its own item, not floating at the top of the file
        assert text.index("steward-delivered") > text.index("## A blocked item")
        assert rqs.undelivered(rqs.parse(text)) == []
        assert rqs.undelivered_line(rqs.parse(text)) == ""


def test_the_delivery_writer_leaves_other_items_alone():
    with tempfile.TemporaryDirectory() as d:
        q = Path(d) / "reject-queue.md"
        q.write_text(QUEUE + "\n" + QUIET.split("\n", 2)[2], encoding="utf-8")
        rqs.record_delivery(q, {"A blocked item"}, "unit test", today="2026-11-10")
        text = q.read_text(encoding="utf-8")
        assert text.count("steward-delivered") == 1, text
        assert rqs.undelivered_line(rqs.parse(text)) == ""


def test_the_live_queue_is_readable_and_the_live_line_matches_it():
    """The report must be able to say something true about the file that is actually on disk."""
    live = (ROOT / "channels" / "reject-queue.md").read_text(encoding="utf-8")
    items = rqs.parse(live)
    assert items, "the reject queue parsed to nothing"
    waiting = rqs.undelivered(items)
    line = rqs.undelivered_line(items)
    if waiting:
        assert str(len(waiting)) in line
    else:
        assert line == ""


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)
