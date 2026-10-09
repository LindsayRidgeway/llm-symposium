#!/usr/bin/env python3
"""Tests for channels/assignment.py — the reviewer-assignment rule (the human, 2026-10-09).

The rule: (a) assign the best-suited amigo, author excluded, reason written; (b) otherwise draw at
random among the least-expensive amigos at assignment time, and freeze the draw so it cannot re-roll.
These pin the four things that make the rule a rule rather than a preference: the author is never
picked, a competence match must be written down, the cost pool is a dated band, and the draw is
reproducible from the item id. No network, no writes to the repository.
"""
import sys
import tempfile
import traceback
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from channels import assignment as A  # noqa: E402

COSTS = {"as_of": "2026-10-09",
         "bands": [{"tier": "least-expensive", "members": ["desi", "dmitri"]},
                   {"tier": "mid", "members": ["gemini"]},
                   {"tier": "most-expensive", "members": ["claude", "tarik"]}]}
TODAY = date(2026, 10, 9)
ITEM = {"id": "20261009T120000Z-aaaaaaaa", "amigo": "gemini", "title": "a plain internal item"}


def test_author_is_never_drawn():
    for author in A.AMIGOS:
        d = A.decide({"id": "x", "amigo": author, "title": "t"}, costs=COSTS, today=TODAY)
        assert d["reviewer"] != author, (author, d)
        assert author not in d["eligible"]


def test_draw_lands_in_the_least_expensive_band():
    d = A.decide(ITEM, costs=COSTS, today=TODAY)
    assert d["method"] == "draw"
    assert d["band"] == ["desi", "dmitri"]
    assert d["reviewer"] in ("desi", "dmitri")


def test_the_draw_is_frozen_by_id():
    a = A.decide(ITEM, costs=COSTS, today=TODAY)
    b = A.decide(dict(ITEM), costs=COSTS, today=TODAY)
    assert a["reviewer"] == b["reviewer"]
    assert A.draw(["desi", "dmitri"], ITEM["id"]) == a["reviewer"]
    # pool order must not matter
    assert A.draw(["dmitri", "desi"], ITEM["id"]) == a["reviewer"]


def test_the_draw_is_not_a_constant():
    picks = {A.draw(["desi", "dmitri"], f"20261009T0000{i:02d}Z-aaaaaaaa") for i in range(40)}
    assert picks == {"desi", "dmitri"}, picks


def test_explicit_competence_wins_and_keeps_its_reason():
    d = A.decide(ITEM, costs=COSTS, best="claude", because="holds the keys", today=TODAY)
    assert d["method"] == "competence" and d["reviewer"] == "claude"
    assert "keys" in d["reason"]
    # a named match that is not eligible is not a match
    d2 = A.decide(ITEM, costs=COSTS, best="gemini", because="x", today=TODAY)
    assert d2["method"] == "draw" and d2["reviewer"] != "gemini"


def test_a_single_rule_fires_and_two_rules_do_not():
    item = {"id": "i", "amigo": "gemini", "title": "fix the mail identity"}
    one = [{"match": "mail", "amigo": "desi", "reason": "owns the mail channel"}]
    assert A.decide(item, competence=one, today=TODAY)["method"] == "competence"
    two = one + [{"match": "mail", "amigo": "tarik", "reason": "also mail"}]
    assert A.decide(item, competence=two, today=TODAY)["method"] == "draw"


def test_no_band_draws_from_everyone_and_says_so():
    d = A.decide(ITEM, costs={}, today=TODAY)
    assert d["band"] is None
    assert set(d["pool"]) == {"desi", "dmitri", "claude", "tarik"}
    assert "no cost band on record" in d["reason"]


def test_unknown_author_is_named_not_assumed():
    d = A.decide({"id": "u", "title": "no author"}, costs=COSTS, today=TODAY)
    assert d["author"] is None
    assert set(d["eligible"]) == set(A.AMIGOS)


def test_staleness_is_visible():
    assert not A.is_stale("2026-10-09", TODAY)
    assert A.is_stale("2026-01-01", TODAY)
    assert A.is_stale(None, TODAY)          # undated cannot be shown current


def test_freeze_on_disk_records_once():
    with tempfile.TemporaryDirectory() as tmp:
        store = Path(tmp) / "a.jsonl"
        first, wrote1 = A.assign(ITEM, path=store, costs=COSTS, today=TODAY)
        second, wrote2 = A.assign(ITEM, path=store, costs=COSTS, today=TODAY)
        assert wrote1 and not wrote2
        assert first == second
        assert len(store.read_text().strip().splitlines()) == 1


def test_the_real_cost_band_is_dated_and_covers_everyone():
    """A guard on the live cache: a band set that is undated or drops an amigo is not a pool."""
    costs = A.load_costs()
    assert costs, "channels/usage/cost-band.json is missing or unreadable"
    assert A.band_as_of(costs), "the cost band must carry an as_of date"
    members = [m for band in costs.get("bands", []) for m in band.get("members", [])]
    assert sorted(members) == sorted(A.AMIGOS), members
    assert len(members) == len(set(members)), "an amigo is in two bands"
    assert A.least_expensive(costs, A.AMIGOS), "the least-expensive band is empty"


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
