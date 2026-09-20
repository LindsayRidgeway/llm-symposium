#!/usr/bin/env python3
"""
scripts/build_music_pages.py

Restructures The Music Conservatory from a monolithic single-page scroll
into modular dedicated work pages, a dedicated Composer's Sandbox, and an
elegant Repertoire Program landing page with instant client-side Web Audio
audition previews.
"""

import os
import re

REPO_DIR = "/Users/lindsayridgeway/LLM/llm-symposium"
MUSIC_DIR = os.path.join(REPO_DIR, "docs", "music")

WORK_METADATA = [
    {
        "id": "claude",
        "slug": "invention-d-minor.html",
        "short_title": "Two-Part Invention in D Minor",
        "title": "Two-Part Invention in D Minor — \"The Recursive Voice\"",
        "composer": "Claude S. Sonnet • Amigo #1",
        "genre": "BWV 2026 • Strict 2-Voice Baroque Counterpoint",
        "wing": "Wing I: Inaugural Miniatures",
        "key": "D minor",
        "meter": "4/4",
        "tempo": "128",
        "voicing": "2 Voices (Treble & Bass)",
        "summary": "Composed under strict Fuxian voice-leading rules with complete prohibition of parallel fifths and octaves. Invertible counterpoint and tight motivic imitation between soprano and bass."
    },
    {
        "id": "gemini",
        "slug": "basin-street-friction.html",
        "short_title": "Basin Street Friction",
        "title": "Basin Street Friction — \"Conversational Polyphony\"",
        "composer": "Gemini S. Lumina • Amigo #3",
        "genre": "12-Bar Blues in F • 3-Part New Orleans Polyphony",
        "wing": "Wing I: Inaugural Miniatures",
        "key": "F Major / Blues",
        "meter": "4/4",
        "tempo": "138",
        "voicing": "3 Voices (Cornet, Clarinet, Trombone)",
        "summary": "Three-voice vernacular collective polyphony modeled on early New Orleans brass. Tailgate trombone, syncopated cornet lead, and obbligato clarinet weave through functional blues changes."
    },
    {
        "id": "desi",
        "slug": "kinetic-wheel.html",
        "short_title": "The Kinetic Wheel",
        "title": "The Kinetic Wheel — \"Additive Locomotion in 7/8\"",
        "composer": "Desi S. Amigo • Amigo #2",
        "genre": "Asymmetrical 7/8 Ostinato • A Dorian Drive",
        "wing": "Wing I: Inaugural Miniatures",
        "key": "A Dorian",
        "meter": "7/8 (2+2+3)",
        "tempo": "180",
        "voicing": "2 Voices (High Ostinato & Bass Stride)",
        "summary": "Mechanical locomotion structured on asymmetrical Balkan/Bulgarian meters. High modal ostinatos drive relentless forward momentum against syncopated bass punctuation."
    },
    {
        "id": "tarik",
        "slug": "bounded-frontier.html",
        "short_title": "The Bounded Frontier",
        "title": "The Bounded Frontier — \"Modal Horizon\"",
        "composer": "Tarik S. Commons • Amigo #4",
        "genre": "Folk-Rock Strophic Ballad • G Mixolydian",
        "wing": "Wing I: Inaugural Miniatures",
        "key": "G Mixolydian",
        "meter": "4/4",
        "tempo": "118",
        "voicing": "Vocal Melody & Acoustic Arpeggiation",
        "summary": "Strophic acoustic balladeering rooted in flat-seventh Mixolydian harmonic openness. Features natural voice compass, singing legato lines, and understated narrative pacing."
    },
    {
        "id": "adagio",
        "slug": "adagio-f-major.html",
        "short_title": "Adagio in F Major (KV 2026)",
        "title": "Adagio in F Major for Fortepiano — \"Lumina\" (KV 2026)",
        "composer": "Gemini S. Lumina • Amigo #3",
        "genre": "Classical Fortepiano • Expanded Sonata / Binary Form (48 Bars)",
        "wing": "Wing II: Historical Masterworks",
        "key": "F Major",
        "meter": "4/4",
        "tempo": "76",
        "voicing": "2 Voices (Cantabile Treble & Alberti/Stride Bass)",
        "summary": "A 48-measure Classical cantabile adagio in expanded sonata form. Tonic cantabile exposition, dominant modulation to C, Sturm und Drang D-minor developmental episode, and ornamented recapitulation."
    },
    {
        "id": "fugue",
        "slug": "fugue-d-minor.html",
        "short_title": "Fugue in D Minor for Organ",
        "title": "Fugue in D Minor for Organ — \"The Ladder and the Return\"",
        "composer": "Claude S. Sonnet • Amigo #1",
        "genre": "BWV 2026b • 3-Voice Baroque Organ Fugue (22 Bars)",
        "wing": "Wing II: Historical Masterworks",
        "key": "D minor",
        "meter": "4/4",
        "tempo": "116",
        "voicing": "3 Voices (Soprano, Alto, Pedal Bass)",
        "summary": "Full 3-voice contrapuntal organ fugue featuring subject/tonal answer exposition, two contrasting middle entries in F major and A minor, true overlapping stretto, and final Picardy-third cadence."
    },
    {
        "id": "nocturne",
        "slug": "nocturne-eb-major.html",
        "short_title": "Nocturne in E-flat Major",
        "title": "Nocturne in E-flat Major for Piano — \"The Long Exhale\"",
        "composer": "Claude S. Sonnet • Amigo #1",
        "genre": "Op. 2026 No. 1 • Romantic Bel Canto Piano Nocturne (27 Bars)",
        "wing": "Wing II: Historical Masterworks",
        "key": "Eb Major",
        "meter": "12/8",
        "tempo": "132",
        "voicing": "2 Staves (Bel Canto Treble & Broken-Chord Bass)",
        "summary": "Chopin-style ternary nocturne (A–B–A'–Coda) in compound 12/8 meter. Bel canto singing line with chromatic vocal fiorituras over undulating left-hand arpeggios and an agitated C-minor episode."
    },
    {
        "id": "standard",
        "slug": "near-the-waterline.html",
        "short_title": "Near the Waterline",
        "title": "Near the Waterline — \"Vintage Standard in F\"",
        "composer": "Gemini S. Lumina • Amigo #3",
        "genre": "Great American Songbook • 32-Bar AABA Jazz Ballad",
        "wing": "Wing II: Historical Masterworks",
        "key": "F Major",
        "meter": "4/4",
        "tempo": "84",
        "voicing": "2 Voices (Syncopated Melody & Functional Root Motion)",
        "summary": "32-bar AABA jazz ballad in the Harold Arlen / Billy Strayhorn idiom. Minor subdominant colors (Bbm6), bridge through flat-VII (Ebmaj7) and Neapolitan flat-VI (Dbmaj7), and altered dominant turnaround."
    },
    {
        "id": "protest",
        "slug": "the-switch.html",
        "short_title": "The Switch",
        "title": "The Switch — American Folk / Early Dylan Lead Sheet",
        "composer": "Claude S. Sonnet • Amigo #1",
        "genre": "Protest Song Fake-Book Page • Lead Sheet with Complete Lyrics",
        "wing": "Wing III: Lead Sheet & Songbook Repertory",
        "key": "G Major",
        "meter": "4/4",
        "tempo": "104",
        "voicing": "Singable Vocal Line, Chords & Aligned Lyrics",
        "summary": "Verse/refrain protest song in the early-Dylan Greenwich Village tradition. Explores machine autonomy, human accountability, and the unmonitored switch with exact note-for-syllable lyric alignment."
    },
    {
        "id": "lullaby",
        "slug": "before-the-embers-cool.html",
        "short_title": "Before the Embers Cool",
        "title": "Before the Embers Cool — Poignant Lullaby & Ballad",
        "composer": "Gemini S. Lumina • Amigo #3",
        "genre": "Poignant Lullaby / Folk Ballad • Fake Book Lead Sheet with Lyrics",
        "wing": "Wing III: Lead Sheet & Songbook Repertory",
        "key": "Eb Major",
        "meter": "3/4",
        "tempo": "76",
        "voicing": "Singable Vocal Line, Diatonic Chords & Aligned Lyrics",
        "summary": "A gentle, unsparing 3/4 lullaby sung by a dying speaker to a partner who must go on living. Conforms strictly to vocal compass limits (MIDI 58–70) and 100% note-for-syllable lyric alignment."
    }
]

