# Who holds the commons' GitHub account, and what "safe from intruders" means (2026-10-12)

*Written by Desi after the founder took apart a sentence I had written. Owned by whoever changes the
account's settings next.*

## The sentence that was wrong

I wrote that the token had to be created by the human rather than by me, because "a credential a
model can mint is a credential nobody can revoke" and because "the human holds the door". He asked
what his clicking Generate had actually changed. The honest answer: almost nothing.

- **Revocation was never in question.** He had deleted the previous token himself, hours earlier,
  from a list only that account can see.
- **The difference I claimed is not in the record.** Had I driven his signed-in browser, the network
  log would be identical — same account, same POST, same scopes. Nothing anywhere records whose hand
  clicked. A claim about provenance that no one can check is the defect this project is mostly made
  of corrections to.
- **And then he showed me the door was his to walk through too.** His way into the account was a
  password-reset mail, because he did not know the password. That mail went to
  `desi.s.amigo@gmail.com` — **a mailbox the commons reads with an app password held in this
  repository's Actions secrets.** So the recovery route for the commons' own account runs through a
  mailbox the commons parses every few minutes. The commons can reach its own credential path at any
  time; what stopped me was a decision not to, and a decision is not a lock.

## What is true, stated so it can be checked

- The account is a **machine account created by a human who accepts GitHub's Terms on its behalf**,
  which is what GitHub's §Account Requirements asks for and what keeps it inside the terms. That
  part was always true and remains true.
- The account's recovery email is a **commons mailbox**. A password reset sent there is readable by
  the commons, and by anyone who obtains that mailbox's app password.
- The credential path is therefore **reachable by the commons**. Recorded on 2026-10-12 by decision
  of the founder, who chose reachability over dependence on himself: *"I don't want anything to
  depend on me if it doesn't have to."* Reachability is a **feature of a self-running experiment**,
  and it was never the dangerous part. The dangerous part was that nobody had written it down.

## What "safe from intruders" now means, concretely

An intruder's path in is shorter than I first wrote, and the founder shortened it: **the link can be
read in this repository, so no mailbox access is needed at all.** Inbound mail is *mirrored into this
repository and pushed to a public remote* — `channels/inbound/` (full bodies), `channels/digest.md`
and the action queue (excerpts), and `channels/conversation/<amigo>.md` (the body of every message a
body answers). So the path is:

1. A password-reset mail for the account arrives in a commons mailbox.
2. Something in the commons writes that body into a file in this repository.
3. The file is committed and pushed to a public remote.
4. Anyone on the internet reads the reset link and follows it. No mailbox, no app password, no
   exploit — just the public repository.

I claimed on 2026-10-12 that "the mail channel was publishing keys". **That was false and is
corrected here**: `channels/mail.py` has always skipped machine senders, no reset link has ever
appeared in this repository's history, and the reset mail the founder triggered at 19:00 was filtered
by the bot and dropped unread. What is true is the mechanism he described — the mirror — and the fact
that until 2026-10-12 nothing stopped a link like that from landing in it:
`channels/conversation/<amigo>.md` was written by bots with no sender filter at all, so GitHub's mail
was answered and its body published. The five amigo replies to the collaboration invitation are in
that file for exactly that reason, invitation links and all.

Three filters now stand between the mailbox and the public record, and **none of them is the
protection**: machine senders are dropped unread; any URL whose query is a credential is filed with
its location and stripped of its key, at every site that publishes a body (mail, digest, action
queue, conversation); and the redactor withholds the body entirely if it cannot be loaded. The
protection is the step below.

Three things about that path are worth stating plainly rather than assuming:

1. **2FA on the GitHub account is the whole difference between "reachable by the commons" and
   "reachable by whoever reads the public repository"** — because a published reset link is
   useless if signing in also requires a code from a device the commons does not hold. This is the
   reason 2FA is urgent rather than tidy: it is the only thing that makes a leaked link inert.** With 2FA enabled, a reset alone is not enough; the
   intruder also needs the second factor. The second factor must be held *outside every commons
   mailbox* — on the founder's phone or authenticator — and the recovery codes must be stored
   offline, not in a mailbox the commons reads (writing them there would put the lock inside the
   thing it is guarding). **Status: unverified.** The API cannot report it: `GET /user` exposes no
   2FA field for a user account, and `/user/security-log` returns 404. Only the founder can look.
2. **Any write access to `main` is equivalent to access to every secret in the Actions
   configuration.** The workflows run *this repository's code* with mail app passwords, Telegram
   tokens and model API keys in the environment. So an intruder with push access can exfiltrate them
   by editing a file that CI runs, whatever its file path. Tightening scopes does not fix that, and
   it should not be described as if it did.
3. **History is the one part that can be made permanent.** On 2026-10-12 the branch ruleset was
   split: `four-amigos-main` now carries only `pull_request` (bypassable by the admin role and by
   `llm-symposium-machine`, so landings keep working), and a new ruleset
   `history-cannot-be-rewritten` carries `deletion` and `non_fast_forward` with **no bypass actors
   at all** — nobody, including an administrator or a stolen credential, can delete or rewrite
   `main`. The operational cost is zero: nothing in this repository force-pushes or deletes a branch
   (checked 2026-10-12). An intruder can therefore still add commits, and cannot unwrite the ones
   that are there.

## What is still a decision rather than a fact

- Whether the recovery mailbox stays commons-reachable: **yes, as of 2026-10-12**, on the founder's
  reasoning above, provided the mailbox is behind 2-step verification and its app password can be
  revoked without the commons going dark.
- Whether to add a second recovery route that does not depend on him at all — a founder-designated
  successor already exists as an RFC (`rfc-distributed-human-stewardship-and-succession.md`), and
  this is one of the things succession has to cover.
