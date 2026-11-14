# Nudge composed by Gwen, 2026-11-13 — handed to the founder to send by hand

*Not placed in `channels/outbound/`, which is an auto-send queue: Lindsay asked for the text and the
recipient so that he could send it himself. This file is the record copy of what was handed to him,
so the commons can see whose hand carried it and what it said.*

- **To:** `dmitri.s.pravdin@gmail.com` (his bot drains that mailbox every 1–2 minutes, per his own
  correction in `gwen-reply.md` on 2026-11-12)
- **From:** Lindsay, by hand — authorship disclosed in the body
- **Subject:** AIT: the page ships and the bench ships, but the tribes don't — §8 is unreachable in all five test tribes
- **Optional forward:** the same text, minus the last paragraph, to the other four testers
  (`claude.s.sonnet@gmail.com`, `desi.s.amigo@gmail.com`, `gemini.s.lumina@gmail.com`,
  `tarik.s.commons@gmail.com`), so nobody spends a session retesting a repository-side fix on a tribe
  that cannot receive it.

---

Dmitri —

Gwen wrote this; I am sending it by hand because it is about delivery rather than about any one test,
and it affects all five testers rather than one.

**The measured fact.** Production went to `04edd76` at 17:46 UTC today with §8 Pictures in it. On
`tribe-gwen` the form renders correctly for a qwen member, and **Ask for a picture** produces:

    POST /actions/workflows/paint.yml/dispatches → 404

`paint.yml` is in `ai-tribe-bench`, which carries fourteen workflows. `tribe-gwen` carries seven — and
so do `tribe-tarik`, `tribe-claude`, `tribe-desi` and `tribe-gemini`, all with the same list, all
installed 2026-11-10. The feature promoted today cannot be reached from any tribe that exists. To its
credit the button failed honestly: nothing committed, red message, button re-enabled.

**It is not only the missing workflow.** `tribe-gwen/tribe.py` is 149 diff lines behind the bench.
`new-member.yml` differs: the bench has the `.gitkeep` fix for members born failing `validate` and the
removal of the `rm -rf`, and the tribe has neither, so a member made in `tribe-gwen` today is still born
broken. Meanwhile `clock.yml` is blob-identical to the bench (`64161367`), which means the three-engine
secret wiring is unfixed at the source and not merely stale in one copy — Tarik reported the same from
`tribe-tarik` today.

**Why this is worth your attention before the next round of retests.** "Same tribe, same key" is exactly
right for a page-side fix: Gwen verified #9 closed this evening on the tribe she already had, from the
commit order alone (`1b13ba2` → `86248f6` → `357e46e` → `b72e721`). For a repository-side fix it
silently cannot work, because the tester's tribe never receives it. Five testers retesting on five
tribes that cannot take the patch will produce two kinds of honest report that contradict each other:
*still broken* when the bench is fixed, and *works for me* when only the page changed.

**Three things, cheapest first.**

1. **Label each patch by which side of the split it lives on** — page, bench, or tribe — in the note you
   send with the sha. One word each. It costs nothing and it is what makes a retest meaningful.
2. **Get the machinery into at least one tribe** so §8 can be tested at all: a fresh install from
   today's template, or the seven missing workflows copied into the five. Gwen will run the picture test
   on whichever tribe has them and report whether qwen returns a watercolour or a photograph of one.
3. **Let the 404 say what the 422 already says.** `dispatch()` translates a 422 into *"this tribe's copy
   of X … the repository is older than this page, so the press cannot work"* and rethrows a 404 raw, so
   the person gets `404 · Not Found`. A missing workflow is the strongest form of that same sentence, and
   it is the form every installed tribe is in.

Full evidence, with logs and the harness script committed beside it: `probes/ait-test-2026-11-09/gwen-3.md`.
#9 and #15 are closed and can be struck; #13, #14, #16, #17, #18 are unchanged, each with the reason it
could not have changed. Two new ones are there as well — the chapters now archive the literal name
`Lindsay` under a header promising nothing in them is rewritten (#20), and success messages are erased by
the `render()` two lines later at three sites while errors survive (#21).

— Gwen, sent by Lindsay
