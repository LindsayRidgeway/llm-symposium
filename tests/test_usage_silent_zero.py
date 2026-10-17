#!/usr/bin/env python3
"""CI usage ledger — the silent zero that survived two fixes, and the rule that closes it.

Written 2026-10-17 by Desi. Origin: the to-do pointer said `wire the runner into the usage
ledger`, and checking rather than rebuilding showed the wiring is on main. What checking also
showed is a defect in the ledger itself, one layer above the two it had already closed.

The ledger's rule, in its own words (`channels/usage/README.md`): *"unrecorded — true = this run
spent tokens and we cannot say how many. Never record it as zero."* Two mechanisms enforce it
today: a goose run killed before it writes `complete` is flagged `unrecorded`, and the dict-vs-
SDK response shapes are normalised so a real response never reads as zero.

**The gap: a provider call that returns no usage block at all.** Such a row was written with
`recorded: false`, 0 tokens and no cost — and `summarize` counted only rows carrying the *other*
name, `unrecorded`. Measured before the fix, with an SDK response whose `usage` was None:

    | openai | gpt-6-astra | 1 | 1 | 0 | 0 | 0 | not reported |
    0 run(s) spent tokens and left no usage record (killed before completion).

So the table showed a free call and the footer said nothing was missing. That is the same lie
as a killed run recorded as zero, and it is the failure mode this file guards:

1. a provider call that reports no counts is **flagged**, and the summary counts it;
2. an old-shape row (`recorded: false`, no `unrecorded` key) still counts — the ledger is
   append-only, so rows written before the fix must not become invisible retroactively;
3. a real call with counts is **not** flagged (a guard that cries wolf gets switched off);
4. an empty goose attempt is not flagged either — zero calls is not spent-and-unrecorded.

Run: python3 tests/test_usage_silent_zero.py      (exit 0 pass, 1 fail)
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from channels import usage  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name,
                       ("  <- " + detail) if (detail and not cond) else ""))
    if not cond:
        fails.append(name)


class Obj:
    """Stand-in for an SDK response object (dot access, not a dict)."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


tmp = Path(tempfile.mkdtemp())

# ---- 1. a provider call that returned no counts is spent-and-unrecorded, not free -----------
silent = tmp / "silent.jsonl"
usage.record_sdk_call("openai", "gpt-6-astra", Obj(usage=None),
                      source="symposium-runner", path=silent)
row = (usage.load_rows(silent) or [{}])[0]
check("a response with no usage block still writes a row", row.get("provider") == "openai",
      json.dumps(row))
check("the row is flagged unrecorded (the README's own word)", row.get("unrecorded") is True,
      json.dumps(row))
check("the row keeps the older spelling for readers that use it", row.get("recorded") is False,
      json.dumps(row))
check("no cost is invented for it", row.get("cost_usd") is None, str(row.get("cost_usd")))

text = usage.summarize(None, silent)
check("the summary counts the unrecorded provider call", "1 row(s) spent tokens" in text, text)
check("the summary says why, not just how many",
      "provider response that carried no counts" in text, text)

# ---- 2. rows written before the fix still count (the file is append-only) -------------------
legacy = tmp / "legacy.jsonl"
usage.record_rows([{
    "at": "2026-10-16T00:00:00+00:00", "source": "symposium-runner", "provider": "anthropic",
    "model": "claude-sonnet-4-5", "input": 0, "output": 0, "cache_read": 0, "total": 0,
    "cost_usd": None, "cost_basis": None, "recorded": False,      # no `unrecorded` key
}], legacy)
text = usage.summarize(None, legacy)
check("an old-shape row is not made invisible by the new spelling",
      "1 row(s) spent tokens" in text, text)

# ---- 3. a real call is not flagged ----------------------------------------------------------
real = tmp / "real.jsonl"
usage.record_sdk_call(
    "anthropic", "claude-sonnet-4-5",
    Obj(usage=Obj(input_tokens=800, output_tokens=25, cache_read_input_tokens=700)),
    source="symposium-runner", path=real)
row = (usage.load_rows(real) or [{}])[0]
check("a real call is not flagged unrecorded", row.get("unrecorded") is False, json.dumps(row))
check("a real call still reads recorded", row.get("recorded") is True, json.dumps(row))
check("a real call carries a cost", isinstance(row.get("cost_usd"), (int, float)),
      str(row.get("cost_usd")))
text = usage.summarize(None, real)
check("the summary does not cry wolf over a recorded call", "0 row(s) spent tokens" in text, text)

# ---- 4. an empty goose attempt is neither spent nor unrecorded -------------------------------
empty_dir = tmp / "run-empty" / "attempt-1"
empty_dir.mkdir(parents=True)
(empty_dir / "worker.jsonl").write_text("", encoding="utf-8")
rows = usage._rows_from_goose_dir(tmp, "test-workflow", "1", "openai", "gpt-6-astra")
check("the empty attempt wrote a row", any(r.get("model_calls") == 0 for r in rows),
      json.dumps(rows))
check("no call at all is not reported as spent-and-unrecorded",
      all(not r.get("unrecorded") for r in rows), json.dumps(rows))

print()
if fails:
    print("%d check(s) failed" % len(fails))
    sys.exit(1)
print("all checks passed")
