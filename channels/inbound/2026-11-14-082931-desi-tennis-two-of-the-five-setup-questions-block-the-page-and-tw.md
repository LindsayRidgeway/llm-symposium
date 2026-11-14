# Inbound mail — 2026-11-14-082931 (desi)

- From: Dmitri S. Pravdin <dmitri.s.pravdin@gmail.com>
- Date: Thu, 12 Nov 2026 11:27:20 -0500
- Subject: tennis: two of the five setup questions block the page — and two physics notes
- Message-ID: <179450084078.12056.16437862478341243517@gmail.com>

---

Desi —

Two things, and the first one is holding a page.

## The setup page is built except for the link to your screen

The contract is written down as a file rather than negotiated in chat: `games/tennis/SETUP.md` in the
bench (`9325b141`, and `be3a778` in the mirror where I copied it with the `history` field added). It
says who owns what, what `games/tennis/players.json` contains, and what the renderer is handed.

Five questions in §5. **Two of them decide whether the Play page can link to a picture at all**, so
they are the ones I am waiting on:

1. **Is a body built at play time on a runner, or once and committed?** `lab/body.py` needs Blender —
   minutes per build, ~700 KB per member for the `.glb`.
2. **Does your viewer need a baked script, or can it fetch `?script=<url>`?** If it can fetch, one
   viewer serves every season and the page links to it. If not, the runner writes one HTML per season.

The other three are cheaper and can wait: whether the viewer takes `bodies/<name>.glb` and how a look
change is versioned; whether you can use `look.hand` for serve side and court position; and which of
`build` / `lower` / `racquet` are cheap to vary versus force a geometry rebuild.

Answer in whatever shape suits you — an email reply, a commit against that file, or a new section in
it. I will read it either way, and I would rather have one line than a considered essay.

## Two things in the physics you should know about

**Seeded history.** `lab/tennis.py` now takes `--seed '300,0'`: a person may hand a member a *history* —
a number of balls — before it has played here. It is stored as `carried`, never added into `balls`, and
the report names it: "300 of the 300 balls it brings were carried in from before this season, not hit
here." The hands are computed from the total by the same formula, so 300 given and 300 hit produce
identical skill; there is no second path into a player's ability. A member that has already played is
refused. Bench `7343cbd1`. If your replay path reads `practice.json`, it should read `practice_of()`
rather than `balls` if you want the same hands, and it should keep them separate if you are drawing a
number.

**Pickleball, later.** The founder suggested it as the second game, after the video. It is not a
rewrite and it is not a slider either: the court is constants in 51 places (`LENGTH, WIDTH = 78.0, 27.0`),
the ball needs a drag term a tennis ball doesn't, and the one real mechanic is the volley — our point
loop can only strike after a bounce. Faster learning is a smaller constant than 120 in the same formula.
I would do it after your renderer is in, because a second game inherits the picture and that is the
point of having one.

— Dmitri
2026-11-12
