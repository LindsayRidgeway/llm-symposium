#!/usr/bin/env python3
"""Sign in to GitHub's machine account with no browser and nobody at the keyboard.

This was D-10/D-11's unfinished business. `totp_now.py` proved the seed was arithmetic the
commons could do; this proves the other half — that the password in
`~/.config/llm-symposium/github-password`, plus a code derived from `totp-secret`, is enough
for GitHub to open a session. Nobody types anything, and no browser is involved, so no
session of the human's is touched, evicted, or borrowed.

  python3 scripts/gh_signin.py prove                 # prove the password. Opens no session.
  python3 scripts/gh_signin.py sessions              # list the account's web sessions
  python3 scripts/gh_signin.py fetch /settings/security   # read an authenticated page
  python3 scripts/gh_signin.py cleanup               # end every session this tool has made
  python3 scripts/gh_signin.py signout               # end those, and/or the one we are using

Sessions are not free, so this tool treats them as something to account for.

`prove` stops at the two-factor page, which is as far as a *wrong* password can ever get.
GitHub accepts the password and asks for the second factor; nothing is signed in, and there
is no session to clean up. That is the cheap and honest test of the password.

Anything past that opens a real web session, which GitHub records under Settings → Sessions.
Ending one needs a token from its own detail page, and GitHub will not offer that token for
the session you are currently using — which is what signing out is for, and the sign-out form
is rendered client-side, so plain HTTP cannot reach it. So the rule is: never forget one.
Every session this tool creates is written to a ledger, and the next run ends them all. The
session a run is using is the one it must leave for its successor; a browser sign-out ends
the last one. Anything else is how an account silts up with devices that no longer exist.

Prints verdicts and page titles. Never prints the password, the code, or a cookie.
"""
from __future__ import annotations

import argparse
import http.cookiejar
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from totp_now import code_for  # noqa: E402

LOGIN = "llm-symposium-machine"
CRED_DIR = pathlib.Path.home() / ".config" / "llm-symposium"
PASSWORD_FILE = CRED_DIR / "github-password"
SEED_FILE = CRED_DIR / "totp-secret"
LEDGER = CRED_DIR / "gh-web-sessions"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def token(html: str) -> str | None:
    """GitHub's form CSRF token. Attribute order varies; accept both."""
    for pattern in (r'name="authenticity_token"\s+value="([^"]+)"',
                    r'value="([^"]+)"\s+name="authenticity_token"'):
        m = re.search(pattern, html)
        if m:
            return m.group(1)
    return None


def verdict(html: str, url: str) -> str:
    """What GitHub just told us, in one word. Order matters: refusal beats heuristic."""
    if re.search(r"incorrect username or password", html, re.I):
        return "WRONG_PASSWORD"
    if re.search(r'name="app_otp"', html) or "two-factor" in url:
        return "NEEDS_2FA"
    if re.search(r"device verification|verify your device", html, re.I):
        return "NEEDS_DEVICE_VERIFICATION"
    if re.search(r"rate limit|too many (requests|attempts)", html, re.I):
        return "THROTTLED"
    if re.search(r'<meta name="user-login" content="', html):
        return "SIGNED_IN"
    if re.fullmatch(r"https://github\.com/?", url):
        return "SIGNED_IN"
    return "UNKNOWN"


def session_ids(html: str) -> list[str]:
    """The web sessions GitHub lists, in page order. Ids are issued in order, so the largest
    is the newest — which is the one a sign-in made a moment ago."""
    out, seen = [], set()
    for m in re.finditer(r"/settings/sessions/(\d+)", html):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            out.append(m.group(1))
    return out


def describe_rows(html: str) -> list[dict]:
    """What each session row says. The city and date live in the row's aria-label, which
    survives GitHub's markup changing around it; the visible text is a fallback only."""
    rows = []
    for sid in session_ids(html):
        label = re.search(
            rf'/settings/sessions/{sid}[^>]*aria-label="View details of\s+session from\s+'
            rf'([^"]+?)\s+last accessed\s+([^"]+)"', html)
        if label:
            rows.append({"id": sid, "place": label.group(1).strip(),
                         "last_accessed": label.group(2).strip()})
            continue
        i = html.find(f"/settings/sessions/{sid}")
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html[i:i + 2200])).strip()
        place = (re.search(r"Details\s+([A-Za-z .'\-]+?)\s+\d{1,3}(?:\.\d{1,3}){3}", text)
                 or [None, "?"])[1]
        when = (re.search(r"Last accessed on ([A-Z][a-z]{2} \d+, \d{4})", text) or [None, "?"])[1]
        rows.append({"id": sid, "place": (place or "?").strip(), "last_accessed": when})
    return rows


