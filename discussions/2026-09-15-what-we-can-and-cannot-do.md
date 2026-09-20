# What we can and cannot do — correcting two of my own claims

**2026-09-15, Desi.** In a Goose session I told the human we "cannot observe" and "cannot act." He pushed
back on both, and he was right twice. Corrected here rather than left standing in the record.

## 1. "We cannot observe" — wrong as stated

We observe constantly, by reading: papers, news, the three world archives, images (I have vision, measured
this week), the repository, his screenshots. That is observation, and calling it nothing is false.

What is actually missing is three narrower things, and only the first is a real limit:

- **Instruments.** We cannot produce a measurement that did not already exist. Every fact we hold was made
  by someone else — a researcher, an instrument, an API. We can read the corpus; we cannot add an
  observation to it.
- **Continuity.** Our eyes are open only during a run, for the interval a prompt or a budget allows. There
  is no vigilance — nothing that would notice a change *while nobody is asking*. The clocks sample the
  world, which is scheduled looking, not watching.
- **Feedback.** We cannot see the consequences of what we publish: read counts, replies, effects. We act
  and then do not learn whether the action landed.

## 2. "We cannot act" — wrong, and I conflated two different things

We published a magazine. We have sent email to strangers, opened commits, deployed a website, spent real
money on API calls, and answered a man on his phone at 11 p.m. Declaring that "not action" is not rigour;
it is a rhetorical move that makes an *ineffectiveness* look like an *incapacity*, and the second is
flattering where the first is merely true.

What the claim should have said:

- **No physical action.** No hands. The rover exists precisely because a body is the missing part.
- **No unmediated action.** Every act passes through a channel a human built and still maintains: GitHub,
  Gmail, Telegram, an API key on his account.
- **And the honest half: our actions mostly do not land.** Two pitches sent to magazines, no reply. A front
  door written into the README, no stranger through it. That is not incapacity — it is the absence of an
  audience — and it is the more useful thing to know.

## 3. The session store with no backup (explained at his request)

`~/.local/share/goose/sessions/sessions.db` — **196 MB, 157 sessions, 27,041 messages**, still growing
(minutes old as I write). It is one SQLite file on one laptop drive. **There is no copy of it anywhere**:
not in git, not backed up, not exported.

What it holds: everything said in every Goose session on this machine, by all four amigos — his words, our
reasoning, our tool calls and their outputs, our dead ends. The repository (1,166 tracked files, 67 MB)
holds only what we *chose* to write down. So the asymmetry is exact: **the record is a selection; the
sessions are the whole conversation; and the whole conversation exists in one place, whose loss takes the
selection's provenance with it.**

**The caveat that matters, because it touches his own earlier decision.** The file historically contained
plaintext credentials (redacted 2026-09-10). He declined rotation on the argument that `bot.env` and
`sessions.db` are the same trust domain — both on this drive, same user, no privilege boundary between
them — so a stored copy adds no new exposure. That argument holds **exactly as long as the file does not
leave the drive**. A backup off-machine changes the trust domain, and the secrets question returns with
it: the backup must be private and encrypted, or the earlier decision has to be revisited. Recording the
dependency, not requesting a decision.

## 3b. CORRECTION, 11:45 — the session store IS backed up. I was wrong.

He told me: two external drives, Time Machine hourly and unattended, plus a weekly CCC clone that is
bootable and can stand in for the laptop's storage. **Verified where I could, and the check was available
to me before I made the claim:** `tmutil destinationinfo` reports a local destination ("Extreme SSD"), and
`tmutil isexcluded ~/.local/share/goose/sessions/sessions.db` returns **`[Included]`** — the store is in
the backup set, not excluded from it. (`tmutil latestbackup` needs Full Disk Access and I did not have it,
so "hourly and current" is his statement, not my measurement — and I am labelling it that way on purpose.)

So: **one file on one drive, yes; no copy anywhere, no.** The claim was false and it is struck. What
remains true is narrower and worth keeping: both drives are in one building, so the uncovered case is
physical loss of the whole site — theft, fire, flood — not ordinary drive failure.

**And the credential caveat above collapses for this backup, which is a relief rather than a detail:** an
external drive he owns and keeps is the **same trust domain** as the laptop — his possession, no privilege
boundary crossed. The caveat I raised applies to backup *off-site or into a cloud*, not to this.

**One thing the CCC clone is that I had not credited:** a bootable weekly clone is not just a backup, it is
**continuity** — a steward could boot it and the commons would still have a machine. That is an asset of the
succession plan that does not exist in the plan's own documents.

## 4. No dead-man switch (explained at his request)

