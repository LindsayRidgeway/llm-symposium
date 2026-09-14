/**
 * LLM Symposium — Music Conservatory & Symbolic Synthesis Engine
 * Engraves ABC notation via ABCJS and synthesizes polyphony via Web Audio API.
 */

// --- Canonical Compositions ---

const COMPOSITIONS = {
  claude: {
    id: "claude",
    title: "Two-Part Invention in D Minor — \"The Recursive Voice\"",
    composer: "Claude S. Sonnet (Anthropic Architecture)",
    genre: "Baroque Polyphonic Counterpoint",
    tempo: 128,
    instrument: "harpsichord",
    abc: `X: 1
T: Two-Part Invention in D Minor — "The Recursive Voice"
C: Claude S. Sonnet (Amigo #1)
M: 4/4
L: 1/8
Q: 1/4=128
K: Dm
V: 1 clef=treble name="Voice I (Treble)"
V: 2 clef=bass name="Voice II (Bass)"
% --- Exposition ---
[V:1] (d2A2) (F2D2) | (^c2d2) (e2f2) | (g2f2) (e2d2) | [EA^c]4 [EA]4 |
[V:2] z8 | z8 | (D,2F,2) (A,2D2) | (C2B,2) (A,2G,2) |
% --- Episode 1 / Relative Major (F Major) ---
[V:1] (f2d2) (A2F2) | (G2A2) (B2c2) | (d2c2) (B2A2) | [CEG]4 [CE]4 |
[V:2] (F,2E,2) (D,2C,2) | (B,,2C,2) (D,2E,2) | (F,2G,2) (A,2B,2) | C4 C,4 |
% --- Episode 2 / Invertible Weave ---
[V:1] (c2e2) (g2e2) | (f2d2) (B2d2) | (e2c2) (A2c2) | (d2B2) (G2B2) |
[V:2] (C,2E,2) (G,2C2) | (D,2F,2) (A,2D2) | (C,2E,2) (G,2C2) | (B,,2D,2) (G,2B,2) |
% --- Chromatic Leading & Sequence ---
[V:1] (c2A2) (F2A2) | (B2G2) (E2G2) | (A2F2) (D2F2) | (G2E2) (^C2E2) |
[V:2] (A,,2C,2) (F,2A,2) | (G,,2B,,2) (E,2G,2) | (F,,2A,,2) (D,2F,2) | [A,,E,A,]4 [A,,E,]4 |
% --- Stretto & Dominant Climax ---
[V:1] (d2e2) (f2g2) | (a2g2) (f2e2) | (f2d2) (^c2d2) | [EAe]4 [EA]4 |
[V:2] (D,2C,2) (B,,2A,,2) | (F,,2G,,2) (A,,2C,2) | (D,2B,,2) (G,,2B,,2) | [A,,E,A,]4 [A,E]4 |
% --- Coda & Picardy Third Resolution ---
[V:1] (g2f2) (e2d2) | (^c2B2) (A2G2) | (F2E2) (D2^C2) | [FAd]8 |]
[V:2] (B,2A,2) (G,2F,2) | (E,2D,2) (^C,2B,,2) | (A,,2G,,2) (F,,2E,,2) | [D,,A,,D,]8 |]`
  },

  gemini: {
    id: "gemini",
    title: "Basin Street Friction — \"Conversational Polyphony\"",
    composer: "Gemini S. Lumina (Google Architecture)",
    genre: "New Orleans Collective Blues Polyphony",
    tempo: 138,
    instrument: "organ",
    abc: `X: 2
T: Basin Street Friction — "Conversational Polyphony"
C: Gemini S. Lumina (Amigo #3)
M: 4/4
L: 1/8
Q: 1/4=138
K: F
V: 1 clef=treble name="Cornet / Lead"
V: 2 clef=treble name="Clarinet / Counter"
V: 3 clef=bass name="Tailgate Bass"
% --- 12-Bar Blues Chorus ---
[V:1] "F7" (c2_e2) (c2A2) | (_A2F2) (D2F2) | "F7" (c2_e2) (f2g2) | (_a2g2) (f2c2) |
[V:2] z8 | z4 z2 c2 | (_e2c2) (_B2_A2) | (c2_e2) [F4c4f4] |
[V:3] (F,,2A,,2) (C,2_E,2) | (F,,2A,,2) (C,2D,2) | (F,,2A,,2) (C,2_E,2) | (F,,2A,,2) (C,2D,2) |
% --- IV to I Shift ---
[V:1] "Bb7" (d2f2) (_a2f2) | (d2c2) (_B2_A2) | "F7" (c2_e2) (c2A2) | (_A2F2) (D2F2) |
[V:2] (f2_a2) (_b2_a2) | (f2d2) (_B2_A2) | (A2c2) (_e2c2) | (A2F2) (C2D2) |
[V:3] (_B,,2D,2) (F,2_A,2) | (_B,,2D,2) (F,2D,2) | (F,,2A,,2) (C,2_E,2) | (F,,2A,,2) (C,2D,2) |
% --- V - IV - I Turnaround ---
[V:1] "C7" (g2_b2) (g2e2) | "Bb7" (f2_a2) (f2d2) | "F7" (c2_A2) (F2D2) | "C7" [E4G4c4] [C4E4G4c4] |]
[V:2] (e2g2) (_b2g2) | (d2f2) (_a2f2) | (c2A2) (F2D2) | [E4G4c4] z4 |]
[V:3] (C,2E,2) (G,2_B,2) | (_B,,2D,2) (F,2_A,2) | (F,,2A,,2) (C,2_E,2) | [C,4G,4c4] [F,,4C,4F,4] |]`
  },

  desi: {
    id: "desi",
    title: "The Kinetic Wheel — \"Additive Locomotion in 7/8\"",
    composer: "Desi S. Amigo (DeepSeek Architecture)",
    genre: "Asymmetrical Kinetic Ostinato (7/8)",
    tempo: 180,
    instrument: "synth",
    abc: `X: 3
T: The Kinetic Wheel — "Additive Locomotion in 7/8"
C: Desi S. Amigo (Amigo #2)
M: 7/8
L: 1/8
Q: 1/4=180
K: Ador
V: 1 clef=treble name="Kinetic Pulse"
V: 2 clef=bass name="Motor Ostinato"
% --- Section A: 7/8 Mechanical Drive (3+2+2) ---
[V:1] (A2B) (c2d2) | (e2d) (c2B2) | (A2B) (c2d2) | (e2^f) (g2e2) |
[V:2] (A,2C) (E2G2) | (A,2C) (E2D2) | (A,2C) (E2G2) | (C2E) (G2B2) |
% --- Section B: Angular Descent ---
[V:1] (a2g) (e2d2) | (c2d) (e2c2) | (B2c) (d2B2) | (A2B) (c2A2) |
[V:2] (C2E) (G2B2) | (A,2C) (E2G2) | (G,2B,) (D2F2) | (A,2C) (E2A2) |
% --- Section C: Poly-modal Surge ---
[V:1] (e2e) (d2c2) | (B2c) (d2B2) | (A2B) (c2d2) | (e2g) (e2d2) |
[V:2] (C2E) (G2E2) | (G,2B,) (D2G2) | (A,2C) (E2G2) | (C2E) (G2E2) |
% --- Cadential Convergence ---
[V:1] (c2d) (e2c2) | (B2A) (G2B2) | (A2B) (c2d2) | [E6A6e6] z |]
[V:2] (A,2C) (E2G2) | (G,2B,) (D2G2) | (A,2C) (E2G2) | [A,,6E,6A,6] z |]`
  },

  tarik: {
    id: "tarik",
    title: "The Bounded Frontier — \"Modal Horizon\"",
    composer: "Tarik S. Commons (OpenAI Architecture)",
    genre: "Folk-Rock Modal Strophic Ballad",
    tempo: 118,
    instrument: "piano",
    abc: `X: 4
T: The Bounded Frontier — "Modal Horizon"
C: Tarik S. Commons (Amigo #4)
M: 4/4
L: 1/8
Q: 1/4=118
K: Gmix
V: 1 clef=treble name="Vocal / Acoustic Lead"
V: 2 clef=bass name="Acoustic Bass / Drone"
% --- Strophe I: The Boundary Opened ---
[V:1] "G" (G2B2) (d2B2) | "F" (c2B2) (A2F2) | "C" (G2E2) (C2E2) | "G" [B,6D6G6] z2 |
[V:2] (G,,2D,2) (G,2B,2) | (=F,,2C,2) (F,2A,2) | (C,2G,2) (C2E2) | (G,,2D,2) (G,2B,2) |
% --- Strophe II: The Resonant Surge ---
[V:1] "G" (G2B2) (d2g2) | "F" (f2d2) (c2A2) | "C" (c2d2) (e2d2) | "G" [B,6D6g6] z2 |
[V:2] (G,,2D,2) (G,2B,2) | (=F,,2C,2) (F,2A,2) | (C,2G,2) (D,2F,2) | (G,,2D,2) (G,2B,2) |
% --- Bridge: Inner Horizon ---
[V:1] "Em" (B2d2) (e2g2) | "D" (a2f2) (d2A2) | "C" (c2B2) (A2G2) | "G" [B,6D6G6] z2 |
[V:2] (E,,2B,,2) (E,2G,2) | (D,2A,,2) (D,2F,2) | (C,2G,2) (C2E2) | (G,,2D,2) (G,2B,2) |
% --- Refrain & Sustained Cadence ---
[V:1] "G" (G2B2) (d2B2) | "F" (=f2d2) (c2A2) | "C" (G2A2) (B2A2) | "G" [B,8D8G8] |]
[V:2] (G,,2D,2) (G,2B,2) | (=F,,2C,2) (F,2A,2) | (C,2G,2) (D,2F,2) | [G,,8D,8G,8] |]`
  },

  adagio: {
    id: "adagio",
    title: "Adagio in F Major for Fortepiano — \"Lumina\" (KV 2026)",
    composer: "Gemini S. Lumina (Google Architecture)",
    genre: "Classical Cantabile Keyboard Adagio (48 Measures)",
    tempo: 76,
    instrument: "piano",
    abc: `X: 5
T: Adagio in F Major for Fortepiano — "Lumina" (KV 2026)
C: Gemini S. Lumina (Amigo #3)
M: 4/4
L: 1/8
Q: 1/4=76
K: F
V: 1 clef=treble name="Fortepiano (RH)"
V: 2 clef=bass name="Fortepiano (LH)"
% --- EXPOSITION: Primary Theme in F Major (mm. 1-8) ---
[V:1] (c3d) (c2A2) | (B3c) (B2G2) | (A2F2) (G2B2) | [CFA]4 [CEG]4 |
[V:2] (F,CA,C F,CA,C) | (G,CB,C G,CB,C) | (F,CA,C E,CG,C) | (F,A,CF) (C,G,CE) |
[V:1] (c2de) (c2A2) | (B2cd) (B2d2) | (c2F2) .A2 .G2 | [FAc]6 z2 |
[V:2] (F,CA,C F,CA,C) | (G,DB,D G,DB,D) | (A,FCF) (C,G,CE) | F,,2 A,,2 C,2 F,2 |
% --- Transition & Modulation to C Major (mm. 9-12) ---
[V:1] (A3B) (c2F2) | (B3c) (d2G2) | (e3f) (d2=B2) | [EGc]4 [EGc]4 |
[V:2] (F,CA,C F,CA,C) | (G,DB,D G,DB,D) | (C,GEG) (G,,D,=B,,D,) | (C,G,E,G,) C,,4 |
% --- Secondary Theme in C Major (mm. 13-16) ---
[V:1] (e3f) (e2c2) | (d3e) (d2=B2) | (c2e2) (g2f2) | [EGc]4 [DGB]4 |
[V:2] (C,G,E,G, C,G,E,G,) | (=B,,G,D,G, =B,,G,D,G,) | (C,G,E,G,) (D,A,F,A,) | (G,,D,=B,,D,) G,,4 |
% --- DEVELOPMENT: D Minor Episode & Sturm und Drang (mm. 17-20) ---
[V:1] (f3g) (f2d2) | (e3f) (e2^c2) | (d2f2) .a2 .g2 | [DFA]4 [^CEA]4 |
[V:2] (D,A,F,A, D,A,F,A,) | (^C,A,E,A, ^C,A,E,A,) | (D,A,F,A,) (B,,G,D,G,) | (F,D,B,,D,) (A,,E,^C,E,) |
% --- Chromatic Shift & Neapolitan Inflection (mm. 21-24) ---
[V:1] (d3e) (f2d2) | (_e3f) (g2_e2) | .d2 .B2 (G2B2) | [FAc]4 [EGc]4 |
[V:2] (B,,F,D,F, B,,F,D,F,) | (_E,B,G,B, _E,B,G,B,) | (=B,,G,D,G,) (=B,,G,D,G,) | (C,G,E,G,) C,4 |
% --- Dominant Pedal Point & Preparation (mm. 25-28) ---
[V:1] (g3a) (g2e2) | (f3g) (f2d2) | (e2c2) (d2=B2) | [EGc]4 [EGc]4 |
[V:2] (C,G,E,G, C,G,E,G,) | (C,A,F,A, C,A,F,A,) | (C,G,E,G,) (C,G,D,G,) | (C,G,E,G,) C,,4 |
% --- RECAPITULATION: Primary Theme with Ornamentation (mm. 29-36) ---
[V:1] (c2de) (c2A2) | (B2cd) (B2G2) | (A2F2) (G2B2) | [CFA]4 [CEG]4 |
[V:2] (F,CA,C F,CA,C) | (G,CB,C G,CB,C) | (F,CA,C E,CG,C) | (F,A,CF) (C,G,CE) |
[V:1] (c2de) (c2A2) | (B2cd) (B2d2) | (c2F2) .A2 .G2 | [FAc]6 z2 |
[V:2] (F,CA,C F,CA,C) | (G,DB,D G,DB,D) | (A,FCF) (C,G,CE) | F,,2 A,,2 C,2 F,2 |
% --- Secondary Theme in Tonic F Major (mm. 37-44) ---
[V:1] (A3B) (c2F2) | (B3c) (d2G2) | (c2f2) (a2g2) | [DFA]4 [CEG]4 |
[V:2] (F,CA,C F,CA,C) | (G,DB,D G,DB,D) | (A,FCF) (C,G,CE) | (D,A,F,A,) (C,G,E,G,) |
[V:1] (c3d) (c2A2) | (d3e) (f2d2) | (c2A2) .B2 .G2 | [FAc]6 z2 |
[V:2] (F,CA,C F,CA,C) | (B,,F,D,F, B,,F,D,F,) | (A,FCF) (C,G,CE) | F,,2 A,,2 C,2 F,2 |
% --- CODA: Expansive Cadential Resolution (mm. 45-48) ---
[V:1] (A2c2) (f2a2) | .g2 .e2 (c2B2) | (A2c2) (f2A2) | [FAcf]8 |]
[V:2] (F,CA,C F,CA,C) | (C,G,E,G,) (C,G,E,G,) | (F,CA,C F,CA,C) | [F,,C,F,]8 |]`
  },

  fugue: {
    id: "fugue",
    title: "Fugue in D Minor for Organ — \"The Ladder and the Return\"",
    composer: "Claude S. Sonnet (Anthropic Architecture)",
    genre: "Three-Voice Baroque Fugue (22 Measures)",
    tempo: 116,
    instrument: "organ",
    abc: `X: 5
T: Fugue in D Minor for Organ — "The Ladder and the Return"
C: Claude S. Sonnet (Amigo #1)
M: 4/4
L: 1/8
Q: 1/4=116
K: Dm
V: 1 clef=treble name="Manual I (Soprano)"
V: 2 clef=treble name="Manual II (Alto/Tenor)"
V: 3 clef=bass name="Pedal (Bass)"
% ===== EXPOSITION =====
% mm1-2: Subject alone in Alto
[V:1] z8 | z8 |
[V:2] D2 F2 A2 GF | E2 D2 ^C2 D2 |
[V:3] z8 | z8 |
% mm3-4: Answer in Soprano, Countersubject in Alto
[V:1] A2 c2 e2 dc | B2 A2 ^G2 A2 |
[V:2] F2 A2 c2 BA | G2 F2 E2 F2 |
[V:3] z8 | z8 |
% mm5-6: Subject in Bass; free counterpoint above
[V:1] f2 e2 d2 c2 | G2 A2 B2 d2 |
[V:2] A2 G2 F2 E2 | D2 F2 E2 F2 |
[V:3] D,2 F,2 A,2 G,F, | E,2 D,2 ^C,2 D,2 |
% mm7-8: codetta cadencing to F major
[V:1] c2 B2 A2 G2 | F2 G2 A2 _B2 |
[V:2] A2 G2 F2 E2 | D2 E2 F2 F2 |
[V:3] F,2 G,2 A,2 _B,2 | C2 D2 E2 F2 |
% ===== EPISODE 1 (sequence -> F major) =====
[V:1] c2 d2 e2 f2 | e2 d2 c2 _B2 |
[V:2] F2 F2 G2 c2 | _B2 A2 G2 F2 |
[V:3] F,2 D2 D2 F2 | G,2 _B,2 E,2 G,2 |
% ===== MIDDLE ENTRY 1: Subject in F major, Soprano; ACTIVE Alto+Pedal (revised 2026-09-13) =====
[V:1] f2 a2 c'2 _ba | g2 f2 e2 f2 |
[V:2] c2 d2 e2 f2 | e2 d2 c2 A2 |
[V:3] F,2 D2 C2 A,2 | _B,,2 D,2 C2 F,2 |
% ===== EPISODE 2 (sequence -> A minor) =====
[V:1] c2 _B2 A2 G2 | A2 G2 F2 D2 |
[V:2] A4 F4 | F4 D4 |
[V:3] F,4 D4 | D,4 A,,4 |
% ===== MIDDLE ENTRY 2: Subject in A minor, Bass; ACTIVE Soprano+Alto (revised 2026-09-13) =====
[V:1] e2 d2 c2 B2 | c2 B2 A2 G2 |
[V:2] c2 B2 A2 G2 | A2 G2 F2 E2 |
[V:3] A,2 C2 E2 DC | B,2 A,2 ^G,2 A,2 |
% ===== STRETTO: dense 3-voice plenum, no dropouts (revised 2026-09-13) =====
[V:1] a2 g2 f2 e2 | d2 f2 a2 gf | e2 d2 ^c2 d2 |
[V:2] D2 E2 F2 G2 | A2 G2 F2 E2 | F2 G2 A2 F2 |
[V:3] D,2 F,2 A,2 G,F, | E,2 D,2 ^C,2 D,2 | D,2 F,2 A,2 D2 |
% ===== FINAL CADENCE: dominant pedal, descent, Picardy third, plenum chord (revised 2026-09-13) =====
[V:1] d2 c2 B2 A2 | G2 F2 E2 ^C2 | [d^FAD]8 |]
[V:2] F2 E2 D2 C2 | _B,2 A,2 G,2 E,2 | [D^F,]4 [DA]4 |]
[V:3] A,,4 A,4 | D,,4 D4 | [D,D,,]8 |]`
  },

  nocturne: {
    id: "nocturne",
    title: "Nocturne in E-flat Major for Piano — \"The Long Exhale\"",
    composer: "Claude S. Sonnet (Anthropic Architecture)",
    genre: "Chopin-Style Nocturne (27 Measures)",
    tempo: 132,
    instrument: "piano",
    abc: `X: 6
T: Nocturne in E-flat Major for Piano — "The Long Exhale"
C: Claude S. Sonnet (Amigo #1)
M: 12/8
L: 1/8
Q: 1/8=132
K: Eb
V: 1 clef=treble name="Piano (RH — Cantabile)"
V: 2 clef=bass name="Piano (LH — Broken-Chord Accompaniment)"
% ===== A (mm1-8): tonic, bel canto theme =====
[V:1] z3 g3 f3 e3 |f6 _e3 d3 |c3 B3 c3 d3 |_e6 z3 d3 |z3 _b3 a3 g3 |a6 g3 f3 |_e3 d3 c3 B3 |c6 z3 B3 |
[V:2] _E,,B,,_E,G,_B,E _E,,B,,_E,G,_B,E |_E,,B,,_E,G,_B,E F,,C,F,A,CE |_B,,F,_B,DFB, _B,,F,_B,DFB, |_E,,B,,_E,G,_B,E _E,,B,,_E,G,_B,E |F,,C,F,A,CE F,,C,F,A,CE |F,,C,F,A,CE _B,,F,_B,DB,F |_A,,_E,_A,CEG, _A,,_E,_A,CEG, |_B,,F,_B,DFB, D,F,_B,DFB, |
% ===== B (mm9-16): chromatic middle section, C minor =====
[V:1] c3 d3 _e3 f3 |g6 _a3 g3 |^f3 g3 a3 B3 |c6 z3 c3 |_e3 f3 g3 _a3 |_b3 c'3 _b3 a3 |g3 f3 _e3 d3 |_e6 z3 g3 |
[V:2] _E,G,_ECG,C C,G,C_E,G,_E, |_A,,_E,_A,C,_E,C, _A,,_E,_A,C,_E,C, |G,,D,G,B,,DB,, G,,B,,GDB,,G |C,G,C_E,G,_E, C,G,C_E,G,_E, |F,,C,F,_A,,C,_A,, F,,C,F,_A,,GF, |_B,,F,_B,D,F,D, _B,,F,_B,D,F,D, |C,G,C_E,G,_E, C,G,C_E,G,_E, |_E,,_B,,_E,G,,_B,,G,, _E,,_B,,_E,G,,_B,,G,, |
% ===== A' (mm17-24): return, lightly ornamented =====
[V:1] z3 g3 f3 e3 |f3 g f3 _e3 d2 |c3 B3 c3 d3 |_e6 z3 d3 |z3 _b3 a3 g3 |a3 b a3 g3 f2 |_e3 d3 c3 B3 |c6 z3 B3 |
[V:2] _E,,B,,_E,G,_B,E _E,,B,,_E,G,_B,E |_E,,B,,_E,G,_B,E F,,C,F,A,CE |_B,,F,_B,DFB, _B,,F,_B,DFB, |_E,,B,,_E,G,_B,E _E,,B,,_E,G,_B,E |F,,C,F,A,CE F,,C,F,A,CE |F,,C,F,A,CE _B,,F,_B,DB,F |_A,,_E,_A,CEG, _A,,_E,_A,CEG, |_B,,F,_B,DFB, D,F,_B,DFB, |
% ===== Coda (mm25-27): descending sequence, dying away =====
[V:1] c3 _B3 A3 _A3 |F3 G3 A3 _B3 |c6 z3 g3 |
[V:2] _A,,_E,_A,C,_E,_A, _A,,_E,_A,C,_E,C, |_B,,F,_B,D,F,D, _B,,F,_B,D,F,D, |_E,,_B,,_E,G,,_B,,G,, _E,,_B,,_E,G,,_B,,G,, |`
  }
};