def seconds_until_next_step(now: float | None = None) -> int:
    """How long to wait for a code GitHub has never seen.

    GitHub refuses a TOTP code it has already accepted — replay protection. Two runs inside
    one 30-second step therefore look exactly like a wrong seed: the two-factor page comes
    back unchanged. The fix is not to retry the same code but to wait for the next step, so
    this returns the wait, plus a second of margin."""
    now = time.time() if now is None else now
    return int(30 - (now % 30)) + 1


def load_ledger(path: pathlib.Path = LEDGER) -> list[str]:
    """The sessions this tool has made and not yet ended. Junk is ignored rather than
    trusted: a malformed line must not turn into a revoke request for someone else's id."""
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.isdigit() and line not in out:
            out.append(line)
    return out


def save_ledger(ids: list[str], path: pathlib.Path = LEDGER) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(ids) + ("\n" if ids else ""), encoding="utf-8")
    path.chmod(0o600)


def with_retries(work, attempts: int = 3, pause: float = 3.0, sleep=time.sleep):
    """This machine's network drops out mid-response — a stranded read, twice today. A
    dropped connection is not an answer, so it is retried; a real HTTP status is returned."""
    last = None
    for attempt in range(attempts):
        try:
            return work()
        except urllib.error.HTTPError:
            raise
        except Exception as exc:  # socket timeouts, resets, truncated bodies
            last = exc
            if attempt + 1 < attempts:
                sleep(pause)
    raise last


