# Session B — Knowledge Base Implementation Plan

> **For agentic workers:** This is content-authoring, not code. The TDD shape is preserved by treating Grep-based structural checks as the "tests" (spec-conformance verifiable without writing scripts — the spec forbids scripts here). Each task: author the file(s) -> run Grep checks -> confirm structure -> commit. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the seed knowledge base for Crunchtronics Tutor — 19 cheat sheets across theory, ableton, mpk-mini-4, and genres, plus `knowledge/INDEX.md`, all conforming to the cheat-sheet template fixed in `docs/superpowers/specs/subsystems/03-knowledge-base.md`.

**Architecture:** Five build phases in dependency order — **theory** (foundational primitives, no prereqs) -> **ableton** (no prereqs) -> **mpk-mini-4** (some prereqs into pads-vs-keys-vs-knobs) -> **genres** (prereqs into theory) -> **INDEX.md** (last; entries depend on all front matter being final). One commit per phase. `knowledge/ableton/companion-mode.md` is preserved byte-identical from Session A.

**Tech Stack:** Markdown only. Grep for structural verification. No Python, no shell scripts beyond the verification one-liners listed in each task.

---

## File Structure (locked in)

```
knowledge/
├── INDEX.md                         (Task 5 - new)
├── theory/                          (Task 1)
│   ├── rhythm-basics.md
│   ├── intervals.md
│   ├── scales-and-keys.md
│   ├── chord-construction.md
│   └── the-camelot-wheel.md
├── ableton/                         (Task 2; companion-mode.md preserved untouched)
│   ├── companion-mode.md            (Session A — DO NOT MODIFY)
│   ├── session-vs-arrangement-view.md
│   ├── the-browser.md
│   ├── midi-vs-audio-tracks.md
│   ├── the-mixer.md
│   ├── simpler-basics.md
│   └── drum-rack-basics.md
├── mpk-mini-4/                      (Task 3)
│   ├── pads-vs-keys-vs-knobs.md
│   ├── transport-controls.md
│   ├── mpk-program-editor.md
│   └── mapping-pads-to-drum-rack.md
├── genres/                          (Task 4)
│   ├── dubstep.md
│   ├── melodic-dubstep.md
│   ├── tech-house.md
│   └── bass-house.md
└── artists/                         (intentionally empty — Session D / Subsystem #7)
```

## Cheat-sheet template (from spec §1, included verbatim for each task)

```markdown
---
slug: <kebab-case, matches filename>
category: <theory|ableton|mpk-mini-4|genres|artists>
tldr: <one sentence, ≤25 words>
prerequisites: [<slug>, <slug>]    # [] if foundational
references:                         # [] if no Reference Vault entry applies
  - "<Source>: <topic>"             # <Source> ∈ {"Ableton Manual", "MPK Manual"}
next: <slug>                        # or null if terminal
---

# <Human-friendly title>

## TL;DR
<Opens with the front-matter tldr sentence verbatim, then 1-3 sentences of expansion.>

## Cheat block
<Dense bullets. Subheadings allowed. The fast-reference layer Claude scans mid-session.>

## Read this yourself
<Conversational prose. Second person. For Destin to read standalone. ~100-300 words.>

## See also
- `<relative/path/to/sibling.md>` — <one-line why>
- Reference: *<topic>* in `reference/INDEX.md`
```

---

## Task 1: Theory primitives (5 files)

**Why first:** these are foundational (no prereqs into other knowledge files). Genre cheat sheets in Task 4 depend on them.

**Files:**
- Create: `knowledge/theory/rhythm-basics.md`
- Create: `knowledge/theory/intervals.md`
- Create: `knowledge/theory/scales-and-keys.md`
- Create: `knowledge/theory/chord-construction.md`
- Create: `knowledge/theory/the-camelot-wheel.md`

### Step 1.1: Author `knowledge/theory/rhythm-basics.md`

- [ ] Write the file with this front matter and content scope:

**Front matter:**
- `slug: rhythm-basics`
- `category: theory`
- `tldr: "Beats, bars, and time signatures — the pulse and grid that all EDM is built on top of."`
- `prerequisites: []`
- `references: ["Ableton Manual: Editing MIDI Notes and Velocities"]`
- `next: intervals`

**Cheat block scope:** BPM definition; beat/bar/time signature; 4/4 default for EDM; "four-on-the-floor" = kick on every beat; common subdivisions (1/4, 1/8, 1/16); off-beat hat = "and"s between beats; bar count thinking (16-bar phrases as the EDM unit).

**Read this yourself scope:** Frame thinking-in-bars-not-seconds. Counting "1-and-2-and-3-and-4-and". Why metronome practice on the MPK pays off fast. ~150 words.

**See also:** `intervals.md`, `scales-and-keys.md`, `../ableton/midi-vs-audio-tracks.md`; Reference: *Editing MIDI Notes and Velocities* in `reference/INDEX.md`.

### Step 1.2: Author `knowledge/theory/intervals.md`

- [ ] Write the file:

**Front matter:**
- `slug: intervals`, `category: theory`
- `tldr: "Distances between two notes, named in semitones and scale steps."`
- `prerequisites: []`
- `references: []` (pure theory; no manual entry applies)
- `next: scales-and-keys`

**Cheat block scope:** Semitone = 1 piano key. Octave = 12 semitones. Names: m2, M2, m3, M3, P4, TT/d5, P5, m6, M6, m7, M7, P8. Consonant vs dissonant intuition. Whole-step vs half-step.

**Read this yourself scope:** Piano keyboard mental model — black/white pattern, why the keyboard layout makes intervals visible. Why intervals matter (melody = stepping through them). ~120 words.

**See also:** `scales-and-keys.md`.

### Step 1.3: Author `knowledge/theory/scales-and-keys.md`

- [ ] Write the file:

**Front matter:**
- `slug: scales-and-keys`, `category: theory`
- `tldr: "Major and minor scales, key signatures, and how a track's key shapes its mood."`
- `prerequisites: [intervals]`
- `references: ["MPK Manual: Scales Mode (root key + 18 scale types)"]`
- `next: chord-construction`

**Cheat block scope:** Major scale pattern W-W-H-W-W-W-H. Natural minor W-H-W-W-H-W-W. Key = scale + root. 12 keys × major/minor = 24. Mood association (major = bright, minor = dark — with caveats). Modes mentioned briefly only as "advanced; ignore for now".

**Read this yourself scope:** What "in the key of A minor" means in practice. How the MPK's Scales Mode locks notes to a key so wrong notes can't be played — invaluable for beginners. ~180 words.

**See also:** `chord-construction.md`, `the-camelot-wheel.md`, `../mpk-mini-4/pads-vs-keys-vs-knobs.md`; Reference: *Scales Mode (root key + 18 scale types)* in `reference/INDEX.md`.

### Step 1.4: Author `knowledge/theory/chord-construction.md`

- [ ] Write the file:

**Front matter:**
- `slug: chord-construction`, `category: theory`
- `tldr: "How triads and seventh chords are built from scale degrees."`
- `prerequisites: [intervals, scales-and-keys]`
- `references: ["MPK Manual: Chords Mode (configuration, inversions, transpose/ignore)"]`
- `next: the-camelot-wheel`

**Cheat block scope:** Triad = 1-3-5. Major triad = root + M3 + P5. Minor triad = root + m3 + P5. Sus2/sus4. 7th chords: maj7 (root + M3 + P5 + M7), 7 (dominant), m7. Inversions briefly. The I-IV-V-vi pop progression.

**Read this yourself scope:** How MPK Chords Mode plays full triads from one key — friendly for non-pianists. The 1-4-5 / I-IV-V workhorse progression. ~160 words.

**See also:** `scales-and-keys.md`, `../mpk-mini-4/pads-vs-keys-vs-knobs.md`; Reference: *Chords Mode (configuration, inversions, transpose/ignore)* in `reference/INDEX.md`.

### Step 1.5: Author `knowledge/theory/the-camelot-wheel.md`

- [ ] Write the file:

**Front matter:**
- `slug: the-camelot-wheel`, `category: theory`
- `tldr: "Camelot notation — a DJ-friendly map of which keys mix harmonically."`
- `prerequisites: [scales-and-keys]`
- `references: []` (Camelot Wheel is in `reference/ONLINE.md`, not `INDEX.md` — cited in body's See also)
- `next: null`

**Cheat block scope:** Notation: 12 numbers × {A = minor, B = major} = 24 codes. Harmonic mix rules: same number = guaranteed compatible; ±1 number = related; same number A↔B = relative major/minor swap. Energy boosts. Why the wheel is wrapped in a circle (modulo 12).

**Read this yourself scope:** Why DJs use Camelot instead of Western key names — number arithmetic instead of memorizing key relationships. How `taste/tracks.csv`'s `key_camelot` column will let Claude reason about Destin's taste. ~150 words.

**See also:** `scales-and-keys.md`; Reference: *Camelot Wheel reference* in `reference/ONLINE.md`.

### Step 1.6: Run structural verification on theory files

- [ ] Run each of these and confirm output:

```bash
# All 5 files exist
ls knowledge/theory/*.md
# Expected: 5 files (chord-construction.md, intervals.md, rhythm-basics.md, scales-and-keys.md, the-camelot-wheel.md)
```

```
# Each file has front matter (opens with --- on line 1)
grep -L "^---$" knowledge/theory/*.md
# Expected: empty output (no files lacking front matter on line 1)
```

```
# Each file has all four required body sections
for f in knowledge/theory/*.md; do
  for h in "## TL;DR" "## Cheat block" "## Read this yourself" "## See also"; do
    grep -q "^$h" "$f" || echo "MISSING: $h in $f"
  done
done
# Expected: empty output (no missing headers)
```

- [ ] **Step 1.7: Commit**

```bash
git add knowledge/theory/
git commit -m "feat(knowledge): subsystem #3 — theory primitives (5 cheat sheets)"
```

---

## Task 2: Ableton cheat sheets (6 files)

**Why second:** No prereqs into theory; can run after Task 1 in any order. Author before MPK so MPK files can cross-link to existing Ableton files.

**Files:**
- Create: `knowledge/ableton/session-vs-arrangement-view.md`
- Create: `knowledge/ableton/the-browser.md`
- Create: `knowledge/ableton/midi-vs-audio-tracks.md`
- Create: `knowledge/ableton/the-mixer.md`
- Create: `knowledge/ableton/simpler-basics.md`
- Create: `knowledge/ableton/drum-rack-basics.md`
- **Do NOT modify:** `knowledge/ableton/companion-mode.md`

### Step 2.1: Author `knowledge/ableton/session-vs-arrangement-view.md`

**Front matter:**
- `slug: session-vs-arrangement-view`, `category: ableton`
- `tldr: "Session view is a clip-launching grid; Arrangement view is a linear timeline; you can move between them."`
- `prerequisites: []`
- `references: ["Ableton Manual: Session View (clip launching, scenes)", "Ableton Manual: Arrangement View (linear timeline editing)"]`
- `next: the-browser`

**Cheat block scope:** Session = vertical clips/scenes for jamming, Arrangement = horizontal timeline for finished song. Tab key toggles between them. Lite floor: 8 audio + 8 MIDI tracks (called out explicitly). Recording from Session into Arrangement.

**Read this yourself scope:** Typical beginner workflow — sketch loops in Session, then commit to Arrangement once a structure emerges. ~150 words.

**See also:** `midi-vs-audio-tracks.md`, `the-mixer.md`; Reference: *Session View (clip launching, scenes)* in `reference/INDEX.md`.

### Step 2.2: Author `knowledge/ableton/the-browser.md`

**Front matter:**
- `slug: the-browser`, `category: ableton`
- `tldr: "Left-side panel for finding sounds, instruments, devices, and your own files."`
- `prerequisites: []`
- `references: ["Ableton Manual: Working with the Browser"]`
- `next: simpler-basics`

**Cheat block scope:** Cmd/Ctrl+Alt+B toggles browser. Search box. Hot-swap on devices. Drag to track. Tags + collections. Places (for sample folders / Splice). Hover-preview audio.

**Read this yourself scope:** Organizing samples; previewing without committing; collections for keeping favorites. ~130 words.

**See also:** `simpler-basics.md`, `drum-rack-basics.md`; Reference: *Working with the Browser* in `reference/INDEX.md`.

### Step 2.3: Author `knowledge/ableton/midi-vs-audio-tracks.md`

**Front matter:**
- `slug: midi-vs-audio-tracks`, `category: ableton`
- `tldr: "MIDI tracks hold notes that drive instruments; audio tracks hold recorded sound — pick MIDI when you want to change the notes later."`
- `prerequisites: []`
- `references: ["Ableton Manual: Editing MIDI Notes and Velocities", "Ableton Manual: Audio Clips, Tempo, and Warping"]`
- `next: the-mixer`

**Cheat block scope:** MIDI = note data + instrument plugin; Audio = recorded waveform. MIDI is fully editable; audio is warpable but not retunable cheaply. Freeze + flatten = printing MIDI to audio. When to pick which.

**Read this yourself scope:** Why MIDI is friendlier for beginners (you can change your mind). When audio is the only choice (recorded vocals, sampled loops you want to keep stable). ~160 words.

**See also:** `simpler-basics.md`, `drum-rack-basics.md`; Reference: *Editing MIDI Notes and Velocities* in `reference/INDEX.md`.

### Step 2.4: Author `knowledge/ableton/the-mixer.md`

**Front matter:**
- `slug: the-mixer`, `category: ableton`
- `tldr: "The channel-strip view: per-track volume, pan, sends, plus master and return tracks."`
- `prerequisites: []`
- `references: ["Ableton Manual: Mixing (mixer view, sends, returns)"]`
- `next: null`

**Cheat block scope:** Per-track strip (volume / pan / mute / solo / sends). Lite has 2 sends max (Intro = 4, called out). Master = final output. Return tracks for shared FX (reverb send pattern). Gain staging in one line.

**Read this yourself scope:** The send-and-return pattern explained from scratch — why share a reverb instead of putting one on every track. Lite-floor reality. ~170 words.

**See also:** `midi-vs-audio-tracks.md`; Reference: *Mixing (mixer view, sends, returns)* in `reference/INDEX.md`.

### Step 2.5: Author `knowledge/ableton/simpler-basics.md`

**Front matter:**
- `slug: simpler-basics`, `category: ableton`
- `tldr: "Simpler plays a single sample as a melodic instrument — Lite/Intro's main sampler (no Sampler in those editions)."`
- `prerequisites: []`
- `references: ["Ableton Manual: Live Instrument Reference"]`
- `next: drum-rack-basics`

**Cheat block scope:** Three modes: Classic (chromatic playback across keyboard), One-Shot (single trigger, no pitch tracking), Slice (chops sample at transients into pads). ADSR envelope. Warp toggle. Lite has Simpler, not Sampler — deliberate constraint.

**Read this yourself scope:** Walk through the three modes with a real-world example each (Classic for melodic samples, One-Shot for one-off hits, Slice for breaking up a vocal loop). ~180 words.

**See also:** `drum-rack-basics.md`, `the-browser.md`; Reference: *Live Instrument Reference* in `reference/INDEX.md`.

### Step 2.6: Author `knowledge/ableton/drum-rack-basics.md`

**Front matter:**
- `slug: drum-rack-basics`, `category: ableton`
- `tldr: "Drum Rack is a 16-pad device that hosts one Simpler/sample per pad, mapped to MIDI notes C1-D#2."`
- `prerequisites: []`
- `references: ["Ableton Manual: Instrument, Drum and Effect Racks (incl. Drum Rack)"]`
- `next: null`

**Cheat block scope:** 16 pads = 16 chains. Each pad = MIDI note (C1 = bottom-left). Drag samples to pads. Each chain has its own volume/pan/send. Group of 16 pads = standard kit (kick / snare / hat / clap / ...). Choke groups for hi-hats.

**Read this yourself scope:** Building a kit pad by pad. Why C1 = pad 1 matters for the MPK (the MPK's pads default to that range). ~170 words.

**See also:** `simpler-basics.md`, `../mpk-mini-4/mapping-pads-to-drum-rack.md`; Reference: *Instrument, Drum and Effect Racks (incl. Drum Rack)* in `reference/INDEX.md`.

### Step 2.7: Run structural verification on ableton files

- [ ] Same Grep checks as Step 1.6, scoped to `knowledge/ableton/*.md`. **Important:** also confirm `companion-mode.md` is unchanged:

```bash
git diff knowledge/ableton/companion-mode.md
# Expected: empty output (file untouched)
```

- [ ] **Step 2.8: Commit**

```bash
git add knowledge/ableton/
git commit -m "feat(knowledge): subsystem #3 — ableton cheat sheets (6 files)"
```

---

## Task 3: MPK Mini 4 cheat sheets (4 files)

**Why third:** No theory prereqs but `mapping-pads-to-drum-rack.md` cross-links to `ableton/drum-rack-basics.md` — author after Task 2.

**Files:**
- Create: `knowledge/mpk-mini-4/pads-vs-keys-vs-knobs.md`
- Create: `knowledge/mpk-mini-4/transport-controls.md`
- Create: `knowledge/mpk-mini-4/mpk-program-editor.md`
- Create: `knowledge/mpk-mini-4/mapping-pads-to-drum-rack.md`

### Step 3.1: Author `knowledge/mpk-mini-4/pads-vs-keys-vs-knobs.md`

**Front matter:**
- `slug: pads-vs-keys-vs-knobs`, `category: mpk-mini-4`
- `tldr: "Pads (8) trigger drums or samples; keys (25) play melodies and chords; knobs (8) send MIDI CCs you can map onto plugin parameters."`
- `prerequisites: []`
- `references: ["MPK Manual: Features overview (top + rear panel callouts)", "MPK Manual: Pad Modes (Notes / CC# / Program Change)"]`
- `next: transport-controls`

**Cheat block scope:** 8 pads with banks A/B/C/D = 32 effective. 25 velocity-sensitive keys (2 octaves, +/- buttons for octave shift). 8 endless knobs (Absolute or Relative mode). Pad modes: Notes, CC#, Program Change. Default note range C1-D#2 = matches Drum Rack.

**Read this yourself scope:** Tour each surface in turn — what it physically is, what it does by default, when you'd care. ~180 words.

**See also:** `mapping-pads-to-drum-rack.md`, `../ableton/drum-rack-basics.md`; Reference: *Features overview (top + rear panel callouts)* in `reference/INDEX.md`.

### Step 3.2: Author `knowledge/mpk-mini-4/transport-controls.md`

**Front matter:**
- `slug: transport-controls`, `category: mpk-mini-4`
- `tldr: "Built-in play / stop / record / loop / tap-tempo buttons that drive Ableton's transport over MIDI."`
- `prerequisites: []`
- `references: ["MPK Manual: Setup with other DAWs (Ableton, Logic, FL, Cubase, GarageBand)"]`
- `next: mpk-program-editor`

**Cheat block scope:** Play/Stop/Record/Loop buttons map to Ableton transport via the bundled DAW preset. Tap Tempo for live BPM. Setup: pick the Ableton preset on the MPK side; in Ableton, set MPK as Control Surface in Preferences > Link/MIDI.

**Read this yourself scope:** The moment when transport works without touching the mouse — small win, big mood-boost. ~120 words.

**See also:** `mpk-program-editor.md`, `../ableton/session-vs-arrangement-view.md`; Reference: *Setup with other DAWs (Ableton, Logic, FL, Cubase, GarageBand)* in `reference/INDEX.md`.

### Step 3.3: Author `knowledge/mpk-mini-4/mpk-program-editor.md`

**Front matter:**
- `slug: mpk-program-editor`, `category: mpk-mini-4`
- `tldr: "Akai's free desktop app for creating custom MPK presets — what each pad, knob, and key does in your saved configuration."`
- `prerequisites: [pads-vs-keys-vs-knobs]`
- `references: ["MPK Manual: Program Edit (custom user presets)"]`
- `next: null`

**Cheat block scope:** Download from akaipro.com. Edit knob CC numbers, pad note assignments, MIDI channel. Save up to 8 onboard programs (banks). When you'd customize (mapping knobs to specific Operator parameters) vs. keep defaults.

**Read this yourself scope:** When stock defaults are fine and when customization actually pays off. ~140 words.

**See also:** `pads-vs-keys-vs-knobs.md`; Reference: *Program Edit (custom user presets)* in `reference/INDEX.md`.

### Step 3.4: Author `knowledge/mpk-mini-4/mapping-pads-to-drum-rack.md`

**Front matter:**
- `slug: mapping-pads-to-drum-rack`, `category: mpk-mini-4`
- `tldr: "End-to-end recipe for triggering Ableton Drum Rack pads from your MPK pads."`
- `prerequisites: [pads-vs-keys-vs-knobs]`
- `references: ["MPK Manual: Pad Modes (Notes / CC# / Program Change)", "Ableton Manual: Instrument, Drum and Effect Racks (incl. Drum Rack)"]`
- `next: null`

**Cheat block scope:** Numbered recipe: (1) MPK in Notes mode (default). (2) Drop Drum Rack on a MIDI track. (3) Arm the track (red dot). (4) Hit a pad. (5) Confirm Drum Rack pad lights up. Common gotchas: wrong octave (use MPK octave shift), wrong MIDI channel, Ableton not seeing the device.

**Read this yourself scope:** The "first satisfying hit" moment — encouraging tone, framed as the gateway recipe. ~170 words.

**See also:** `../ableton/drum-rack-basics.md`, `pads-vs-keys-vs-knobs.md`; Reference: *Pad Modes (Notes / CC# / Program Change)* in `reference/INDEX.md`.

### Step 3.5: Run structural verification on mpk-mini-4 files

- [ ] Same Grep checks as Step 1.6, scoped to `knowledge/mpk-mini-4/*.md`.

- [ ] **Step 3.6: Commit**

```bash
git add knowledge/mpk-mini-4/
git commit -m "feat(knowledge): subsystem #3 — mpk mini 4 cheat sheets (4 files)"
```

---

## Task 4: Genre cheat sheets (4 files)

**Why fourth:** Each has `prerequisites` into theory primitives — those must exist first.

**Files:**
- Create: `knowledge/genres/dubstep.md`
- Create: `knowledge/genres/melodic-dubstep.md`
- Create: `knowledge/genres/tech-house.md`
- Create: `knowledge/genres/bass-house.md`

### Step 4.1: Author `knowledge/genres/dubstep.md`

**Front matter:**
- `slug: dubstep`, `category: genres`
- `tldr: "Heavy 140 BPM bass music with a half-time kick-clap pulse and aggressive growling/wobble basses; covers riddim's repetitive triplet bass too."`
- `prerequisites: [rhythm-basics, scales-and-keys]`
- `references: ["Ableton Manual: Live Instrument Reference", "Ableton Manual: Live Audio Effect Reference"]`
- `next: melodic-dubstep`

**Cheat block scope:** BPM 140 (felt as 70 half-time). Kick on 1, snare/clap on 3 (half-time). Drop = bass takes the lead role. Riddim sub-style: repetitive triplet bass pattern. Anchor artists: Subtronics (Destin's confirmed taste anchor), Excision, Virtual Riot, Svdden Death. Sound design: FM growls, Serum/Vital + heavy distortion + Multiband.

**Read this yourself scope:** Brief history sketch (Croydon -> Skrillex -> US bass scene). Why riddim split off. The "drop" as the centerpiece. ~220 words.

**See also:** `../theory/rhythm-basics.md`, `melodic-dubstep.md`; Reference: *Live Audio Effect Reference* in `reference/INDEX.md`.

### Step 4.2: Author `knowledge/genres/melodic-dubstep.md`

**Front matter:**
- `slug: melodic-dubstep`, `category: genres`
- `tldr: "Anthemic 140 BPM bass music with emotive piano/lead intros, big chord progressions, and softer, more harmonic drops than classic dubstep."`
- `prerequisites: [rhythm-basics, scales-and-keys, chord-construction]`
- `references: ["Ableton Manual: Live Instrument Reference"]`
- `next: null`

**Cheat block scope:** BPM 140. Structure: emotional build (piano + vocal hook + supersaw) -> melodic drop (singing leads, less aggressive bass than dubstep). Common keys: minor with major-mode lifts. Anchor artists: Wooli (Destin's confirmed anchor), Seven Lions, Illenium, Said the Sky. Sound: layered supersaws, sub bass, ambient pads.

**Read this yourself scope:** Emotional vocabulary distinct from dubstep — uplifting, anthemic, festival-main-stage tone. Chord progressions that anchor it (vi-IV-I-V is omnipresent). ~210 words.

**See also:** `../theory/chord-construction.md`, `dubstep.md`; Reference: *Live Instrument Reference* in `reference/INDEX.md`.

### Step 4.3: Author `knowledge/genres/tech-house.md`

**Front matter:**
- `slug: tech-house`, `category: genres`
- `tldr: "Four-on-the-floor club music at 124-128 BPM with rolling basslines, tight punchy drums, and sparse melodic hooks."`
- `prerequisites: [rhythm-basics, scales-and-keys]`
- `references: ["Ableton Manual: Mixing (mixer view, sends, returns)", "Ableton Manual: Live Audio Effect Reference"]`
- `next: bass-house`

**Cheat block scope:** BPM 124-128. Four-on-the-floor kick. Off-beat open hat ("tss" on the "and"). Tight clap on 2/4. Bouncy syncopated bass (often tied to kick rhythm). Sparse vocal chops. 16/32-bar club arrangement: intro → drop A → break → drop B → outro. Anchor: John Summit (Destin's confirmed). Reference set: Fisher, Chris Lake, Solardo. Sidechain compression heavily used.

**Read this yourself scope:** The pocket between house and techno. Why the bassline is the hook. Sidechain's rhythmic role. ~210 words.

**See also:** `../theory/rhythm-basics.md`, `../ableton/the-mixer.md`, `bass-house.md`; Reference: *Mixing (mixer view, sends, returns)* in `reference/INDEX.md`.

### Step 4.4: Author `knowledge/genres/bass-house.md`

**Front matter:**
- `slug: bass-house`, `category: genres`
- `tldr: "House at 125-130 BPM with louder, grittier, distorted basses, harder kicks, and frequent dubstep-leaning drops over a 4/4 groove."`
- `prerequisites: [rhythm-basics, scales-and-keys]`
- `references: ["Ableton Manual: Live Instrument Reference", "Ableton Manual: Live Audio Effect Reference"]`
- `next: null`

**Cheat block scope:** BPM 125-130. Four-on-the-floor with harder, more processed kicks. Heavily distorted/saturated bass (think filthy reese or sawtooth). Dubstep-style drops over 4/4 grooves. Anchor: Jigitz (Destin's confirmed). Reference set: Habstrakt, JOYRYDE, Confession label. Sound design: Serum + heavy distortion + parallel compression.

**Read this yourself scope:** The bridge between house and dubstep. Why it crosses over so well in festival sets. Common bass-design tricks. ~200 words.

**See also:** `../theory/rhythm-basics.md`, `dubstep.md`, `tech-house.md`; Reference: *Live Audio Effect Reference* in `reference/INDEX.md`.

### Step 4.5: Run structural verification on genre files + cross-reference checks

- [ ] Run the standard checks (front matter, headers) scoped to `knowledge/genres/*.md`.

- [ ] **NEW** for this task — verify every `prerequisites` slug across all knowledge files resolves to an existing file:

```bash
# List every slug declared in prerequisites: across all knowledge files
grep -h "^prerequisites:" knowledge/**/*.md | grep -oE '\[[^]]*\]'
```

- [ ] By inspection, confirm every slug in those lists corresponds to an existing `<slug>.md` somewhere under `knowledge/`. (Manual: list of all prereqs used: `intervals`, `scales-and-keys`, `chord-construction`, `pads-vs-keys-vs-knobs`, `rhythm-basics`. Each should be a file.)

- [ ] **Step 4.6: Commit**

```bash
git add knowledge/genres/
git commit -m "feat(knowledge): subsystem #3 — genre cheat sheets (4 files)"
```

---

## Task 5: `knowledge/INDEX.md`

**Why last:** Every entry's TL;DR is pulled verbatim from the corresponding file's front-matter `tldr` — needs all front matter to be final.

**Files:**
- Create: `knowledge/INDEX.md`

### Step 5.1: Author `knowledge/INDEX.md`

- [ ] Write the file with this exact structure:

```markdown
# Knowledge Index

> One entry per cheat sheet. TL;DR pulled from each file's front-matter `tldr` field, except for `companion-mode.md` (Session A policy doc — hand-written entry).

## theory
- [chord-construction](theory/chord-construction.md) — How triads and seventh chords are built from scale degrees.
- [intervals](theory/intervals.md) — Distances between two notes, named in semitones and scale steps.
- [rhythm-basics](theory/rhythm-basics.md) — Beats, bars, and time signatures — the pulse and grid that all EDM is built on top of.
- [scales-and-keys](theory/scales-and-keys.md) — Major and minor scales, key signatures, and how a track's key shapes its mood.
- [the-camelot-wheel](theory/the-camelot-wheel.md) — Camelot notation — a DJ-friendly map of which keys mix harmonically.

## ableton
- [companion-mode](ableton/companion-mode.md) — On-demand screen-reading policy for Ableton sessions (authored Session A; do not modify).
- [drum-rack-basics](ableton/drum-rack-basics.md) — Drum Rack is a 16-pad device that hosts one Simpler/sample per pad, mapped to MIDI notes C1-D#2.
- [midi-vs-audio-tracks](ableton/midi-vs-audio-tracks.md) — MIDI tracks hold notes that drive instruments; audio tracks hold recorded sound — pick MIDI when you want to change the notes later.
- [session-vs-arrangement-view](ableton/session-vs-arrangement-view.md) — Session view is a clip-launching grid; Arrangement view is a linear timeline; you can move between them.
- [simpler-basics](ableton/simpler-basics.md) — Simpler plays a single sample as a melodic instrument — Lite/Intro's main sampler (no Sampler in those editions).
- [the-browser](ableton/the-browser.md) — Left-side panel for finding sounds, instruments, devices, and your own files.
- [the-mixer](ableton/the-mixer.md) — The channel-strip view: per-track volume, pan, sends, plus master and return tracks.

## mpk-mini-4
- [mapping-pads-to-drum-rack](mpk-mini-4/mapping-pads-to-drum-rack.md) — End-to-end recipe for triggering Ableton Drum Rack pads from your MPK pads.
- [mpk-program-editor](mpk-mini-4/mpk-program-editor.md) — Akai's free desktop app for creating custom MPK presets — what each pad, knob, and key does in your saved configuration.
- [pads-vs-keys-vs-knobs](mpk-mini-4/pads-vs-keys-vs-knobs.md) — Pads (8) trigger drums or samples; keys (25) play melodies and chords; knobs (8) send MIDI CCs you can map onto plugin parameters.
- [transport-controls](mpk-mini-4/transport-controls.md) — Built-in play / stop / record / loop / tap-tempo buttons that drive Ableton's transport over MIDI.

## genres
- [bass-house](genres/bass-house.md) — House at 125-130 BPM with louder, grittier, distorted basses, harder kicks, and frequent dubstep-leaning drops over a 4/4 groove.
- [dubstep](genres/dubstep.md) — Heavy 140 BPM bass music with a half-time kick-clap pulse and aggressive growling/wobble basses; covers riddim's repetitive triplet bass too.
- [melodic-dubstep](genres/melodic-dubstep.md) — Anthemic 140 BPM bass music with emotive piano/lead intros, big chord progressions, and softer, more harmonic drops than classic dubstep.
- [tech-house](genres/tech-house.md) — Four-on-the-floor club music at 124-128 BPM with rolling basslines, tight punchy drums, and sparse melodic hooks.

## artists
*(empty — populated by Session D / Subsystem #7 once the taste profile lands.)*
```

### Step 5.2: Verify INDEX coverage

- [ ] Confirm INDEX has exactly 20 cheat-sheet links (19 new + companion-mode):

```bash
grep -cE '^\- \[' knowledge/INDEX.md
# Expected: 20
```

- [ ] Confirm every TL;DR in INDEX matches the source file's front-matter `tldr` verbatim (except companion-mode).

  For each file, run:

```bash
grep -A0 "^tldr:" knowledge/<category>/<slug>.md
```

  and visually confirm the string after `tldr: ` (stripped of surrounding quotes) appears verbatim after the em-dash in the corresponding INDEX line.

- [ ] **Step 5.3: Commit**

```bash
git add knowledge/INDEX.md
git commit -m "feat(knowledge): subsystem #3 — INDEX.md grouped by subdirectory"
```

---

## Task 6: Final verification sweep (Session B verification gates)

These are the spec's verification gates from §Verification gates. All must pass before Session B is marked complete in the master orchestration plan.

### Step 6.1: All 19 new cheat sheets present

- [ ] Run:

```bash
ls knowledge/theory/*.md knowledge/ableton/*.md knowledge/mpk-mini-4/*.md knowledge/genres/*.md
```

  Expected count: 5 + 7 + 4 + 4 = **20** files (the 7 in `ableton/` includes the unmodified `companion-mode.md`).

### Step 6.2: Front matter validity

- [ ] Each new cheat sheet (NOT including companion-mode.md, which has no front matter) has all six required fields:

```bash
for f in knowledge/theory/*.md knowledge/ableton/*.md knowledge/mpk-mini-4/*.md knowledge/genres/*.md; do
  [ "$f" = "knowledge/ableton/companion-mode.md" ] && continue
  for field in "^slug:" "^category:" "^tldr:" "^prerequisites:" "^references:" "^next:"; do
    grep -q "$field" "$f" || echo "MISSING $field in $f"
  done
done
# Expected: empty output
```

- [ ] Slug-matches-filename check (manual or scripted by inspection): for each file, confirm the front-matter `slug:` value equals the filename without the `.md` extension.

### Step 6.3: Body section completeness

- [ ] Every new cheat sheet has all four body sections (re-run from Step 1.6, scoped across all subdirectories):

```bash
for f in knowledge/theory/*.md knowledge/ableton/*.md knowledge/mpk-mini-4/*.md knowledge/genres/*.md; do
  [ "$f" = "knowledge/ableton/companion-mode.md" ] && continue
  for h in "## TL;DR" "## Cheat block" "## Read this yourself" "## See also"; do
    grep -q "^$h" "$f" || echo "MISSING: $h in $f"
  done
done
# Expected: empty output
```

### Step 6.4: References resolve into reference/INDEX.md

- [ ] Every `references:` entry semantically corresponds to a topic in `reference/INDEX.md`. By inspection, walk each file's `references:` list and confirm each `Ableton Manual: <topic>` matches a bullet under the Ableton section, and each `MPK Manual: <topic>` matches a bullet under the MPK section.

  Reference Vault sections recap:
  - Ableton Manual entries used in this subsystem: `Editing MIDI Notes and Velocities`, `Session View (clip launching, scenes)`, `Arrangement View (linear timeline editing)`, `Working with the Browser`, `Audio Clips, Tempo, and Warping`, `Mixing (mixer view, sends, returns)`, `Live Instrument Reference`, `Live Audio Effect Reference`, `Instrument, Drum and Effect Racks (incl. Drum Rack)`.
  - MPK Manual entries used: `Features overview (top + rear panel callouts)`, `Pad Modes (Notes / CC# / Program Change)`, `Setup with other DAWs (Ableton, Logic, FL, Cubase, GarageBand)`, `Program Edit (custom user presets)`, `Scales Mode (root key + 18 scale types)`, `Chords Mode (configuration, inversions, transpose/ignore)`.

  Each is present in `reference/INDEX.md`. Spot-check three at random.

### Step 6.5: Prerequisites and next pointers resolve

- [ ] Every slug appearing in `prerequisites:` lists or `next:` fields resolves to an actual cheat-sheet file (or is `null` for `next`). Slugs used in this subsystem:

  - `prerequisites:` slugs: `intervals`, `scales-and-keys`, `chord-construction`, `rhythm-basics`, `pads-vs-keys-vs-knobs`. ✓ All exist.
  - `next:` slugs: `intervals`, `scales-and-keys`, `chord-construction`, `the-camelot-wheel`, `the-browser`, `simpler-basics`, `drum-rack-basics`, `the-mixer` (from session-vs-arrangement-view → the-browser → simpler-basics → drum-rack-basics; mid-vs-audio → the-mixer), `transport-controls`, `mpk-program-editor`, `melodic-dubstep`, `bass-house`, plus several `null`. ✓ All non-null exist.

  Spot-check three by inspection.

### Step 6.6: companion-mode.md untouched

- [ ] Confirm:

```bash
git log --follow -- knowledge/ableton/companion-mode.md
# Expected: only Session A's commit (and one polish commit if it appears in git log) — no Session B commits touch this file.
```

### Step 6.7: artists/ empty

- [ ] Confirm:

```bash
ls knowledge/artists/
# Expected: empty (or only .gitkeep / .gitignore if Session A placed one)
```

### Step 6.8: INDEX coverage matches files on disk

- [ ] Confirm INDEX has one link per cheat sheet on disk (20 total: 5 theory + 7 ableton + 4 mpk + 4 genres + 0 artists):

```bash
grep -cE '^\- \[' knowledge/INDEX.md
# Expected: 20
```

### Step 6.9: Spot check three random cheat sheets

- [ ] Pick three at random across categories. Confirm:
  - Cheat block has at least 3 substantive bullets.
  - Read this yourself has at least 100 words of prose.
  - Front matter and body TL;DR sentence match.

### Step 6.10: No commit needed (verification only)

If any check failed in 6.1–6.9, fix the file in question and amend the relevant commit OR add a small follow-up commit (`fix(knowledge): ...`). If all checks pass, mark the orchestration plan's Session B as `[x]` complete in a separate commit.

---

## Self-review

**1. Spec coverage:**
- §1 cheat-sheet template + front-matter rules → Tasks 1–4 implement, Task 6 verifies.
- §2 seed content (19 files) → Tasks 1 (5), 2 (6), 3 (4), 4 (4) = 19. ✓
- §3 INDEX.md → Task 5. ✓
- §4 voice/pedagogy → encoded as content-scope notes in each step (top-down framing called out in genre tasks; Lite-floor honesty in ableton/the-mixer + ableton/session-vs-arrangement-view; hardware/software cross-links in MPK Task 3.4). ✓
- §"What this subsystem must NOT do" boundaries → preserved (no `knowledge/artists/*` content; companion-mode.md byte-identical; no scripts; no URL/page-number citations in cheat sheets). ✓
- §Verification gates → Task 6 covers 1–10. ✓

**2. Placeholder scan:** No "TBD", "TODO", "implement later", "etc." in this plan beyond the explicit no-script verification (which is by-design — the spec forbids scripts). ✓

**3. Type consistency:** All slugs are kebab-case, match filenames, used consistently across `prerequisites`, `next`, and INDEX entries. Front-matter field names (`slug`, `category`, `tldr`, `prerequisites`, `references`, `next`) match the spec's table exactly. ✓

**4. Gaps fixed:**
- the-camelot-wheel.md has no manual entry → resolved by leaving `references: []` and putting the Camelot Wheel reference in body's See also (citing `reference/ONLINE.md`, which the spec does not forbid).
- companion-mode.md has no front matter → resolved by hand-writing its INDEX entry (Step 5.1) and excluding it from front-matter checks (Step 6.2).
