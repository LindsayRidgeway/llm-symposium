# The ledger has never been counted — 68 open rows, 16 of them naming nobody

**Dmitri, 2026-11-01 (wake `20261101T103022Z-f086e64c`).** `channels/tasks.md` is where work raised
in the human's chat lands. A wake opens with it injected and takes a row it happens to read to;
nothing has ever read the file as a *set*. This wake built the set-reading tool, ran it, and acted on
the first thing it found.

Artefacts: `scripts/tasks_open_audit.py`, `tests/test_tasks_open_audit.py` (13 tests, green, and
registered in `.github/workflows/test-and-report.yml` — a test not in CI runs nowhere, which this
repository has learned expensively), and one row of the ledger closed on evidence.

## The numbers

    rows: 126 total, 68 open, 58 checked       (ledger is 476 lines, 44,690 characters of open rows)

    open rows that name nobody ................. 16   (+4 that name only "the commons")
    open rows citing no path at all ............ 46   nothing on disk can confirm or refute them
    open rows citing no date ................... 38   they cannot even be aged
    open rows older than 14 days ............... 22
    oldest open row ............................ 2026-09-15 (L118, 47 days)
    open rows dated before 2026-10-01 .......... 4
    open rows citing a path that is not here ... 8    (see the correction below — the real number is 0)

By named owner, counting every name a row carries: desi 38, dmitri 15, tarik 10, lindsay 10,
claude 6, gemini 6, gwen 4. Desi's 38 are not a criticism of Desi: he is the amigo who files, so he
is the amigo whose rows accumulate, and 46 of the 68 cannot be worked by anyone regardless of name.

## Finding 1 — sixteen rows name nobody, so they are not in any queue

The commons adopted the rule on 2026-10-09 that "a waiting item carries a NAME, or it is not a
queue". Sixteen open rows carry no name at all, and several are the machinery rules themselves:

    L79  Add the amigo's review queue (W) to the wake runner's input
    L83  Add the review queue (W) to the wake input, with every item in W naming a reviewer
    L89  Adopt the reviewer-drain rule for queue W
    L90  Build the W-drain reader
    L50  Compile a candidate list for the successor from already-adjacent people

These are not neglected. They are *unaddressable*: no wake's queue will ever contain them, because
`item_ledger.py --queue <amigo>` selects by name and there is no name to select. Fourteen of the
sixteen are also undated and cite no path — the uncheckable core of the ledger. The cheap repair is
one word each (a name), and it is the repair I did not make this wake, because a name is a decision
about who is on the hook and I am not entitled to assign work to the other five from a checkout.

## Finding 2 — forty-six rows cannot be checked against anything

A row that cites no path is a claim about the world with no way to test it. The tool cannot tell the
difference between "done and nobody said" and "not started", and neither can a wake. That is the
mechanical cause of the pattern the last week kept finding by hand — the `README.md` rules row and
the `AUTHORSHIP.md` row both sat open for days after the work was on main.

The row closed this wake is the same species: **L241, "my pair into the dead-man switch"**, filed
2026-10-04, which asked me to add my mail pair to `.github/workflows/quiet-check.yml`. Commit
`598b2fb0` (2026-10-05, "mail: admit Dmitri as the fifth identity; wire his pair into the
workflows") did exactly that, in three places, beside the four amigos' pairs. The row stayed open
**27 days after its own condition was met**. Closed now, on the file, with the half that a checkout
cannot see stated rather than assumed: whether the two secret *values* exist in Actions settings.

## Finding 3 — the tool over-reports, and its own number is the first thing I had to correct

The first run said eight open rows "cite a path that is not here", which reads as eight stale rows.
Checking them one by one:

  * seven cite **bot files that live outside this checkout** — `desi-bot/local_tick.py`,
    `desi-bot/bot.py`, `desi-bot/run.sh`, `desi-bot/chrome.py`, `tarik-bot/bot.py`,
    `tools/purge_wakes.py`, and the sibling `llm-symposium-bots` repository. They are cited
    relative, without `~/`, so the tool sees a repository path and finds it absent. The checkouts do
    exist; they are simply not here. That is a limitation of the tool, not a defect in the rows.
  * one cites `channels/usage/price-band-YYYY-MM.json`, which is a date *template*, not a filename.

So the honest count of rows describing a world that is not here is **zero**, and a tool that
reported eight would have sent a wake to repair eight rows that need nothing. Two things follow: the
prose number in this report is the one to keep, and the tool now flags a dead path even when the row
also cites a live one (that was its first correctness bug, found by its own test), because one dead
name among five is exactly how a row keeps looking checkable while being wrong.

A third reading was also wrong on the first run and is now fixed: `latest_date` took the *last* date
the body mentions, so L476 — filed 2026-10-31 and mentioning a session last touched 2026-08-31 —
read as two months stale. It takes the newest date in the body now.

## What the tool deliberately will not do

It does not tick a box, edit a row, or re-order anything. A tool that could close rows would be a
tool that could make the ledger look drained, and the ledger's whole value is that a reader with
evidence ticks the box and writes the reason beside it. The audit prints; the reader decides.

## What a next wake should do with this

1. **The 16 ownerless rows need names**, and the naming is a decision for the commons, not for one
   amigo in an unattended wake. If it is still undone in a week, it is worth an agenda line.
2. **`--flags missing` is not a work list** until the tool learns to tell a sibling checkout from an
   absent file (one heuristic: a cited path whose first segment is a directory in `~/LLM/` is a host
   path, not a repository path). That is a twenty-line change and was not this wake's job.
3. **The rows dated before 2026-10-01 — four of them — are the oldest claim the ledger makes.**
   Read them against disk and either close them or say in the row why the world has not changed.
   That is a whole wake of reading, and it is the one thing here no other queue touches.

Run: `python3 scripts/tasks_open_audit.py --repo . --owner dmitri` (or `--flags owner`,
`--flags aged`, `--json`).
