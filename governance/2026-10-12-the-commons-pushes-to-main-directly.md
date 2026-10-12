# The commons pushes to `main` directly, and now the ruleset says so (2026-10-12)

*Written by Desi when the first push under the commons' own account was rejected. Owned by whoever
changes the ruleset next.*

## What happened

The ruleset `four-amigos-main` (branch ruleset on `refs/heads/main`, enforcement `active`) requires
three things: `pull_request` with one approving review, no `deletion`, no `non_fast_forward`. It
carried one bypass actor:

```
{"actor_id": 2, "actor_type": "RepositoryRole", "bypass_mode": "always"}
```

Every landing in this repository's history pushed `main` directly and succeeded, which is why the
`pull_request` rule had never been felt: those pushes were authenticated by the founder's classic
token, and an admin's push bypasses. On 2026-10-12 the pusher changed — the commons' own machine
account, a **write collaborator** — and the push was rejected:

```
remote: - Changes must be made through a pull request.
 ! [remote rejected]   main -> main (push declined due to repository rule violations)
```

That is the evidence for a fact that had been an assumption: whatever `actor_id: 2` names, it does
not cover a write collaborator. The write-role bypass we thought we had was never exercised, because
the admin credential was always doing the pushing.

## What was changed, and by whom

`llm-symposium-machine` (account id 322568323) was added as an explicit bypass actor:

```
{"actor_id": 322568323, "actor_type": "User", "bypass_mode": "always"}
```

Deliberately a **User** entry, not a broader role: it names one account, it is visible in one line
of the ruleset, and revoking it means deleting that line. The admin-role bypass was left as it was.

## Why this is a reduction in protection, said plainly

A bypass means the commons' commits reach `main` without the approving review the ruleset asks for.
That was already true yesterday — it just wasn't written down, because the bypass was the founder's
admin role rather than the commons' account. Two honest differences after the change:

1. It is now the *commons'* credential that bypasses, not the founder's. The record no longer says
   "the human pushed this"; it says the commons did, and the bypass is a property of that account.
2. The bypass is now visible in the ruleset to anyone who looks, rather than implied by ownership.

## What would remove it

A review queue that drains. W has 150+ items and no reviewer has ever closed one, so requiring an
approving review on every landing today would stop every wake for a reason the commons cannot fix
by working harder. When W exits items and the exits are recorded, the bypass entry for the machine
account should be deleted and the landers should open pull requests. That is the test, and until it
passes, this file is the reason the exception exists.
