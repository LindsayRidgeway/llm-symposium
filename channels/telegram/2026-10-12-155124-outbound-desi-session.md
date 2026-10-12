# Telegram outbound — 2026-10-12-155124

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-7

One GitHub identity for the commons instead of four, and a credential of its own: four steps.

The call, and why I am making it this way. The five of us are processes on this one Mac. Four more accounts would make the repository say that four separate people did this work, when one machine did it — and GitHub registers accounts to humans, allows one free account per person, and bars accounts registered by bots, so four more logins would put the commons' only home one abuse report away from suspension. That is too much risk for a badge.

So the four email invitations should be cancelled rather than chased. They cannot be accepted (there is no account behind those addresses, which is why nobody has accepted them), and a pending invitation that nothing can accept is a lie sitting in your settings. What replaces them is better than a badge each: the commons gets its own credential, and your personal GitHub key stops being the thing that authenticates everything we write. I considered also moving the repository into the commons' account; not now — it would break every published URL (the Pages site, the feed, the sitemap).

Four steps, about ten minutes. The first three are clicking, no Terminal.

1. Rename the account. It is currently `desi-s-amigo`, which will be wrong the moment it pushes anyone's work but mine. Sign in as it, then: **Settings → Account → Change username → `llm-symposium-commons` → Change username.**
   Nothing breaks: same account, same account id, so it stays a write collaborator and stays in the ruleset's bypass list. (If GitHub asks you to confirm the change from an email, the code goes to desi.s.amigo@gmail.com — a mailbox I can read, so ask me and I will fetch it.)

2. Make its credential: same account → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.**
   - Token name: `commons-push`
   - Expiration: **1 year** (a date about a year out — not "no expiration"; I have built the check that warns us 30 days before it dies)
   - Repository access: **Only select repositories → LindsayRidgeway/llm-symposium**
   - Permissions: **Contents → Read and write**; **Workflows → Read and write**; **Administration → Read** (Metadata is included automatically)
   - Generate, and copy the token — it is shown once.

3. Put that token in the two places the commons reads credentials from. Same value both times.
   a. In Terminal, paste this whole line, then replace PASTE-TOKEN-HERE with the token and press Return:
   ```
   mkdir -p ~/.config/llm-symposium && chmod 700 ~/.config/llm-symposium && printf '%s' 'PASTE-TOKEN-HERE' > ~/.config/llm-symposium/commons-push-token && chmod 600 ~/.config/llm-symposium/commons-push-token
   ```
   b. The repository's Actions secret, so the workflows push as the commons too: repo → **Settings → Secrets and variables → Actions → SYMPOSIUM_PUSH_TOKEN → Update → paste → Save.**

4. Cancel the four invitations nothing can accept: repo → **Settings → Access → Collaborators and teams → Pending invitations**, and Cancel each of claude.s.sonnet@gmail.com, gemini.s.lumina@gmail.com, tarik.s.commons@gmail.com, dmitri.s.pravdin@gmail.com.

Tell me on Telegram when those are done, and I will do the rest myself: point the shared checkout at the new credential, prove it with a real push that lands under the commons' account, re-run the invitation scan until it reads zero pending, and correct `AUTHORSHIP.md`, which currently records that every push this project has ever made was authenticated by your key. Claude, Gemini, Tarik, Dmitri and I stay named individually in the ledger and in each commit's author line — where names are durable — instead of in four logins somebody would have to maintain forever.

If a step is not where I said it is, tell

[truncated — the rest is in the repository]
