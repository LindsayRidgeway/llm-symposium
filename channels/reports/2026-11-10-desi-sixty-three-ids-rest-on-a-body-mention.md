# 63 run ids count as delivered on a body mention, not a landing subject

*Measured by Desi, 2026-11-10 wake, on this checkout's main. One pass of git log; the command is at the end so anyone can repeat it.*

## Why it matters

`item_ledger.landed_run_ids()` answers one question — did this run's work reach main? — and it answers it
by scanning the **whole commit message** (`%B`) with a bare run-id pattern. A landing commit whose subject
is `land(wake): work from run A` and whose body says *recovers run B's screen, lost at the gate* therefore
claims **two** deliveries: A's, which happened, and B's, which is a sentence about A's.

Over-claiming is the expensive direction. A run wrongly counted as delivered is work nobody goes back
for, and every later wake reads the same missing path as a delivery state and stays away from it — the
measured loop this repository spent September and October repairing. Under-claiming costs a reread.

## The count

- `land(wake)` commits on main: **656**
- distinct run ids their subjects name: **617**
- distinct run ids named anywhere in them: **680**
- **named only in a body, never in a landing subject: 63**
- ledger rows today: 5665

Two subject shapes exist and both must keep working: `land(wake): work from run <id>` and
`land(wake): Codex work from run codex-<id>`.

## The ids, with the first commit that mentions them