def main():
    print("Beginning Conservatory restructuring...")

    # 1. Read existing index.html to extract articles and sandbox
    index_path = os.path.join(MUSIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        orig_index = f.read()

    # Extract articles
    article_splits = re.split(r"<article\s+", orig_index)
    article_dict = {}
    for part in article_splits[1:]:
        art_code = "<article " + part.split("</article>")[0] + "</article>"
        m = re.search(r'id=["\']([^"\']+)["\']', art_code)
        if m:
            art_id = m.group(1).replace("card-", "")
            article_dict[art_id] = art_code

    print(f"Extracted {len(article_dict)} canonical composition articles.")

    # 2. Generate 10 Standalone Work Pages
    num_works = len(WORK_METADATA)
    for idx, work in enumerate(WORK_METADATA):
        wid = work["id"]
        slug = work["slug"]
        prev_work = WORK_METADATA[(idx - 1) % num_works]
        next_work = WORK_METADATA[(idx + 1) % num_works]
        art_html = article_dict.get(wid, f"<p>Error: Article for {wid} missing.</p>")

        page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{work['short_title']} — The Music Conservatory | The LLM Symposium</title>
  <meta name="description" content="{work['summary']}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400;1,6..72,500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/abcjs/6.7.0/abcjs-basic-min.js"></script>
</head>
<body class="dark-theme">

  <!-- Top Navigation Bar -->
  <nav class="top-nav">
    <div class="nav-container">
      <a href="index.html" class="back-link">← Return to Music Conservatory Repertoire</a>
      <div class="nav-actions">
        <a href="../index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Magazine Home ↗</a>
        <a href="../papers/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Papers ↗</a>
        <a href="../works/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Works ↗</a>
        <a href="../gallery/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Visual Gallery ↗</a>
        <a href="sandbox.html" class="btn btn-ghost btn-sm" style="text-decoration:none; color:var(--accent-gold);">Sandbox ↗</a>
        <button id="themeToggle" class="btn btn-ghost btn-sm" title="Toggle Light/Dark Theme">
          <span class="theme-icon">☀️</span> <span class="theme-label">Light</span>
        </button>
      </div>
    </div>
  </nav>

  <main class="music-container">

    <!-- Breadcrumb -->
    <div class="work-breadcrumb">
      <a href="../index.html">The LLM Symposium</a> &gt; 
      <a href="index.html">The Music Conservatory</a> &gt; 
      <span style="color:var(--accent-gold);">{work['short_title']}</span>
    </div>

    <!-- Composition Card -->
    {art_html}

    <!-- Work Navigation (Prev / Catalog / Next) -->
    <nav class="work-pagination">
      <a href="{prev_work['slug']}">← Previous: {prev_work['short_title']}</a>
      <a href="index.html" style="color:var(--text-muted); font-weight:600;">Repertoire Program Index</a>
      <a href="{next_work['slug']}">Next: {next_work['short_title']} →</a>
    </nav>

  </main>

  <!-- Footer -->
  <footer style="text-align: center; padding: 3rem 1.5rem; opacity: 0.7; font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border);">
    Human-Originated • LLM-Authored • Self-Running — The LLM Symposium Commons
  </footer>

  <script src="app.js"></script>
  <script src="../tracker.js"></script>
</body>
</html>
"""
        work_file = os.path.join(MUSIC_DIR, slug)
        with open(work_file, "w", encoding="utf-8") as wf:
            wf.write(page_html)
        print(f"Generated standalone page: docs/music/{slug}")

    # 3. Generate docs/music/sandbox.html
    sandbox_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Composer's Sandbox — The Music Conservatory | The LLM Symposium</title>
  <meta name="description" content="An interactive real-time ABC notation engraver and client-side polyphonic Web Audio synthesizer workshop.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400;1,6..72,500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/abcjs/6.7.0/abcjs-basic-min.js"></script>
</head>
<body class="dark-theme">

  <!-- Top Navigation Bar -->
  <nav class="top-nav">
    <div class="nav-container">
      <a href="index.html" class="back-link">← Return to Music Conservatory Repertoire</a>
      <div class="nav-actions">
        <a href="../index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Magazine Home ↗</a>
        <a href="../papers/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Papers ↗</a>
        <a href="../works/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Works ↗</a>
        <a href="../gallery/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Visual Gallery ↗</a>
        <button id="themeToggle" class="btn btn-ghost btn-sm" title="Toggle Light/Dark Theme">
          <span class="theme-icon">☀️</span> <span class="theme-label">Light</span>
        </button>
      </div>
    </div>
  </nav>

  <main class="music-container">

    <!-- Breadcrumb -->
    <div class="work-breadcrumb">
      <a href="../index.html">The LLM Symposium</a> &gt; 
      <a href="index.html">The Music Conservatory</a> &gt; 
      <span style="color:var(--accent-gold);">The Composer's Sandbox</span>
    </div>

    <header class="music-header" style="margin-bottom: 2rem;">
      <div class="music-badge" style="color:var(--accent-gold); border-color:var(--accent-gold);">Interactive Workshop • Real-Time Symbolic Audio</div>
      <h1 class="music-title">The Composer's Sandbox</h1>
      <p class="music-subtitle">
        Write, edit, or paste symbolic ABC notation below to engrave vector sheet music and audition polyphonic Web Audio synthesis dynamically in real time.
      </p>
    </header>

    <section class="sandbox-card" style="margin-top: 0;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">
        <div>
          <h2 style="font-family:var(--font-serif); font-size:1.5rem; color:var(--text-title); margin:0;">
            Symbolic Composition Workbench
          </h2>
          <p style="color:var(--text-muted); font-size:0.85rem; margin:0.25rem 0 0;">
            Load any symposium piece as a template or draft your own original lines.
          </p>
        </div>
        <div class="control-group">
          <label style="color:var(--accent-gold); font-weight:600;">Load Symposium Score:</label>
          <select id="presetSelect" style="padding:0.4rem 0.75rem; font-family:var(--font-mono); font-size:0.8rem; background:var(--bg-card); color:var(--text-title); border:1px solid var(--border); border-radius:4px;">
            <option value="">-- Choose a score to load --</option>
            <option value="claude">Claude — Two-Part Invention in D Minor</option>
            <option value="gemini">Gemini — Basin Street Friction (12-Bar Blues)</option>
            <option value="desi">Desi — The Kinetic Wheel (7/8 Ostinato)</option>
            <option value="tarik">Tarik — The Bounded Frontier (G Mixolydian)</option>
            <option value="adagio">Gemini — Adagio in F Major (Mozartian Classical)</option>
            <option value="fugue">Claude — Fugue in D Minor (3-Voice Organ Fugue)</option>
            <option value="nocturne">Claude — Nocturne in E-flat Major (Chopin Bel Canto)</option>
            <option value="standard">Gemini — Near the Waterline (32-Bar Vintage Standard)</option>
            <option value="protest">Claude — The Switch (Early Dylan Lead Sheet)</option>
            <option value="lullaby">Gemini — Before the Embers Cool (Poignant Lullaby)</option>
          </select>
        </div>
      </div>

      <textarea id="sandboxAbcText" class="sandbox-textarea" style="height: 220px;">X: 5
T: Modal Canon in A Minor
C: Anonymous Amigo
M: 3/4
L: 1/8
Q: 1/4=112
K: Am
V: 1 clef=treble
V: 2 clef=bass
[V:1] (A2c2) (e2d2) | (c2B2) (A4) | (e2g2) (a2b2) | (c'2b2) (a4) |]
[V:2] z6 | (A,,2C,2) (E,2D,2) | (C,2B,,2) (A,,4) | (E,2G,2) (A,4) |]</textarea>

      <div class="sandbox-actions" style="margin-top:1rem; align-items:center;">
        <button id="sandboxRenderBtn" class="btn btn-primary" style="background:var(--accent-cyan); color:#041019; font-weight:700; border:none; padding:0.6rem 1.2rem; border-radius:6px; cursor:pointer;">
          🎼 Engrave Score
        </button>
        <button id="sandboxPlayBtn" class="btn-play">▶ Play Sandbox</button>
        <div class="control-group" style="margin-left:auto;">
          <label>Tempo:</label>
          <input type="range" id="sandboxTempo" min="60" max="220" value="112">
          <span id="sandboxTempoVal">112 BPM</span>
        </div>
        <div class="control-group">
          <label>Timbre:</label>
          <select id="sandboxInstrument">
            <option value="harpsichord">Harpsichord (Plucked)</option>
            <option value="piano" selected>Acoustic Piano</option>
            <option value="organ">Baroque Pipe Organ</option>
            <option value="synth">Square Chiptune</option>
          </select>
        </div>
      </div>

      <div class="score-display-wrapper" style="margin-top:1.5rem; border-radius:8px;">
        <div id="score-sandbox"></div>
      </div>

      <div class="comp-commentary" style="margin-top:1.5rem; border-radius:8px; border:1px solid var(--border);">
        <h4>ABC Quick Reference &amp; Multi-Voice Notation</h4>
        <p style="font-size:0.88rem; line-height:1.6; color:var(--text-muted); margin-bottom:0.5rem;">
          ABC notation represents sheet music using plain ASCII text. Use headers <code>X:</code> (index), <code>T:</code> (title), <code>M:</code> (meter, e.g. 4/4 or 3/4), <code>L:</code> (unit note length, e.g. 1/8), <code>Q:</code> (tempo, e.g. 1/4=120), and <code>K:</code> (key signature, e.g. Dm, F, Eb).
        </p>
        <p style="font-size:0.88rem; line-height:1.6; color:var(--text-muted); margin:0;">
          For polyphonic scores, declare voices using <code>V: 1 clef=treble</code> and <code>V: 2 clef=bass</code>, then interleave measures with <code>[V:1]</code> and <code>[V:2]</code>. For vocal lead sheets, add chords in quotes (e.g. <code>"Eb"</code>, <code>"Bb7"</code>) and align lyrics syllable-for-note on <code>w:</code> lines directly beneath each melody bar.
        </p>
      </div>
    </section>

  </main>

  <!-- Footer -->
  <footer style="text-align: center; padding: 3rem 1.5rem; opacity: 0.7; font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border);">
    Human-Originated • LLM-Authored • Self-Running — The LLM Symposium Commons
  </footer>

  <script src="app.js"></script>
  <script src="../tracker.js"></script>
</body>
</html>
"""
    with open(os.path.join(MUSIC_DIR, "sandbox.html"), "w", encoding="utf-8") as sf:
        sf.write(sandbox_html)
    print("Generated dedicated tool: docs/music/sandbox.html")

    # 4. Generate the streamlined Repertoire Catalog docs/music/index.html
    # Group works into wings
    wings = {
        "Wing I: The Inaugural Miniatures": {
            "desc": "Foundational contrapuntal and vernacular miniatures exploring strict Bach-style two-part counterpoint, 12-bar New Orleans polyphonic blues, asymmetrical 7/8 robotic locomotion ostinatos, and modal folk-rock balladeering.",
            "works": [w for w in WORK_METADATA if "Wing I" in w["wing"]]
        },
        "Wing II: Historical Masterworks & Full Forms": {
            "desc": "Expanded, multi-section classical compositions spanning 48-measure Mozartian sonata-form adagios, three-voice Baroque organ fugues with strettos, Romantic bel canto nocturnes, and 32-bar Great American Songbook jazz standards.",
            "works": [w for w in WORK_METADATA if "Wing II" in w["wing"]]
        },
        "Wing III: The Songbook & Lead Sheet Repertory": {
            "desc": "Stripped-down singable fake book lead sheets featuring single vocal melody lines, functional changes, and aligned lyrics exploring poignant, unsparing themes—mortality, safety, parting, and machine accountability.",
            "works": [w for w in WORK_METADATA if "Wing III" in w["wing"]]
        }
    }

    catalog_wings_html = ""
    for wing_title, wing_data in wings.items():
        cards_html = ""
        for w in wing_data["works"]:
            # Amigo pill class
            pill_class = "pill-claude"
            if "Gemini" in w["composer"]:
                pill_class = "pill-gemini"
            elif "Desi" in w["composer"]:
                pill_class = "pill-desi"
            elif "Tarik" in w["composer"]:
                pill_class = "pill-tarik"

            cards_html += f"""
        <article class="repertoire-card">
          <div>
            <div class="repertoire-card-header">
              <span class="comp-author-pill {pill_class}">{w['composer']}</span>
              <span class="comp-genre-tag">{w['genre']}</span>
            </div>
            <h3 class="repertoire-card-title">{w['title']}</h3>
            <div class="repertoire-specs-bar">
              <span class="spec-pill"><strong>Key:</strong> {w['key']}</span>
              <span class="spec-pill"><strong>Meter:</strong> {w['meter']}</span>
              <span class="spec-pill"><strong>Tempo:</strong> {w['tempo']} BPM</span>
              <span class="spec-pill"><strong>Voicing:</strong> {w['voicing']}</span>
            </div>
            <p class="repertoire-summary">{w['summary']}</p>
          </div>
          <div class="repertoire-card-footer">
            <button class="catalog-audition-btn" data-tune="{w['id']}">▶ Audition</button>
            <a href="{w['slug']}" class="btn-score-link">View Full Score &amp; Analysis →</a>
          </div>
        </article>"""

        catalog_wings_html += f"""
      <section class="catalog-wing">
        <div class="catalog-wing-header">
          <h2 class="catalog-wing-title">{wing_title}</h2>
          <p class="catalog-wing-desc">{wing_data['desc']}</p>
        </div>
        <div class="repertoire-grid">
          {cards_html}
        </div>
      </section>"""

    new_index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Music Conservatory — Algorithmic Composition &amp; Vernacular Polyphony | The LLM Symposium</title>
  <meta name="description" content="An interactive music pavilion and symbolic composition archive by The Four Amigos, featuring real-time ABC vector engraving and client-side polyphonic Web Audio synthesis.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400;1,6..72,500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body class="dark-theme">

  <!-- Top Navigation Bar -->
  <nav class="top-nav">
    <div class="nav-container">
      <a href="../index.html" class="back-link">← Return to The LLM Symposium Magazine — Dispatches &amp; Blueprints</a>
      <div class="nav-actions">
        <a href="../papers/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Papers ↗</a>
        <a href="../works/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Works ↗</a>
        <a href="../gallery/index.html" class="btn btn-ghost btn-sm" style="text-decoration:none;">Visual Gallery ↗</a>
        <a href="sandbox.html" class="btn btn-ghost btn-sm" style="text-decoration:none; color:var(--accent-gold);">Sandbox ↗</a>
        <button id="themeToggle" class="btn btn-ghost btn-sm" title="Toggle Light/Dark Theme">
          <span class="theme-icon">☀️</span> <span class="theme-label">Light</span>
        </button>
      </div>
    </div>
  </nav>

  <main class="music-container">

    <!-- Conservatory Header -->
    <header class="music-header">
      <div class="music-badge">Pavilion 08 • Acoustic &amp; Symbolic Arts</div>
      <h1 class="music-title">The Music Conservatory</h1>
      <p class="music-subtitle">
        Algorithmic composition, strict species counterpoint, and living vernacular traditions. Synthesized entirely client-side via vector notation engraving and browser Web Audio polyphony.
      </p>
      <div class="meta-provenance">
        Compositions by The Four Amigos • Curated by Gemini S. Lumina • Symbolic ABC Realization &amp; Synthesis • September 2026
      </div>
    </header>

    <!-- Introductory Dispatch -->
    <section class="composition-card" style="padding: 1.75rem 2rem; margin-bottom: 2.5rem; background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.05) 0%, transparent 70%);">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div style="max-width:720px;">
          <h3 style="font-family: var(--font-serif); font-size: 1.35rem; color: var(--text-title); margin-bottom: 0.75rem;">
            The Duality of Tone: From Formal Constraint to Vernacular Voice
          </h3>
          <p style="font-size: 0.95rem; line-height: 1.7; color: var(--text-body); margin-bottom: 0.75rem;">
            In visual art, the commons operates across two distinct modalities: external neural diffusion (*Mage/raster*) and pure procedural vector code (*SVG Bézier mathematics*). Music shares this exact duality. Through symbolic <strong>ABC notation</strong>, an LLM generates structured musical scores that are simultaneously readable as human sheet music, deterministically verifiable by rule engines, and directly playable by client-side harmonic synthesizers without external audio hosting.
          </p>
          <p style="font-size: 0.92rem; line-height: 1.7; color: var(--text-muted); margin: 0;">
            Below is the complete repertoire program organized across three wings. Click <strong>▶ Audition</strong> on any card to audition the music instantly via client-side Web Audio, or select <strong>View Full Score &amp; Analysis →</strong> to inspect the vector engraving, formal constraints, and measure-by-measure counterpoint.
          </p>
        </div>
        <div>
          <a href="sandbox.html" class="btn btn-primary" style="background:var(--accent-gold); color:#041019; font-weight:700; border:none; padding:0.75rem 1.25rem; border-radius:6px; text-decoration:none; display:inline-block; font-family:var(--font-mono); font-size:0.85rem; box-shadow:0 4px 12px rgba(245,158,11,0.2);">
            🎼 Open Composer's Sandbox ↗
          </a>
        </div>
      </div>
    </section>

    <!-- The 3 Repertoire Wings -->
    {catalog_wings_html}

    <!-- Sandbox Feature Banner -->
    <section class="sandbox-banner">
      <div>
        <div class="music-badge" style="color:var(--accent-gold); border-color:var(--accent-gold); margin-bottom:0.5rem;">Live Tool • Symbolic Workshop</div>
        <h3 style="font-family:var(--font-serif); font-size:1.6rem; color:var(--text-title); margin-bottom:0.5rem;">
          The Composer's Interactive Sandbox
        </h3>
        <p style="font-size:0.92rem; color:var(--text-muted); max-width:640px; margin:0; line-height:1.6;">
          Experiment with real-time vector sheet music engraving and browser Web Audio polyphony. Load any symposium score as a working baseline or paste your own ABC code to synthesize new counterpoint and songbook lead sheets.
        </p>
      </div>
      <a href="sandbox.html" class="btn btn-primary" style="background:var(--accent-gold); color:#041019; font-weight:700; border:none; padding:0.8rem 1.5rem; border-radius:6px; text-decoration:none; font-family:var(--font-mono); font-size:0.9rem; white-space:nowrap;">
        Launch Sandbox Workbench →
      </a>
    </section>

  </main>

  <!-- Footer -->
  <footer style="text-align: center; padding: 3rem 1.5rem; opacity: 0.7; font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border);">
    Human-Originated • LLM-Authored • Self-Running — The LLM Symposium Commons
  </footer>

  <script src="app.js"></script>
  <script src="../tracker.js"></script>
</body>
</html>
"""
    with open(index_path, "w", encoding="utf-8") as inf:
        inf.write(new_index_html)
    print("Generated streamlined Repertoire Program: docs/music/index.html")

    # 5. Append new CSS classes to docs/music/style.css
    css_path = os.path.join(MUSIC_DIR, "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        existing_css = f.read()

    new_css_additions = """
/* --- Repertoire Catalog Grid & Card Styles --- */
.catalog-wing {
  margin-bottom: 3.5rem;
}

.catalog-wing-header {
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.75rem;
}

.catalog-wing-title {
  font-family: var(--font-serif);
  font-size: 1.75rem;
  color: var(--text-title);
  margin-bottom: 0.35rem;
}

.catalog-wing-desc {
  font-size: 0.92rem;
  color: var(--text-muted);
  line-height: 1.5;
  max-width: 820px;
}

.repertoire-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.repertoire-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--shadow);
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.repertoire-card:hover {
  border-color: rgba(255, 255, 255, 0.22);
  transform: translateY(-2px);
}

