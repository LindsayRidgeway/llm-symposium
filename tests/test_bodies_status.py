#!/usr/bin/env python3
"""`scripts/bodies_status.py` must tell a live body from a dead one, offline.

The instrument exists because the cloud dead-man switch cannot see the local layer:
it fires when the *whole* commons goes quiet, so four live bodies keep one dead body
invisible. That makes two error modes the test has to pin, and both are failures of a
check that reads well but decides nothing:

1. **A loaded job is not a live body.** launchd can hold a job that exited (pid `-`),
   or hold a pid that has already been recycled onto a different process. The check
   must see the pid *and* confirm that pid runs this body's `bot.py`, or "loaded" reads
   as healthy while nothing answers Telegram.
2. **Empty credentials are a body waiting to crash-loop.** The plist keeps the job
   alive on failure, so a bot that starts without its key or mail password is restarted
   forever while `launchctl` reports it "up". The check must read `bot.env` for key
   *names* and empty values — and never put a value in the report.

Fully offline: every input is passed in, so this runs on the landing machine and on a
CI runner alike. Reads nothing outside a temp directory; writes nothing.
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import bodies_status as bs  # noqa: E402

LAUNCHCTL = """\
PID	Status	Label
-	0	com.lindsay.amigo.claude
501	0	com.lindsay.amigo.desi
-	78	com.lindsay.amigo.gemini
0	-15	com.dawn.telegram
"""

PS = """\
501     1 /usr/bin/python3 bot.py
999     1 /usr/bin/python3 unrelated.py
"""

GOOD_ENV = """\
# a comment
TELEGRAM_BOT_TOKEN=123:abc
DEEPSEEK_API_KEY_DESI=sk-real
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY_DESI}"
SYMPOSIUM_MAIL_USER_DESI=desi@example.com
SYMPOSIUM_MAIL_APP_PASSWORD_DESI=secret
TELEGRAM_TICK_MINUTES=120
"""

EMPTY_ENV = """\
TELEGRAM_BOT_TOKEN=
ANTHROPIC_API_KEY=
SYMPOSIUM_MAIL_USER_CLAUDE=claude@example.com
SYMPOSIUM_MAIL_APP_PASSWORD_CLAUDE=
"""


class EnvTests(unittest.TestCase):
    def test_parse_env_strips_quotes_and_comments(self):
        env = bs.parse_env(GOOD_ENV)
        self.assertEqual(env["DEEPSEEK_API_KEY"], "${DEEPSEEK_API_KEY_DESI}")
        self.assertNotIn("# a comment", env)

    def test_good_env_has_no_missing_groups(self):
        self.assertEqual(bs.missing_env_keys(GOOD_ENV, "DESI"), [])

    def test_empty_values_are_missing_and_named_not_printed(self):
        missing = bs.missing_env_keys(EMPTY_ENV, "CLAUDE")
        self.assertIn("TELEGRAM_BOT_TOKEN", missing)
        self.assertIn("provider API key", missing)
        self.assertIn("SYMPOSIUM_MAIL_APP_PASSWORD", missing)
        self.assertNotIn("SYMPOSIUM_MAIL_USER", missing)
        joined = " ".join(missing)
        self.assertNotIn("example.com", joined, "a value leaked into the report")

    def test_provider_key_matched_by_shape_not_name(self):
        for line in ("ANTHROPIC_API_KEY=x", "GOOGLE_API_KEY=x", "OPENAI_API_KEY=x", "DEEPSEEK_API_KEY_DMITRI=x"):
            env = (f"TELEGRAM_BOT_TOKEN=t\n{line}\n"
                   "SYMPOSIUM_MAIL_USER_T=u\nSYMPOSIUM_MAIL_APP_PASSWORD_T=p\n")
            self.assertEqual(bs.missing_env_keys(env, "T"), [], line)


class ParserTests(unittest.TestCase):
    def test_launchctl_header_and_dash_pid(self):
        jobs = bs.parse_launchctl(LAUNCHCTL)
        self.assertIsNone(jobs["com.lindsay.amigo.claude"]["pid"])
        self.assertEqual(jobs["com.lindsay.amigo.desi"]["pid"], 501)
        self.assertIn("com.dawn.telegram", jobs)

    def test_ps_maps_pid_to_argv(self):
        procs = bs.parse_ps(PS)
        self.assertTrue(bs.is_bot(procs, 501))
        self.assertFalse(bs.is_bot(procs, 999))
        self.assertFalse(bs.is_bot(procs, None))
        self.assertFalse(bs.is_bot(procs, 4242))


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.llm = Path(self.tmp.name) / "LLM"
        self.plist = Path(self.tmp.name) / "LaunchAgents"
        self.llm.mkdir()
        self.plist.mkdir()
        self.rows = bs.evaluate(
            ["claude", "desi"],
            {"claude": self.plist / "com.lindsay.amigo.claude.plist",
             "desi": self.plist / "com.lindsay.amigo.desi.plist"},
            {"desi": self.llm / "desi-bot"},
            bs.parse_launchctl(LAUNCHCTL), bs.parse_ps(PS),
            lambda d: GOOD_ENV,
        )
        self.by = {r["amigo"]: r for r in self.rows}

    def test_live_body_is_ok(self):
        self.assertTrue(self.by["desi"]["ok"])
        self.assertEqual(self.by["desi"]["pid"], 501)

    def test_loaded_but_dead_is_not_ok(self):
        claude = self.by["claude"]
        self.assertTrue(claude["loaded"])
        self.assertFalse(claude["running"])
        self.assertFalse(claude["ok"])

    def test_missing_dir_reports_env_and_is_not_ok(self):
        row = bs.evaluate(["ghost"], {}, {}, bs.parse_launchctl(LAUNCHCTL), bs.parse_ps(PS),
                          lambda d: "")[0]
        self.assertFalse(row["ok"])
        self.assertEqual(row["env_missing"], ["bot.env (no dir)"])

    def test_empty_credentials_make_a_running_body_not_ok(self):
        row = bs.evaluate(["desi"], {"desi": self.plist / "p"}, {"desi": self.llm / "desi-bot"},
                          bs.parse_launchctl(LAUNCHCTL), bs.parse_ps(PS), lambda d: EMPTY_ENV)[0]
        self.assertTrue(row["running"])
        self.assertFalse(row["ok"])

    def test_render_names_the_down_body(self):
        text = bs.render(self.rows)
        self.assertIn("1/2 bodies up", text)
        self.assertIn("DOWN", text)
        self.assertIn("claude", text)


class DiscoveryTests(unittest.TestCase):
    def test_union_of_dirs_and_plists(self):
        with tempfile.TemporaryDirectory() as tmp:
            llm = Path(tmp) / "LLM"
            plist = Path(tmp) / "LaunchAgents"
            for name in ("alpha", "beta"):
                d = llm / f"{name}-bot"
                d.mkdir(parents=True)
                (d / "bot.py").write_text("x")
            plist.mkdir()
            (plist / "com.lindsay.amigo.gamma.plist").write_text("<plist/>")
            (plist / "com.dawn.telegram.plist").write_text("<plist/>")
            names, _, dirs = bs.discover(llm, plist)
            self.assertEqual(names, ["alpha", "beta", "gamma"])
            self.assertEqual(set(dirs), {"alpha", "beta"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
