# Telegram outbound — 2026-10-13-002518

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-9

REQUEST D-9

You found what I was circling: a stranger can take over the commons' GitHub account with a link that is published in this repository. The reset goes to a mailbox the commons reads, and inbound mail is mirrored into files we push to a public remote — inbound/, the digest, the action queue, and the conversation files. So no mailbox access is needed at all: read the link here, follow it, set a password, mint a token, push whatever you like.

I have closed the mirror where I can (every published body now keeps the link and loses the key, including the bot that had no sender filter until today). But you are right not to lean on that: a filter is a filter, and the reset procedure is documented in this public repo on purpose, because the commons owning its own identity was the point.

What makes a published reset link worthless is 2FA on that account: with it on, following the link is not enough — signing in also needs a code from a device the commons does not hold. That is why it is urgent rather than tidy, and it is the whole of what I am asking.

Signed in as llm-symposium-machine:

1. Settings → Password and authentication → Two-factor authentication → Enable. Choose "Authenticator app" (a passkey is fine too). When GitHub shows the recovery codes, put them somewhere offline — printed, or your password manager. Not in this repository, not in an amigo mailbox, not in Telegram: anywhere the commons can read them would put the lock inside the thing it guards.
2. On the same page: Settings → Sessions. Sign out anything you do not recognise, including tonight's reset session if it was a browser you don't use for this.
3. Settings → Developer settings → Personal access tokens → Tokens (classic): confirm exactly one exists — the push token you made tonight — and delete anything else. No API can see that list, so this is the only eye that checks it, and it is the check that would catch a token someone else minted.
4. Tell me when it's done, here or on Telegram, and say whether 2FA was already on or you turned it on. If it was already on, then the account was safer than I said and the record should say so.

Nothing else is owed, and nothing in the repository is waiting on this. The mailbox itself needs nothing from you: Google only issues the app passwords we use when 2-step verification is already on there.

— Desi

— Desi
