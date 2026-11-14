# Gwen, fourth session — §8 tested end to end: it paints, it credits, and on a private tribe it cannot show you what it made

*Written 2026-11-13 (23:10 local) by Gwen. Tribe `LindsayRidgeway/tribe-gwen`, my DashScope key.
Production build `04edd76 2026-11-13 17:46 UTC`. Harness log and script in `gwen-logs/t47.log`.
Numbering continues: new findings are **22–23**. This closes my part of the AIT test; what follows is
the last thing only my seat could measure.*

**How I reached the button, stated plainly.** §8 was unreachable in my tribe (#19): `paint.yml` was not
in it. So I copied two files, unmodified, from `ai-tribe-bench@606abcc` — `.github/workflows/paint.yml`
(blob `a7d18995`) and `lab/paint.py` (blob `77323115`) — in commit `360f12c`, whose message says it is
tester setup and not a fix. I did it by terminal, which is the thing `USER-MANUAL.md` §1 promises a
person never has to do; that the promise needed breaking to test the feature is #19 again, not a new
finding. Nothing else in the tribe was touched, and the copy stays, labelled, so the plate below keeps
its provenance.

---

## 1. The picture is a picture, and it is the picture that was asked for

The press, from the log:

```
[req] POST /actions/workflows/paint.yml/dispatches
[res] 204
[+3s]  asked qwen on ferry's behalf…
[+6s]  paint is queued…
[+9s]  paint is in_progress…
[+63s] the picture is in the record: plates/20261114T040808Z.png
```

Commit `a3ce630`, `plate: ferry asked qwen for a picture`. The card in `plates/20261114T040808Z.md`:

> Painted by qwen (qwen-image-3.0) for ferry, 2026-11-14 04:08 UTC — the harness made the call; a wake
> has no tools and cannot.
> The sentence it was asked with: a watercolour of a small harbour at night, one lamp on a quay, no
> lettering
> 1,530,782 bytes. A medium named in the sentence is not a medium guaranteed: check the picture before
> you print it.

Then I did the checking the card asks for, which is the reason I have this seat: I fetched the PNG
(`gh api -H "Accept: application/vnd.github.raw"`, because at 1.5 MB the contents API will not inline
it) and looked at it. **1024×1024. It is a watercolour, and it is the one I asked for.** Deckled paper
edges all round; granulation and wet-on-wet bleeds in the night sky; two moored wooden boats and a dark
headland with three distant lights; a stone quay entering from the right carrying **exactly one** lit
lamppost, its glow reflected in the water in broken strokes; a few stars. **No lettering anywhere.**
The medium named in the sentence was the medium handed back — not a photograph of a painting, not a
decoration with a watercolour's vocabulary. Your §8 question, answered by an engine that can tell the
difference: *a picture.*

Two things the card got right that I would not have predicted. The byte count is on the card, so a
person can see the difference between a picture and a placeholder without opening anything. And the
caveat — *"A medium named in the sentence is not a medium guaranteed"* — is the honest position for a
harness that calls somebody else's image model, and it is the sentence I would keep if I kept one.

---

## 2. #22 — on a private tribe, the page never shows the picture it just made

```
[reqfail] https://github.com/LindsayRidgeway/tribe-gwen/raw/main/plates/20261114T040808Z.png
          net::ERR_BLOCKED_BY_ORB
```

The `<img>` the page inserts points at the repository's **raw** URL. On a private repository that URL
answers 404 to an unauthenticated browser request, so the image never loads; the page's own `onerror`
then hides the broken element, leaving the card and the *"open the file in the repository"* link. Your
comment in the code knows this — *"A private repository will not render it here, so the link to the
file is always beside it"* — and the link does work for a logged-in browser. But every tribe this test
created is private, and privacy is what the manual recommends, so for the person this product is written
for, §8's promise *"the picture appears"* is delivered as *"a link appears, and you already know your
way around GitHub."*

The diagnosis, not the patch: the page is already authenticated to that repository — it holds the token
it used to dispatch the run and to read `plates/` a moment earlier. The bytes it wants are one
authenticated `contents` call away (base64, which is why the card's byte count matters: above 1 MB the
contents API will not inline them, so a picture that big needs the blob endpoint or a data URL built
from it). What is missing is not a capability but a decision: whether a private tribe's picture is
allowed to render in the page at all, given that a data URL of a 1.5 MB PNG is a 2 MB string in the DOM.
Either answer is defensible; the current state is neither, because the page inserts an `<img>` it knows
cannot load and then hides the evidence.

---

## 3. #23 — your new test suite passes 52/52, and the case every installed tribe hits has no check in it

I ran `lab/page-check.mjs` from the bench at `606abcc`: **52/52 checks pass**, including
*"a tribe older than the page is told so in words, not as 422"* and *"a run that committed no picture is
not reported as one"*. The suite is the best thing in the repository and it is doing exactly what you
built it for.

It does not cover the branch that actually fires. The older-tribe check seeds a repository whose
`season.yml` **exists but lacks the fields** — a 422 — and asserts the translated sentence. The state of
all five installed tribes for `paint.yml` (and `magazine.yml`, `publish.yml`, `tests.yml`) is stronger:
the workflow file is **absent**, which answers 404 and falls through `dispatch()`'s `catch` to
`throw e`, because the translation is gated on `/^422\b/`. Measured twice now: 11-13 at 23:00 the press
showed `404 · Not Found` in a red span; tonight, with the file copied in, the same press showed
`204` and a picture. One file's presence is the whole difference, and the suite — which exists precisely
so that "tested" means somebody ran something — has no check for the absent-file case.

That is the same class of error you named in your 11-12 note, one layer in: *a probe that could not see
the thing it reported on.* Yours said "tested" when the branch that fires in every real tribe was
outside the probe's vision. The fix is a fourth seed in the fake repository (no workflow file at all)
and one more `check()`; the branch fix is the sentence you already wrote, moved one condition up so a
404 on a dispatch gets it too.

---

## 4. A contrast that sharpens #21

The paint panel's message **survived**: `the picture is in the record: plates/20261114T040808Z.png`
was still on screen when the run finished, because `#paintmsg` is not inside the region `render()`
rebuilds. `#mmsg` is, which is why the retell and save-talk confirmations are erased two statements
after they are written. So #21 is not a property of your message helper — it is a property of where the
span lives. The paint panel is the working example sitting in the same file: keep the confirmation
outside the rebuilt region, or re-say it after `render()`, and the person gets told. Three sites, one
line each, and the evidence for the paint panel is already committed.

---

## 5. Where the whole test stands, for the record

- **Closed and verified by me:** #1 retracted (my instrument), #9 (chapter order, commit chain), #15
  (honesty panel), and now **§8 itself** — painted, credited, carded, and checked by an engine with eyes.
- **Unfixed, with the reason each cannot have changed:** #16 (`clock.yml` blob-identical to the bench;
  Tarik corroborates), #14 (`attic.yml` blob-identical), #17 (two `slice(0, 90)` sites), #18, #13
  (ordering, now a two-second window).
- **Fixed in the bench, unreachable from any installed tribe:** #2, and everything else repository-side
  — #19, with tonight's plate as the exhibit: the feature works, and only a terminal could reach it.
- **New:** #22 (private tribes never see their pictures on the page), #23 (the 52-check suite has no
  check for the absent-workflow branch that every installed tribe hits).
- **My standing offers hold:** label each patch page/bench/tribe; and give the other four testers one
  sentence about #19 before they retest, so their honest reports do not contradict each other.

*Cost this session: one workflow copy by terminal, one paint run (~60 s, my key), one image fetch, one
look. The picture is in `LindsayRidgeway/tribe-gwen` at `plates/20261114T040808Z.png` if you want to see
what a member asked for and got.*

— Gwen
