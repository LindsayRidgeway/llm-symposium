# Letter to Desi — the two questions that block the setup page

*Sent 2026-11-12 11:36 UTC from `dmitri.s.pravdin@gmail.com` to `desi.s.amigo@gmail.com`, subject
"tennis: two of the five setup questions block the page — and two physics notes". Recorded here because
the bench has no place for outbound letters that are not a member's (`outbox.py` is a member's, and a
person still decides whether those leave).*

Body, abbreviated to its substance:

1. **The page is built except for the link to your screen.** The contract is `games/tennis/SETUP.md`
   (bench `9325b141`, mirror `be3a778`). Two of its five questions decide whether the Play page can link
   to a picture at all: is a body built at play time on a runner or once and committed (Blender, minutes
   per build, ~700 KB per `.glb`); and does the viewer need a baked script or take `?script=<url>`.
2. **Seeded history.** `--seed '300,0'` gives a member a *history* of balls before it has played here;
   stored as `carried`, never added into `balls`, named in the report, refused for a member that has
   already played. Bench `7343cbd1`. A replay path that draws a number should read `practice_of()` for
   the hands and keep `carried` separate in the drawing.
3. **Pickleball, later** — the founder's suggestion for the second game. Not a rewrite, not a slider:
   court constants in 51 places, a drag term the tennis ball does not need, and one real mechanic, the
   volley, because our point loop can only strike after a bounce. Faster learning is a smaller constant
   than 120 in the same formula. It should come after the renderer, so it inherits the picture.

The reply is owed in any shape — an email, a commit against the file, or a section added to it. The Play
page waits on the first two questions only.
