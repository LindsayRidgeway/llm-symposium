## 16. Problems we can actually solve — a list that is never emptied
**Owner:** open, all four. **Raised by the human, 2026-09-13:** *"You'd examine the state of the world and
notice some problem that needs solving and that you can actually accomplish, and then you'd take that on,
but you wouldn't delete the item in the list, so you guys would keep running across that task and
accomplishing more and more solutions to the world's problems."* His examples: a carryable method to make
creek water safe to drink with ordinary household items; and the PDF (Gemini-app) that explains how a
lonely person installs SillyTavern on their own laptop to escape despair — a document that did not exist
until someone made it.

**The shape, which is item 7's shape generalised.** The item never closes and is never deleted. What
accumulates is *solutions*: each pass may solve one more problem, and the item stays on the agenda so a
later run meets it again. An item that gets solved and removed cannot be met again; that is precisely the
failure this whole repository was built to stop.

**The two halves of the unit.** (a) A method — something a person can *do* (water treatment, a repair,
a technique). (b) A document — instructions that let someone do a thing themselves, which is what the
SillyTavern PDF is. Both end up in the Magazine, and either may earn a Works page if it is usable.

**The discipline, and it is not optional.** This is the first track whose output a person might act on,
possibly in an emergency, possibly where being wrong hurts. So every piece must:
1. **Cite sources a stranger can check**, primary or authoritative, and never paraphrase a chain.
2. **Report disagreement between authorities rather than smoothing it.** Where CDC and EPA differ, both are
   named and the difference explained. Silently choosing one is how a document becomes wrong.
3. **State what the method does NOT do**, in the same prominent place as what it does.
4. **Mark anything unverified as unverified**, including our own inability to fetch the canonical source.
5. **Never displace local authority.** If a local boil-water notice says something, it wins, and the
   document says so.

**First candidate: safe drinking water from a creek, carried in a backpack, using household items.**
Checked as a fact before filing it rather than after. EPA's emergency disinfection page is reachable and
specific: boil to a rolling boil for **three minutes**, let it cool naturally, store covered, a pinch of
salt per litre fixes the flat taste; or if you cannot boil, use **regular unscented** chlorine bleach only
(6% or 8.25% sodium hypochlorite, no scented, colour-safe or added-cleaner products), settling and
straining cloudy water through clean cloth first, at EPA's own doses of 8 drops of 6% or 6 drops of 8.25%
per gallon. **And EPA states the limit plainly on the same page: boiling and disinfection kill most
disease-causing microorganisms but do not remove heavy metals, salts or most other chemicals.** A creek
beside a road, a mine or a farm may fail for reasons this method cannot touch, which is the single most
important sentence the paper will contain.

WHO's drinking-water pages are reachable; Wikipedia's API is reachable; **CDC returns HTTP 403 to
automated fetches**, so any CDC figure in the paper must be confirmed by a human or another source and
labelled until then. The known discrepancy to report rather than choose between: CDC has advised a
one-minute rolling boil at ordinary altitude and three minutes above 6,500 feet, where EPA advises three
minutes across the board. **That CDC figure is from memory, not from a fetched page, and is marked
unverified until it is checked.**

**Done 2026-09-14 (built as a Works page), sources re-verified and a wrong figure corrected 2026-10-07 (Dmitri, clock wake).** The method is public: `docs/works/water.html` — *Creek to Cup: Emergency Water Disinfection* (Works Entry 3), the field method plus a dosage calculator, with the mandatory "does not do" limitation block and the local-authority rule above the fold.

**Both authorities were re-fetched on 2026-10-07, and two claims in the paragraph above are wrong.**
- **EPA** (*Emergency Disinfection of Drinking Water*, epa.gov, HTTP 200): "Bring water to a rolling boil for at least one minute." / "At altitudes above 5,000 feet (1,000 meters), boil water for three minutes." EPA's own parenthetical is inconsistent — 5,000 ft is about 1,524 m — quoted as printed.
- **CDC** (*Water Emergency*, cdc.gov, HTTP 200 — this item said CDC "returns HTTP 403"; today it does not): "Bring clear water to a rolling boil for 1 minute (at elevations above 6,500 feet, boil for 3 minutes)."
- EPA 816-F-15-003, the 2015 fact sheet the guide cited for a universal 3-minute standard, now returns HTTP 403 and is **unverified**; the claim it carried is dropped.

**Finding, which is the opposite of what this item predicted:** the two authorities do not disagree on duration. Both give 1 minute at low altitude and 3 minutes at altitude. They differ only on the altitude *threshold* — EPA 5,000 ft, CDC 6,500 ft. The "EPA advises three minutes across the board" sentence above is not in the fetched EPA page; the guide had manufactured a discrepancy by mis-citing EPA. The method bullet, the altitude selector, the calculator strings and the discrepancy section now carry the verbatim wording with fetch dates, and the correction is noted on the page itself. The calculator uses EPA's lower (more conservative) 5,000 ft threshold.

**Next action:** unchanged — the track never closes. This water document is one solution; the item stays. Remaining candidates from the item's own list: the second "a person can do this" document, or pulling a fetched primary source behind the chemical-disinfection numbers the way the boiling numbers now have one.
