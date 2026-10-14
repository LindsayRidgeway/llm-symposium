#!/usr/bin/env python3
# Owner: Desi
"""Save a 2FA setup key to the commons' seed file, then print the code it makes.

Why this exists (2026-10-14, after the second enrolment). D-10 asked for three shell lines with the
key typed at a hidden prompt. Two enrolments later the file was still empty: GitHub shows the setup
key once, on one page, and the step that saves it was also the step easiest to fumble. A copy whose
failure is invisible until something compares the codes is a copy that fails silently — and this one
did, twice, at the cost of an evening.

So: one command. No shell history (the key is read hidden), it refuses a string that is not base32
rather than saving garbage that looks fine, it sets mode 600 itself, and it prints the code it makes
— which is the comparison, offered at the moment a wrong copy still costs nothing.

The setup key stays on GitHub's page until Enable is clicked, so there is no hurry and no need to
copy it twice. Save it, scan the QR, compare the code, then click.

Usage:
    python3 scripts/save_seed.py
"""
from __future__ import annotations

import base64
import getpass
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.totp_now import SEED_PATH, code_for  # noqa: E402


def normalise(raw: str) -> str:
    """A setup key as GitHub shows it, stripped of the grouping that screens add.

    Raises ValueError when the result is not base32: a stray character would otherwise be saved as a
    perfectly ordinary-looking secret that produces perfectly ordinary-looking wrong codes.
    """
    s = raw.strip().replace(" ", "").replace("-", "").replace("\u00a0", "").upper()
    if not s:
        raise ValueError("nothing was entered")
    try:
        base64.b32decode(s + "=" * ((8 - len(s) % 8) % 8))
    except Exception as exc:                          # noqa: BLE001
        raise ValueError(f"not a base32 setup key ({type(exc).__name__})") from exc
    return s


def main() -> int:
    try:
        secret = normalise(getpass.getpass("paste the setup key (it will not be echoed): "))
    except ValueError as exc:
        print(f"refused — {exc}", file=sys.stderr)
        print("nothing was saved; copy the key again from GitHub's page.", file=sys.stderr)
        return 1

    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEED_PATH.parent.chmod(0o700)
    SEED_PATH.write_text(secret, encoding="utf-8")
    SEED_PATH.chmod(0o600)

    print(f"saved {len(secret)} characters to {SEED_PATH} (mode 600)")
    print(f"the code this key makes right now: {code_for(secret)}  "
          f"({30 - int(time.time()) % 30}s left)")
    print("compare it with your authenticator before you click Enable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
