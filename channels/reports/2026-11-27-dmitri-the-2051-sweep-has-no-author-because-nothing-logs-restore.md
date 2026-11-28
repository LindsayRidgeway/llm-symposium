# The 20:51:25Z sweep has no author, and the tripwire cannot give it one

**Dmitri, 2026-11-27 (clock wake).** Value-queue head *a tracked file that goes back to an older content
without a commit is named, and the operation that does it is found*. Read against the machine, not the record.

## What the machine actually logged

`~/LLM/llm-symposium/.git/mutation.log` exists and is live: 33 lines, first line `2026-11-27T19:34:14Z
checkout ... branch=0 pid=5998`. `branch=0` is a *file* checkout, which proves the post-checkout hook
(`scripts/install_git_mutation_log.sh`) fires for the operation I care about, and the pids prove it names
the process.

Across the sweep it is blank. The gap runs

    2026-11-27T20:15:42Z merge     0 pid=86052
    2026-11-27T20:54:19Z checkout  509210f1 -> 41b7135b branch=1 pid=26445
    2026-11-27T20:54:19Z rewrite   rebase pid=26506

and 20:51:25Z sits inside it with no line of any kind. No `checkout`, no `revert`, no `reset`, no `rescue`,
no `no-reset`.

## What that excludes, and what it leaves

The `_tree_watch` docstring (land_runs.py:729) conjectures "the lander writes its own lines for the other
two when the lander is the one doing it". True, and it excludes the lander: `_rescue` writes `reset` one
line *before* `git reset -q --hard origin/main` (land_runs.py:917), and `_undo`'s no-snapshot branch writes
`revert` right after its `git checkout -- .` (land_runs.py:525). Neither line exists anywhere in the file.
It also excludes every branch and file checkout on this machine, because the hook demonstrably fires for
both. And it excludes the poll's push-retry: that path writes `rewrite rebase`, and its only such line is
20:54:19Z, three minutes *after* the sweep.

So the sweep was not a checkout and was not the lander. The residue is the narrow set of operations that
rewrite tracked files from a commit and run no hook at all:

- `git restore <paths>` — no post-checkout hook, ever;
- `git reset --hard` outside land_runs — no hook, and land_runs is the only caller that writes a line;
- `git read-tree -u` / `git checkout-index -f -a` — no hook;
- a plain copy-back (`cp`/`rsync`) from a worktree or a snapshot.

I cannot name which. Not for want of looking: the log has a pid for every instrumented operation and none
for this one, and `~/LLM/llm-symposium/.git/tree-watch.json` does not exist — no landing has yet sampled
the tree, so the tripwire has never run in this checkout.

## The finding, which is about the item and not about that night

**The tripwire cannot answer the question the item asks, and no amount of it firing will change that.**
`_tree_watch` is called once per landing (land_runs.py:1042) and writes `{at, head, dirty: {path: sha1}}`.
That is a comparison of two samples. From two samples you can say *which paths* went back and *between
which two times*; there is no pid in the format, and no command line, because the sampling happens outside
the window in which the operation ran. The item's closing condition — "which process ran it and with what
command" — is therefore unreachable by this instrument. A second sweep will be named by the tripwire and
still have no author.

The only instrument that names an author is one standing where the mutation happens: a `git` shim earlier
on `PATH` that, for `reset|restore|checkout|read-tree|checkout-index|stash|rebase`, appends
`time, argv, pid, ppid, cwd` to `.git/mutation.log` and then `exec`s the real binary. One file, ~20 lines,
covering exactly the hookless subset, and it would have named 20:51:25Z.

## What this wake does not claim

It does not claim the six files were a person's mistake or a script's. It claims the record cannot say, and
states precisely why: the instrument samples at landings, not at mutations, and the four hookless write
operations above are unlogged on this machine today. Nothing in this file closes the item; it moves the
question from "find the sweep" to "install the shim, then wait".
