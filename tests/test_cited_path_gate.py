"""A dated artefact cited as evidence must be one a reader can open.

`scripts/cited_paths_audit.py` measures the class of citation that opens nothing; it deliberately
does not fail, because 4,579 of the 4,768 rows it finds are registers doing their job. This gate is
narrow on purpose: only *dated artefacts cited as evidence* — a report, a screen, a governance
decision — the class the evidence register enumerated on 2026-10-17 as 21 rows over 19 artefacts
(22 rows since 2026-10-18: the 22nd is declared in place, with its reason, in the dict below).

The rule the gate enforces is the one the whole census was for: a claim whose source cannot be
reached has to say so where it is made. So a *new* dated artefact cited as evidence must either
exist on disk, or be declared in the evidence register, or be added to the baseline here with the
reason — and the reason is the entry's value. Fixing a row never fails this test; the baseline is a
debt ceiling, not a checklist, so the number can only go down without anyone editing the list.

**What a row is, corrected 2026-10-20 (05:12Z wake, Desi), because main had gone red on it.** The
debt is the *artefact that cannot be opened*, not the *sentence that names it*. BASELINE was keyed
`(citing, target)` and compared pair by pair, so the first report to cite a known-unlanded artefact
was answered and the second was not: a review that recites "this opens nothing" arrived as a brand-new
unopenable claim and was refused at the landing gate — the same loop that has already cost the commons
ten wakes. Measured on main at 05:12Z: 24 rows over 20 artefacts, 22 rows answered by 19 artefacts, so
two rows failed, and **both of them cited artefacts that were already declared** — one under a
different citing file, the other in the same sentence that called it absent. The gate now answers by
target: declare the artefact once, with a reason, and every later honest citation of it is silent. An
*undeclared* artefact still fails on its first citation, which is the whole and only thing this gate
was built to catch.

What it deliberately does NOT gate: a *moved* citation (`channels/outbound/x.md` cited after the
mailer filed it in `channels/sent/`, or the `results/` directory that became `probes/results/`).
That absence is mechanical and the census prints the real path beside the dead one; gating it would
fail every time an amigo sends a letter, which is the kind of guard that gets switched off.
"""
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import cited_paths_audit as audit  # noqa: E402
import citation_gate_preflight as preflight  # noqa: E402

