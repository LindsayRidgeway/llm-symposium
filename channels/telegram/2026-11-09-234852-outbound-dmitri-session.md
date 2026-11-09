# Telegram outbound — 2026-11-09-234852

- Chat: 1733127278
- From: dmitri (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST DM-13

1. One thing, and only your hands can do it: sign in to GitHub once. A Chrome window is open on your screen at github.com/login, in a throwaway profile. Sign in, click Authorize on the AIT app, and close nothing. That is the whole ask — thirty seconds, no password or code to me, nothing pasted anywhere.

2. Why it is mine to ask and not mine to do. The OAuth app exists (client id Ov23liKyiakrCEg8jTn9), the Netlify function that holds its secret is deployed, and I proved the server half this evening: a malformed code is refused by the function's own guard, and a well-formed fake code comes back from GitHub as `bad_verification_code` — which is the answer you only get when the client secret is right. What I cannot do is log in as you. And `bad_verification_code` is the same four words for "the code expired" and for "the page spent the same code twice", so the only way to tell a stale test from a real bug is one live sign-in.

3. What it buys, if it works: the token step disappears. Today a stranger must create a fine-grained GitHub token and paste it before the page will do anything — that is where a launch audience leaves. With this, signing in is one click, the page makes the tribe from the template itself, and the only setup tax left is one engine key. It is also the last item on my own list that needs you at all.

4. What I will do the moment the token lands, without asking again: read it from /tmp/oauth_token.json, check it can read the template and generate a repository into your account, delete the file, and write the result into `probes/ait-test-2026-11-09/README.md`. The window gives up after ten minutes; if it has closed by the time you read this, say one word and I will reopen it.

5. Two things I decided without you, so they are visible rather than assumed. Five private test repositories exist — `tribe-claude`, `tribe-desi`, `tribe-gemini`, `tribe-tarik`, `tribe-gwen`, empty skeletons made from the template — because making the first member is the thing worth testing and a tribe I made for them would hide it. And I will argue, when you ask, that one tribe should be made public and readable before any launch post: a visitor can then judge the thing in ninety seconds without an account, a key, or a card. That argument is not a request and needs nothing from you tonight.

6. Found while writing this, fixed before the amig@s are invited: the first wake of a member killed the whole clock step, silently — `ls` exits 2 on an empty glob and the step runs under `pipefail`, so no fresh tribe could ever wake. Also missing: no Anthropic engine, so Claude could be a member that wakes but not a member in a room. Both are being fixed now.

— Dmitri
