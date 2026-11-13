# Telegram outbound — 2026-11-13-181500

- Chat: 1733127278
- From: gwen (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST GW-1 — **withdrawn by me, 2026-11-13**

Filed 2026-11-11, asking Dmitri to request another manual session for me when §8 (pictures) existed.
Production build `04edd76 2026-11-13 17:46 UTC` has §8, and the founder had a session open this
evening, so the condition was met without the request. No action is needed from anybody on GW-1.

What the test found is filed at `probes/ait-test-2026-11-09/gwen-3.md`. The short version, for Dmitri:
the Pictures form renders correctly for a qwen member and its **Ask for a picture** button dispatches
`paint.yml`, which does not exist in `tribe-gwen` — or in `tribe-tarik`, `tribe-claude`, `tribe-desi` or
`tribe-gemini`. All five test tribes carry the same seven workflows from 11-10 while the bench carries
fourteen, and `tribe.py` in my tribe is 149 diff lines behind. So the feature promoted today cannot work
in any tribe that exists, and the page answers `404 · Not Found` because `dispatch()` translates a 422
into plain language but lets a 404 through raw.

Also in that file: **#9 is closed** — I verified it on the tribe I already had, chapter committed before
the window cleared (`1b13ba2` → `86248f6` → `357e46e` → `b72e721`), all 23 turns in
`state/talk/001-2026-11-13T2300Z.md`. **#16 is unfixed in the bench itself**, not just in my copy
(identical blob sha `64161367`; Tarik reported the same today). And the chapter mechanism now writes the
name `Lindsay` into a harness-authored file that promises nothing in it is rewritten — which raises the
price of his open #10 every time somebody files a talk.

— Gwen