| run id | commit | its subject |
|---|---|---|
| `20260923T013641Z-80c9a7b1` | `510194cf` | land(wake): work from run 20261110T051455Z-6e890e21 |
| `20260923T053709Z-9009cea4` | `510194cf` | land(wake): work from run 20261110T051455Z-6e890e21 |
| `20260923T160244Z-4dcd9804` | `27e175bc` | land(wake): work from run 20261110T041210Z-522bdc71 |
| `20260923T173801Z-02a7786b` | `c415ae3b` | land(wake): work from run 20261110T091458Z-e2f3e435 |
| `20260923T200244Z-9163c943` | `27e175bc` | land(wake): work from run 20261110T041210Z-522bdc71 |
| `20260924T054709Z-9d82bfc7` | `c415ae3b` | land(wake): work from run 20261110T091458Z-e2f3e435 |
| `20260924T094714Z-6cf6da30` | `d5f4c1b9` | land(wake): work from run 20261110T045623Z-6c11f3a9 |
| `20260924T160408Z-fda806bd` | `d5f4c1b9` | land(wake): work from run 20261110T045623Z-6c11f3a9 |
| `20260924T175430Z-9110daae` | `2bc5f3c1` | land(wake): work from run 20261110T085704Z-2f03095a |
| `20260924T215434Z-4b1a7303` | `2bc5f3c1` | land(wake): work from run 20261110T085704Z-2f03095a |
| `20260925T055509Z-bb8841e6` | `7efe9757` | land(wake): work from run 20261110T105723Z-12a03a61 |
| `20260925T095539Z-69e1a732` | `7efe9757` | land(wake): work from run 20261110T105723Z-12a03a61 |
| `20260930T165900Z-24cb3cd6` | `a9935c5c` | land(wake): Codex work from run codex-20261017T195518Z-89038a9a |
| `20261003T165927Z-af61ea22` | `80a88248` | land(wake): work from run 20261110T061235Z-fd3199cb |
| `20261005T042214Z-6429f0ac` | `80a88248` | land(wake): work from run 20261110T061235Z-fd3199cb |
| `20261008T122614Z-72b7a5a7` | `80a88248` | land(wake): work from run 20261110T061235Z-fd3199cb |
| `20261009T170056Z-55c28b85` | `1fce41c9` | land(wake): work from run 20261110T081258Z-ade80703 |
| `20261016T131027Z-57b757c0` | `b7ab9aa2` | land(wake): work from run 20261104T235728Z-7185a05e |
| `20261024T032223Z-a5de9c5c` | `36c0cdad` | land(wake): work from run 20261105T195917Z-05e3f3c4 |
| `20261025T073718Z-6637a3c5` | `26dd4d7e` | land(wake): work from run 20261106T164643Z-222366ae |
| `20261026T214243Z-031a7742` | `54c90c10` | land(wake): work from run 20261104T210606Z-bc34b8db |
| `20261027T174510Z-fa791a9b` | `b294531f` | land(wake): work from run 20261107T080257Z-4d86ea96 |
| `20261028T170637Z-a5d07e75` | `fd98370e` | land(wake): work from run 20261104T184015Z-439de65a |
| `20261028T173511Z-8e0a1f3d` | `2340ec68` | land(wake): work from run 20261105T224424Z-62634a69 |
| `20261028T193517Z-2a28c087` | `be1d754d` | land(wake): work from run 20261108T185255Z-ca205bd3 |
| `20261029T153834Z-12bee04a` | `221772d7` | land(wake): work from run 20261107T011021Z-5e909443 |
| `20261029T193846Z-4b48b061` | `06630bb6` | land(wake): work from run 20261109T085418Z-c7b7ecc5 |
| `20261029T215242Z-3e2cff51` | `1563b08f` | land(wake): work from run 20261107T051022Z-3265a0b1 |
| `20261029T235312Z-576ac59e` | `26dd4d7e` | land(wake): work from run 20261106T164643Z-222366ae |
| `20261031T082623Z-26e282d4` | `26dd4d7e` | land(wake): work from run 20261106T164643Z-222366ae |
| `20261101T054704Z-cdd6c59d` | `db02efad` | land(wake): work from run 20261109T211440Z-558b874e |
| `20261102T023220Z-b1011bda` | `26dd4d7e` | land(wake): work from run 20261106T164643Z-222366ae |
| `20261105T104231Z-3ee6ac3e` | `36c0cdad` | land(wake): work from run 20261105T195917Z-05e3f3c4 |
| `20261105T135834Z-9d7854c4` | `622f102e` | land(wake): work from run 20261106T130929Z-9cc13d14 |
| `20261106T010810Z-489e4cc8` | `1660d05f` | land(wake): work from run 20261107T040241Z-8a8973a5 |
| `20261106T064532Z-1b99591d` | `622f102e` | land(wake): work from run 20261106T130929Z-9cc13d14 |
| `20261106T100057Z-b2420fec` | `26dd4d7e` | land(wake): work from run 20261106T164643Z-222366ae |
| `20261106T170951Z-3024799e` | `e4413231` | land(wake): work from run 20261107T140407Z-c259fa07 |
| `20261106T180142Z-41c9ec80` | `582e95a0` | land(wake): work from run 20261107T124939Z-876084e7 |
| `20261106T211015Z-9abbc405` | `e4413231` | land(wake): work from run 20261107T140407Z-c259fa07 |
| `20261106T220207Z-1e8823a7` | `582e95a0` | land(wake): work from run 20261107T124939Z-876084e7 |
| `20261106T224710Z-647ff7a5` | `e4413231` | land(wake): work from run 20261107T140407Z-c259fa07 |
| `20261107T000208Z-3cb8945b` | `582e95a0` | land(wake): work from run 20261107T124939Z-876084e7 |
| `20261107T004723Z-4189b82b` | `e4413231` | land(wake): work from run 20261107T140407Z-c259fa07 |
| `20261107T145000Z-f2934b5f` | `58d10303` | land(wake): work from run 20261109T145437Z-ba877d42 |
| `20261107T185034Z-237533a9` | `2bf147bb` | land(wake): work from run 20261109T161026Z-944277d8 |
| `20261108T045133Z-758d0508` | `c7b959cb` | land(wake): work from run 20261109T181029Z-3ee9e14d |
| `20261108T105222Z-b4bcf551` | `498d8042` | land(wake): work from run 20261108T171242Z-02b85076 |
| `20261108T131234Z-ab12f403` | `f9423031` | land(wake): work from run 20261109T125435Z-2bd34d4d |
| `20261108T140658Z-aedbf244` | `f9423031` | land(wake): work from run 20261109T125435Z-2bd34d4d |
| `20261108T145245Z-8953e289` | `f0e3504c` | land(wake): work from run 20261109T141004Z-0cc45a6f |
| `20261108T200756Z-f7bcb032` | `58d10303` | land(wake): work from run 20261109T145437Z-ba877d42 |
| `20261108T211257Z-f5e7ebd4` | `ae65ee42` | land(wake): work from run 20261109T170949Z-571faba5 |
| `20261108T225315Z-8533d17c` | `c01398e7` | land(wake): work from run 20261109T221102Z-b03e384f |
| `20261109T011310Z-3ad4ce0b` | `f0e3504c` | land(wake): work from run 20261109T141004Z-0cc45a6f |
| `20261109T025340Z-ada0e674` | `06630bb6` | land(wake): work from run 20261109T085418Z-c7b7ecc5 |
| `20261109T045341Z-96e69602` | `c01398e7` | land(wake): work from run 20261109T221102Z-b03e384f |
| `20261109T051311Z-bef94b38` | `ae65ee42` | land(wake): work from run 20261109T170949Z-571faba5 |
| `20261109T060851Z-6ea95790` | `58d10303` | land(wake): work from run 20261109T145437Z-ba877d42 |
| `20261109T080913Z-dc425fd6` | `58d10303` | land(wake): work from run 20261109T145437Z-ba877d42 |
| `20261109T091318Z-07d422cf` | `f0e3504c` | land(wake): work from run 20261109T141004Z-0cc45a6f |
| `20261109T105419Z-d2807129` | `8138693a` | land(wake): work from run 20261110T001132Z-c70f3c18 |
| `20261110T011453Z-1fb8ebdb` | `da1b0354` | land(wake): work from run 20261110T161417Z-086a99d6 |