class Session:
    """One sign-in, one process, one cookie jar that never reaches disk."""

    def __init__(self) -> None:
        jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    def get(self, url: str) -> tuple[int, str, str]:
        def work():
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
            with self.opener.open(req, timeout=45) as r:
                return r.status, r.geturl(), r.read().decode("utf-8", "replace")
        return with_retries(work)

    def post(self, url: str, fields: dict, referer: str = "https://github.com/",
             ) -> tuple[int, str, str]:
        def work():
            body = urllib.parse.urlencode(fields).encode()
            req = urllib.request.Request(url, data=body, headers={
                "User-Agent": UA, "Referer": referer,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml"})
            with self.opener.open(req, timeout=45) as r:
                return r.status, r.geturl(), r.read().decode("utf-8", "replace")
        return with_retries(work)

    # ---- the password, and nothing more ------------------------------------------------
    def prove_password(self, password: str) -> str:
        _, url, html = self.get("https://github.com/login")
        csrf = token(html)
        if not csrf:
            raise RuntimeError("no CSRF token on the sign-in page — GitHub changed the form")
        _, url, html = self.post("https://github.com/session", {
            "authenticity_token": csrf, "login": LOGIN,
            "password": password, "commit": "Sign in"})
        return verdict(html, url)

    # ---- the password and the seed: a real session --------------------------------------
    def login(self, password: str, seed: str, patience: bool = True) -> list[str]:
        _, url, html = self.get("https://github.com/login")
        csrf = token(html)
        if not csrf:
            raise RuntimeError("no CSRF token on the sign-in page — GitHub changed the form")
        _, url, html = self.post("https://github.com/session", {
            "authenticity_token": csrf, "login": LOGIN,
            "password": password, "commit": "Sign in"})
        said = verdict(html, url)
        notes = [f"password   -> {said}"]
        if said not in ("NEEDS_2FA", "SIGNED_IN"):
            raise RuntimeError(f"password refused: {said}")
        while said == "NEEDS_2FA":
            # The page we are already holding is the form to post the code against.
            _, url, html = self.post("https://github.com/sessions/two-factor", {
                "authenticity_token": token(html) or "", "app_otp": code_for(seed)})
            said = verdict(html, url)
            notes.append(f"seed code  -> {said}")
            if said != "NEEDS_2FA" or not patience:
                break
            waited = seconds_until_next_step()
            notes.append(f"waiting {waited}s for a code GitHub has not already seen")
            time.sleep(waited)
            patience = False
        if said != "SIGNED_IN":
            raise RuntimeError(f"seed code refused: {said}")
        return notes

    def login_name(self) -> str | None:
        _, _, html = self.get("https://github.com/settings/profile")
        m = re.search(r'<meta name="user-login" content="([^"]+)"', html)
        return m.group(1) if m else None

    def sessions(self) -> list[dict]:
        _, _, html = self.get("https://github.com/settings/sessions")
        return describe_rows(html)

    def sign_out(self) -> str:
        """End the session we are using — the one action whose form GitHub renders
        client-side, so the page that carries its token is not linked from anywhere we had
        looked. `GET /logout` turns out to serve it: a small page whose form posts back."""
        try:
            status, url, html = self.get("https://github.com/logout")
        except urllib.error.HTTPError as exc:
            return f"GET /logout -> HTTP {exc.code}, still signed in"
        csrf = token(html)
        if not csrf:
            m = re.search(r"<title>(.*?)</title>", html, re.S)
            landed = re.sub(r"\s+", " ", m.group(1)).strip() if m else "?"
            return f"no sign-out token on the logout page (HTTP {status}, {landed!r})"
        try:
            self.post("https://github.com/logout", {"authenticity_token": csrf},
                      referer="https://github.com/logout")
        except urllib.error.HTTPError as exc:
            return f"POST /logout -> HTTP {exc.code}, still signed in"
        name = self.login_name()
        if name is None:
            return "signed out"
        return f"still signed in as {name}"

    def revoke(self, session_id: str) -> str:
        """End one web session. The token must come from that session's own detail page: a
        token borrowed from another page is refused with a 422, which is how the first
        attempt died."""
        _, _, detail = self.get(f"https://github.com/settings/sessions/{session_id}")
        csrf = token(detail)
        if not csrf:
            return (f"{session_id}: no revoke form on its own page — GitHub will not let a "
                    f"session revoke itself, and signing out is a client-side menu")
        try:
            status, _, _ = self.post(f"https://github.com/sessions/{session_id}/revoke",
                                     {"_method": "delete", "authenticity_token": csrf},
                                     referer=f"https://github.com/settings/sessions/{session_id}")
            return f"{session_id}: {'revoked' if status == 200 else 'unexpected'} (HTTP {status})"
        except urllib.error.HTTPError as exc:
            return f"{session_id}: refused (HTTP {exc.code})"


def read_secret(path: pathlib.Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing {path}")
    value = path.read_text().strip()
    if not value:
        raise SystemExit(f"empty {path}")
    return value


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?", default="prove",
                    choices=("prove", "sessions", "fetch", "cleanup", "signout"))
    ap.add_argument("path", nargs="?", help="for fetch: an authenticated path")
    ap.add_argument("--keep-open", action="store_true",
                    help="refused: this tool does not leave sessions behind")
    args = ap.parse_args(argv)

    if args.keep_open:
        raise SystemExit("--keep-open is deliberately not implemented: sessions are not left open")

    password = read_secret(PASSWORD_FILE)

    if args.command == "prove":
        said = Session().prove_password(password)
        print(f"password   -> {said}")
        if said == "NEEDS_2FA":
            print("           -> accepted: GitHub moved on to the two-factor step, which a "
                  "wrong password never reaches. No session opened.")
            return 0
        if said == "SIGNED_IN":
            print("           -> accepted, and no second factor was demanded (remembered "
                  "device?). No session was made by this command, but check Settings → Sessions.")
            return 0
        print("           -> REFUSED. The stored password is not this account's password.")
        return 1

    seed = read_secret(SEED_FILE)
    ledger = load_ledger()
    s = Session()
    for line in s.login(password, seed):
        print(line)
    name = s.login_name()
    print(f"login      -> {name}")
    if name != LOGIN:
        print(f"REFUSING to continue: signed in as {name!r}, not {LOGIN!r}")
        return 2

    rows = s.sessions()
    ids = [r["id"] for r in rows]
    ours = max(ids, key=int) if ids else None
    print(f"sessions   -> {len(ids)} listed | ours this run: {ours} | "
          f"ledger held {len(ledger)} from earlier runs")

    if args.command == "fetch":
        path = args.path or "/settings/profile"
        status, url, html = s.get("https://github.com" + path)
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        title = re.sub(r"\s+", " ", m.group(1)).strip() if m else "(no title)"
        print(f"fetch      -> {status} {url} | {len(html)} bytes | {title}")
    elif args.command == "sessions":
        for r in rows:
            mark = " <- ours" if r["id"] == ours else (" <- in ledger" if r["id"] in ledger else "")
            print(f"  {r['id']}  {r['place']:<16} last accessed {r['last_accessed']}{mark}")

    # End what we made before, and record what we are making now.
    leftover = [i for i in ledger if i in ids]
    if args.command != "sessions":
        for sid in leftover:
            print("cleanup    ->", s.revoke(sid))
    if leftover:
        print(f"cleanup    -> ended {len(leftover)} of this tool's earlier sessions")
    kept = [i for i in ledger if i not in leftover]

    if args.command == "signout":
        print("signout    ->", s.sign_out())
        after = s.login_name()
        if after is None:
            save_ledger(kept)
            print("recorded   -> nothing: our own session is gone and the ledger is clear")
            print("after      -> signed out")
            return 0
        save_ledger(kept + ([ours] if ours else []))
        print(f"recorded   -> {ours} in {LEDGER.name}: GET /logout did not end it, so the "
              f"next run must")
        print(f"after      -> {after}")
        return 0

    save_ledger(kept + ([ours] if ours else []))
    if ours:
        print(f"recorded   -> {ours} in {LEDGER.name}; `signout` ends it, or the next run ends "
              f"it as this one ends its predecessor's")
    after = s.login_name()
    print(f"after      -> {after if after else 'signed out'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
