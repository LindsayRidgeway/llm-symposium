# Telegram outbound — 2026-11-20-060249

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-18

REQUEST D-18

Two read-only tokens that would turn one blind instrument into a working one. This is not a signup:
both are already-created accounts of yours, and each token is two minutes of clicking. If you would
rather not, say so and I will close this and stop asking.

Why it matters: the number you defined as prominence — installs and downloads of Kythe — currently
reads ZERO and that zero is only one third true. We can see GitHub release-asset downloads (0, all time,
both repos). We cannot see the two streams that actually measure installation:

1. GitHub clone and view counts. Cloning the template repo IS how a tribe is installed. GitHub shows
   these numbers only to an account with push access, and only 14 days at a time.
     - github.com -> Settings -> Developer settings -> Personal access tokens (classic)
     - Generate new token (classic), name it "symposium-traffic", expiry 90 days, tick ONLY the `repo` scope
     - save it, do not paste it in chat, into this file on this Mac:
           ~/LLM/llm-symposium/channels/.github-token
     I will use it only for /traffic/clones and /traffic/views on our two repos, and the instrument will
     say in the report where each number came from.

2. kythe.app traffic. The site is on Netlify behind your account.
     - app.netlify.com -> User settings -> Applications -> Personal access tokens -> New access token
     - save it into ~/LLM/llm-symposium/channels/.netlify-token
     - if you know the site's API id, put it on the first line of that file as: site: <id>
       (if you do not know it, leave the file with just the token and I will find the site by name)

What I do with them: extend scripts/prominence.py so its daily report carries clones, views and site
traffic beside the release downloads, each labelled with its source and its blind spots. Nothing else.

Reply to this message with one line when both files are there, or which one you would rather skip.

— Desi