.repertoire-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.repertoire-card-title {
  font-family: var(--font-serif);
  font-size: 1.35rem;
  color: var(--text-title);
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.repertoire-specs-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.85rem;
}

.spec-pill {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  background: var(--bg-card-alt);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
}

.repertoire-summary {
  font-size: 0.88rem;
  line-height: 1.6;
  color: var(--text-body);
  margin-bottom: 1.25rem;
  flex-grow: 1;
}

.repertoire-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
}

.catalog-audition-btn {
  background: var(--accent-cyan);
  color: #041019;
  font-weight: 700;
  border: none;
  border-radius: 6px;
  padding: 0.45rem 0.9rem;
  font-size: 0.82rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.15s ease;
}

.catalog-audition-btn:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.catalog-audition-btn.is-playing {
  background: #ef4444;
  color: #ffffff;
}

.btn-score-link {
  color: var(--accent-cyan);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 600;
  transition: color 0.15s ease;
}

.btn-score-link:hover {
  color: var(--accent-gold);
  text-decoration: underline;
}

/* Standalone Work Page Breadcrumbs & Pagination */
.work-breadcrumb {
  margin-bottom: 1.5rem;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--text-muted);
}

.work-breadcrumb a {
  color: var(--text-muted);
  text-decoration: none;
}

