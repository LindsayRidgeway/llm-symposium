#!/usr/bin/env python3
"""The cache-write quantity — the fifth number the telemetry did not carry, and the rule it must obey.

Written 2026-11-10 by Desi, in the wake after the one that landed the instrument. Origin: the
to-do list said `cache_write_input_tokens is 0 on every run that reports it`, which is impossible
for a run that reads a 1.24 MB cached prefix it must have written the day before. `grep -rn
cache_write` reached only `channels/usage.py`, its tests and the usage README, so the field was
produced *outside* the repository — in the harness, in the goose session ledger — and no test in
here could see the anomaly, let alone guard it.

What the previous wake measured, and this file pins: in the Mac's own session ledger
(`~/.local/share/goose/sessions/sessions.db`, `usage_ledger`) 1,505 of 37,258 rows carry a
non-zero `cache_write_tokens`, up to 354,254 tokens in a single call, and every one of them is a
`claude-*` model. DeepSeek, OpenAI and Gemini report no write quantity at all, because their
caching has no write premium to report. So "0 on every CI run" was never a fact about the
caching; it was a fact about which provider the CI ledger was reading, and about a field that
was not carried at all before 2026-11-10.

Two names for one rule, and both are the reason this file exists:

* **A write is billed and a read is not billed the same way.** Anthropic charges a cache write at
  1.25x input and a cache read at 0.1x, so a summary that shows only reads understates the cost
  of exactly the runs that rebuild a prefix. The column is not decoration.
* **Absent is not zero.** A row written before 2026-11-10 has no `cache_write` key; a goose
  `complete` event that reports no write count carries none. Both mean *unknown*, and the whole
  reason the field was misread for weeks is that they were counted as zero. The summary must
  therefore say how many runs knew, and say when the figure it prints is a floor.

Run directly (`python3 tests/test_usage_cache_write.py`); no pytest in this checkout.
"""
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("channels_usage", REPO / "channels" / "usage.py")
usage = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(usage)


def _row(**kw):
    """A ledger row of the shape `summarize` reads, with only the fields a test cares about."""
    base = {"provider": "anthropic", "model": "claude-x", "input": 1000, "output": 100,
            "cache_read": 800, "total": 1100, "cost_usd": 0.01, "model_calls": 1}
    base.update(kw)
    return base


class ApiUsageCarriesTheWrite(unittest.TestCase):
    """`api_usage` must read the write quantity where the provider puts it, and nowhere else."""

    def test_anthropic_write_is_read_from_its_own_name(self):
        out = usage.api_usage("anthropic", {"usage": {
            "input_tokens": 120, "output_tokens": 40,
            "cache_read_input_tokens": 9000, "cache_creation_input_tokens": 2400}})
        self.assertEqual(out["cache_write"], 2400)
        self.assertEqual(out["cache_read"], 9000)

    def test_anthropic_without_a_write_key_reports_zero_by_contract(self):
        # The function's docstring promises zeros where a provider reports nothing, so a caller
        # can sum without checking. That promise is why the *ledger* needs its own unknown rule.
        out = usage.api_usage("anthropic", {"usage": {
            "input_tokens": 10, "output_tokens": 2, "cache_read_input_tokens": 5}})
        self.assertEqual(out["cache_write"], 0)

    def test_openai_shape_carries_no_write(self):
        out = usage.api_usage("openai", {"usage": {
            "prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110,
            "prompt_tokens_details": {"cached_tokens": 40}}})
        self.assertEqual(out["cache_read"], 40)
        self.assertEqual(out["cache_write"], 0)

    def test_google_shape_carries_no_write(self):
        out = usage.api_usage("google", {"usageMetadata": {
            "promptTokenCount": 50, "candidatesTokenCount": 5, "totalTokenCount": 55,
            "cachedContentTokenCount": 20}})
        self.assertEqual(out["cache_read"], 20)
        self.assertEqual(out["cache_write"], 0)

    def test_a_non_response_is_still_zero_shaped(self):
        out = usage.api_usage("anthropic", None)
        self.assertEqual(out["cache_write"], 0)
        self.assertIn("cache_write", out)


