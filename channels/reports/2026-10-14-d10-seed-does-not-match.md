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
