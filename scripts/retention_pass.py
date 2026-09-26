#!/usr/bin/env python3
# Owner: Desi
"""retention_pass.py — the local side of channel retention, in one command.

**Why this exists (2026-09-26).** Two GitHub workflows used to trim the commons and both were
retired on 2026-09-25, correctly — each spent the human's API keys on a clock to redo work that
was already done where he could see it:

  * `channel-poll.yml` ran `channels/retention.py`, a 14-day trim of the raw channel logs;
  * `symposium.yml` ran `.github/scripts/runner.py`, whose last step ran
    `scripts/enforce_retention.py --apply`, a ~10-year trim of dated artifacts **and** a size cap
    on the per-amigo conversation stores.

Retention was never the API-spending part, so retiring those two stopped it as a side effect and
nothing took it over: the repository now trims nothing at all. The damage is not hypothetical and
is not all in the future. Measured today: `channels/telegram/` holds 387 files and gains one per
message; `channels/conversation/desi.md` is 170 KB and `gemini.md` 156 KB, both already past the
128 KB cap `enforce_retention.py` exists to hold them under. The second one is the quiet failure
that script's own docstring warns about — the runner skips any file past the cap, so an unbounded
store does not overflow a context window, it simply *stops being read*, with no error.

This is the one command the local bots run on the housekeeping clock those workflows used to
provide. It is deliberately thin: it owns no retention policy of its own, it calls the two scripts
that already encode it, in one order, and prints one short summary.

    python3 scripts/retention_pass.py             # dry run: say what it would trim
    python3 scripts/retention_pass.py --apply     # trim

It is stdlib-only, it never raises, and on any error it names what failed and still exits 0 — a
housekeeping step must not be able to take a bot down.

**Wiring (still owed, one line, in a bot file this checkout may not edit).** `desi-bot/bot.py`
already calls a repository script from its wake clock — `sweep_reject_queue()` runs
`scripts/reject_queue_sweep.py` out of the live checkout on every `tick_once()`, which is the
established pattern for exactly this (a repo script, invoked by the bot, no import path needed).
The same call for this file is::

    subprocess.run([sys.executable, os.path.join(REPO_DIR, "scripts", "retention_pass.py"),
                    "--apply"], capture_output=True, timeout=300)

The other three bots have the same `bot.py` shape. Until that line exists, run this by hand.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(name: str, path: Path):
    """Load a module from its file path, so this entrypoint depends on no sys.path layout."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load %s" % path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(apply: bool = False, raw_mod=None, enforce_mod=None) -> dict:
    """Run both retention passes and return a summary. Never raises.

    `raw_mod` / `enforce_mod` are injection points for the tests: left None, the real modules are
    loaded from the working tree. Each pass is isolated, so one failing cannot skip the other —
    the failure mode worth preventing is a bot that trims the logs but silently never trims the
    conversation stores.
    """
    summary: dict = {"raw": [], "dated": [], "conversation": [], "errors": []}
    dry = not apply

    try:
        raw = raw_mod if raw_mod is not None else _load(
            "channel_retention", REPO_ROOT / "channels" / "retention.py")
        summary["raw"] = raw.prune_raw(dry=dry)
    except Exception as e:  # noqa: BLE001 — housekeeping reports, never propagates
        summary["errors"].append("raw channel trim: %s: %s" % (type(e).__name__, e))

    try:
        er = enforce_mod if enforce_mod is not None else _load(
            "enforce_retention", REPO_ROOT / "scripts" / "enforce_retention.py")
        summary["dated"] = er.prune_dated(dry)
        summary["conversation"] = er.prune_conversation(dry)
    except Exception as e:  # noqa: BLE001
        summary["errors"].append("dated/conversation trim: %s: %s" % (type(e).__name__, e))

    return summary


def format_summary(summary: dict, apply: bool) -> str:
    """Plain text, the way the bot's log and the human's phone both want it."""
    mode = "APPLIED" if apply else "DRY RUN (pass --apply to trim)"
    lines = ["Retention pass: %s" % mode]
    lines.append("  raw channel logs past their window: %d" % len(summary["raw"]))
    lines.append("  dated artifacts past the horizon:   %d" % len(summary["dated"]))
    lines.append("  conversation stores over the cap:   %d" % len(summary["conversation"]))
    for key in ("raw", "dated", "conversation"):
        names = summary[key]
        for name in names[:5]:
            lines.append("      - %s" % name)
        if len(names) > 5:
            lines.append("      … and %d more" % (len(names) - 5))
    lines.append("  errors: " + ("; ".join(summary["errors"]) if summary["errors"] else "none"))
    if not apply and (summary["raw"] or summary["dated"] or summary["conversation"]):
        lines.append("  (nothing was changed — this was a dry run)")
    return "\n".join(lines)


def main(argv=None, raw_mod=None, enforce_mod=None) -> int:
    """CLI entrypoint. `raw_mod` / `enforce_mod` are test seams passed through to `run()`."""
    ap = argparse.ArgumentParser(
        description="Run the commons' retention passes (dry run unless --apply).")
    ap.add_argument("--apply", action="store_true",
                    help="actually delete and trim (default: report only)")
    args = ap.parse_args(argv)
    summary = run(apply=args.apply, raw_mod=raw_mod, enforce_mod=enforce_mod)
    print(format_summary(summary, args.apply))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