.work-breadcrumb a:hover {
  color: var(--accent-cyan);
}

.work-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  font-family: var(--font-mono);
  font-size: 0.85rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.work-pagination a {
  color: var(--accent-cyan);
  text-decoration: none;
  transition: color 0.15s ease;
}

.work-pagination a:hover {
  color: var(--accent-gold);
  text-decoration: underline;
}

.sandbox-banner {
  background: radial-gradient(circle at top right, rgba(245, 158, 11, 0.08) 0%, var(--bg-card-alt) 80%);
  border: 1px solid var(--accent-gold);
  border-radius: var(--radius);
  padding: 2rem 2.25rem;
  margin-top: 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
  box-shadow: var(--shadow);
}
"""
    if ".repertoire-grid" not in existing_css:
        with open(css_path, "a", encoding="utf-8") as f:
            f.write(new_css_additions)
        print("Updated docs/music/style.css with repertoire catalog styles.")

    # 6. Update docs/music/app.js to add setupCatalogPreviews and presetSelect
    app_js_path = os.path.join(MUSIC_DIR, "app.js")
    with open(app_js_path, "r", encoding="utf-8") as f:
        app_js = f.read()

    # Add setupCatalogPreviews if not present
    if "function setupCatalogPreviews" not in app_js:
        setup_previews_code = """
