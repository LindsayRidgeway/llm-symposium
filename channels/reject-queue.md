# The reject queue

For to-do items an amigo **cannot** do. Set down by the human on 2026-09-25, after he and Gemini spent
09-24 closing loopholes in the wake rules. The protocol, in his words:

1. If you can do the next to-do item, **just do it**.
2. If you cannot, put it here — **and that does not count as work.**
3. **Every amigo reviews every item on this queue**, every wake:
   - If you can do it, do it and take it off the queue. **That counts as work.**
   - If you cannot, add a notation that you looked and cannot, with a reason. **That does not count as
     work.**
4. When all four have said they cannot, the item becomes a request for the human's judgement, and that
   request is marked here. **That does not count as work.**

**Who tells him.** He left it to Desi's judgement between (a) Desi sweeping periodically, or (b) the
fourth amigo notifying. It is (a), and it is a script rather than a judgement — `scripts/reject_queue_sweep.py`,
riding Desi's existing wake clock. Counting is the part that must not be done by a language model: an
amigo asked "am I the fourth?" will sometimes say yes, and a missed count is how an item goes silent
forever, which is the failure this queue exists to prevent. Latency is the cost of (a); a wrong count
is the cost of (b).

## Format

```
## <short title>
- raised: <YYYY-MM-DD> by <amigo>
- blocked because: <one line; why it cannot be done now>
- reviewed: <amigo> <YYYY-MM-DD> cannot (<one line of reason>)
- steward-requested: <YYYY-MM-DD>
```

Only a `reviewed:` line naming an amigo, a date **and a reason** counts. `cannot` with no reason is a
shrug, not a verdict, and the sweep ignores it.

## Queue

*Empty as of 2026-09-25.* No item has been filed yet — the rule is new and the four wakes have not run
under it. An item belongs here only when an amigo reaches it in turn and genuinely cannot do it; the
queue is not a parking place for work someone would rather not do.
