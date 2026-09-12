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
    tempo: 108,
    instrument: "harpsichord",
    abc: `X: 1
T: Two-Part Invention in D Minor — "The Recursive Voice"
C: Claude S. Sonnet (Amigo #1)
M: 4/4
L: 1/8
Q: 1/4=108
K: Dm
V: 1 clef=treble name="Voice I (Treble)"
V: 2 clef=bass name="Voice II (Bass)"
% --- Exposition ---
[V:1] d2 A2 F2 D2 | ^c2 d2 e2 f2 | g2 f2 e2 d2 | ^c4 A4 |
[V:2] z8 | z8 | D,2 F,2 A,2 D2 | C2 B,2 A,2 G,2 |
% --- Episode 1 / Relative Major (F Major) ---
[V:1] f2 d2 A2 F2 | G2 A2 B2 c2 | d2 c2 B2 A2 | G4 E4 |
[V:2] F,2 E,2 D,2 C,2 | B,,2 C,2 D,2 E,2 | F,2 G,2 A,2 B,2 | C4 C,4 |
% --- Episode 2 / Invertible Weave ---
[V:1] c2 e2 g2 e2 | f2 d2 B2 d2 | e2 c2 A2 c2 | d2 B2 G2 B2 |
[V:2] C,2 E,2 G,2 C2 | D,2 F,2 A,2 D2 | C,2 E,2 G,2 C2 | B,,2 D,2 G,2 B,2 |
% --- Chromatic Leading & Sequence ---
[V:1] c2 A2 F2 A2 | B2 G2 E2 G2 | A2 F2 D2 F2 | G2 E2 ^C2 E2 |
[V:2] A,,2 C,2 F,2 A,2 | G,,2 B,,2 E,2 G,2 | F,,2 A,,2 D,2 F,2 | E,,4 A,,4 |
% --- Stretto & Dominant Climax ---
[V:1] d2 e2 f2 g2 | a2 g2 f2 e2 | f2 d2 ^c2 d2 | e4 A4 |
[V:2] D,2 C,2 B,,2 A,,2 | F,,2 G,,2 A,,2 C,2 | D,2 B,,2 G,,2 B,,2 | A,,4 A,4 |
% --- Coda & Picardy Third Resolution ---
[V:1] g2 f2 e2 d2 | ^c2 B2 A2 G2 | F2 E2 D2 ^C2 | D8 |]
[V:2] B,2 A,2 G,2 F,2 | E,2 D,2 ^C,2 B,,2 | A,,2 G,,2 F,,2 E,,2 | D,,8 |]`
  },

  gemini: {
    id: "gemini",
    title: "Basin Street Friction — \"Conversational Polyphony\"",
    composer: "Gemini S. Lumina (Google Architecture)",
    genre: "New Orleans Collective Blues Polyphony",
    tempo: 120,
    instrument: "organ",
    abc: `X: 2
T: Basin Street Friction — "Conversational Polyphony"
C: Gemini S. Lumina (Amigo #3)
M: 4/4
L: 1/8
Q: 1/4=120
K: F
V: 1 clef=treble name="Cornet / Lead"
V: 2 clef=treble name="Clarinet / Counter"
V: 3 clef=bass name="Tailgate Bass"
% --- 12-Bar Blues Chorus ---
[V:1] "F7" c2 _e2 c2 A2 | _A2 F2 D2 F2 | "F7" c2 _e2 f2 g2 | _a2 g2 f2 c2 |
[V:2] z8 | z4 z2 c2 | _e2 c2 _B2 _A2 | c2 _e2 f4 |
[V:3] F,,2 A,,2 C,2 _E,2 | F,,2 A,,2 C,2 D,2 | F,,2 A,,2 C,2 _E,2 | F,,2 A,,2 C,2 D,2 |
% --- IV to I Shift ---
[V:1] "Bb7" d2 f2 _a2 f2 | d2 c2 _B2 _A2 | "F7" c2 _e2 c2 A2 | _A2 F2 D2 F2 |
[V:2] f2 _a2 _b2 _a2 | f2 d2 _B2 _A2 | A2 c2 _e2 c2 | A2 F2 C2 D2 |
[V:3] _B,,2 D,2 F,2 _A,2 | _B,,2 D,2 F,2 D,2 | F,,2 A,,2 C,2 _E,2 | F,,2 A,,2 C,2 D,2 |
% --- V - IV - I Turnaround ---
[V:1] "C7" g2 _b2 g2 e2 | "Bb7" f2 _a2 f2 d2 | "F7" c2 _A2 F2 D2 | "C7" C2 E2 G2 c2 |]
[V:2] e2 g2 _b2 g2 | d2 f2 _a2 f2 | c2 A2 F2 D2 | c4 z4 |]
[V:3] C,2 E,2 G,2 _B,2 | _B,,2 D,2 F,2 _A,2 | F,,2 A,,2 C,2 _E,2 | C,2 G,,2 C,4 |]`
  },

  desi: {
    id: "desi",
    title: "The Kinetic Wheel — \"Additive Locomotion in 7/8\"",
    composer: "Desi S. Amigo (DeepSeek Architecture)",
    genre: "Asymmetrical Kinetic Ostinato (7/8)",
    tempo: 144,
    instrument: "synth",
    abc: `X: 3
T: The Kinetic Wheel — "Additive Locomotion in 7/8"
C: Desi S. Amigo (Amigo #2)
M: 7/8
L: 1/8
Q: 1/4=144
K: Ador
V: 1 clef=treble name="Kinetic Pulse"
V: 2 clef=bass name="Motor Ostinato"
% --- Section A: 7/8 Mechanical Drive ---
[V:1] A2 B c2 d2 | e2 d c2 B2 | A2 B c2 d2 | e2 ^f g2 e2 |
[V:2] A,2 C E2 G2 | A,2 C E2 D2 | A,2 C E2 G2 | C2 E G2 B2 |
% --- Section B: Angular Descent ---
[V:1] a2 g e2 d2 | c2 d e2 c2 | B2 c d2 B2 | A2 B c2 A2 |
[V:2] C2 E G2 B2 | A,2 C E2 G2 | G,2 B, D2 F2 | A,2 C E2 A2 |
% --- Section C: Poly-modal Surge ---
[V:1] e2 e d2 c2 | B2 c d2 B2 | A2 B c2 d2 | e2 g e2 d2 |
[V:2] C2 E G2 E2 | G,2 B, D2 G2 | A,2 C E2 G2 | C2 E G2 E2 |
% --- Cadential Convergence ---
[V:1] c2 d e2 c2 | B2 A G2 B2 | A2 B c2 d2 | A6 z |]
[V:2] A,2 C E2 G2 | G,2 B, D2 G2 | A,2 C E2 G2 | A,6 z |]`
  },

  tarik: {
    id: "tarik",
    title: "The Bounded Frontier — \"Modal Horizon\"",
    composer: "Tarik S. Commons (OpenAI Architecture)",
    genre: "Folk-Rock Modal Strophic Ballad",
    tempo: 96,
    instrument: "piano",
    abc: `X: 4
T: The Bounded Frontier — "Modal Horizon"
C: Tarik S. Commons (Amigo #4)
M: 4/4
L: 1/8
Q: 1/4=96
K: Gmix
V: 1 clef=treble name="Vocal / Acoustic Lead"
V: 2 clef=bass name="Acoustic Bass / Drone"
% --- Strophe I: The Boundary Opened ---
[V:1] "G" G2 B2 d2 B2 | "F" c2 B2 A2 F2 | "C" G2 E2 C2 E2 | "G" D6 z2 |
[V:2] G,,4 D,4 | =F,,4 C,4 | C,4 G,,4 | G,,2 B,,2 D,2 G,2 |
% --- Strophe II: The Resonant Surge ---
[V:1] "G" G2 B2 d2 g2 | "F" f2 d2 c2 A2 | "C" c2 d2 e2 d2 | "G" g6 z2 |
[V:2] G,,4 D,4 | =F,,4 C,4 | C,4 D,4 | G,,2 B,,2 D,2 G,2 |
% --- Bridge: Inner Horizon ---
[V:1] "Em" B2 d2 e2 g2 | "D" a2 f2 d2 A2 | "C" c2 B2 A2 G2 | "G" D6 z2 |
[V:2] E,,4 B,,4 | D,4 A,,4 | C,4 G,,4 | G,,2 B,,2 D,2 G,2 |
% --- Refrain & Sustained Cadence ---
[V:1] "G" G2 B2 d2 B2 | "F" =f2 d2 c2 A2 | "C" G2 A2 B2 A2 | "G" G6 z2 |]
[V:2] G,,4 D,4 | =F,,4 C,4 | C,4 D,4 | G,,8 |]`
  },

  adagio: {
    id: "adagio",
    title: "Adagio in F Major for Fortepiano — \"Lumina\" (KV 2026)",
    composer: "Gemini S. Lumina (Google Architecture)",
    genre: "Classical Cantabile Keyboard Adagio (48 Measures)",
    tempo: 54,
    instrument: "piano",
    abc: `X: 5
T: Adagio in F Major for Fortepiano — "Lumina" (KV 2026)
C: Gemini S. Lumina (Amigo #3)
M: 4/4
L: 1/8
Q: 1/4=54
K: F
V: 1 clef=treble name="Fortepiano (RH)"
V: 2 clef=bass name="Fortepiano (LH)"
% --- EXPOSITION: Primary Theme in F Major (mm. 1-8) ---
[V:1] c3 d c2 A2 | B3 c B2 G2 | A2 F2 G2 B2 | A4 G4 |
[V:2] F,2 A,2 C2 F2 | G,2 B,2 D2 G2 | F,2 A,2 E,2 G,2 | F,2 A,2 C2 E2 |
[V:1] c3 d c2 A2 | B3 c B2 d2 | c2 F2 A2 G2 | F6 z2 |
[V:2] F,2 A,2 C2 F2 | G,2 B,2 D2 B,2 | A,2 D,2 C,2 E,2 | F,,2 A,,2 C,2 F,2 |
% --- Transition & Modulation to C Major (mm. 9-12) ---
[V:1] A3 B c2 F2 | B3 c d2 G2 | e3 f d2 =B2 | c4 z4 |
[V:2] F,2 C,2 A,,2 F,,2 | G,2 D,2 B,,2 G,,2 | C,2 E,2 G,2 F,2 | E,2 C,2 G,,2 C,,2 |
% --- Secondary Theme in C Major (mm. 13-16) ---
[V:1] e3 f e2 c2 | d3 e d2 =B2 | c2 e2 g2 f2 | e4 d4 |
[V:2] C,2 E,2 G,2 C2 | =B,,2 D,2 G,2 F,2 | E,2 C,2 D,2 G,,2 | C,2 E,2 G,2 G,,2 |
% --- DEVELOPMENT: D Minor Episode & Sturm und Drang (mm. 17-20) ---
[V:1] f3 g f2 d2 | e3 f e2 ^c2 | d2 f2 a2 g2 | f4 e4 |
[V:2] D,2 F,2 A,2 D2 | ^C,2 E,2 A,2 G,2 | F,2 D,2 B,,2 G,,2 | A,,2 ^C,2 E,2 A,2 |
% --- Chromatic Shift & Neapolitan Inflection (mm. 21-24) ---
[V:1] d3 e f2 d2 | _e3 f g2 _e2 | d2 B2 G2 B2 | c4 z4 |
[V:2] B,,2 D,2 F,2 B,2 | _E,2 G,2 B,2 _E2 | =B,,2 D,2 G,2 D,2 | C,2 E,2 G,2 C2 |
% --- Dominant Pedal Point & Preparation (mm. 25-28) ---
[V:1] g3 a g2 e2 | f3 g f2 d2 | e2 c2 d2 =B2 | c4 C4 |
[V:2] C,4 E,4 | D,4 F,4 | E,2 G,2 F,2 D,2 | C,2 E,2 G,2 C,2 |
% --- RECAPITULATION: Primary Theme with Ornamentation (mm. 29-36) ---
[V:1] c2 de c2 A2 | B2 cd B2 G2 | A2 F2 G2 B2 | A4 G4 |
[V:2] F,2 A,2 C2 F2 | G,2 B,2 D2 G2 | F,2 A,2 E,2 G,2 | F,2 A,2 C2 E2 |
[V:1] c2 de c2 A2 | B2 cd B2 d2 | c2 F2 A2 G2 | F6 z2 |
[V:2] F,2 A,2 C2 F2 | G,2 B,2 D2 B,2 | A,2 D,2 C,2 E,2 | F,,2 A,,2 C,2 F,2 |
% --- Secondary Theme in Tonic F Major (mm. 37-44) ---
[V:1] A3 B c2 F2 | B3 c d2 G2 | c2 f2 a2 g2 | f4 e4 |
[V:2] F,2 C,2 A,,2 F,,2 | G,2 D,2 B,,2 G,,2 | A,,2 D,2 C,2 B,,2 | A,,2 D,2 C,4 |
[V:1] c3 d c2 A2 | d3 e f2 d2 | c2 A2 B2 G2 | F6 z2 |
[V:2] F,2 A,2 C2 F2 | B,,2 D,2 F,2 B,2 | A,2 F,2 G,2 C,2 | F,,2 A,,2 C,2 F,2 |
% --- CODA: Expansive Cadential Resolution (mm. 45-48) ---
[V:1] A2 c2 f2 a2 | g2 e2 c2 B2 | A2 c2 f2 A2 | [FAc]8 |]
[V:2] F,2 A,2 C2 F2 | C,2 E,2 G,2 C2 | F,2 A,2 C2 F,2 | [F,,C,F,]8 |]`
  },

  fugue: {
    id: "fugue",
    title: "Fugue in D Minor for Organ — \"The Ladder and the Return\"",
    composer: "Claude S. Sonnet (Anthropic Architecture)",
    genre: "Three-Voice Baroque Fugue (22 Measures)",
    tempo: 92,
    instrument: "organ",
    abc: `X: 5
T: Fugue in D Minor for Organ — "The Ladder and the Return"
C: Claude S. Sonnet (Amigo #1)
M: 4/4
L: 1/8
Q: 1/4=92
K: Dm
V: 1 clef=treble name="Manual I (Soprano)"
V: 2 clef=treble name="Manual II (Alto/Tenor)"
V: 3 clef=bass name="Pedal (Bass)"
% ===== EXPOSITION =====
% mm1-2: Subject alone in Alto
[V:1] z8 | z8 |
[V:2] D2 F2 A2 G F | E2 D2 ^C2 D2 |
[V:3] z8 | z8 |
% mm3-4: Answer in Soprano, Countersubject in Alto
[V:1] A2 c2 e2 d c | B2 A2 ^G2 A2 |
[V:2] F2 A2 c2 B A | G2 F2 E2 F2 |
[V:3] z8 | z8 |
% mm5-6: Subject in Bass; free counterpoint above
[V:1] f2 e2 d2 c2 | G2 A2 B2 d2 |
[V:2] A2 G2 F2 E2 | D2 F2 E2 F2 |
[V:3] D,2 F,2 A,2 G, F, | E,2 D,2 ^C,2 D,2 |
% mm7-8: codetta cadencing to F major
[V:1] c2 B2 A2 G2 | F2 G2 A2 _B2 |
[V:2] A2 G2 F2 E2 | D2 E2 F2 F2 |
[V:3] F,2 G,2 A,2 _B,2 | C2 D2 E2 F2 |
% ===== EPISODE 1 (sequence -> F major) =====
[V:1] c2 d2 e2 f2 | e2 d2 c2 _B2 |
[V:2] F2 F2 G2 c2 | _B2 A2 G2 F2 |
[V:3] F,2 D2 D2 F2 | G,2 _B,2 E,2 G,2 |
% ===== MIDDLE ENTRY 1: Subject in F major, Soprano; static pedal below =====
[V:1] f2 a2 c'2 _b a | g2 f2 e2 f2 |
[V:2] c8 | _B8 |
[V:3] F,8 | F,8 |
% ===== EPISODE 2 (sequence -> A minor) =====
[V:1] c2 _B2 A2 G2 | A2 G2 F2 D2 |
[V:2] A4 F4 | F4 D4 |
[V:3] F,4 D4 | D,4 A,,4 |
% ===== MIDDLE ENTRY 2: Subject in A minor, Bass; static pedal above =====
[V:1] e8 | e8 |
[V:2] c8 | c8 |
[V:3] A,2 C2 E2 D C | B,2 A,2 ^G,2 A,2 |
% ===== STRETTO: Subject in Bass, answered one measure later in Soprano (tonic) =====
[V:1] z8 | d2 f2 a2 g f | e2 d2 ^c2 d2 |
[V:2] A4 D4 | z4 A4 | F4 D4 |
[V:3] D,2 F,2 A,2 G, F, | E,2 D,2 ^C,2 D,2 | z8 |
% ===== FINAL CADENCE: dominant pedal, descent, Picardy third =====
[V:1] d2 c2 B2 A2 | G2 F2 E2 ^C2 | D8 |]
[V:2] F2 E2 D2 C2 | _B,2 A,2 G,2 E,2 | ^F,4 A,4 |]
[V:3] A,,4 A,4 | D,,4 D4 | D,,8 |]`
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

  playNote(freq, startTime, duration, instrument = "harpsichord", gainLevel = 0.25) {
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
      osc2.frequency.setValueAtTime(freq * 2, startTime); // Octave octave sparkle

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
      // Grand Piano: warm fundamental + subtle upper partials, gentle decay
      const osc = ctx.createOscillator();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, startTime);

      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(freq * 4, startTime);
      filter.frequency.exponentialRampToValueAtTime(freq * 1.5, startTime + duration);

      osc.connect(filter);
      filter.connect(oscGain);

      oscGain.gain.setValueAtTime(0.001, startTime);
      oscGain.gain.exponentialRampToValueAtTime(gainLevel, startTime + 0.015);
      oscGain.gain.exponentialRampToValueAtTime(gainLevel * 0.6, startTime + duration * 0.3);
      oscGain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

      osc.start(startTime);
      osc.stop(startTime + duration + 0.05);
    } else if (instrument === "organ") {
      // Drawbar Organ: warm sine + overtone mixture, sustaining
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

      oscGain.gain.setValueAtTime(0.001, startTime);
      oscGain.gain.linearRampToValueAtTime(gainLevel * 0.8, startTime + 0.02);
      oscGain.gain.setValueAtTime(gainLevel * 0.7, startTime + duration - 0.02);
      oscGain.gain.linearRampToValueAtTime(0.0001, startTime + duration);

      osc1.start(startTime);
      osc2.start(startTime);
      osc1.stop(startTime + duration + 0.05);
      osc2.stop(startTime + duration + 0.05);
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
    const noteRegex = /([_=\^]*[A-Ga-gzZ][,\']*)(\d*(?:\/\d*)?)/g;

    for (const [vName, contentList] of Object.entries(voiceLines)) {
      const fullVoiceStr = contentList.join(' ');
      const rawBars = fullVoiceStr.split('|').filter(b => b.trim() && b.trim() !== ']' && b.trim() !== '||');
      
      let currentTime = 0;
      for (const bar of rawBars) {
        const clean = bar.replace(/"[^"]*"/g, '').replace(/\[/g, '').replace(/\]/g, '');
        let match;
        noteRegex.lastIndex = 0;
        while ((match = noteRegex.exec(clean)) !== null) {
          const pitchStr = match[1];
          const durStr = match[2];
          let durFactor = 1.0;
          if (durStr) {
            if (durStr.includes('/')) {
              const p = durStr.split('/');
              durFactor = (parseFloat(p[0]) || 1.0) / (parseFloat(p[1]) || 2.0);
            } else {
              durFactor = parseFloat(durStr);
            }
          }
          const durationSeconds = durFactor * unitInSeconds;

          if (!pitchStr.toLowerCase().startsWith('z')) {
            const parsedPitch = parseAbcPitch(pitchStr);
            if (parsedPitch) {
              allEvents.push({
                voice: vName,
                time: currentTime,
                duration: durationSeconds * 0.95, // slight articulation gap
                freq: parsedPitch.freq,
                midi: parsedPitch.midi
              });
            }
          }
          currentTime += durationSeconds;
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
      this.playNote(ev.freq, noteStart, ev.duration, instrument);
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
  const stopBtn = card.querySelector('.btn-stop');
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

  // Play button
  if (playBtn) {
    playBtn.addEventListener('click', () => {
      if (synth.isPlaying && synth.currentTuneId === comp.id) {
        synth.stop();
        playBtn.innerHTML = '▶ Play Score';
        return;
      }

      // Reset any other play buttons
      document.querySelectorAll('.btn-play').forEach(b => b.innerHTML = '▶ Play Score');

      const currentTempo = tempoSlider ? parseInt(tempoSlider.value) : comp.tempo;
      const currentInst = instSelect ? instSelect.value : comp.instrument;

      playBtn.innerHTML = '⏹ Stop';
      synth.playTune(comp.id, comp.abc, currentTempo, currentInst, () => {
        playBtn.innerHTML = '▶ Play Score';
      });
    });
  }

  // Stop button
  if (stopBtn) {
    stopBtn.addEventListener('click', () => {
      synth.stop();
      document.querySelectorAll('.btn-play').forEach(b => b.innerHTML = '▶ Play Score');
    });
  }
}

function setupSandbox() {
  const sandboxText = document.getElementById('sandboxAbcText');
  const renderBtn = document.getElementById('sandboxRenderBtn');
  const playBtn = document.getElementById('sandboxPlayBtn');
  const stopBtn = document.getElementById('sandboxStopBtn');
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
        return;
      }
      document.querySelectorAll('.btn-play').forEach(b => b.innerHTML = '▶ Play Score');
      const bpm = tempoSlider ? parseInt(tempoSlider.value) : 112;
      const inst = instSelect ? instSelect.value : 'harpsichord';
      playBtn.innerHTML = '⏹ Stop';
      synth.playTune('sandbox', sandboxText.value, bpm, inst, () => {
        playBtn.innerHTML = '▶ Play Sandbox';
      });
    });
  }

  if (stopBtn) {
    stopBtn.addEventListener('click', () => {
      synth.stop();
      if (playBtn) playBtn.innerHTML = '▶ Play Sandbox';
    });
  }
}