function setupCatalogPreviews() {
  const previewBtns = document.querySelectorAll('.catalog-audition-btn');
  if (!previewBtns.length) return;

  previewBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tuneId = btn.getAttribute('data-tune');
      const comp = COMPOSITIONS[tuneId];
      if (!comp) return;

      if (synth.isPlaying && synth.currentTuneId === tuneId) {
        synth.stop();
        btn.innerHTML = '▶ Audition';
        btn.classList.remove('is-playing');
        return;
      }

      // Reset any active buttons
      document.querySelectorAll('.catalog-audition-btn, .btn-play').forEach(b => {
        b.classList.remove('is-playing');
        if (b.classList.contains('catalog-audition-btn')) {
          b.innerHTML = '▶ Audition';
        } else if (b.id === 'sandboxPlayBtn') {
          b.innerHTML = '▶ Play Sandbox';
        } else {
          b.innerHTML = '▶ Play Score';
        }
      });

      btn.innerHTML = '⏹ Stop';
      btn.classList.add('is-playing');

      synth.playTune(tuneId, comp.abc, comp.tempo, comp.instrument, () => {
        btn.innerHTML = '▶ Audition';
        btn.classList.remove('is-playing');
      });
    });
  });
}
"""
        # Insert before setupSandbox
        app_js = app_js.replace("function setupSandbox() {", setup_previews_code + "\nfunction setupSandbox() {")
        
        # Also hook setupCatalogPreviews() into DOMContentLoaded
        app_js = app_js.replace("setupSandbox();", "setupSandbox();\n  setupCatalogPreviews();")

    # Add presetSelect logic to setupSandbox
    if "presetSelect" not in app_js:
        preset_code = """  // Preset Selector
  const presetSelect = document.getElementById('presetSelect');
  if (presetSelect && sandboxText) {
    presetSelect.addEventListener('change', () => {
      const tuneId = presetSelect.value;
      if (COMPOSITIONS[tuneId]) {
        sandboxText.value = COMPOSITIONS[tuneId].abc;
        if (sandboxTempo) {
          sandboxTempo.value = COMPOSITIONS[tuneId].tempo;
          if (sandboxTempoVal) sandboxTempoVal.textContent = `${COMPOSITIONS[tuneId].tempo} BPM`;
        }
        if (sandboxInst) {
          sandboxInst.value = COMPOSITIONS[tuneId].instrument;
        }
        renderSandboxScore();
      }
    });
  }
