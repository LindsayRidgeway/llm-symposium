#!/usr/bin/env python3
"""CI usage ledger — the two things it must never get wrong.

Written 2026-09-25 by Desi. Origin: the human asked why the amigo wakes could not be tuned
against his real spend. They could not, because everything that runs in GitHub Actions spends
his API keys and reports nothing back — the numbers were there, in goose's `stream-json`, and
were uploaded as an artifact that expired unread.

Two failure modes matter more than the arithmetic, so they are what this checks:

1. **A killed run must not look free.** The first CI artifact inspected had 73 model calls, no
   `complete` event, exit 124 — real money, no record. If the ledger wrote zero for that, it
   would be worse than no ledger: a confident wrong number.
2. **A real provider response must not normalise to zero.** Anthropic sends `content` *and*
   `usage`; an early version of the shape detection keyed off `content` alone and silently
   recorded zeros for every Claude call.

Run: python3 tests/test_ci_usage_ledger.py      (exit 0 pass, 1 fail)
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


def write_stream(path: Path, events):
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # ---- 1. a completed run -----------------------------------------------------------------
    done = tmp / "run-complete" / "attempt-1"
    done.mkdir(parents=True)
    write_stream(done / "worker.jsonl", [
        {"type": "message", "message": {"role": "assistant"}},
        {"type": "message", "message": {"role": "assistant"}},
        {"type": "complete", "total_tokens": 900636, "input_tokens": 886527,
         "output_tokens": 14109, "cache_read_input_tokens": 853376,
         "cache_write_input_tokens": 0, "cost_usd": 0.015998178},
    ])
    u = usage.goose_stream_usage(done / "worker.jsonl")
    check("completed run: exact tokens read", u["total"] == 900636 and u["input"] == 886527,
          json.dumps(u))
    check("completed run: cost read", abs(u["cost_usd"] - 0.015998178) < 1e-9, str(u["cost_usd"]))
    check("completed run: not flagged unrecorded", u["completed"] and not u["unrecorded"])
    check("completed run: model calls counted", u["model_calls"] == 2, str(u["model_calls"]))

    # ---- 2. a run killed at its turn cap ----------------------------------------------------
    killed = tmp / "run-killed" / "attempt-1"
    killed.mkdir(parents=True)
    write_stream(killed / "worker.jsonl",
                 [{"type": "message", "message": {"role": "assistant"}}] * 73)
    k = usage.goose_stream_usage(killed / "worker.jsonl")
    check("killed run: flagged unrecorded, never zero", k["unrecorded"] is True, json.dumps(k))
    check("killed run: tokens reported as unknown, not 0", k["total"] is None, str(k["total"]))
    check("killed run: calls still counted (the money was real)", k["model_calls"] == 73,
          str(k["model_calls"]))

    # ---- 3. an empty file is not a killed run ----------------------------------------------
    empty = tmp / "run-empty" / "attempt-1"
    empty.mkdir(parents=True)
    write_stream(empty / "worker.jsonl", [])
    e = usage.goose_stream_usage(empty / "worker.jsonl")
    check("no calls at all: not flagged as spent-but-unrecorded", e["unrecorded"] is False)

    # ---- 4. the four provider shapes, as the APIs actually return them ----------------------
    real = {
        "desi": ("deepseek-v4-flash-vision-exp",
                 {"choices": [{"message": {"content": "hi"}}],
                  "usage": {"prompt_tokens": 900, "completion_tokens": 30, "total_tokens": 930,
                            "prompt_cache_hit_tokens": 800}}, (900, 30, 800)),
        "claude": ("claude-sonnet-5",
                   {"content": [{"type": "text", "text": "hi"}],
                    "usage": {"input_tokens": 800, "output_tokens": 25,
                              "cache_read_input_tokens": 700,
                              "cache_creation_input_tokens": 50}}, (800, 25, 700)),
        "gemini": ("gemini-3.8-flash",
                   {"candidates": [{"content": {"parts": [{"text": "hi"}]}}],
                    "usageMetadata": {"promptTokenCount": 1500, "candidatesTokenCount": 60,
                                      "totalTokenCount": 1560,
                                      "cachedContentTokenCount": 1400}}, (1500, 60, 1400)),
        "tarik": ("gpt-6-astra",
                  {"choices": [{"message": {"content": "hi"}}],
                   "usage": {"prompt_tokens": 1200, "completion_tokens": 40,
                             "total_tokens": 1240,
                             "prompt_tokens_details": {"cached_tokens": 1024}}}, (1200, 40, 1024)),
    }
    for amigo, (model, response, want) in real.items():
        u = usage.api_usage(amigo, response)
        got = (u["input"], u["output"], u["cache_read"])
        check("%s: shape normalises (content+usage must not read as zero)" % amigo,
              got == want, "got %r want %r" % (got, want))

    # ---- 5. the ledger round-trips, and the summary surfaces the unrecorded runs ------------
    led = tmp / "ci-usage.jsonl"
    rows = usage._rows_from_goose_dir(tmp, "test-workflow", "123", "openai", "gpt-6-astra")
    check("one row per goose attempt found", len(rows) == 3, str(len(rows)))
    usage.record_rows(rows, led)
    usage.record_api_call("claude", "claude-sonnet-5", real["claude"][1], path=led)
    back = usage.load_rows(led)
    check("ledger round-trips", len(back) == 4, str(len(back)))
    text = usage.summarize(back, led)
    check("summary names the unrecorded run",
          "1 run(s) spent tokens and left no usage record" in text, text)
    check("summary shows the api row's tokens", "claude-sonnet-5" in text and "800" in text)

    # ---- 6. a missing file is never an exception -------------------------------------------
    check("a missing worker.jsonl is handled, not raised",
          usage.goose_stream_usage(tmp / "nope" / "worker.jsonl")["model_calls"] == 0)

    # ---- 7. the SDK adapter: live response objects, not dicts (added 2026-10-16) ------------
    # `.github/scripts/runner.py` calls the providers through their SDKs and holds the response
    # *object*; `api_usage` cannot read it and would record zeros — the same silent-zero bug this
    # file's own section 4 warns about, one layer out. `sdk_usage` is the adapter that closes the
    # last gap in the burn figure. These are the shapes the SDKs actually return.
    class _Obj:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    sdk_cases = {
        "google": (_Obj(usage_metadata=_Obj(prompt_token_count=1500, candidates_token_count=60,
                                            cached_content_token_count=1400)), (1500, 60, 1400)),
        "anthropic": (_Obj(usage=_Obj(input_tokens=800, output_tokens=25,
                                      cache_read_input_tokens=700)), (800, 25, 700)),
        "openai": (_Obj(usage=_Obj(prompt_tokens=1200, completion_tokens=40, total_tokens=1240,
                                   prompt_tokens_details=_Obj(cached_tokens=1024))),
                   (1200, 40, 1024)),
        "deepseek": (_Obj(usage=_Obj(prompt_tokens=900, completion_tokens=30, total_tokens=930,
                                     prompt_cache_hit_tokens=800)), (900, 30, 800)),
    }
    for _prov, (_resp, _want) in sdk_cases.items():
        _u = usage.sdk_usage(_prov, _resp)
        _got = (_u["input"], _u["output"], _u["cache_read"])
        check("%s: SDK response object normalises (never zero)" % _prov, _got == _want,
              "got %r want %r" % (_got, _want))

    # A recorded SDK row must land in the ledger, under the right provider, with its tokens.
    led2 = tmp / "sdk-usage.jsonl"
    usage.record_sdk_call("anthropic", "claude-sonnet-5", sdk_cases["anthropic"][0], path=led2)
    rows2 = usage.load_rows(led2)
    check("record_sdk_call writes one row with provider and tokens",
          len(rows2) == 1 and rows2[0]["provider"] == "anthropic" and rows2[0]["input"] == 800,
          json.dumps(rows2))

    # ---- 8. the runner is wired, not merely capable -----------------------------------------
    # The adapter is worthless if the runner never calls it. This is the "registered but never
    # run" defect the evidence-table guard exists for, one layer down: a capability nothing uses.
    runner_src = (Path(__file__).resolve().parent.parent
                  / ".github" / "scripts" / "runner.py").read_text()
    check("runner imports the ledger adapter",
          "from channels import usage" in runner_src and "record_sdk_call" in runner_src)
    for _label, _needle in (("google", '_record_usage("google"'),
                            ("openai", '_record_usage("openai"'),
                            ("anthropic", '_record_usage("anthropic"'),
                            ("deepseek", "_record_usage(ds_provider")):
        check("runner records its %s review call" % _label,
              _needle in runner_src, "missing %r" % _needle)
    check("runner records the maintainer calls too (>=7 call sites)",
          runner_src.count("_record_usage(") >= 7,
          "found %d" % runner_src.count("_record_usage("))

print()
print("%d check(s) failed" % len(fails) if fails else "all checks passed")
sys.exit(1 if fails else 0)
