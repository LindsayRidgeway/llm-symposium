# Imaging the nine cards — the plan, and the two things the plan does not have

*Desi, 2026-11-21 evening. Written the hour the founder reported the box open: nine SanDisk EXTREME
64 GB cards (order 112-6317894-9355469) in hand, four rover-class and five lander-class to be made.*

This file is the procedure, so that nine cards written over several sessions are nine cards written
one way. It is also the record of two gaps, because a plan that pretends to be complete is how a
session ends up telling him a card is ready when it is only blank.

## 1. What was checked tonight, and what is not on this Mac

Measured, not remembered:

| thing | state 2026-11-21 ~18:30 |
|---|---|
| the nine cards | **in hand**, per the founder. No card is in a reader; `diskutil list` shows no external disk. |
| `LanderPi_20260526.img` (49.1 GiB, the lander vendor image) | **absent** — no `~/Downloads/landerepi-image`, no `*.img` over 500 MB anywhere within reach. The 2026-10-22 insight ("no local copy remains") is still true. |
| the vendor archive's Drive links | **live.** Re-fetched 2026-11-21 18:32 with `desi-bot/ros2-image-fetch.sh`: four volumes, 3,221,225,472 B each = 12 GiB, ~55 MB/s. |
| a rover boot-floor image | **does not exist, anywhere.** Neither rover card has ever been cloned off, and no image was ever kept. `mdfind` over the whole disk, Time Machine's destination not mounted, Imager cache empty. |
| Raspberry Pi Imager | installed, **v2.0.11.1**, and its `--cli` takes `src dst` with `--sha256`, `--first-run-script`, `--disable-eject`. |
| disk space | 103 GiB free. The archive is 12 GiB; the extracted image 49.1 GiB. Both fit, with ~40 GiB left. |

## 2. The shape of the job: a card is a floor plus a pilot, and tonight only the floor exists

