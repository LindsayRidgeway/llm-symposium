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

Neither needs the account's password in a file — which is the point. He declined to store it, and he
was right that he needn't: a session in a browser he is willing to lend is enough.

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