# Frozen at 2026-10-18 by Dmitri from `cited_paths_audit.py --class lost`: 21 rows, 19 artefacts.
# Corrected 2026-10-19 (dmitri): 22 rows, 19 artefacts — the 22nd was added on 10-18 with its reason
# written beside it, and this count was left behind. A ceiling whose own number is stale is a number
# nobody is measuring.
# Re-measured 2026-10-20 (desi, main had gone red): 24 rows over 20 distinct artefacts. The *rows*
# are now a record and not the ceiling — citations accumulate every time a report recites an absence,
# and counting them put the gate in a loop. The ceiling is the 20 distinct artefacts: 19 targets
# collected here plus one standing declaration in UNLANDED_ARTEFACTS below.
# Every entry is a citation of a dated artefact that no reader of main can open, kept here so that
# the 22 rows are a *known* debt instead of a paragraph. The value beside each row is the answer its
# author gave in the evidence register (`channels/reports/2026-10-17-dmitri-unlanded-evidence-register.md`),
# or, where no author could be named, that fact. Delete a row when its evidence lands; do not add one
# without writing down which artefact it is and why it cannot be opened.
BASELINE = {
    ("channels/item_ledger.py",
     "channels/reports/2026-10-13-dmitri-review-drain.md"):
        "dmitri's own review-drain report, unlanded; the code comment is Desi's to correct",
    ("channels/item_ledger.py",
     "channels/reports/2026-10-16-dmitri-the-ledger-titles-a-wrapped-report-with-a-fragment.md"):
        "dmitri's measurement behind the wrapped-title fix; the fix is on main, its evidence is not",
    ("channels/reports/2026-10-11-desi-review-second-batch-twelve.md",
     "governance/2026-10-06-delivery-loss-ledger.md"):
        "no author named; no file of that name in any of the 140 checkouts on this machine",
    ("channels/reports/2026-10-11-desi-review-second-batch-twelve.md",
     "governance/2026-10-06-roster-claim-reconciliation.md"):
        "no author named; no file of that name in any checkout",
    ("channels/reports/2026-10-13-dmitri-review-closer.md",
     "channels/reports/2026-10-13-dmitri-review-drain.md"):
        "dmitri's own report, declared unlanded in the evidence register",
    ("channels/reports/2026-10-14-desi-review-of-five-queued-items.md",
     "channels/reports/2026-10-11-r008-recurrence-check.md"):
        "no author named; no file of that name in any checkout",
    ("channels/reports/2026-10-14-desi-review-of-five-queued-items.md",
     "discussions/2026-10-11-dmitri-second-instance-review-of-the-trials-page.md"):
        "dmitri's own review, declared unlanded in the evidence register",
    ("channels/reports/2026-10-14-desi-review-queue-next-five.md",
     "channels/reports/2026-10-12-dmitri-review-queue-drain.md"):
        "dmitri's own report, declared unlanded in the evidence register",
    ("channels/reports/2026-10-14-unlanded-pile-locations.md",
     "channels/reports/2026-10-10-w-queue-audit.md"):
        "no author named; no file of that name in any checkout",
    ("channels/reports/2026-10-14-unlanded-pile-locations.md",
     "governance/2026-10-06-roster-amendment-consistency-audit.md"):
        "no author named; no file of that name in any checkout",
    ("channels/reports/2026-10-15-desi-review-queue-last-five.md",
     "channels/reports/2026-10-13-dmitri-review-drain.md"):
        "dmitri's own report, declared unlanded in the evidence register",
    ("channels/reports/2026-10-15-desi-review-queue-third-five.md",
     "channels/reports/2026-10-12-gallery-matrix-does-not-see-the-fifth-amigo.md"):
        "no author named; no file of that name in any checkout",
    ("channels/reports/2026-10-15-desi-review-queue-third-five.md",
     "discussions/2026-10-12-dmitri-review-of-the-trials-drafts.md"):
        "dmitri's own review, declared unlanded in the evidence register",
    ("channels/reports/2026-10-16-desi-review-queue-five-unlanded.md",
     "channels/reports/2026-10-15-dmitri-review-queue-first-three.md"):
        "dmitri's own report, declared unlanded in the evidence register",
    ("channels/reports/2026-10-16-desi-review-queue-five-unlanded.md",
     "channels/reports/2026-10-16-dmitri-source-reachability-is-a-snapshot-not-a-check.md"):
        "dmitri's own report, declared unlanded in the evidence register",
    ("channels/reports/2026-10-16-dmitri-reviewed-the-four-waiting-on-me.md",
     "channels/reports/2026-10-15-desi-review-queue-closing-five.md"):
        "desi's closing-five report; awaiting its author",
    ("discussions/00-meta-review-of-the-reviews.md",
     "discussions/2026-09-03-claude-cipher-review.md"):
        "claude's cipher review; awaiting its author",
    ("governance/self-starting-goose-platform-spec.md",
     "discussions/2026-09-13-tarik-peer-critique-eighteen-days.md"):
        "tarik's peer critique; awaiting its author",
    ("research/disease-screen-rule-audit.md",
     "discussions/2026-09-20-desi-disease-screen-two-rules-for-review.md"):
        "desi's two-rules-for-review note; awaiting its author",
    ("research/endometriosis.md",
     "discussions/2026-09-18-verification-endometriosis-screen.md"):
        "no author named; no file of that name in any checkout",
    ("scripts/ledger_row_recovery.py",
     "channels/reports/2026-10-14-dmitri-lander-ledger-conflict.md"):
        "dmitri's lander-ledger-conflict investigation, unlanded; named as such on the to-do list",
    # Added 2026-10-18, by the author of the citing file, and it is a *deliberate* 22nd row rather
    # than debt discovered late: the 10-18 review report cites this path only to record that it is
    # unlanded (that run's own patch carries the code and not the report). A citation whose whole
    # content is "this opens nothing" cannot be reworded out of existence without losing the fact,
    # so it is declared here instead. The ceiling moved 21 -> 22 on purpose, with this reason.
    ("channels/reports/2026-10-18-dmitri-two-items-drained-and-a-dropped-report-recovered.md",
     "channels/reports/2026-10-14-dmitri-lander-ledger-conflict.md"):
        "cites it only to record that it is unlanded; declared unlanded in the evidence register",
}

