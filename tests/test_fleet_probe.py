#!/usr/bin/env python3
"""Tests for `scripts/fleet_probe.py`. Offline — canned records and injected probes, no network.

Why these exist. The tool's whole claim is that a record and the wire can be compared without a sweep,
and its whole danger is the opposite: a record that looks authoritative while the network says something
else. So the cases pinned here are the ones where the two disagree — a name that resolves somewhere the
record does not hold (`MISMATCH`, exit 3), a body that is merely asleep (`down`, exit 0), and a record
that cannot be read as data at all (exit 2, never guessed around). The last class is the one that would
otherwise fail quietly: a fenced block that has been hand-edited into invalid JSON would silently turn
"three bodies" into "no bodies".

Nothing here calls ping or dscacheutil: both are injected.
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fleet_probe as fp  # noqa: E402

RECORD_TEXT = """
Some prose above the data.

```json
{
  "measured_utc": "2026-10-24T11:35:00Z",
  "hosts": [
    {"name": "lander", "address": "192.168.1.178", "role": "the body", "mdns": "raspberrypi.local"},
    {"name": "gemini", "address": "192.168.1.175", "role": "gemini's body", "mdns": "gemini.local"}
  ]
}
```

Prose below it, which the parser must ignore.
"""


class LoadRecordTest(unittest.TestCase):
    def test_reads_the_fenced_block_and_ignores_the_prose(self):
        record = fp.load_record(RECORD_TEXT)
        self.assertEqual(record["measured_utc"], "2026-10-24T11:35:00Z")
        self.assertEqual([h["name"] for h in record["hosts"]], ["lander", "gemini"])

    def test_no_fence_is_an_error_not_an_empty_fleet(self):
        with self.assertRaises(fp.RecordError):
            fp.load_record("# a record with no data in it\n")

    def test_invalid_json_is_an_error(self):
        with self.assertRaises(fp.RecordError):
            fp.load_record('```json\n{"hosts": [,]}\n```')

    def test_empty_hosts_list_is_an_error(self):
        with self.assertRaises(fp.RecordError):
            fp.load_record('```json\n{"hosts": []}\n```')

    def test_missing_required_field_names_the_row(self):
        text = '```json\n{"hosts": [{"name": "lander", "role": "no address"}]}\n```'
        with self.assertRaises(fp.RecordError) as caught:
            fp.load_record(text)
        self.assertIn("lander", str(caught.exception))
        self.assertIn("address", str(caught.exception))

    def test_two_bodies_at_one_address_is_an_error(self):
        text = (
            '```json\n{"hosts": ['
            '{"name": "a", "address": "192.168.1.178", "role": "x"},'
            '{"name": "b", "address": "192.168.1.178", "role": "y"}]}\n```'
        )
        with self.assertRaises(fp.RecordError) as caught:
            fp.load_record(text)
        self.assertIn("192.168.1.178", str(caught.exception))

    def test_one_name_twice_is_an_error(self):
        text = (
            '```json\n{"hosts": ['
            '{"name": "a", "address": "192.168.1.1", "role": "x"},'
            '{"name": "a", "address": "192.168.1.2", "role": "y"}]}\n```'
        )
        with self.assertRaises(fp.RecordError):
            fp.load_record(text)

    def test_missing_file_is_an_error(self):
        with self.assertRaises(fp.RecordError):
            fp.load_record_file(str(ROOT / "rover" / "no-such-record.md"))


class ProbeTest(unittest.TestCase):
    def record(self):
        return fp.load_record(RECORD_TEXT)

    def test_answers_at_the_recorded_address_is_up(self):
        rows = fp.probe(self.record(), ping_fn=lambda a: True, resolve_fn=lambda n: None)
        self.assertEqual([row["verdict"] for row in rows], ["up", "up"])
        self.assertTrue(all(row["answers"] is True for row in rows))

    def test_silence_is_down_and_not_an_error(self):
        rows = fp.probe(self.record(), ping_fn=lambda a: False, resolve_fn=lambda n: None)
        self.assertEqual([row["verdict"] for row in rows], ["down", "down"])
        out = fp.render(rows, "2026-10-24T11:35:00Z")
        self.assertIn("0 of 2 answered", out)
        self.assertIn("Nothing in the record contradicts", out)

    def test_a_name_that_resolves_elsewhere_is_a_mismatch(self):
        def resolve(name):
            return "192.168.1.199" if name == "raspberrypi.local" else None

        rows = fp.probe(self.record(), ping_fn=lambda a: True, resolve_fn=resolve)
        self.assertEqual(rows[0]["verdict"], "MISMATCH")
        self.assertEqual(rows[0]["resolved"], "192.168.1.199")
        out = fp.render(rows)
        self.assertIn("MISMATCH: lander resolves to 192.168.1.199 but the record says 192.168.1.178", out)

    def test_a_name_that_resolves_correctly_is_not_a_mismatch(self):
        rows = fp.probe(
            self.record(),
            ping_fn=lambda a: True,
            resolve_fn=lambda n: "192.168.1.178" if n == "raspberrypi.local" else None,
        )
        self.assertEqual(rows[0]["verdict"], "up")

    def test_a_host_without_a_mdns_name_is_never_resolved(self):
        seen = []

        def resolve(name):
            seen.append(name)
            return None

        record = fp.load_record('```json\n{"hosts": [{"name": "mac", "address": "192.168.1.163", "role": "the Mac"}]}\n```')
        fp.probe(record, ping_fn=lambda a: True, resolve_fn=resolve)
        self.assertEqual(seen, [])

    def test_unprobed_rows_carry_no_verdict_about_the_wire(self):
        rows = fp.unprobed(self.record())
        self.assertEqual([row["answers"] for row in rows], [None, None])
        out = fp.render(rows)
        self.assertIn("nothing was probed", out)


class RenderTest(unittest.TestCase):
    def test_the_table_names_every_body_and_its_address(self):
        rows = fp.probe(fp.load_record(RECORD_TEXT), ping_fn=lambda a: True, resolve_fn=lambda n: None)
        out = fp.render(rows, "2026-10-24T11:35:00Z")
        for expected in ("lander", "192.168.1.178", "gemini", "192.168.1.175", "record measured 2026-10-24T11:35:00Z"):
            self.assertIn(expected, out)


class MainTest(unittest.TestCase):
    def write(self, text):
        handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def run_main(self, argv, **kwargs):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = fp.main(argv, **kwargs)
        return code, out.getvalue(), err.getvalue()

    def test_all_up_exits_zero(self):
        code, out, _ = self.run_main(
            ["--record", self.write(RECORD_TEXT)],
            ping_fn=lambda a: True,
            resolve_fn=lambda n: None,
        )
        self.assertEqual(code, 0)
        self.assertIn("2 of 2 answered", out)

    def test_mismatch_exits_three(self):
        code, _, _ = self.run_main(
            ["--record", self.write(RECORD_TEXT)],
            ping_fn=lambda a: False,
            resolve_fn=lambda n: "192.168.1.199",
        )
        self.assertEqual(code, 3)

    def test_unreadable_record_exits_two_with_a_message(self):
        code, _, err = self.run_main(["--record", self.write("no data here\n")])
        self.assertEqual(code, 2)
        self.assertIn("fleet_probe:", err)

    def test_no_network_prints_the_record_and_touches_nothing(self):
        def explode(*_args, **_kwargs):
            raise AssertionError("--no-network must not probe")

        code, out, _ = self.run_main(
            ["--record", self.write(RECORD_TEXT), "--no-network"],
            ping_fn=explode,
            resolve_fn=explode,
        )
        self.assertEqual(code, 0)
        self.assertIn("nothing was probed", out)

    def test_json_mode_is_machine_readable(self):
        code, out, _ = self.run_main(
            ["--record", self.write(RECORD_TEXT), "--json"],
            ping_fn=lambda a: True,
            resolve_fn=lambda n: None,
        )
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["measured_utc"], "2026-10-24T11:35:00Z")
        self.assertEqual(len(data["hosts"]), 2)


class TheRealRecordTest(unittest.TestCase):
    """The file shipped in the repository, checked as data — a record that cannot be parsed is no record."""

    def setUp(self):
        self.record = fp.load_record_file(str(fp.DEFAULT_RECORD))

    def test_it_parses_and_says_when_it_was_measured(self):
        self.assertTrue(self.record.get("measured_utc"))

    def test_every_address_is_on_the_home_lan(self):
        for host in self.record["hosts"]:
            self.assertTrue(host["address"].startswith("192.168.1."), host)

    def test_every_host_says_how_sure_the_record_is(self):
        for host in self.record["hosts"]:
            self.assertTrue(host.get("confidence"), host["name"])


if __name__ == "__main__":
    unittest.main()