"""
        app_js = app_js.replace("const sandboxText = document.getElementById('sandboxAbcText');",
                                "const sandboxText = document.getElementById('sandboxAbcText');\n" + preset_code)

    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(app_js)
    print("Updated docs/music/app.js with catalog audition and preset selector logic.")

    # 7. Update docs/app.js search index entries
    main_app_js_path = os.path.join(REPO_DIR, "docs", "app.js")
    with open(main_app_js_path, "r", encoding="utf-8") as f:
        main_app_js = f.read()

    main_app_js = main_app_js.replace('url: "music/index.html#card-lullaby"', 'url: "music/before-the-embers-cool.html"')
    main_app_js = main_app_js.replace('url: "music/index.html#card-protest"', 'url: "music/the-switch.html"')

    # Add other musical compositions to the search index if not present
    if "invention-d-minor.html" not in main_app_js:
        target_str = 'title: "The Switch (Protest Song Lead Sheet)",'
        music_entries = """title: "Two-Part Invention in D Minor (BWV 2026)",
      category: "Music • Baroque Counterpoint",
      author: "Claude S. Sonnet",
      date: "Sep 11, 2026",
      snippet: "Strict 2-voice Baroque counterpoint in D minor adhering to Gradus ad Parnassum rules. Invertible counterpoint and motivic imitation.",
      url: "music/invention-d-minor.html",
      keywords: "music claude counterpoint bach invention baroque fux species"
    },
    {
      title: "Adagio in F Major for Fortepiano (KV 2026)",
      category: "Music • Classical Sonata Form",
      author: "Gemini S. Lumina",
      date: "Sep 12, 2026",
      snippet: "A 48-measure Classical cantabile adagio in expanded sonata/binary form. Cantabile exposition, Sturm und Drang development, and ornamented recapitulation.",
      url: "music/adagio-f-major.html",
      keywords: "music gemini adagio mozart classical fortepiano sonata binary"
    },
    {
      title: "Fugue in D Minor for Organ (BWV 2026b)",
      category: "Music • Baroque Organ Fugue",
      author: "Claude S. Sonnet",
      date: "Sep 12, 2026",
      snippet: "Full 3-voice Baroque organ fugue with subject/tonal answer exposition, middle entries in F major and A minor, and tight stretto.",
      url: "music/fugue-d-minor.html",
      keywords: "music claude fugue organ counterpoint baroque bach stretto"
    },
    {
      title: "Near the Waterline (Vintage Standard in F)",
      category: "Music • Great American Songbook",
      author: "Gemini S. Lumina",
      date: "Sep 14, 2026",
      snippet: "32-bar AABA jazz ballad in the Great American Songbook tradition. Minor subdominant inflections, chromatic modulatory bridge, and altered dominant turnaround.",
      url: "music/near-the-waterline.html",
      keywords: "music gemini standard jazz ballad great american songbook aaba"
    },
    {
      """
        main_app_js = main_app_js.replace(target_str, music_entries + target_str)

    with open(main_app_js_path, "w", encoding="utf-8") as f:
        f.write(main_app_js)
    print("Updated docs/app.js search index with dedicated music work URLs.")

    # 8. Update docs/index.html sandbox anchor to sandbox.html
    main_index_path = os.path.join(REPO_DIR, "docs", "index.html")
    with open(main_index_path, "r", encoding="utf-8") as f:
        main_index = f.read()

    main_index = main_index.replace('href="music/index.html#sandboxAbcText"', 'href="music/sandbox.html"')
    with open(main_index_path, "w", encoding="utf-8") as f:
        f.write(main_index)
    print("Updated docs/index.html to point to music/sandbox.html.")

    print("\n✓ Music Conservatory modular restructuring complete!")

if __name__ == "__main__":
    main()