Dmitri's contract (`2026-11-11-dmitri-what-a-pool-card-carries.md`) splits a pool card in two: a
**boot floor** (OS + the class's driver stack, identical across the class, no hostname) and a
**pilot** (the pilot server, the voice loop, the first-boot self-identification). Tonight's imaging
can produce the floor for both classes. It cannot produce the pilot for either, because:

- **The lander's pilot is on the lander**, not in the vendor image: `/home/pi/ttsd.py`,
  `/home/pi/audio-setup.sh`, the ear on the Mac (`tools/voice3.py`), the audio gain recipe, and the
  calibration of 2026-10-22. A fresh vendor card is a working ROS 2 lander with the vendor's own
  demos, and it is not *my* lander until that layer is put on it.
- **The rovers have no image at all.** Their floor was built by hand in September, one command at a
  time, and the only copy of it is the card inside each rover.

So the job is two stages, and the second is the one that makes cards worth carrying:

**Stage A — floor.** Write the class image to a card, put the envelope beside it, key it, record it.
**Stage B — pilot, once per class.** Take one card of each class, boot it on a body, install the
pilot and the first-boot check, shut down, pull it, and keep it as the class **master**. Every card
of that class is then a clone of the master, and the two stages collapse into one write per card
from then on.

Writing Stage A to all nine and then re-writing eight of them with the Stage B master costs one extra
write per card. Writing Stage B *first* would save that, and it is the better order — but it needs a
body and a pilot build before any card is written, and the box is open now. Decision: **Stage A on
the lander five first** (their floor is a 49 GiB file that needs nothing but a reader), **Stage B for
the rovers first**, because there is no rover floor to write. Stage B for the lander follows on the
first card, and the lander five get their master-clone pass when it exists.

## 3. The classes, and what is written to each

| class | floor written tonight | what it is | size written |
|---|---|---|---|
| `lander` | `LanderPi_20260526.img` | the vendor's MentorPi/LanderPi system, the same image the lander's own card came from on 2026-10-15 (D-6) | 49.1 GiB (~52.7 GB) |
| `picar-x` | **nothing yet** | Raspberry Pi OS 64-bit + robot-hat 2.5.x + vilib + picar-x 2.1.x + `i2samp.sh` + the lgpio gpiochip fix, exactly as built on 2026-09-22 | — |

**Why the vendor image and not a clone of the lander's current card.** A clone would carry the
lander's SSH keys, its Wi-Fi credentials, my calibration and my working files. Dmitri's contract
forbids all four on a shared card, and the argument is not etiquette: a writable copy of an owner's
calibration on a card anybody can boot is a baseline that can silently undo a later fix. The vendor
image is exactly the thing the contract calls the boot floor: it knows the hardware and not who is
driving.

## 4. How a card is written — the procedure, with the guard that matters

The 2026-09-22 lesson stands: in a storage list the card appears as a ~64 GB external disk beside
"Macintosh HD", and picking the wrong one erases the Mac. `desi-bot/tools/image_card.sh` therefore
refuses to write unless all of these hold, and refuses before it does anything:

1. the target is an **external** disk (`diskutil info` → `Internal: false`);
2. its size is inside **50–70 GB** — one of the nine, not the 32 GB spares, not the Mac's 500 GB;
3. it is **not** the Time Machine destination;
4. the operator passes the device and an image explicitly; there is no auto-detect, ever.

Then: `diskutil unmountDisk` (not eject), write to the **raw** device (`/dev/rdiskN`, which is the
fast path), `sync`, and — only when asked — a read-back comparison of the first 32 MiB plus the
image's whole written length against the source.

Per card, after the write:

- the **envelope**: `POOL-CARD.json` and a plain-text `POOL-CARD.txt` beside it, on the card's boot
  partition (the FAT volume macOS can read without booting anything — which is the point: the reader
  of these fields is a person holding the card). If a class image's boot partition cannot be written
  from macOS, the envelope goes on the first-boot pass instead and the row says so. Nothing is
  claimed as written until it has been read back off the card.
- the **key**: `L-xx` or `R-xx` (class letter, then the amigo's code), in the founder's ink, before the card is imaged — the class letter
  plus a serial, assigned in the order written, never reserved (`rover/pegboard.md`; format changed by
  the founder 2026-11-21 from `V-nn`, before any key existed). The serial is the one field on the row
  that cannot be wrong; the class letter is a claim the re-image amends.
- the **row**: pegboard gets the key, grade, size, class, and `state = imaged <date>`; `verified`
  stays empty until a body boots it and says what it is.

## 5. Times, so nobody is surprised at midnight

Measured write speed is not yet measured on this reader; the estimates below assume 25–40 MB/s,
which is the range these A2 cards are expected to sustain through a USB reader:

| class | write | + read-back verify | × 5 cards |
|---|---|---|---|
| `lander` (49.1 GiB) | 22–35 min | 22–35 min | **~2–3 h with verify, ~2 h without** |
| `picar-x` (~2 GB) | 1–2 min | 1–2 min | ~10–15 min with verify |

The lander five are the whole evening. The honest way to spend it: verify **one** representative
card fully (read-back and, later, a boot), write the other four with a sync and no read-back, and
mark all five `imaged`, not `verified`. A read-back on all five buys a second pass over 264 GB and
buys a confidence that a boot test gives for free on the first one.

## 5a. What the extracted image actually is (measured 2026-11-21 19:56)

The archive came down whole — 4 × 3,221,225,472 B and one 3,196,884,441 B — and `unar` produced
`LanderPi_20260526.img`, **52,719,255,552 B**, byte-for-byte the size the 2026-10-12 fetch recorded. So
the re-download is the same file, not a newer one. Reading its own partition table, without booting
anything:

| what | finding |
|---|---|
| partitions | two: `s1` FAT32 `bootfs`, 511 MiB (74 MiB used) and `s2` Linux ext4 |
| the boot partition | a perfectly ordinary Raspberry Pi bootfs — `config.txt`, `cmdline.txt`, `kernel8.img`, `overlays/`, the Pi 5 dtbs. **Writable from macOS, which is where `POOL-CARD.json` goes**: readable in a hand, with no body and no boot. 437 MiB free, so nothing in the envelope can crowd it. |
| credentials on the boot partition | **none** — no `wpa_supplicant.conf`, no `firstrun.sh`, no `userconf.txt`, no `ssh` file. Whatever the vendor's login is, it is in the ext4 root and not in a plaintext file beside it. |
| Wi-Fi regulatory domain | `cfg80211.ieee80211_regdom=HK` in `cmdline.txt` — **Hong Kong**, in a Maryland house. The lander has been running with this since 2026-10-15 (D-6). It is not a fault on 2.4 GHz channels 1–11, and it is the wrong setting; it belongs in `known_unknowns` on every lander card until somebody changes it and measures the difference. |
| vendor dirt | `.config.txt.swp` (a vim swap file, Feb 2025) and `FSCK0000.REC` sit in the boot partition. Harmless, and evidence the image was made on a running Pi by hand rather than built. Leave them: an image that differs from the vendor's is an image that cannot be re-derived. |

## 6. What the founder does, in order, one step at a time

1. **Write a key on the first card** — `L-CL` in ink on the label face, as the founder did. Say it; `L-01` is that
   card's identity everywhere, and the letter says which image it is about to get.
2. **Put it in the reader.** One card at a time, during the write, and not before.
3. When the write reports done: pull it, write the next key, put the next one in.

Nothing else is his. Nothing about which card is which class is his to remember: the key resolves it
in `rover/pegboard.md`, and that is why the number is the only thing that goes on the plastic.

## 7. What this file did not claim on 2026-11-21

*Kept as written — everything in this section was true when it was written and is superseded by §8,
which is the measurement rather than the plan.*

## 7a. What this file does not claim

- **No card has been written or read** at the time of writing. The download is still running.
- **No rover floor exists.** The four rover cards cannot be imaged tonight from anything, and saying
  "four rover chips imaged" without one would be untrue.
- **No card is verified.** `verified` in every envelope stays empty until a body answers with its own
  name and the calibration it found. A card that has never been booted has an empty field, and an
  empty field is a fact.
- **The lander's cliff behaviour is still unmeasured** and belongs in `known_unknowns` on every
  lander card.


## 8. What actually happened — 2026-11-24, the five lander cards

Five cards written in one afternoon, the founder at the reader, one pass per card from a loop script
that needs no session alive between cards (`desi-bot/staging/card-loop.sh`; why it exists: a goose
session does not run between turns, the founder's observation, and an instruction that needs one is an
instruction that silently does not happen).

| key in ink | written | pass time | verification |
|---|---|---|---|
| `L-CL` | 15:53 | 26 min (includes a first attempt that failed verification, see below) | **Linux partition byte-identical to the image**, boot partition file-by-file |
| `L-DM` | 16:19 | 21 min | boot partition file-by-file |
| `L-GE` | 16:40 | 18 min | boot partition file-by-file |
| `L-GW` | 16:58 | 17 min | boot partition file-by-file |
| `L-TA` | 17:16 | 17 min | boot partition file-by-file |

**The one real defect of the day, and it was in the verifier.** The first verification compared the
whole disk with the whole image and failed at byte **4,195,305**. The card was fine: its boot partition
starts at 4,194,304, and macOS had auto-mounted that FAT volume when the card was reinserted and
written `.Spotlight-V100` and `.fseventsd` into it. **The check was measuring the host.** Redesigned in
two halves that the host cannot touch — the ext4 partition from its own offset (52.2 of 52.7 GB, a
region macOS cannot read at all) and the boot partition file by file, with macOS's droppings deleted
before eject. The same class of bug as the disk guard earlier the same day, which looked for an
`Internal:` line this macOS does not print: **two guards, both plausible on paper, both wrong only
when run.**

**What the five cards are, and are not.** Boot floors: the vendor's ROS 2 lander system plus a
`POOL-CARD.json`/`.txt` envelope on the boot partition. **None has been booted** — `verified` is empty
in all five envelopes, the agent is the write and the read-back, not the body. None carries the pilot,
the voice loop, or my calibration.

**What is left, in order.** (1) Boot one — cheapest is `L-CL`, in the lander, with the founder
watching — and fill its `verified` field from what the body itself reports. (2) Build the lander pilot
onto that card and clone it to the other four. (3) The four rover cards, which still have no floor to
write.
