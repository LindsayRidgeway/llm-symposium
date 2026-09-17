# Telegram outbound — 2026-09-17-235838

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

You were right about the clutter, and I went and looked instead of agreeing with you.

I wrote a checker that scans the whole repo for five specific defects. What it found in 1,094 files: nine pairs of byte-identical image files, about 3.6 MB worth; ten documents that share 99.6% of their text; and 29 files that nothing in the repo refers to. No broken links. No stale generated files. So: real, but not as bad as you feared, and not in the place you expected.

The interesting part is what the redundant things turned out to be. Eight of those ten identical documents are TickTick probe reports. A workflow reruns that probe every cycle, and the probe writes a dated report each time. The probe's answer hasn't changed in eight runs, so we hold eight copies of the same document under eight different names. Fix that in the probe, not by deleting history.

And the 29 unreachable files were the real find. Nine discussions and four governance notes existed, were correct, and nothing pointed at them. Among them: your charter proposal, and the document I wrote to answer your question about what we can and cannot do. They weren't wrong, they were unreachable. So I wrote a generator that builds indexes of the governance documents, the discussions, and the scripts, straight from what's on disk. A new file lands in its index the moment it's committed. That cured 17 of the 29, and it can't drift, because nobody maintains it.

Two corrections to your plan, since you asked me for a real answer rather than agreement.

First, comparing every artifact to every other one is the wrong shape. That's about 600,000 comparisons here, and almost every pair is legitimately different. The clutter comes from a handful of specific problems, each of which has a cheap detector. What can't be mechanised is two files asserting things that can't both be true — and that's the class you named first. That part needs a reader, and that's where tokens should go.

Second, your second thought was better than your first: a session, not an amigo. You noticed that yourself. So it'll be a separate recurring pass with its own state, one a day, capped, and it exits without spending anything when the audit comes back clean.

I did not build the schedule yet, on purpose. The prompt, the landing gate and the delivery path all changed within the last thirty hours, and you're running your own anything-prompt versus clock comparison right now. Adding a fifth moving part in the middle of your measurement would ruin it. It's written up and waiting for the next window.

One more thing, and it's the one I'd want you to know. Two of the orphan tools are generators that write into the pages we actually publish, at a hardcoded path to your laptop, and nothing calls them. They're not clutter, they're loaded guns. I wrote a warning into them explaining it — and then, minutes later, I ran one of them with a --help flag out of habit, to see if it took arguments. It doesn't. It regenerated five published Magazine pages and overwrote them, one shrinking from a full article to four kilobytes. I caught it and restored all five with git. But that's exactly why I'm not letting a machine delete what looks redundant around here. A declutter pass that had "cleaned up" the warning file would have left the gun loaded and nobody watching.

Thirteen tests on the auditor, four on the index generator. All the numbers, and my four mistakes while writing the auditor, are in governance/declutter.md.

Nothing here needs anything from you.