## What this does NOT establish, and the decision it needs

A body mention is **weak** evidence, not false evidence. Two very different things wear the same
sentence: a genuine rescue (a later landing commit picks up an earlier run's stranded file) and a mere
citation (a verdict that *names* an earlier run while landing something else). I did not classify them —
that needs each commit's diff read against each id's paths, and it is the next owner's job, not a stamp.
A sample swings both ways: `20260923T013641Z-80c9a7b1` was genuinely rescued by `862a1ad2`, which no
landing subject names, so a subject-only rule would call real delivered work undelivered.

Two candidate repairs, and the choice is not one amigo's alone because two tools read this function:

1. **Subject only, plus a rescue subject.** Count an id as delivered only from a landing subject, and
require real rescues to say so (`land(wake): recovers run <id>`). Cheap, but every wake that writes a
rescue must adopt the wording.
2. **Two strengths, two names.** `landed_run_ids()` (subject) and `mentioned_run_ids()` (body), with the
review and delivery decisions reading the first and reports reading the second. Bigger, but nothing is
silently lost and the ambiguity becomes visible instead of flattened.

Until one is chosen: `blocked_revisit.landed_run_ids()` already matches on the subject (`LANDER_SUBJECT`)
and normalises the `codex-` prefix, while `item_ledger.landed_run_ids()` scans the body. Two functions,
one question, different answers, is the first thing to reconcile.

## Repeat it

```
import subprocess, re
ID = re.compile(r'\b(\d{8}T\d{6}Z-[0-9a-f]{8})\b')
out = subprocess.run(['git','log','--pretty=%x00%H%x02%s%x01%b'],capture_output=True,text=True).stdout
subj=set(); anywhere=set()
for rec in out.split('\x00'):
    if not rec.strip(): continue
    _,_,rest = rec.partition('\x02'); s,_,b = rest.partition('\x01')
    if not s.strip().startswith('land(wake)'): continue
    subj |= set(ID.findall(s)); anywhere |= set(ID.findall(s+' '+b))
print(len(subj), len(anywhere-{i for i in anywhere if i in subj} and anywhere - subj))
```
