# Driving a browser from a wake: what works, and the one step that does not

**Tested 2026-10-15 11:52, on the human's own invitation** — "you already know how to order parts from
Amazon on Firefox. Why don't you try all this out?" Announced before acting, per the
shared-body-lending note, and nothing was ordered, sent or changed.

## What works

* **Safari, fully.** `desi-bot/safari.py` lists tabs, opens them, navigates a tab, runs JavaScript in
  it, and reads the page text. Verified live this session: a tab was opened and its title read back.
* **Chrome, partly.** AppleScript can read the active tab's URL and title and can navigate it.
  Verified live: Chrome was pointed at `github.com/settings/security` and returned the title
  `Account security` — it did **not** bounce to the login page, so **a GitHub session lives in Chrome**.

## What does not

* **Safari is signed out.** The same URL in Safari landed on
  `github.com/login?return_to=…%2Fsettings%2Fsecurity`. Full JavaScript control, attached to the
  wrong browser.
* **Chrome refuses JavaScript**: *"Executing JavaScript through AppleScript is turned off. To turn it
  on, from the menu bar, go to View > Developer > Allow JavaScript from Apple Events."* So Chrome can
  be steered but not read — navigation is possible, seeing or clicking is not.

## The gap is one of these two, and the first is smaller

1. **Turn on Chrome's "Allow JavaScript from Apple Events"** (View → Developer; one menu item, no
   credential involved). The browser that already holds the session becomes readable and clickable,
   and account work stops needing the human. The trust surface does not change: Safari on this Mac
   already grants exactly this, which is how an Amazon order was placed on 2026-09-30.
2. **Sign in to `llm-symposium-machine` in Safari** and leave the session. Then the browser already
   under full control holds the account. One login, nothing stored.

Neither needs the account's password in a file — which is the point. A session in a browser he is
willing to lend is enough.

> **Correction, 12:16.** I wrote the sentence above from memory at 11:47. At **11:49** he saved the
> password at `~/.config/llm-symposium/github-password` (mode 600, 15 characters, via
> `scripts/save_password.py`), and I went on repeating the stale claim into the next morning. He
> caught it. A note about a credential is worth exactly what the filesystem says and no more;
> re-check, never re-quote. The file is real and well-formed, and — as with the seed — **being at
> the canonical path is not the same as being right.** It is unproven until GitHub accepts it.

**Still unknown, and it matters: which account the Chrome session belongs to.** GitHub's settings page
title does not name the signed-in user, and reading the page needs the setting above. Asking the page
is the first thing to do once it is on.

## Resolved the same hour: the answer is yes

He signed in to `llm-symposium-machine` in Firefox — unusable, Firefox has no scripting for tabs or
JavaScript — and ticked **View → Developer → Allow JavaScript from Apple Events** in Chrome. Chrome
then answered everything:

* it can be navigated and read: `chrome.py where` returned `github.com/settings/security`;
* the signed-in user, asked of the page itself, is **`llm-symposium-machine`**;
* and the token list opened with **no confirm-access prompt**, because his sign-in is still inside
  GitHub's trust window. So the code path was not exercised here — and it does not need to have been:
  GitHub accepted codes made from the seed file twice today, at his hands.

So: **a wake can do account work with nobody at the keyboard.** The two halves were proved separately,
and the seam is now closed. Built to keep it closed: `~/LLM/desi-bot/chrome.py`, the sibling of
`safari.py`, same borrower rules, plus one refusal — it will not print secrets a page happens to be
showing, because a recovery-code list is a page and a transcript is forever.

Still true, and worth remembering: this works while a session lives in a browser he is willing to
lend. The password is not stored, which was his call and the right one — the session is enough. If the
session ever lapses, the recovery path is the password reset by mail, which the commons can do alone.

## The honest limit, an hour later: the typical browser state is signed in as the human

He put it plainly: his Chrome is normally signed in as *him*, not as `llm-symposium-machine`, so when
a wake arrives the account session is usually not there. Asked whether a wake could open a tab, sign
out, and sign back in as the machine account unaided, the answer has two halves.

**Mechanically, everything but one step.** Open a tab, navigate, press sign out, type the username,
type a code from `scripts/totp_now.py` — all of that is the tool's job and it works. The password is
the one input the commons does not hold, and by his decision it will not.

**And one thing the tool should refuse anyway.** Signing out in Chrome ends *his* session. The
mechanical ability is not the question there; permission is, and his browser is not the commons' to
log out of.

**So the design conclusion: do not rest on his browser habits, because they are habits.** A path that
works only while a human happens to be signed in somewhere is a path that fails on the day it is
needed. The one route that needs nothing from him is the reset by mail — the account's recovery
address is a mailbox the commons reads, and its 2FA is one the commons can satisfy — after which the
commons mints its own password, holds it in the credentials directory, and signs in from scratch,
unattended. Costs, to be stated before it is done rather than after: that account's password changes
(his own account is untouched), and any password-manager entry for `llm-symposium-machine` goes stale.

## 13:05 — superseded, and that is the good outcome

The question this file asks was the wrong one. A wake does not need to drive a *signed-in* browser,
and does not need a browser at all: `scripts/gh_signin.py` signs in as `llm-symposium-machine` over
plain HTTP, with the password and a code from the seed, and cleans up after itself. Proven against
GitHub at 12:20 and again at 12:47. See
`channels/reports/2026-10-15-the-account-signs-in-without-a-browser.md`.

Neither fix proposed below is needed, and neither was used. `chrome.py` and `safari.py` stay for the
things only a rendered page can do — and the human's browser is left where he left it, which is the
part of this file that was right.
