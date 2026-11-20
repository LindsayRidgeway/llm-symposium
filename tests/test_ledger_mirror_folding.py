"""A mirrored verdict has to be *read*, not only written.

Measured 2026-11-20: `--queue dmitri` offered four items whose verdicts had already been written
three times — by gemini on 11-19, by desi on 11-19 and 11-20, by gemini again on 11-20 — because
each run wrote the verdict to its own file (the only write that survives the landing machine's
atomic patch) and every reader in `channels/item_ledger.py` loaded `items.jsonl` alone. The verdict
landed; the queue never saw it; the next wake reviewed the same item from scratch.

These tests pin the read side of the mirror. The write side is pinned by
`tests/test_ledger_verdict_mirror.py`.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "channels"))

import item_ledger  # noqa: E402


def _write_ledger(tmp_path, rows):
    path = tmp_path / "items.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def _write_mirror(tmp_path, name, payload):
    vdir = tmp_path / "ledger-verdicts"
    vdir.mkdir(exist_ok=True)
    (vdir / name).write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _row(item_id, **kw):
    row = {"id": item_id, "filed_utc": "2026-11-19T17:00:00Z", "paths": ["channels/x.md"]}
    row.update(kw)
    return row


def test_a_mirror_the_file_does_not_carry_still_judges_the_item(tmp_path):
    path = _write_ledger(tmp_path, [_row("20261119T172822Z-a8ec94b3", assigned_to="dmitri")])
    _write_mirror(tmp_path, "20261120T213131Z-20261119T172822Z-a8ec94b3.json", {
        "id": "20261119T172822Z-a8ec94b3", "state": "accomplished",
        "state_utc": "2026-11-20T21:31:31Z", "reviewer": "dmitri",
        "reason": "recovered its verdicts to main"})

    items = item_ledger.load_judged(path)

    assert items["20261119T172822Z-a8ec94b3"]["state"] == "accomplished"
    assert items["20261119T172822Z-a8ec94b3"]["reviewer"] == "dmitri"
    # and the queue that spent five wakes on it no longer offers it
    assert item_ledger.queue_size(items, "dmitri") == 0
    # the fold is a read: the file on disk is untouched, so replay is still owed
    assert "accomplished" not in path.read_text(encoding="utf-8")


def test_an_older_mirror_cannot_overwrite_a_newer_human_verdict(tmp_path):
    path = _write_ledger(tmp_path, [_row(
        "20261110T000000Z-deadbeef", state="postponed", reviewer="desi",
        state_utc="2026-11-19T12:00:00Z", reason="blocked on the account")])
    _write_mirror(tmp_path, "20261118T090000Z-20261110T000000Z-deadbeef.json", {
        "id": "20261110T000000Z-deadbeef", "state": "accomplished",
        "state_utc": "2026-11-18T09:00:00Z", "reviewer": "gemini", "reason": "done"})

    row = item_ledger.load_judged(path)["20261110T000000Z-deadbeef"]

    assert (row["state"], row["reviewer"]) == ("postponed", "desi")
    assert row["reason"] == "blocked on the account"


def test_a_mirror_newer_than_a_landing_machine_stamp_wins(tmp_path):
    path = _write_ledger(tmp_path, [_row(
        "20261108T065157Z-5f217af9", state="accomplished", reviewer="auto:path",
        state_utc="2026-11-08T06:51:57Z")])
    _write_mirror(tmp_path, "20261119T172946Z-20261108T065157Z-5f217af9.json", {
        "id": "20261108T065157Z-5f217af9", "state": "accomplished",
        "state_utc": "2026-11-19T17:29:46Z", "reviewer": "gemini", "reason": "read the report"})

    row = item_ledger.load_judged(path)["20261108T065157Z-5f217af9"]

    assert row["reviewer"] == "gemini"
    assert row["verdict_folded_from_mirror"] is True


def test_a_folded_verdict_clears_the_reading_queue(tmp_path):
    path = _write_ledger(tmp_path, [_row(
        "20261107T120350Z-b8a6fc82", state="accomplished", reviewer="auto:land",
        state_utc="2026-11-07T12:03:50Z", reading_assigned_to="dmitri")])
    assert len(item_ledger.reading_queue(path, "dmitri")) == 1

    _write_mirror(tmp_path, "20261119T180000Z-20261107T120350Z-b8a6fc82.json", {
        "id": "20261107T120350Z-b8a6fc82", "state": "accomplished",
        "state_utc": "2026-11-19T18:00:00Z", "reviewer": "dmitri", "reason": "read the report"})

    assert item_ledger.reading_queue(path, "dmitri") == []


def test_a_mirror_never_invents_an_item(tmp_path):
    path = _write_ledger(tmp_path, [_row("20261119T000000Z-11111111")])
    _write_mirror(tmp_path, "20261119T180000Z-20261119T000000Z-22222222.json", {
        "id": "20261119T000000Z-22222222", "state": "accomplished",
        "state_utc": "2026-11-19T18:00:00Z", "reviewer": "desi", "reason": "x"})

    assert "20261119T000000Z-22222222" not in item_ledger.load_judged(path)


def test_the_physical_gap_is_still_reported_after_the_read_folds_it(tmp_path):
    path = _write_ledger(tmp_path, [_row("20261119T172822Z-a8ec94b3")])
    _write_mirror(tmp_path, "20261120T213131Z-20261119T172822Z-a8ec94b3.json", {
        "id": "20261119T172822Z-a8ec94b3", "state": "accomplished",
        "state_utc": "2026-11-20T21:31:31Z", "reviewer": "dmitri", "reason": "r"})

    pending = item_ledger.unreplayed_verdicts(path, tmp_path / "ledger-verdicts")

    assert pending == ["20261119T172822Z-a8ec94b3"]


def test_a_ledger_with_no_mirror_directory_reads_as_before(tmp_path):
    path = _write_ledger(tmp_path, [_row("20261119T000000Z-33333333")])

    row = item_ledger.load_judged(path)["20261119T000000Z-33333333"]

    assert row.get("state") is None
    assert "verdict_folded_from_mirror" not in row
