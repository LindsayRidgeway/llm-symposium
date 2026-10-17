#!/usr/bin/env python3
"""CI usage ledger — what a direct provider call cost, and how we know.

Written 2026-10-17 by Desi. Origin: `research/2026-10-16-the-burn-so-far.md` gap 1 — the daily
GitHub Actions runner bills the human's API keys and reported nothing. The wiring that records
*tokens* landed 2026-10-16; the money did not, because no provider returns a price with a
response, so every runner row carried `cost_usd: None` and `--summary` printed "not reported"
for the largest automatic spender in the commons.

The fix is an estimate from the *measured* blended rate in `channels/usage/model-prices.json`
(what these architectures actually cost per million tokens in a real month, not a list price).
Two failure modes matter more than the arithmetic:

1. **A guess dressed as a measurement.** An unknown provider or an unreadable price file must
   produce no cost at all, never a plausible-looking number. `None` is a true statement about
   our ignorance; `0.0` would say the call was free.
2. **A number whose provenance is hidden.** Every estimated row says so in `cost_basis`, and
   `--summary` marks it and footnotes the rate's date — otherwise the estimate quietly becomes
   a bill, which is how an endowment gets sized against a fiction.

Run: python3 tests/test_usage_cost_estimate.py      (exit 0 pass, 1 fail)
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


DOC = usage.load_prices()
RATES = DOC.get("rates_usd_per_million") or {}
AS_OF = DOC.get("as_of")


def blended(amigo):
    return ((RATES.get(amigo) or {}).get("blended"))


# ---- 1. the arithmetic, against the file rather than against a remembered number ------------
for provider, amigo, tokens in (("openai", "tarik", 1_000_000),
                                ("google", "gemini", 2_000_000),
                                ("anthropic", "claude", 500_000),
                                ("deepseek", "desi", 1_000_000)):
    rate = blended(amigo)
    if not isinstance(rate, (int, float)):
        check("rate present for %s" % amigo, False, "missing from model-prices.json")
        continue
    cost, basis = usage.estimate_cost_usd(provider, "some-model-name",
                                         {"total": tokens})
    want = round(tokens * rate / 1_000_000, 6)
    check("%s: %d tokens priced at the measured rate" % (provider, tokens),
          cost is not None and abs(cost - want) < 1e-9,
          "got %r want %r" % (cost, want))
    check("%s: the row says the number is an estimate" % provider,
          isinstance(basis, str) and basis.startswith("estimate:"),
          str(basis))

check("the basis names the measurement date, not today's date",
      AS_OF is None or any((usage.estimate_cost_usd(p, "m", {"total": 1000})[1] or ""
                            ).endswith(str(AS_OF))
                           for p in ("openai", "deepseek")),
      str(AS_OF))

# ---- 2. never a guess ------------------------------------------------------------------------
cost, basis = usage.estimate_cost_usd("cohere", "command", {"total": 1_000_000})
check("unknown provider: no cost, no basis", cost is None and basis is None,
      "%r %r" % (cost, basis))

cost, basis = usage.estimate_cost_usd("openai", "gpt-6-astra", {"total": 0})
check("no tokens reported: no cost (not a free call)", cost is None, str(cost))

cost, basis = usage.estimate_cost_usd("openai", "gpt-6-astra", {"total": 1000},
                                     path=Path(tempfile.gettempdir()) / "no-such-prices-xyz.json")
check("unreadable price file: no cost", cost is None, str(cost))

# ---- 3. a real row, written the way the runner writes it -------------------------------------
tmp = Path(tempfile.mkdtemp()) / "ci-usage.jsonl"
usage.record_api_call("openai", "gpt-6-astra",
                      {"usage": {"prompt_tokens": 900_000, "completion_tokens": 100_000}},
                      source="symposium-runner", path=tmp)
rows = usage.load_rows(tmp)
check("one row written", len(rows) == 1, str(len(rows)))
row = rows[0] if rows else {}
check("row carries a cost", isinstance(row.get("cost_usd"), (int, float)),
      str(row.get("cost_usd")))
check("row carries its provenance", str(row.get("cost_basis") or "").startswith("estimate:"),
      str(row.get("cost_basis")))
check("row keeps the source that named it", row.get("source") == "symposium-runner",
      str(row.get("source")))

summary = usage.summarize(None, tmp)
check("summary prices the row", "$1.86 (est)" in summary, summary)
check("summary marks the price as an estimate", "(est)" in summary, summary)
check("summary footnotes the rate's date",
      ("measured %s" % AS_OF) in summary if AS_OF else "blended rate measured" in summary,
      summary)

# ---- 4. a cost the provider or goose reported is not painted as an estimate -------------------
reported = Path(tempfile.mkdtemp()) / "ci-usage.jsonl"
usage.record_rows([
    {"at": "2026-10-17T00:00:00+00:00", "source": "ci-goose", "provider": "openai",
     "model": "goose-run", "model_calls": 12, "input": 10, "output": 10, "cache_read": 0,
     "total": 20, "cost_usd": 0.015998178, "completed": True, "unrecorded": False},
    {"at": "2026-10-17T00:00:01+00:00", "source": "api", "provider": "cohere",
     "model": "command", "input": 5, "output": 5, "cache_read": 0, "total": 10,
     "cost_usd": None, "cost_basis": None, "recorded": True},
], reported)
summary = usage.summarize(None, reported)
check("a reported cost is not marked as an estimate",
      "$0.0160" in summary and "(est)" not in summary, summary)
check("an unpriced model reads 'not reported', never $0.00",
      "not reported" in summary, summary)

print()
if fails:
    print("%d check(s) failed" % len(fails))
    sys.exit(1)
print("all checks passed")