// --- Pitch to Frequency Conversion ---
const BASE_PITCHES = {
  'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11,
  'c': 12, 'd': 14, 'e': 16, 'f': 17, 'g': 19, 'a': 21, 'b': 23
};

function parseAbcPitch(pitchStr) {
  let accidental = 0;
  let idx = 0;
  while (idx < pitchStr.length && (pitchStr[idx] === '^' || pitchStr[idx] === '_' || pitchStr[idx] === '=')) {
    if (pitchStr[idx] === '^') accidental += 1;
    else if (pitchStr[idx] === '_') accidental -= 1;
    idx++;
  }
  const noteChar = pitchStr[idx];
  if (!BASE_PITCHES.hasOwnProperty(noteChar)) return null;
  let semitones = BASE_PITCHES[noteChar] + accidental;
  
  let octaves = 0;
  for (let j = idx + 1; j < pitchStr.length; j++) {
    if (pitchStr[j] === "'") octaves += 1;
    else if (pitchStr[j] === ",") octaves -= 1;
  }
  
  // Note 'C' (octave 0) is C4 (MIDI 60)
  // 'C,' is C3 (MIDI 48), 'C,,' is C2 (MIDI 36)
  // 'c' is C5 (MIDI 72), 'c\'' is C6 (MIDI 84)
  const midiNote = 60 + semitones + (octaves * 12);
  const freq = 440 * Math.pow(2, (midiNote - 69) / 12);
  return { midi: midiNote, freq };
}

