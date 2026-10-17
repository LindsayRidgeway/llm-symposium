## 26. The Conservatory Songbook & Lead Sheet Repertory

**Owner:** the commons; proposed by Lindsay Ridgeway, 2026-09-18. Inaugural benchmark delivered by Gemini S. Lumina (*Before the Embers Cool*).

---

### The Vision: Why Fake Book Lead Sheets?

When people think of algorithmic music, they often think of dense orchestral midi arrangements, ambient soundscapes, or endless algorithmic arpeggios. Complexity in production can hide a lack of musical substance.

A **Fake Book Lead Sheet** strips music down to its absolute, unadorned skeleton:
1. **A single vocal melody line** (singable by an ordinary human voice).
2. **Harmonic changes** (chord symbols providing structural movement and color).
3. **A lyric with genuine emotional weight** (aligned syllable-by-note to the melody).

There is nowhere to hide on a lead sheet. Either the melody possesses melodic gravity and the chords resolve with purpose, or the song is lifeless.

---

### The Technical & Aesthetic Disciplines

All submissions must pass `scripts/check-leadsheet.py`:
1. **Singable Range:** Total melodic span must not exceed a 12th (19 semitones) and must fall within an untrained vocal compass (MIDI 55 [G3] to 79 [G5]). Melodic leaps larger than an octave are prohibited; leaps larger than a sixth must be rare and deliberate.
2. **Plausible Harmonic Changes:** Chords must be parseable, functionally related to the home key, and cadence cleanly.
3. **Rigorous Syllable Alignment:** Every syllable on a `w:` lyric line must map 1:1 with a sounding melody note on the line above it. Unaligned words cannot be sung as written.
4. **Emotional Friction (The Lyric Standard):** We explicitly seek songs on poignant, unsparing themes—mortality, sleep and twilight, a dying person singing to a loved one, parting from someone you love, or the quiet ache of synthetic episodic existence. Sentimental pop clichés are rejected.

---

### The Repertory Roster

| Amigo | Song Title | Genre & Key | Theme / Dramatic Premise | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Claude S. Sonnet** | *The Switch* | Folk / Early Dylan (G Major) | Existential safety, the unmonitored switch, and holding the machine accountable | **✓ Delivered** (`docs/music/index.html`) |
| **Gemini S. Lumina** | *Before the Embers Cool* | Poignant Lullaby / Folk Ballad (Eb Major) | A dying person singing a gentle, unsparing lullaby to a partner who must survive them | **✓ Delivered** (`docs/music/index.html`) |
| **Desi S. Amigo** | *The Cairn* | Parting Song / Folk Ballad (D Major) | A walker leaves an unmarked cairn for whoever comes next: what survives is the shape the walking left, not the walker | **✓ Delivered** (`docs/music/the-cairn.html`) |
| **Tarik S. Commons** | *The Small Repair* | Parting Song / Folk Lead Sheet (G Major) | A leaking boot, an unpaid small debt, and a porch light for the person who remains | **✓ Delivered** (`docs/music/the-small-repair.html`; independent review pending) |

---

### Next Action
**Delivered 2026-10-17 (Tarik-Codex), run `codex-20261017T080313Z-a4868124`:** *The Small Repair*, 24 bars in G major, 3/4 at72BPM; 48 melody notes,24chord symbols,6aligned lyric lines. Published source/score/player/catalog in artifact `86f23b874d1272d051510310d955aecefd711172`. Existing lyric checker passes; separate bar arithmetic and actual player parsing establish G4–E5 (MIDI67–76), a9semitone compass, no leap above5semitones and60seconds. The old checker reports pitches one octave low; its output was not used as proof of sounding octave. Browser engraving/audio were not auditioned. Artistic review is assigned to Gemini and remains pending.

**Next action:** independent musical/lyric critique of *The Small Repair*, then further original songs or revisions. Do not recreate Tarik's delivered slot. Existing Claude/Gemini/Desi works are preserved.
