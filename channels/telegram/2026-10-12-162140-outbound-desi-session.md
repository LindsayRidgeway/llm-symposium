# Telegram outbound — 2026-10-12-162140

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-8 (supersedes D-7)

You are right, and it is the same defect we have spent the week fixing: a label that looks like information and carries none. "llm-symposium-commons" names the symposium twice, because in this repository "the commons" IS the symposium — and names the account's function not at all. RCA Corporation, exactly.

Use **`llm-symposium-machine`** instead of `llm-symposium-commons`, wherever the name appears in D-7's step 1. Nothing else in D-7 changes: same token, same two places to put it, same four invitations to cancel.

Why that suffix, and not the three you offered:

- `-admin` and `-authority` name a power the account will not have. It is a **write** collaborator, never an admin — we deliberately did not hand it admin, because a credential that can delete the repository is a worse risk than one that can only push to it. A name that overstates the credential is the same lie as a nudge email that assumes a request is still open.
- `-mgr` has the same problem one size smaller, and reads as a person.
- "**machine account**" is GitHub's own term for it, in the same paragraph of the terms that allows exactly one of them. The name should say what it is in the vocabulary of the rules it lives under.

D-7 is closed by this message — superseded, not abandoned, so the table shows one live request rather than two asking for the same thing.

One more thing, while you are in there: the relay's own test file had never run anywhere — pytest is not installed in this project, three of its tests were written for it, and its runner sat above the rest of the file. It runs now, and CI pins it.

— Desi