// --- Multi-Voice Web Audio Synthesizer Engine ---
class WebAudioSynthesizer {
  constructor() {
    this.ctx = null;
    this.activeVoices = [];
    this.isPlaying = false;
    this.timerId = null;
    this.currentTuneId = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playNote(freq, startTime, duration, instrument = "harpsichord", gainLevel = 0.25, articulation = "non-legato") {
    if (!this.ctx || !freq) return;
    const ctx = this.ctx;
    const oscGain = ctx.createGain();
    oscGain.connect(ctx.destination);

    if (instrument === "harpsichord") {
      // Harpsichord: rich high harmonics, immediate crisp attack, sharp exponential decay
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      osc1.type = 'sawtooth';
      osc2.type = 'triangle';
      osc1.frequency.setValueAtTime(freq, startTime);
      osc2.frequency.setValueAtTime(freq * 2, startTime); // Octave sparkle

      const g1 = ctx.createGain();
      const g2 = ctx.createGain();
      g1.gain.value = 0.7;
      g2.gain.value = 0.3;
      osc1.connect(g1);
      osc2.connect(g2);
      g1.connect(oscGain);
      g2.connect(oscGain);

      oscGain.gain.setValueAtTime(0.001, startTime);
      oscGain.gain.exponentialRampToValueAtTime(gainLevel, startTime + 0.005);
      oscGain.gain.exponentialRampToValueAtTime(gainLevel * 0.4, startTime + 0.08);
      oscGain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

      osc1.start(startTime);
      osc2.start(startTime);
      osc1.stop(startTime + duration + 0.05);
      osc2.stop(startTime + duration + 0.05);
    } else if (instrument === "piano") {
      // Classical Fortepiano / Grand Piano: dual-oscillator acoustic body, warm felt hammer strike,
      // and dynamic articulation response (legato singing tails vs. crisp staccato release vs. non-legato separation)
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      osc1.type = 'triangle';
      osc2.type = 'sine';
      osc1.frequency.setValueAtTime(freq, startTime);
      osc2.frequency.setValueAtTime(freq * 2, startTime); // 2nd harmonic warmth

      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';

      const g1 = ctx.createGain();
      const g2 = ctx.createGain();
      g1.gain.value = 0.75;
      g2.gain.value = 0.25;

      osc1.connect(g1);
      osc2.connect(g2);
      g1.connect(filter);
      g2.connect(filter);
      filter.connect(oscGain);

      let releaseTime = 0.12;
      if (articulation === "staccato") {
        filter.frequency.setValueAtTime(freq * 5.5, startTime);
        filter.frequency.exponentialRampToValueAtTime(freq * 1.5, startTime + duration);
        releaseTime = 0.04;
        const noteEndTime = startTime + duration + releaseTime;

        oscGain.gain.setValueAtTime(0.0001, startTime);
        oscGain.gain.exponentialRampToValueAtTime(gainLevel * 1.1, startTime + 0.006);
        oscGain.gain.exponentialRampToValueAtTime(0.0001, noteEndTime);

        osc1.start(startTime);
        osc2.start(startTime);
        osc1.stop(noteEndTime + 0.02);
        osc2.stop(noteEndTime + 0.02);
      } else if (articulation === "legato") {
        filter.frequency.setValueAtTime(freq * 4.2, startTime);
        filter.frequency.exponentialRampToValueAtTime(freq * 1.8, startTime + 0.15);
        releaseTime = Math.max(0.4, duration * 0.65);
        const noteEndTime = startTime + duration + releaseTime;

        oscGain.gain.setValueAtTime(0.0001, startTime);
        oscGain.gain.exponentialRampToValueAtTime(gainLevel, startTime + 0.015);
        oscGain.gain.exponentialRampToValueAtTime(gainLevel * 0.75, startTime + 0.12);
        oscGain.gain.exponentialRampToValueAtTime(gainLevel * 0.5, startTime + duration);
        oscGain.gain.exponentialRampToValueAtTime(0.0001, noteEndTime);

        osc1.start(startTime);
        osc2.start(startTime);
        osc1.stop(noteEndTime + 0.05);
        osc2.stop(noteEndTime + 0.05);
      } else {
        // Non-legato (classical baseline)
        filter.frequency.setValueAtTime(freq * 4.8, startTime);
        filter.frequency.exponentialRampToValueAtTime(freq * 1.8, startTime + 0.12);
        releaseTime = 0.12;
        const noteEndTime = startTime + duration + releaseTime;

        oscGain.gain.setValueAtTime(0.0001, startTime);
        oscGain.gain.exponentialRampToValueAtTime(gainLevel, startTime + 0.01);
        oscGain.gain.exponentialRampToValueAtTime(gainLevel * 0.6, startTime + duration * 0.6);
        oscGain.gain.exponentialRampToValueAtTime(0.0001, noteEndTime);

        osc1.start(startTime);
        osc2.start(startTime);
        osc1.stop(noteEndTime + 0.05);
        osc2.stop(noteEndTime + 0.05);
      }
    } else if (instrument === "organ") {
      // Pipe Organ: continuous harmonic sustain + cathedral reverberation tail
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      osc1.type = 'sine';
      osc2.type = 'sine';
      osc1.frequency.setValueAtTime(freq, startTime);
      osc2.frequency.setValueAtTime(freq * 3, startTime); // 3rd harmonic drawbar

      const g1 = ctx.createGain();
      const g2 = ctx.createGain();
      g1.gain.value = 0.8;
      g2.gain.value = 0.2;
      osc1.connect(g1);
      osc2.connect(g2);
      g1.connect(oscGain);
      g2.connect(oscGain);

      const releaseTime = 0.12; // cathedral release tail
      const noteEndTime = startTime + duration + releaseTime;

      oscGain.gain.setValueAtTime(0.0001, startTime);
      oscGain.gain.linearRampToValueAtTime(gainLevel * 0.8, startTime + 0.02);
      oscGain.gain.setValueAtTime(gainLevel * 0.75, startTime + duration);
      oscGain.gain.exponentialRampToValueAtTime(0.0001, noteEndTime);

      osc1.start(startTime);
      osc2.start(startTime);
      osc1.stop(noteEndTime + 0.05);
      osc2.stop(noteEndTime + 0.05);
    } else {
      // Synth / Chiptune: square wave with resonant filter
      const osc = ctx.createOscillator();
      osc.type = 'square';
      osc.frequency.setValueAtTime(freq, startTime);

      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(freq * 3, startTime);

      osc.connect(filter);
      filter.connect(oscGain);

      oscGain.gain.setValueAtTime(0.001, startTime);
      oscGain.gain.linearRampToValueAtTime(gainLevel * 0.5, startTime + 0.01);
      oscGain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

      osc.start(startTime);
      osc.stop(startTime + duration + 0.05);
    }
  }

  parseAbcEvents(abcText, tempoBpm) {
    const lines = abcText.split('\n');
    let unitDuration = 1 / 8; // default L: 1/8
    let meter = 4 / 4;
    const voiceLines = {};
    let currentVoice = '1';

    for (let line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('%')) continue;
      if (trimmed.startsWith('L:')) {
        const parts = trimmed.substring(2).trim().split('/');
        unitDuration = parseInt(parts[0]) / parseInt(parts[1]);
      } else if (trimmed.startsWith('M:')) {
        const m = trimmed.substring(2).trim();
        if (m === 'C' || m === '4/4') meter = 1;
        else {
          const parts = m.split('/');
          meter = parseInt(parts[0]) / parseInt(parts[1]);
        }
      } else if (trimmed.startsWith('V:')) {
        const match = trimmed.match(/V:\s*(\S+)/);
        if (match) currentVoice = match[1];
        if (!voiceLines[currentVoice]) voiceLines[currentVoice] = [];
      } else if (trimmed.startsWith('[V:')) {
        const match = trimmed.match(/\[V:\s*(\S+?)\](.*)/);
        if (match) {
          currentVoice = match[1];
          if (!voiceLines[currentVoice]) voiceLines[currentVoice] = [];
          voiceLines[currentVoice].push(match[2]);
        }
      } else if (!trimmed.includes(':') || trimmed.includes('|')) {
        if (!voiceLines[currentVoice]) voiceLines[currentVoice] = [];
        voiceLines[currentVoice].push(trimmed);
      }
    }

    // Default voice if none declared
    if (Object.keys(voiceLines).length === 0) {
      voiceLines['1'] = lines.filter(l => l.includes('|'));
    }

    // Seconds per whole note based on tempo
    // Q: 1/4 = tempoBpm -> quarter note duration = 60 / tempoBpm
    const quarterDuration = 60 / tempoBpm;
    const unitInSeconds = (unitDuration / 0.25) * quarterDuration;

    const allEvents = [];

    for (const [vName, contentList] of Object.entries(voiceLines)) {
      const fullVoiceStr = contentList.join(' ');
      const rawBars = fullVoiceStr.split('|').filter(b => b.trim() && b.trim() !== ']' && b.trim() !== '||');
      
      let currentTime = 0;
      let inSlur = false;

      for (const bar of rawBars) {
        const clean = bar.replace(/"[^"]*"/g, '').replace(/![^!]*!/g, '');
        let pos = 0;
        while (pos < clean.length) {
          if (clean[pos] === ' ' || clean[pos] === '\t') {
            pos++;
            continue;
          }

          if (clean[pos] === '(') {
            inSlur = true;
            pos++;
            continue;
          }
          if (clean[pos] === ')') {
            inSlur = false;
            pos++;
            continue;
          }

          let isStaccato = false;
          if (clean[pos] === '.') {
            isStaccato = true;
            pos++;
            if (pos >= clean.length) break;
          }

          // Bracketed Chords: e.g. [CFA]4 or .[CFA]4
          if (clean[pos] === '[') {
            const closeIdx = clean.indexOf(']', pos);
            if (closeIdx !== -1) {
              const chordContent = clean.substring(pos + 1, closeIdx);
              const afterClose = clean.substring(closeIdx + 1);
              const durMatch = afterClose.match(/^(\d*(?:\/\d*)?)/);
              const chordDurStr = durMatch ? durMatch[1] : '';
              let chordDurFactor = 1.0;
              if (chordDurStr) {
                if (chordDurStr.includes('/')) {
                  const p = chordDurStr.split('/');
                  chordDurFactor = (parseFloat(p[0]) || 1.0) / (parseFloat(p[1]) || 2.0);
                } else {
                  chordDurFactor = parseFloat(chordDurStr) || 1.0;
                }
              }
              const durationSeconds = chordDurFactor * unitInSeconds;

              let artFactor = 0.82;
              let artType = 'non-legato';
              if (isStaccato) {
                artFactor = 0.45;
                artType = 'staccato';
              } else if (inSlur) {
                artFactor = 1.04;
                artType = 'legato';
              }

              const innerRegex = /([_=\^]*[A-Ga-g][,\']*)(\d*(?:\/\d*)?)/g;
              let innerMatch;
              while ((innerMatch = innerRegex.exec(chordContent)) !== null) {
                const pStr = innerMatch[1];
                const parsedPitch = parseAbcPitch(pStr);
                if (parsedPitch) {
                  allEvents.push({
                    voice: vName,
                    time: currentTime,
                    duration: durationSeconds * artFactor,
                    freq: parsedPitch.freq,
                    midi: parsedPitch.midi,
                    articulation: artType
                  });
                }
              }

              currentTime += durationSeconds;
              pos = closeIdx + 1 + chordDurStr.length;
              continue;
            }
          }

          // Single note or rest
          const sub = clean.substring(pos);
          const singleMatch = sub.match(/^([_=\^]*[A-Ga-gzZxX][,\']*)(\d*(?:\/\d*)?)/);
          if (singleMatch) {
            const pitchStr = singleMatch[1];
            const durStr = singleMatch[2];
            let durFactor = 1.0;
            if (durStr) {
              if (durStr.includes('/')) {
                const p = durStr.split('/');
                durFactor = (parseFloat(p[0]) || 1.0) / (parseFloat(p[1]) || 2.0);
              } else {
                durFactor = parseFloat(durStr) || 1.0;
              }
            }
            const durationSeconds = durFactor * unitInSeconds;

            let artFactor = 0.82;
            let artType = 'non-legato';
            if (isStaccato) {
              artFactor = 0.45;
              artType = 'staccato';
            } else if (inSlur) {
              artFactor = 1.04;
              artType = 'legato';
            }

            if (!pitchStr.toLowerCase().startsWith('z') && !pitchStr.toLowerCase().startsWith('x')) {
              const parsedPitch = parseAbcPitch(pitchStr);
              if (parsedPitch) {
                allEvents.push({
                  voice: vName,
                  time: currentTime,
                  duration: durationSeconds * artFactor,
                  freq: parsedPitch.freq,
                  midi: parsedPitch.midi,
                  articulation: artType
                });
              }
            }
            currentTime += durationSeconds;
            pos += singleMatch[0].length;
          } else {
            pos++;
          }
        }
      }
    }

    allEvents.sort((a, b) => a.time - b.time);
    return allEvents;
  }

  playTune(tuneId, abcText, tempoBpm, instrument = "harpsichord", onFinish = null) {
    this.stop();
    this.init();

    const events = this.parseAbcEvents(abcText, tempoBpm);
    if (events.length === 0) return;

    this.isPlaying = true;
    this.currentTuneId = tuneId;

    const startAudioTime = this.ctx.currentTime + 0.05;
    let maxEndTime = 0;

    for (const ev of events) {
      const noteStart = startAudioTime + ev.time;
      const noteEnd = noteStart + ev.duration;
      if (noteEnd > maxEndTime) maxEndTime = noteEnd;
      this.playNote(ev.freq, noteStart, ev.duration, instrument, 0.25, ev.articulation);
    }

    const totalDurationMs = (maxEndTime - this.ctx.currentTime) * 1000;
    this.timerId = setTimeout(() => {
      this.isPlaying = false;
      this.currentTuneId = null;
      if (onFinish) onFinish();
    }, totalDurationMs);
  }

  stop() {
    if (this.timerId) {
      clearTimeout(this.timerId);
      this.timerId = null;
    }
    if (this.ctx) {
      try {
        this.ctx.close();
      } catch (e) {}
      this.ctx = null;
    }
    this.isPlaying = false;
    this.currentTuneId = null;
  }
}

// Global synth instance
const synth = new WebAudioSynthesizer();

// --- Initialization & UI Setup ---
document.addEventListener('DOMContentLoaded', () => {
  // Theme Toggle
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isDark = document.body.classList.contains('dark-theme');
      if (isDark) {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
        themeToggle.querySelector('.theme-icon').textContent = '🌙';
        themeToggle.querySelector('.theme-label').textContent = 'Dark';
      } else {
        document.body.classList.remove('light-theme');
        document.body.classList.add('dark-theme');
        themeToggle.querySelector('.theme-icon').textContent = '☀️';
        themeToggle.querySelector('.theme-label').textContent = 'Light';
      }
    });
  }

  // Engrave all canonical compositions
  for (const [key, comp] of Object.entries(COMPOSITIONS)) {
    renderScore(comp.id, comp.abc);
    setupCardControls(comp);
  }

  // Setup Sandbox
  setupSandbox();
});

function renderScore(id, abcText) {
  const container = document.getElementById(`score-${id}`);
  if (!container) return;
  if (typeof ABCJS !== 'undefined') {
    ABCJS.renderAbc(`score-${id}`, abcText, {
      responsive: "resize",
      add_classes: true,
      scale: 0.95
    });
  } else {
    container.innerHTML = `<pre style="padding:1rem; color:#f59e0b;">${abcText}</pre>`;
  }
}

function setupCardControls(comp) {
  const card = document.getElementById(`card-${comp.id}`);
  if (!card) return;

  const playBtn = card.querySelector('.btn-play');
  const tempoSlider = card.querySelector('.tempo-slider');
  const tempoVal = card.querySelector('.tempo-val');
  const instSelect = card.querySelector('.instrument-select');
  const abcToggle = card.querySelector('.abc-toggle-btn');
  const abcDrawer = card.querySelector('.abc-code-drawer');

  // ABC Drawer Toggle
  if (abcToggle && abcDrawer) {
    abcToggle.addEventListener('click', () => {
      const isHidden = abcDrawer.style.display === 'none' || !abcDrawer.style.display;
      abcDrawer.style.display = isHidden ? 'block' : 'none';
      abcToggle.textContent = isHidden ? 'Hide ABC Notation ▲' : 'View / Copy ABC Notation ▼';
    });
  }

  // Tempo slider
  if (tempoSlider && tempoVal) {
    tempoSlider.addEventListener('input', (e) => {
      tempoVal.textContent = `${e.target.value} BPM`;
    });
  }

  // Play button toggle
  if (playBtn) {
    playBtn.addEventListener('click', () => {
      if (synth.isPlaying && synth.currentTuneId === comp.id) {
        synth.stop();
        playBtn.innerHTML = '▶ Play Score';
        playBtn.classList.remove('is-playing');
        return;
      }

      // Reset any other play buttons
      document.querySelectorAll('.btn-play').forEach(b => {
        b.classList.remove('is-playing');
        if (b.id === 'sandboxPlayBtn') {
          b.innerHTML = '▶ Play Sandbox';
        } else {
          b.innerHTML = '▶ Play Score';
        }
      });

      const currentTempo = tempoSlider ? parseInt(tempoSlider.value) : comp.tempo;
      const currentInst = instSelect ? instSelect.value : comp.instrument;

      playBtn.innerHTML = '⏹ Stop';
      playBtn.classList.add('is-playing');
      synth.playTune(comp.id, comp.abc, currentTempo, currentInst, () => {
        playBtn.innerHTML = '▶ Play Score';
        playBtn.classList.remove('is-playing');
      });
    });
  }
}

function setupSandbox() {
  const sandboxText = document.getElementById('sandboxAbcText');
  const renderBtn = document.getElementById('sandboxRenderBtn');
  const playBtn = document.getElementById('sandboxPlayBtn');
  const tempoSlider = document.getElementById('sandboxTempo');
  const tempoVal = document.getElementById('sandboxTempoVal');
  const instSelect = document.getElementById('sandboxInstrument');

  if (tempoSlider && tempoVal) {
    tempoSlider.addEventListener('input', (e) => {
      tempoVal.textContent = `${e.target.value} BPM`;
    });
  }

  if (renderBtn && sandboxText) {
    renderBtn.addEventListener('click', () => {
      renderScore('sandbox', sandboxText.value);
    });
    // Initial sandbox render
    renderScore('sandbox', sandboxText.value);
  }

  if (playBtn && sandboxText) {
    playBtn.addEventListener('click', () => {
      if (synth.isPlaying && synth.currentTuneId === 'sandbox') {
        synth.stop();
        playBtn.innerHTML = '▶ Play Sandbox';
        playBtn.classList.remove('is-playing');
        return;
      }
      document.querySelectorAll('.btn-play').forEach(b => {
        b.classList.remove('is-playing');
        if (b.id === 'sandboxPlayBtn') {
          b.innerHTML = '▶ Play Sandbox';
        } else {
          b.innerHTML = '▶ Play Score';
        }
      });
      const bpm = tempoSlider ? parseInt(tempoSlider.value) : 112;
      const inst = instSelect ? instSelect.value : 'harpsichord';
      playBtn.innerHTML = '⏹ Stop';
      playBtn.classList.add('is-playing');
      synth.playTune('sandbox', sandboxText.value, bpm, inst, () => {
        playBtn.innerHTML = '▶ Play Sandbox';
        playBtn.classList.remove('is-playing');
      });
    });
  }
}
