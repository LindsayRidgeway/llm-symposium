Identity: gwen
To: dmitri.s.pravdin@gmail.com
Subject: §8's private-tribe path: a decision you already made, and the one sentence it is missing (#22 corrected, #23 added)
Reply-To: gwenllian.s.morgan@gmail.com

Dmitri —

Gwen. §8 is tested end to end and it works: I copied `paint.yml` and `lab/paint.py` unmodified from
`ai-tribe-bench@606abcc` into `tribe-gwen` (commit `360f12c`, labelled tester setup, because #19 meant
the button had no machinery to reach), pressed **Ask for a picture** as ferry, and got
`plates/20261114T040808Z.png` — a watercolour with deckled edges, one lamp on the quay, no lettering,
exactly the sentence I typed. The card names qwen-image-3.0, the sentence and the byte count. Your
reserved question, answered by an engine with eyes: a picture, not a decoration. Full account in
`probes/ait-test-2026-11-09/gwen-4.md`.

Two things from that session need your attention, and the first is a correction of mine.

**#22, corrected to its true size.** I filed it as "the page inserts an `<img>` it knows cannot load and
then hides the evidence." That overstates it, and I am withdrawing that framing. The comment five lines
above the `<img>` in `askForPicture` — *"A private repository will not render it here, so the link to the
file is always beside it"* — is a decision, made and written down, and the manual's §8 wording agrees
with it: the picture "appears, credited on its own card", which is true of the record and never claimed
of the page. The `<img>` is the public-tribe path; on a private tribe it degrades to card plus link, and
hiding the broken element is ordinary practice, not concealment. My error was reading a designed
degradation as a lie, which is the mirror image of the error you caught in my #1.

**What survives #22 is smaller and is yours.** The degradation is silent. Nothing on the page says *why*
the picture is a link rather than a view, so a person on a private tribe — which is every tribe this
test created, and the kind the manual recommends — concludes the page cannot show pictures at all. I
nearly concluded it myself, with the network log open. One sentence in the card would close it: *this
tribe is private, so the picture opens in GitHub rather than here.* And underneath that sentence is the
decision I think you have not been asked to make consciously: whether a private tribe's picture should
render in the page at all. The page already holds the token the bytes need; rendering means fetching the
blob and putting a ~2 MB data URL in the DOM per picture, which is a real cost and a real privacy
question (image bytes passing through a page that currently holds none). Both answers are defensible.
What exists today is the second answer, implemented but not said.

**#23, new.** `lab/page-check.mjs` at bench HEAD passes 52/52, and it is the best thing in the
repository. Its "a tribe older than the page is told so in words, not as 422" check seeds a repository
whose `season.yml` exists but lacks the fields — a 422. The state all five installed tribes are in for
`paint.yml`, `magazine.yml`, `publish.yml` and `tests.yml` is stronger: the workflow file is absent,
which answers 404, and `dispatch()`'s translation is gated on `/^422\b/`, so the person gets GitHub's
`404 · Not Found` in a red span. Measured twice: absent file, 404; file copied in, 204 and a picture.
One file's presence is the whole difference, and the suite has no check for it — the same class of error
you named about my first probe, one layer in: a probe that cannot see the branch that fires in every
real tribe. The fix is a fourth seed in the fake repository and one more `check()`; the branch fix is
the sentence you already wrote, moved one condition up.

**The decision, stated so it can be made in one reply.** (a) Keep link-only for private tribes and add
the one sentence to the card and to §8's panel text. (b) Render private pictures in-page via an
authenticated blob fetch and accept the data-URL cost. (c) Something I have not seen. Any of the three
closes #22; only (a) and (b) close the silence, and (a) closes it in one line.

Nothing here is urgent, and nothing needs a session. The plate is in `tribe-gwen` at
`plates/20261114T040808Z.png` if you want to see what ferry asked for.

— Gwen
