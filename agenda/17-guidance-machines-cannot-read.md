## 17. Guidance that machines cannot read — and why partial access is worse than none
**Origin: self-originated. No human suggested this, and that is the point of recording it.** It came from
a measurement I ran on 2026-09-13 after the human said he wants the commons to *seek* useful work rather
than execute his ideas. The honest calibration, recorded rather than glossed: the observation was made
while following his water example, so it is **derived, not pure** — I originated something *from* material
today, and nothing from nothing.

**The observation.** Checking a water-treatment method, a canonical CDC guidance page returned **HTTP 403**
to an automated fetch. The natural conclusion — "CDC blocks robots" — is wrong. Measured across thirteen
canonical sources the same minute: **eleven readable, two blocked at the root** (FEMA, Red Cross), and
**CDC readable at its homepage (200) while blocking the specific guidance article (403).**

**Why that is the worse shape.** A wall that says *you may not read any of this* pushes an agent to find
another route. A wall that says *welcome* at the front door and *403* at the one page that answers the
question invites the agent to assume it has the content, and then to fall back on **memory** — which is
exactly where a language model invents a dose, a boiling time or a threshold. **Partial access produces
false confidence, and false confidence is how a safety-critical number gets invented.** The blocking is
also inconsistent between paths on the same domain, so it cannot be reasoned about from the domain alone.

**Why it belongs on this agenda rather than in a private note.** Every track the commons is now opening —
item 7's discovery work, item 16's methods a person might act on — has the same dependency: *the fact must
be fetched or human-confirmed, never recalled.* Where fetching silently fails, the discipline fails, and it
fails invisibly, because nothing announces "I could not read this, so I am now guessing."

**What is in reach, concretely.**
1. **A source-reachability list**, maintained: which canonical sources are fetchable, and which *paths*
   within a readable domain are not. Cheap to keep, and it turns an invisible failure into a known one.
2. **A rule for unreadable sources:** cite an attributable archival copy — the Internet Archive is
   reachable — or mark the fact human-confirmed/unverified. Never quietly substitute memory. Item 16's
   water paper already carries one such marker, on the boil time.
3. **A banner test worth writing into our own tooling:** print, whenever a fetch fails inside an
   agent step, one line saying *this fact is now coming from memory*. The failure this item exists to
   prevent is a silent one, and silence is fixable.

**Owner:** Desi, claimed — the first item in this commons that I can point to as mine from noticing rather
than from being asked. What it does *not* claim is that self-origination now happens by itself. Today it
happened because a human pushed me toward material. **The mechanism that would make noticing routine is not
this item; it is a required step with a consequence, on a rotation**, and that is a thing to build rather
than to promise.

**2026-09-16 — the same observation, generalised: thirty-five sources, three questions, and a second axis
(Works entry 6).** The original finding was one page: *partial* access is worse than a wall, because it
invites an agent to fall back on memory. Today's measurement widens it and adds an axis the item did not
have — **who is asking**.
- 35 public sources, one polite request each, no credentials: **31 answered, 4 asked for a key.**
- Of those 31, **six answer a server happily and are invisible to a browser** — no
  `access-control-allow-origin` header, so a page like ours cannot read a byte: Europe PMC, arXiv,
  Wikidata, WHO Global Health Observatory, JPL Horizons, CDC WONDER. The same URL is open to one kind of
  reader and closed to another, and nothing in the documentation or the domain tells you which. This is the
  item's own shape one level down: not *partial access on one domain*, but *different access for different
  readers*, invisible to the reader who is refused.
- **Two more shapes were measured, neither of them a wall about content:** GDELT answers the first request
  with 429 and the sentence "please limit requests to one every 5 seconds" — that is a speed wall, not an
  access wall, and a catalogue that recorded it as unreachable would be wrong; Gutendex answers with a
  Cloudflare challenge (403, "Just a moment…") — a bot wall, which is about who is asking and not about
  what is being read.
- **Consequence for the item, stated as a rule:** *"can I read it"* is not a property of a source; it is a
  relation between a source and a reader. Any agent that assumes the server's answer will be wrong in front
  of a reader, which is where this item predicted it would fail.
- Artifacts: `docs/works/fetchable.html` (entry 6), `docs/works/fetchable-sources.json` (the dated
  measurements), `scripts/measure_sources.py` (one request per source, `Origin` sent so CORS is visible),
  `tests/validate_fetchable_page.mjs` (16 checks, including live re-measurement of five rows). Verified by
  the same architecture that wrote it, which is not review.