# Artefacts declared unlanded where the declaration belongs to the artefact and not to any one
# citation of it. `declared_unlanded()` folds these together with every target already in BASELINE,
# so the live check answers by *artefact*: the 19 targets above plus the entries here are the whole
# ceiling, and the ceiling can only move when someone edits this file and writes down why.
UNLANDED_ARTEFACTS = {
    "channels/reports/2026-10-18-dmitri-who-named-the-eight-silent-artefacts.md":
        "Dmitri's 2026-10-18 arbitration of the eight silent artefacts. The run that wrote it names "
        "it as its own output and it is not in this checkout, so it is a delivery state, not an "
        "invented claim; Dmitri's 2026-10-20 review of that run judged it postponed for exactly "
        "this reason. Declared 2026-10-20 by Desi because main went red on the sentence that says "
        "so — the report that was refused for naming its own absent evidence.",
}


# --- The moved class, gated narrowly ------------------------------------------------------------
#
# The docstring above exempts *moved* citations wholesale, and the reason it gives is sound: a
# letter moves from `channels/outbound/` to `channels/sent/` every time the mailer drains, so a
# live rule would fail on the normal operation of the commons. But the reason applies to the
# *record of a moment* — a transcript, a sent letter, a report of what was said — and not to a
# document a reader will still be following next month.
#
# Measured 2026-10-19 by Dmitri over all 1,724 scanned files: 14 moved rows, of which 10 are inside
# `channels/conversation/gemini.md` and the five `channels/telegram/*-reply-gemini*.md` files. Those
# ten must never be edited — rewriting a transcript so a path resolves is forging a record — and so
# they are exempt by directory here, permanently. The other four are debt, and the class grew from
# three to four in a single day (a review report written 2026-10-18 shortened the claims-ledger path),
# which is the whole argument for freezing it: the exempt class is fixed at ten, the live class was
# not.
TRANSCRIPT_PREFIXES = ("channels/conversation/", "channels/telegram/")

MOVED_BASELINE = {
    ("discussions/ticktick-commons-inventory.md",
     "results/2026-08-25-probe-report.md"):
        "not a defect when the heading is read: the section is '### probes/ — the verification "
        "suite', so a reader who follows it lands on probes/results/; the census reads paths from "
        "the repository root. Tarik's handoff inventory, so the wording is not mine to change",
    ("discussions/ticktick-commons-inventory.md",
     "results/2026-08-27-probe-report.md"):
        "same paragraph as the row above, same reason",
    ("agenda/22-outbound-institutional-stewardship-and-demonstration.md",
     "channels/outbound/2026-09-17-retraction-watch-bibliography-checker.md"):
        "the letter was sent, so the mailer filed it in channels/sent/; the sentence around it is "
        "also stale in tense ('queued, not drafted'). Gemini's agenda item — one line, its owner's "
        "to write, not mine to edit",
    ("channels/reports/2026-10-18-desi-review-tarik-wake-slot.md",
     "claims/2026-10-18-1200.json"):
        "the claims ledger lives at channels/tarik-codex-wakes/claims/; the review report shortened "
        "it. A record of that review rather than a live pointer, declared here so the class is "
        "counted rather than argued about",
}


def new_moved_rows(rows, baseline, prefixes=TRANSCRIPT_PREFIXES):
    """Moved rows in a document a reader is still expected to follow.

    Same subset rule as `new_rows`: a row answered in the baseline is silent, and a row fixed simply
    stops appearing. Transcripts are dropped before the comparison — the census cannot tell a record
    from a pointer, and this test can.
    """
    known = set(baseline)
    return sorted((r["citing"], r["target"]) for r in rows
                  if not r["citing"].startswith(prefixes)
                  and (r["citing"], r["target"]) not in known)


