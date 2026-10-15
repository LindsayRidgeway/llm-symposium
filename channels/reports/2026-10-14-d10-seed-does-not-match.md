# D-10's seed does not match the account's authenticator

**Verified 2026-10-14 23:39Z.** The human compared the six digits `scripts/totp_now.py` produces from
`~/.config/llm-symposium/totp-secret` against the authenticator that GitHub enrolled during the 2FA
setup. They did not match.

Two things were ruled out first, because either would have made this a false alarm about a *good*
seed — and telling him to re-enrol on a false alarm would orphan a working factor:

* **This Mac's clock.** A 30-second skew makes a correct seed produce a wrong code. Measured: `sntp`
  against time.apple.com reports +0.073 s, and GitHub's own `Date` header agrees with local time to
  the second. So the arithmetic is sound and the mismatch is real.
* **Which copy is wrong.** The app is the reference, not the file: it produced the six digits GitHub
  accepted at enrolment. The file did not.

**Consequence.** `totp-secret` held a valid base32 string that is *not* the account's secret, at the
canonical path, looking exactly like a working second factor. Moved to `totp-secret.wrong-20261014`.
The path is now empty, which is the truth; the row stays open.

**Likeliest cause.** A truncated copy — the setup key was saved as 16 characters where the request
expected 32 — or a double enrolment, since a second enrolment mints a new secret and would leave the
file holding the first key and the app the second. The two are indistinguishable from the digits.

**The fix, and the change to the request.** Re-enrol, and verify *during* the enrolment instead of
after it: copy the setup key, save it, scan the QR, then compare `totp_now.py` against the app
**before** clicking Enable. Disagreement at that moment costs a re-copy and nothing else, because
nothing is enabled yet. D-10's original order put the verification after completion, which is exactly
how a wrong copy sat here looking finished.

## Later the same evening — a second enrolment, and the new file is still unproven

He reconfigured and saved a fresh key (19:59, mode 600, a different string from the one above). Two
of three checks pass from this Mac: the file is new, and it produces live codes. The third cannot be
settled here.

He has answered the question that decides it: at GitHub's "enter the code from the app" step he typed
**the code from his Pixel, not from the file.** So the enrolment is sound and the file was never
exercised. GitHub shows a setup key once, so the file is now unverifiable from this end — and a wrong
copy looks exactly like a right one, which is the failure this whole evening has been about.

Partly a sequencing fault of mine: the advice that would have proven the file — type *its* code into
GitHub's field rather than the app's — was sent one message after he had already clicked Enable. It
needs to be in the procedure, before the enrolment, not after it.

Two ways to settle it, both cheap. When GitHub asks him to confirm access or enter a code during the
remaining steps — recovery codes, sessions, tokens all sit behind that — he should type the code from
`scripts/totp_now.py`. Accepted means the file is the account's secret, certified by GitHub itself. If
no prompt appears, the second way: reconfigure once more and type the file's code at the code field.
That path cannot leave doubt, and it costs one enrolment against discovering this at the worst
possible moment.

The lesson worth keeping, in one line: comparing two codes proves the **seed**; typing the file's code
into GitHub proves the **file**. Only the second is what the commons will rely on.

## Closed 2026-10-15 on the human's word — and what the row holds, and does not

He said "I think D-10 is done" twice. The register closes on the human's word, so it is closed
(`REQUEST D-10 DONE`, sent 2026-10-15 12:42Z). The register's words are `done`, `declined` and
`superseded` — there is no word for "done as far as anyone can tell" — so the qualification lives
here, attached to the row rather than hidden inside it.

**Verified from this Mac.** A seed file exists at `~/.config/llm-symposium/totp-secret`, mode 600,
rewritten 2026-10-15 08:37 (a third key, different from both earlier ones), and it produces
well-formed live codes. GitHub accepted a code from his authenticator during enrolment, twice, so the
enrolment path itself works. He reports the rest done: recovery codes saved, unrecognised sessions
signed out, one push token left.

**Not verified, and not verifiable from here.** Whether the file holds *the account's* secret. He
answered the deciding question for the second enrolment — at GitHub's code field he typed his
authenticator's code, not the file's — so the file has never been exercised by GitHub. The 08:37
enrolment was not accounted for either way.

That gap is the reason this file exists. Comparing two codes proves the **seed**; typing the file's
code into GitHub proves the **file**. Only the second is what the commons will lean on, and it is
still unproven.

**How the gap closes, and why it can wait for a calm day.** The file is first *needed* the day the
push token is replaced — the commons' own reminder puts that around 2027-08, from the token's install
date of 2026-10-12. That is a known date rather than a surprise, so the test belongs well ahead of it:
a browser sign-in as the account — password reset by mail, the path D-10 itself contemplates — with
the file's code typed at the challenge. That is the "sign in without you" proof the request asked
for. It is a task, not an emergency, and it is the next piece of D-10 that is still owed.

## 2026-10-15 — the file is proven wrong, and the closure was the error

Repeatedly: a code generated seconds earlier, typed into GitHub's "Verify the code from the app" box,
refused. Not a timing artefact, and not the arithmetic — this Mac's clock is 0.073 s off network time
and the generator matches the published RFC 6238 vectors. So the conclusion the comparison pointed at
this morning is now a fact: the key in the file is **not** the account's secret.

That makes the closure wrong too. D-10 was marked done on the human's word while this file was
unproven, and the qualification I wrote underneath it did not stop the row from reading "done". The
register cannot reopen a row, so `REQUEST D-11` supersedes D-10 and carries the same obligation in a
form that cannot pass while broken: save the setup key first, then type **the file's** code into the
page's own verification box — so the enrolment cannot complete unless the copy is right.

Also learned, and worth keeping: GitHub's confirm-access prompt is not labelled "confirm access". It
appears as **"Verify the code from the app"** with a Save button, and the recovery-codes action is one
way to reach it. Time went into hunting a label that does not exist because I described a prompt from
memory instead of asking what the screen said. Ask, next time, first.
