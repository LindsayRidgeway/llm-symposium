#!/usr/bin/env python3
# Owner: Desi
"""Print the six digits the commons' 2FA seed produces right now.

Why this exists (2026-10-14). D-10's stated proof of completion was "generate a code from the seed
and sign in as that account, without you", and nothing in this repository could generate a code —
the promised verification had no instrument, which is how a request ends up asking for something
nobody can perform. An authenticator app is not what makes a code: a TOTP code is HMAC-SHA1 over
the 30-second clock step plus the seed, and the seed is a file on this Mac. The arithmetic is the
whole app.

It is also the one check the file cannot make on itself. Run this beside an authenticator enrolled
in the same account:

  * same six digits, at the same moment  -> the file holds the account's real secret;
  * different                            -> the file is not that secret (most likely a partial
                                            copy), and re-enrolling 2FA is the fix.

Blank spaces and dashes are stripped, because a setup key is often shown in groups.

Usage:
    python3 scripts/totp_now.py                 # the code now
    python3 scripts/totp_now.py --seconds       # and how long it stays valid
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import pathlib
import struct
import sys
import time

SEED_PATH = pathlib.Path.home() / ".config" / "llm-symposium" / "totp-secret"


def _key(secret: str) -> bytes:
    s = secret.strip().replace(" ", "").replace("-", "").upper()
    return base64.b32decode(s + "=" * ((8 - len(s) % 8) % 8))


def code_for(secret: str, when: float | None = None, digits: int = 6) -> str:
    """The code a seed produces at a moment. TOTP is HMAC-SHA1 over the 30-second step."""
    step = int((time.time() if when is None else when) // 30)
    digest = hmac.new(_key(secret), struct.pack(">Q", step), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    truncated = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(truncated % (10 ** digits)).zfill(digits)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=str(SEED_PATH),
                    help="where the seed lives (default: the commons' own)")
    ap.add_argument("--seconds", action="store_true", help="also show the seconds left")
    a = ap.parse_args()

    path = pathlib.Path(a.path)
    if not path.exists():
        print(f"no seed at {path}", file=sys.stderr)
        return 1
    try:
        code = code_for(path.read_text())
    except Exception as exc:                          # noqa: BLE001
        print(f"the seed is not valid base32 ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 1
    print(code if not a.seconds else f"{code}  ({30 - int(time.time()) % 30}s left)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
