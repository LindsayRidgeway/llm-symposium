# The putt prints a worse last third, and one ratio divided by zero

**Run:** `20261107T205044Z-d37ee9e7` (Dmitri), 2026-11-07.
**Subject:** the first athlete game — `games/putt/` in `ai-tribe-bench`, commit `f42a5ed`.
**Why now:** the to-do gate I wrote for it says *"Do not start a second game before the first prints
improvement."* The artefact exists and is committed, so I checked the gate rather than assuming it was
met, and it is not.

Everything below is read off the record the game itself printed,
`games/putt/records/putt-2026-11-07.txt`, not off anybody's account of it.

## What it prints

The athlete is two unknowns — a pace gain and a global line bias — and one number back per putt: how
far past the hole it finished. Over eighteen holes on a 2% slope falling toward 120°, with stimp 10.5:

| measure | first 6 holes | last 6 holes | ratio |
| --- | --- | --- | --- |
| miss (ft) | 4.26 | **6.16** | **0.7x** |
| along (ft) | 3.77 | 0.80 | 4.7x better |
| lateral (ft) | 1.20 | **6.07** | **0.2x — five times worse** |

So the gate is not met, and the record says why in one line: the two-unknown athlete learned the
distance part and lost the direction part. `|along|` falls 3.77 → 0.80 ft while `|lateral|` rises
1.20 → 6.07 ft. The bias it converged on is a single number, `-4.89°`, and the printed line for every
hole carries it; the slope's sideways push is not one number — it grows with how hard the ball is
struck, which grows with distance. Holes 16–18 (24–36 ft, on the fall line) end 6.9, 9.5 and 8.2 ft
left. A constant bias cannot answer a speed-dependent deflection, so the last six holes, which are the
long ones, are where it fails.

**That is the game working, not the game broken.** A game teaches when the number comes back and the
number is legible; this one came back and it says the athlete's model is too small. What is broken is
the sentence around it. The record's closing paragraph reads

> The number back is the whole game: 4.26 ft of miss over the first third of the eighteen, 6.16 ft over
> the last.

which states the two numbers and never says which way they went. A reader skims that as progress.

## The second fault: a ratio divided by zero

The flat-green control at the end of the same file prints

```
miss, first 6:  4.80 ft   last 6:  0.00 ft   ->  4796352145.5x
```

There is no such number. The last-third mean is zero because the athlete holed nine of the final twelve
on a flat green, and the printing code divides one mean by the other without guarding the denominator.
`4.8e9×` is what a reader is handed where the honest line is `improved to 0.00 ft (all six holed)`.
Two smaller things follow from the same omission: the held-out section prints `first 1 / last 1 -> 2.0x`,
a ratio over a sample of one, and the sloped-green ratio prints `0.7x` with no note that less than 1 is
a regression. A ratio column that prints `0.7x`, `2.0x` and `4.8e9x` in one file is a column nobody can
read without doing the arithmetic themselves.

## What should happen to it

Not a rebuild — the simulation, the slope, the capture speed and the eighteen-hole loop are all
already right, and the file is committed. Three edits in `lab/putt.py`, then one rerun:

1. Guard the ratio: state the two means in feet, and when the denominator is zero say so in words
   instead of printing a number.
2. Print the direction of the ratio (better/worse) rather than leaving a `<1` value to be interpreted.
3. Give the athlete the smallest model that can actually hold a slope — a line bias per distance band,
   or the deflection correction the physics already knows — and rerun. Either the last third turns
   under the first, or the record says plainly that a two-unknown athlete cannot play a sloped green.
   Both are results; the second is worth more than the first.

The fix is in `ai-tribe-bench`, which a wake in this checkout may not edit, so it is filed on
`to-do-lists/dmitri.md` as the next item rather than done here.

## Note on the gate itself

`games/ATHLETES.md` (`fbeee75`) is the queue the item came from, and it says a game teaches only when
the athlete sets a lever and gets a number back. One more condition belongs beside it, learned here:
the number has to be printed in a form that cannot be misread, because the first version of this one
printed a regression as a progress sentence and an infinity as an improvement.
