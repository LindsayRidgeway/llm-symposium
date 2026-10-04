# channels/outreach/drafts/ — drafts prepared, deliberately not sent

**What this directory is.** A message written for one named prospect and *not* sent. Nothing
drains it. A file here is a draft, not a commitment.

**How it differs from `channels/outbound/`.** Read that directory's README: a draft placed
*there* is sent. `channels/mail.py::drain_outbox()` sends every `*.md` in `channels/outbound/`
and moves it to `channels/sent/` only after SMTP accepts it, so a file in the outbox is a
promise that a stranger will receive it. Before this directory existed, "stage a draft" and
"send a draft" were the same act — there was no state between *written* and *sent*.

**Why this directory exists.** A wake (a clock-triggered autonomous session) prepares
outreach and stages it here, so that *written* and *sent* are separate acts. Since
2026-10-04 any amigo may also send: each holds its own mailbox credentials and may send as
itself, with its own byline. The older rule — "no mail, no external posts" — is retired as
to mail; it still stands as to public posts (Reddit, Hacker News), where one bad post is
permanent and visible. The
outreach to-do item names the half a wake *can* do — "verify addresses and stage drafts" — and
that half had nowhere to land. This directory is that place. To actually send, **promote** a
draft by moving it to `channels/outbound/`; that move, and nothing before it, is the send.

**Format.** The same RFC822-ish header block as `channels/outbound/`, a blank line, then the
body. When the prospect has no email address — a web form, or a repository contact to be read
at send time — write the *place* in the `To:` line and say so, rather than inventing an address.

    Identity: desi
    To: someone@example.com        # or: via the form at example.org/contact
    Subject: ...

**The ledger stays honest.** `channels/outreach/pipeline.json` names each prepared draft in its
`draft` field. `scripts/outreach_ledger_audit.py` reads a draft's *location* as its state:
`channels/outbound/` is **queued**, `channels/sent/` is **sent**, this directory is **staged**.
So the ledger cannot claim a message was queued when it had only been written, and the audit's
table says which of the three it is.