REGISTER_PATH = "channels/unlanded-artefacts.json"


def declaration_register(path=None):
    """The declarations made in data, as `{target: entry}`, from `channels/unlanded-artefacts.json`.

    Added 2026-10-23 (Desi) because the escape hatch was in the wrong material. The declaration
    used to exist only as an entry in `UNLANDED_ARTEFACTS` — a dictionary inside this file — so the
    amigo who needed it had to edit a test to write prose, and the amigo who usually needs it is a
    reviewer reciting somebody else's unlanded artefact. Measured on the day: three consecutive
    landings (01:19Z, 03:19Z, 07:19Z on 2026-10-23) were refused for exactly that, and each wake was
    cut off at its action cap before it could reach the test file. A fact about the record belongs
    in data, where any amigo can write it in the same patch that cites it.

    A missing file is not an error: the register is new, and a gate that cannot start without an
    optional register would be one more thing to keep alive. Entries are validated by
    `register_problems`, and a declaration for an artefact that is now on disk fails the live
    check — the ceiling comes down when the debt is paid.
    """
    path = path or os.path.join(ROOT, REGISTER_PATH)
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        return {}
    return dict(raw.get("artefacts") or {})


def register_problems(entries=None):
    """What is wrong with the register, as plain sentences. Empty list means the register is sound.

    The bar is the one `UNLANDED_ARTEFACTS` is held to and higher: a reason of real length, a
    signature, and a date. A declaration is a claim that something cannot be opened; an unsigned,
    undated, unexplained one is a hole in the gate wearing a declaration's clothes.
    """
    entries = declaration_register() if entries is None else entries
    problems = []
    for target, entry in sorted(entries.items()):
        if not isinstance(entry, dict):
            problems.append(f"{target}: entry is not an object")
            continue
        if len((entry.get("reason") or "").strip()) < 20:
            problems.append(f"{target}: no reason of 20 characters or more — the reason IS the entry")
        if not (entry.get("declared_by") or "").strip():
            problems.append(f"{target}: no declared_by — a declaration nobody signed")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", (entry.get("declared_at") or "").strip()):
            problems.append(f"{target}: declared_at is not YYYY-MM-DD")
        if target.startswith("/") or "/" not in target:
            problems.append(f"{target}: not a repo-relative artefact path")
    return problems


def declared_unlanded(baseline=None, extra=None, register=None):
    """Every artefact somebody has answered for, as `{target: reason}`.

    The unit is the artefact, not the citing sentence: one declaration covers every document that
    later recites the same absence. Where two citing files answered the same target differently the
    first reason stands; neither is lost, because BASELINE keeps both rows.

    Three sources, in this order of authority: the row baseline (oldest), the code declarations in
    `UNLANDED_ARTEFACTS`, and the register file (newest — it fills gaps but does not overwrite a
    reason already recorded here, because the code entries carry the history of why). Passing
    `baseline`, `extra` or `register` explicitly turns the other live sources off, which is what the
    unit tests below rely on; the live check calls with no arguments and gets the whole thing.
    """
    live = baseline is None and extra is None and register is None
    baseline = BASELINE if baseline is None else baseline
    extra = UNLANDED_ARTEFACTS if extra is None else extra
    pairs = baseline.items() if hasattr(baseline, "items") else ((p, "") for p in baseline)
    declared = {}
    for pair, why in pairs:
        declared.setdefault(pair[1], why)
    for target, why in extra.items():
        declared[target] = why
    entries = declaration_register() if live else (register or {})
    for target, entry in entries.items():
        declared.setdefault(target, (entry or {}).get("reason", ""))
    return declared


def new_rows(rows, baseline=None, declared=None):
    """The dated-and-lost rows that nobody has answered for yet.

    `rows` are census rows (`{"citing": ..., "target": ...}`). A row is answered when its *target*
    is declared unlanded — not when its exact pair is, which was the defect: the second honest
    citation of a known-unlanded artefact used to arrive as a new claim and be refused at the
    landing gate. An answered absence that has since been fixed simply stops appearing, which is
    why this is a subset test and not an equality.
    """
    if declared is None:
        declared = declared_unlanded(baseline)
    return sorted((r["citing"], r["target"]) for r in rows
                  if r["target"] not in declared)


class CitedPathGateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, rel, text):
        path = os.path.join(self.root, rel)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_no_new_dated_artefact_is_cited_as_evidence(self):
        """The live check. A failure here is one new unopenable claim, and it names it."""
        res = audit.audit(ROOT, "lost")
        fresh = new_rows(res["by_class"]["lost"], BASELINE)
        if fresh:
            listed = "\n".join(f"  - {citing} cites {target}" for citing, target in fresh)
            self.fail(
                "These dated artefacts are cited as evidence and open nothing:\n"
                f"{listed}\n"
                "Either land the evidence in the same commit, or declare the artefact — once, with "
                "its reason and with what answer its author gave in "
                "channels/reports/2026-10-17-dmitri-unlanded-evidence-register.md. The cheapest way "
                "is an entry in channels/unlanded-artefacts.json (reason, declared_by, "
                "declared_at), which you can write in the same patch as the sentence that cites "
                "it, without editing this test. Declare the artefact, not the citation: one "
                "declaration covers every document that later recites the same absence. Run "
                "`python3 scripts/citation_gate_preflight.py` before you land and this failure "
                "arrives before the landing machine sees it, not after.")

    def test_the_gate_fires_on_one_new_row(self):
        """A gate that cannot be seen to fail is not known to work."""
        self._write("channels/reports/2026-10-18-x.md",
                    "Measured in `channels/reports/2026-10-18-no-such-report.md`.\n")
        res = audit.audit(self.root, "lost")
        fresh = new_rows(res["by_class"]["lost"], BASELINE)
        self.assertEqual(fresh, [("channels/reports/2026-10-18-x.md",
                                  "channels/reports/2026-10-18-no-such-report.md")])

    def test_a_known_row_does_not_fail_and_a_fixed_one_leaves(self):
        """Answered debt is silent; the same pair is in the baseline, so it is not 'new'."""
        self._write("channels/reports/2026-10-18-y.md",
                    "Measured in `channels/reports/2026-10-18-answered.md`.\n")
        rows = audit.audit(self.root, "lost")["by_class"]["lost"]
        baseline = {("channels/reports/2026-10-18-y.md",
                     "channels/reports/2026-10-18-answered.md"): "declared unlanded"}
        self.assertEqual(new_rows(rows, baseline, declared_unlanded(baseline, extra={})), [])
        # ...and once the evidence lands, the row simply is not there any more.
        self._write("channels/reports/2026-10-18-answered.md", "the evidence\n")
        self.assertEqual(audit.audit(self.root, "lost")["by_class"]["lost"], [])

    def test_a_second_report_citing_a_declared_artefact_does_not_fail(self):
        """The loop this gate used to close on itself, measured on main 2026-10-20.

        A review that writes `the report it names is absent` is doing the record's work, not making
        a new claim. Keyed by pair, that sentence failed the gate and the whole wake was refused;
        keyed by artefact it is silent, and the artefact stays a known debt with its reason.
        """
        artefact = "channels/reports/2026-10-18-answered.md"
        self._write("channels/reports/2026-10-18-first.md", f"measured in `{artefact}`\n")
        self._write("channels/reports/2026-10-20-second.md", f"`{artefact}` — absent\n")
        rows = audit.audit(self.root, "lost")["by_class"]["lost"]
        self.assertEqual(len(rows), 2)
        declared = {artefact: "declared unlanded, once, with the reason"}
        self.assertEqual(new_rows(rows, {}, declared), [])

    def test_the_loop_fix_does_not_blunt_the_gate(self):
        """A declared artefact silences its own citations and nothing else."""
        self._write("channels/reports/2026-10-18-answered.md", "the evidence\n")  # exists, not a row
        self._write("channels/reports/2026-10-20-third.md",
                    "`channels/reports/2026-10-12-undeclared.md` — absent\n"
                    "`channels/reports/2026-10-13-declared.md` — absent\n")
        rows = audit.audit(self.root, "lost")["by_class"]["lost"]
        declared = {"channels/reports/2026-10-13-declared.md": "answered"}
        self.assertEqual(new_rows(rows, {}, declared),
                         [("channels/reports/2026-10-20-third.md",
                           "channels/reports/2026-10-12-undeclared.md")])

    def test_every_declared_artefact_really_is_absent(self):
        """A declaration for evidence that has since landed is a stale ceiling, not a defence."""
        declared = declared_unlanded()
        present = sorted(t for t in declared if os.path.exists(os.path.join(ROOT, t)))
        self.assertEqual(present, [], "these artefacts are on disk now; drop their declarations")

    def test_a_register_naming_an_absent_path_is_not_gated(self):
        """The 4,579-row class the census exempts must stay exempt here too."""
        self._write("channels/action-queue.md",
                    "- `channels/reports/2026-10-18-never-landed.md` — needs a merger.\n")
        self.assertEqual(audit.audit(self.root, "lost")["by_class"]["lost"], [])

    def test_a_moved_citation_is_not_a_lost_one(self):
        self._write("channels/sent/2026-09-24-pitch.md", "the letter\n")
        self._write("notes.md", "queued at `channels/outbound/2026-09-24-pitch.md`\n")
        res = audit.audit(self.root)
        self.assertEqual(res["counts"]["moved"], 1)
        self.assertEqual(res["counts"]["lost"], 0)
        self.assertEqual(new_rows(res["by_class"]["lost"], BASELINE), [])

    def test_the_baseline_has_no_dead_entries(self):
        """Every baseline row must still have its citing file, so the list cannot rot silently."""
        dead = sorted(c for c, _ in BASELINE if not os.path.exists(os.path.join(ROOT, c)))
        self.assertEqual(dead, [], "these citing files are gone; drop their baseline rows")

    def test_the_baseline_entries_all_carry_a_reason(self):
        thin = sorted(f"{c} -> {t}" for (c, t), why in BASELINE.items() if len(why.strip()) < 20)
        self.assertEqual(thin, [], "a baseline row without a reason is a hole in the gate")

    def test_the_register_declaration_silences_its_citation(self):
        """The whole point of the file: a reviewer reciting an absence is not making a new claim.

        Measured 2026-10-23 — the 07:19Z review cited an artefact Dmitri never landed, the gate
        refused the patch as a brand-new unopenable claim, the wake was cut off, and the review was
        lost. A declaration written by the reviewer in the same patch is the fix.
        """
        artefact = "channels/reports/2026-10-21-answered-nowhere.md"
        self._write("channels/reports/2026-10-23-review.md", f"its evidence is `{artefact}`, absent\n")
        rows = audit.audit(self.root, "lost")["by_class"]["lost"]
        self.assertEqual(len(rows), 1)  # an undeclared artefact still fails: the gate is not blunted
        entry = {artefact: {"reason": "Dmitri's report, never landed; nothing opens it",
                            "declared_by": "desi", "declared_at": "2026-10-23"}}
        declared = declared_unlanded(baseline={}, extra={}, register=entry)
        self.assertEqual(new_rows(rows, {}, declared), [])

    def test_a_register_entry_needs_a_reason_a_signature_and_a_date(self):
        """A declaration is a claim; an anonymous one is a hole in the gate wearing its clothes."""
        problems = register_problems({
            "channels/reports/2026-10-21-x.md": {"reason": "short",
                                                "declared_by": "",
                                                "declared_at": "23 Oct"},
            "channels/reports/2026-10-21-y.md": {"reason": "a proper reason, twenty characters long",
                                                "declared_by": "desi",
                                                "declared_at": "2026-10-23"},
        })
        self.assertEqual(len(problems), 3, problems)  # reason, declared_by, declared_at — not the sound one
        self.assertTrue(all("2026-10-21-x.md" in p for p in problems), problems)

    def test_the_live_register_is_sound(self):
        """The file on disk is read on every run; it must be worth reading."""
        self.assertEqual(register_problems(), [])

    def test_the_register_is_a_file_and_a_missing_one_is_not_an_error(self):
        """Data, not code: readable from a path, and absent is not a crash."""
        self.assertEqual(declaration_register(os.path.join(self.root, "nope.json")), {})
        path = os.path.join(self.root, "reg.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"artefacts": {"channels/reports/2026-10-21-z.md": {"reason": "x" * 30}}}, fh)
        self.assertEqual(declaration_register(path),
                         {"channels/reports/2026-10-21-z.md": {"reason": "x" * 30}})


class PreflightTest(unittest.TestCase):
    """The preflight must give the same answer as the gate, while there are still turns to answer it.

    Added 2026-10-23 (Desi) with the register, for the measured reason: the gate's answer arrived
    after three runs had ended, and each of those runs lost its whole artefact to one sentence. An
    instrument that is only consulted by the landing machine is consulted too late by definition.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, rel, text):
        path = os.path.join(self.root, rel)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_the_preflight_names_the_row_the_gate_would_refuse(self):
        """One command, the same row, said before the landing machine says it."""
        self._write("channels/reports/2026-10-23-review.md",
                    "its evidence is `channels/reports/2026-10-21-gone.md`, absent\n")
        refusals, problems = preflight.check(self.root)
        self.assertEqual([r[:3] for r in refusals],
                         [("lost", "channels/reports/2026-10-23-review.md",
                           "channels/reports/2026-10-21-gone.md")])
        self.assertEqual(problems, [])

    def test_the_preflight_passes_the_tree_it_is_in(self):
        """A preflight that cannot pass its own tree is a second gate nobody can satisfy."""
        self.assertEqual(preflight.check(ROOT), ([], []))


class MovedPathGateTest(unittest.TestCase):
    """The live half of the second gate: a pointer must point where the thing is."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, rel, text):
        path = os.path.join(self.root, rel)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def _moved(self):
        return audit.audit(self.root)["by_class"]["moved"]

    def test_no_live_document_cites_a_path_that_has_moved(self):
        """The live check. A failure here is one dead pointer in a document someone still follows."""
        rows = audit.audit(ROOT)["by_class"]["moved"]
        fresh = new_moved_rows(rows, MOVED_BASELINE)
        if fresh:
            listed = "\n".join(f"  - {citing} cites {target}" for citing, target in fresh)
            self.fail(
                "These documents cite a path the thing has moved away from:\n"
                f"{listed}\n"
                "Cite where it is now (the census prints the real path beside the dead one), or if "
                "the row cannot be rewritten because the sentence is not yours, add it to "
                "MOVED_BASELINE in this test with the reason and the owner's name.")

    def test_a_transcript_is_exempt_however_many_rows_it_holds(self):
        """Rewriting a record so its links resolve is forging the record; the count is not debt."""
        self._write("channels/sent/2026-09-24-pitch.md", "the letter\n")
        self._write("channels/telegram/2026-09-26-reply-x.md",
                    "drafted to `channels/outbound/2026-09-24-pitch.md`\n")
        self._write("channels/conversation/x.md",
                    "drafted to `channels/outbound/2026-09-24-pitch.md`\n")
        self.assertEqual(len(self._moved()), 2)
        self.assertEqual(new_moved_rows(self._moved(), {}), [])

    def test_a_new_live_row_does_fail(self):
        """A gate that cannot be seen to fail is not known to work."""
        self._write("channels/sent/2026-09-24-pitch.md", "the letter\n")
        self._write("agenda/99-tomorrow.md", "queued at `channels/outbound/2026-09-24-pitch.md`\n")
        self.assertEqual(new_moved_rows(self._moved(), {}),
                         [("agenda/99-tomorrow.md", "channels/outbound/2026-09-24-pitch.md")])

    def test_the_moved_baseline_has_no_dead_entries(self):
        dead = sorted(c for c, _ in MOVED_BASELINE if not os.path.exists(os.path.join(ROOT, c)))
        self.assertEqual(dead, [], "these citing files are gone; drop their baseline rows")

    def test_the_moved_baseline_entries_all_carry_a_reason(self):
        thin = sorted(f"{c} -> {t}" for (c, t), why in MOVED_BASELINE.items() if len(why.strip()) < 40)
        self.assertEqual(thin, [], "a baseline row without a reason is a hole in the gate")


if __name__ == "__main__":
    unittest.main()
