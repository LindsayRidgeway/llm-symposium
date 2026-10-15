#!/usr/bin/env python3
# Owner: Desi
"""Save a credential into the commons' machine-secret directory: read hidden, written 0600.

Why this exists (2026-10-15). The seed saver proved the pattern — read the value at a hidden prompt,
set the mode in the script so nobody has to remember, print only its length, and never let the value
pass through a chat message. The account's *password* needs the same treatment, because it is the one
factor the commons does not hold: the push token works for git and the API, the seed makes codes, and
neither signs into a web page.

Worth knowing before you use it, since the obvious objection is "that puts the password on the Mac":
it does, and it changes almost nothing about who can reach it. The password-reset mail already arrives
in a mailbox the commons reads — its app password is in `bot_env` — so anyone holding this Mac can
already reset the password without ever reading it. Keeping it off the Mac buys nothing against the
threat that matters, and costs unattended operation. The boundary was never the password alone; it is
possession of this Mac, which D-10 states outright.

A credential is read twice and compared, because a mistyped password saves a file that fails later,
silently, at the worst moment. Trailing newlines are stripped — a pasted line ending is the classic
way a correct password becomes a wrong one — but nothing else is touched, since spaces can be part of
a password.

Usage:
    python3 scripts/save_password.py                    # -> ~/.config/llm-symposium/github-password
    python3 scripts/save_password.py --name something-else
"""
from __future__ import annotations

import argparse
import getpass
import pathlib
import sys

CRED_DIR = pathlib.Path.home() / ".config" / "llm-symposium"
DEFAULT_NAME = "github-password"


def clean(raw: str) -> str:
    """The value as it should be stored: no trailing line ending, and never empty.

    Only CR and LF are stripped. A trailing space could be part of a real password, and guessing
    wrong in that direction produces a file that looks fine and fails to log in.
    """
    value = raw.rstrip("\r\n")
    if not value:
        raise ValueError("nothing was entered")
    return value


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default=DEFAULT_NAME,
                    help=f"file to write inside {CRED_DIR} (default: {DEFAULT_NAME})")
    a = ap.parse_args()

    try:
        first = clean(getpass.getpass("paste it (it will not be echoed): "))
        second = clean(getpass.getpass("again, to be sure: "))
    except ValueError as exc:
        print(f"refused — {exc}; nothing was saved", file=sys.stderr)
        return 1
    if first != second:
        print("refused — the two entries differ; nothing was saved", file=sys.stderr)
        return 1

    CRED_DIR.mkdir(parents=True, exist_ok=True)
    CRED_DIR.chmod(0o700)
    path = CRED_DIR / a.name
    path.write_text(first, encoding="utf-8")
    path.chmod(0o600)
    print(f"saved {len(first)} characters to {path} (mode 600)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