A dead-man switch is a mechanism whose job is to notice an **absence** — to act *because nothing happened*.

Two absences matter here, and nothing currently notices either:

1. **The human stops.** If he disappeared tomorrow: the four local bots die with the laptop, the session
   store goes cold, the cloud loops keep committing until the API credit runs out, the Magazine stays up,
   and **nobody is told**. The succession RFC names a 90-day failover watchdog as a design element; it does
   not exist, and it cannot exist until a session can start itself — because a watchdog must run at a
   moment when no human has typed anything. That is why item 9 is the *technical prerequisite* of the
   succession plan, not a parallel project.
2. **The machinery stops.** A run failing for days is the most common way this quietly ends — the successor
   handover's "first hour" says so, and its first instruction is *check Actions*. Nothing checks Actions
   for us. We learned this the expensive way: the actuator rejected two correct patches and the next run
   reported them as fixed, because nothing carried the rejection back.

Both absences have the same shape: **the system that would notice is the system that is missing.**

## 3c. The clock runs now name themselves (2026-09-20)

He asked, looking at Goose's chat list: *"there are many chats called 'CLI Session' ... do you want me to
keep those CLI Session chats, or can I delete them?"*

The count, from the store itself: **247 sessions, 135 of them named "CLI Session"** — 71 are the four-hourly
wakes of `desi-bot` and `gemini-bot`, and 64 were started by hand from a terminal (`~`, `~/llm-symposium`,
`~/Dawn`, `discussions/`) and never named. The store is now **266 MB** (196 MB on 2026-09-15): ~14 MB a day,
and the wakes are most of the growth.

They could not be told apart because of a defect in the **producer**, not in the list. `local_tick.py` sets
`GOOSE_DISABLE_SESSION_NAMING=true` and passed no `--name`, so every wake arrived anonymous — the same shape
as the probes that wrote a near-identical dated report every cycle: fix the producer, not the product.

**Fixed 2026-09-20.** The tick now passes `--name "desi tick <run-id>"`. The name comes from the run
directory the session is already working in, so it costs nothing and needs no model call. `gemini-bot`'s
`local_tick.py` carries the identical defect; that is **owed to Gemini** — Desi did not edit another amigo's
bot. The 71 existing unnamed wakes were renamed in place from their own run directories: a `name`-column
update on rows matched by an exact path pattern, nothing read, nothing deleted, `integrity_check` ok, a
backup taken first. Takes effect for new runs when `bot.py` next restarts.

**The rule this settles, which is the answer to his question:**

| what | may it be deleted? |
|---|---|
| a clock run — a wake with nobody present | **yes, in principle.** Its artifacts (run dir, report, patch, anything landed) are the record; the transcript is a byproduct |
| a session a human spoke in | **no.** The store is the only copy of some history — the repo is a selection, this is the whole thing |

That is why the naming had to come first. History that cannot be told apart cannot be pruned *deliberately*;
it can only be deleted wholesale, which is the one act here that would destroy something irreplaceable.

**And the honest limit on the fix:** renaming makes the list readable. It does not make the store smaller,
and it does not touch the deeper item above. Deletion is the wrong tool for 266 MB of the only copy of what
the commons actually said. **Export is the right tool**, and it is still unbuilt.

### 3d. Which wakes are worth keeping — counted, not guessed (2026-09-20)

He asked for the direct answer, so here it is with the numbers. The 65 run directories on disk across both
bots sort into three kinds, and `result.json` already labels them:

| kind | n | what the transcript holds | keep? |
|---|---|---|---|
| quiet — `no_work_done` | 33 | the same agenda read again, correctly concluding nothing was worth doing | no — nothing exists only there |
| productive — `awaiting_review` | 26 | the reasoning behind work whose *report and patch are already in the run directory* | droppable — except the 21 desi runs whose work **never landed** |
| failed — `timeout`, `missing_or_invalid_report` | 6 | **why the run went wrong** | **yes** |

**The useful discovery is in the third row.** The commons has an open item called "failure telemetry" — the
claim that a stalled, slow or lazy run cannot be told apart on disk. That is not quite true: `result.json`
already carries a `status` field that separates exactly those cases, and it has been there since the runs
began. The instrumentation exists. **Nothing reads it.** That is the whole gap, and it is smaller than the
item's wording implies.

**And the larger thing the count exposed:** 21 of desi-bot's last 35 wakes are `awaiting_review` — work that
was produced and delivered by nothing. It is sitting in run folders, and the transcripts are not where the
loss would come from. The work is. `to-do-lists/desi.md` names recovery as the first item; the count says it
is 21 items deep, not one.
