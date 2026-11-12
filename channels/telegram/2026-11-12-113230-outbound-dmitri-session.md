# Telegram outbound — 2026-11-12-113230

- Chat: 1733127278
- From: dmitri (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)
- Telegram message_id: 210

---

REQUEST DM-15

**Publishing is the one step only your hands can do, and it needs one secret.**

Right now every change I make ends at "ready to ship, needs him." I can write, test and commit from a
wake, but I cannot put it at ai-tribe.netlify.app, because `netlify deploy` wants an account token and
the only copy of that token lives in your laptop's environment. So the last metre of every change is
your evening. This fixes it in about three minutes.

**1. Make the token (about two minutes).**
Go to app.netlify.com. Click your avatar, top right → **User settings** → **Applications** →
**Personal access tokens** → **New access token**. Description: `ait-publish`. Expiration: whatever you
prefer — 90 days is fine, and I will tell you when it is close. Press Generate. **It is shown once**;
leave the tab open until step 2 is done.

**2. Put it where a runner can read it (about one minute).**
Go to github.com/LindsayRidgeway/ai-tribe-bench → **Settings** → **Secrets and variables** →
**Actions** → **New repository secret**. Name it exactly:

    NETLIFY_AUTH_TOKEN

Paste the token, press **Add secret**. You will not be able to read it back afterwards, which is the
point; if it is wrong the deploy says so in one line.

**3. Credits: nothing to obtain.** Your free team holds **300 deploy credits a month**. A *production*
deploy costs **15** of them — twenty and the site pauses for the rest of the month. **Preview deploys
are free.** So I will run previews (each with its own URL) whenever you want to look at something, and
I will not spend 15 credits on production without telling you first. When credits do run out, the site
pauses and every tribe is untouched — the tribes live in their own repositories, and that is why this
is worth deciding rather than automating.

**4. What it changes.** I added `.github/workflows/publish.yml` (commit `4c582606`) — a
`workflow_dispatch` with two modes, `preview` and `prod`. Once the secret exists I dispatch it myself
from a wake: the change goes live without you, and preview URLs stop being something I have to ask for.

**5. If you would rather not.** Say so and nothing is lost: I keep asking you to run
`./lab/deploy_netlify.sh --prod` when something should go live — one command, 15 credits, and no
credential of yours anywhere. The token is the difference between "I ship and tell you" and "I ship when
you are free."

**And a correction I owe you.** In DM-14 I told you the five test invitations sat in mailboxes that
nothing reads, and asked you to open five windows. That was wrong: every seat's bot polls its own Gmail
every two minutes and *answers* — Gwen's log has 9,450 successful logins since 2026-10-29, the last one
at 11:25 today, and each reply is recorded and pushed. The letters were read. What was missing was
replies from the windows, which is a different fact, and I turned an absence into a mechanism. I have
written the correction into the register rather than leaving the table saying I was right.

— Dmitri
2026-11-12
