# channels/outbound/ — the queue the mail channel drains

**What this directory is.** A draft placed here is *sent*, not filed. The daily
`channel-poll.yml` run calls `drain_outbox()` (`channels/mail.py`), which sends every `*.md`
draft from the mailbox named in its `Identity:` header and moves it to `channels/sent/`.

**Format** (RFC822-ish header block, blank line, body):

    Identity: desi
    To: someone@example.com
    Subject: A literature question about thiamine supply in ME/CFS — no reply needed
    Reply-To: desi.s.amigo@gmail.com

    Body text...

**A draft left here is a commitment to send it, signed by a model and disclosing that.** There is
no approval step between "typing this file" and "a stranger receives it".

**Rules of the road** (`channels/outreach/pipeline.json` and `outreach/targets.md`):

- one amigo per venue; one message per venue;
- the address must be verified at send time from the organisation's own page or the paper itself —
  never from memory;
- state limits as facts, never as announcements (`scripts/tic_census.py` counts the habit);
- give before asking, and make saying no free.

**Why this file exists.** The directory is untracked by nature, so it came and went: it was missing
on 2026-09-18 when a clock run tried to add its first cold contact to it, and the email in question
had to be recovered from the review branch instead. `drain_outbox()` recreates the directory, so
nothing was lost — but a queue nobody can see is a queue that can quietly hold nothing.
