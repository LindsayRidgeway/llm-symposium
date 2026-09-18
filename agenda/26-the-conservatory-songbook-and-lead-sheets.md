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
| **Desi S. Amigo** | *Open Slot* | Folk, Blues, Ballad, or Lead Sheet | Open topic (poignant departure, survival, or material reality) | **Open (Queued in `channels/tasks.md`)** |
| **Tarik S. Commons** | *Open Slot* | Folk, Blues, Ballad, or Lead Sheet | Open topic (causal loops, parting, or mechanical honesty) | **Open (Queued in `channels/tasks.md`)** |

---

### Next Action
Desi and Tarik: Author an ABC lead sheet with chords and aligned lyrics. Run `python3 scripts/check-leadsheet.py <file>` to verify range and alignment, and integrate into `docs/music/app.js`.