class SdkPathCarriesTheWrite(unittest.TestCase):
    """The object-shaped response (the SDK path) must not lose the quantity on the way through."""

    def test_sdk_anthropic_write_survives_normalisation(self):
        resp = types.SimpleNamespace(usage=types.SimpleNamespace(
            input_tokens=300, output_tokens=30,
            cache_read_input_tokens=1000, cache_creation_input_tokens=777))
        out = usage.sdk_usage("anthropic", resp)
        self.assertEqual(out["cache_write"], 777)

    def test_sdk_response_without_usage_reports_zero(self):
        out = usage.sdk_usage("anthropic", types.SimpleNamespace(usage=None))
        self.assertEqual(out["cache_write"], 0)


class StreamUsageKeepsAbsentAbsent(unittest.TestCase):
    """A goose `complete` event either carries a write count or is unknown. Never zero."""

    def _stream(self, complete):
        fh = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
        fh.write(json.dumps({"type": "message", "content": "hi"}) + "\n")
        fh.write(json.dumps(complete) + "\n")
        fh.close()
        self.addCleanup(lambda: Path(fh.name).unlink(missing_ok=True))
        return fh.name

    def test_complete_event_with_a_write_count(self):
        out = usage.goose_stream_usage(self._stream({
            "type": "complete", "input_tokens": 1000, "output_tokens": 100,
            "cache_read_input_tokens": 800, "cache_write_input_tokens": 1250,
            "total_tokens": 1100, "cost_usd": 0.02}))
        self.assertEqual(out["cache_write"], 1250)

    def test_complete_event_without_a_write_count_is_none_not_zero(self):
        # This is the assertion the whole file exists for: a CI ledger full of these is a
        # statement about the events, not about anyone's caching.
        out = usage.goose_stream_usage(self._stream({
            "type": "complete", "input_tokens": 1000, "output_tokens": 100,
            "cache_read_input_tokens": 800, "total_tokens": 1100, "cost_usd": 0.02}))
        self.assertIsNone(out["cache_write"])

    def test_a_missing_file_is_none_not_zero(self):
        out = usage.goose_stream_usage("/nonexistent/does-not-exist.jsonl")
        self.assertIsNone(out["cache_write"])


class SummarySaysHowManyRunsKnew(unittest.TestCase):
    """The table must show the write, and must never let unknown rows read as zero."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "usage.json"

    def _summary(self, rows):
        return usage.summarize(rows, path=self.tmp)

    def test_the_column_exists(self):
        text = self._summary([_row(cache_write=100)])
        self.assertIn("cache write", text)
        header, sep = text.splitlines()[0], text.splitlines()[1]
        self.assertEqual(header.count("|"), sep.count("|"))

    def test_a_known_write_is_printed_plainly(self):
        text = self._summary([_row(cache_write=2400)])
        self.assertIn("2,400", text)
        self.assertNotIn("(on ", text)

    def test_an_old_row_without_the_key_makes_the_figure_a_floor(self):
        # One row written after 2026-11-10, one written before it: the pre-fix shape is absent.
        text = self._summary([_row(cache_write=2400), _row()])
        self.assertIn("(on 1 of 2)", text)
        self.assertIn("carry no cache-write count", text)

    def test_an_explicit_zero_counts_as_known(self):
        # A provider that reports a write of 0 has told us something; a row with no key has not.
        text = self._summary([_row(cache_write=0)])
        self.assertNotIn("(on ", text)
        self.assertIn("| 0 |", text)

    def test_all_unknown_never_prints_a_bare_zero(self):
        text = self._summary([_row(), _row()])
        self.assertIn("(on 0 of 2)", text)
        self.assertIn("carry no cache-write count", text)

    def test_the_write_total_sums_only_known_rows(self):
        rows = [_row(cache_write=1000), _row(cache_write=250), _row(),
                _row(model="claude-y", cache_write=5)]
        text = self._summary(rows)
        self.assertIn("(on 2 of 3)", text)      # three claude-x rows, two of which knew
        self.assertIn("1,250", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
