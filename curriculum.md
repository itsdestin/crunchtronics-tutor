---
last_updated: 2026-04-28T23:57:31Z
next: lesson-001
generated_from_profile: 2026-04-28T23:23:31Z
profile_anchors: [bass-house, dubstep, melodic-dubstep, tech-house]
---

# Curriculum

> Schema reference: `docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md` §3.3.
> Seed authored Session D, 2026-04-28.

## lesson-001: MPK ↔ Ableton first connection [active]

- **Why next:** Foundation. Master spec §11 #8 — hardware and software learned
  together from day 1; nothing else works until the MPK is sounding through
  Ableton.
- **Estimated time:** 30 min
- **Depends on:** none
- **Hardware:** MPK USB cable connected to PC; Ableton Live 12 Lite open.
- **Practice task:** Connect the MPK over USB, verify Ableton shows it under
  Preferences → Link/Tempo/MIDI, arm a MIDI track, and play notes from the
  MPK keys. If a sound doesn't come out, walk through the troubleshooting
  steps in `knowledge/mpk-mini-4/pads-vs-keys-vs-knobs.md` and
  `knowledge/ableton/the-browser.md`. If you can't find a screen element,
  prefer `knowledge/ableton/companion-mode.md` over guessing.
- **Done criteria:**
  - [ ] MPK appears as a Control Surface or Input device in Ableton's
        Preferences → Link/Tempo/MIDI panel
  - [ ] Pressing an MPK key produces sound through a default Ableton
        instrument (Operator preset or Drum Rack)
  - [ ] Ableton's transport (play/stop) responds to the MPK's transport
        buttons (or you've consciously decided to use the on-screen
        transport instead)
- **Notes:**

## lesson-002: Map MPK pads to Drum Rack, play kick + clap [blocked]

- **Why blocked:** depends on lesson-001 (need the MPK already routed into Ableton).
- **Why next once unblocked:** First real beat-making exercise; gets the pads
  feeling tactile before any genre work begins.
- **Estimated time:** 30 min
- **Depends on:** lesson-001
- **Hardware:** MPK pads (8 pads → MIDI notes C1-D#2 per
  `knowledge/ableton/drum-rack-basics.md`).
- **Practice task:** Following `knowledge/mpk-mini-4/mapping-pads-to-drum-rack.md`,
  drop a Drum Rack onto a MIDI track, load a 909 kick on pad 1 and a clap on
  pad 2, and play a "kick on 1 and 3, clap on 2 and 4" pattern by hand. Loop
  it for 30 seconds at 126 BPM and tap along on the pads.
- **Done criteria:**
  - [ ] Drum Rack on a MIDI track with kick on pad 1 (C1) and clap on pad 2 (C#1)
  - [ ] Project tempo set to 126 BPM
  - [ ] You can play the kick-clap-kick-clap pattern by feel without looking
        at the screen
  - [ ] Saved at projects/lesson-002-pads.als
- **Notes:**

## lesson-003: Four-on-the-floor at 126 BPM [blocked]

- **Why blocked:** depends on lesson-002 (kick + clap pad muscle memory).
- **Why next once unblocked:** Tech house is the dominant cluster in your
  taste profile (the 124-128 BPM bucket is the largest). Four-on-the-floor
  is the genre's foundational groove per `knowledge/genres/tech-house.md`.
- **Estimated time:** 45 min
- **Depends on:** lesson-002
- **Hardware:** MPK pads for kick / clap / hi-hat; MPK keys not used yet.
- **Practice task:** Build a 16-bar four-on-the-floor pattern in MIDI per
  the structure in `knowledge/genres/tech-house.md` Cheat block: kick on
  every beat (1, 2, 3, 4), clap on 2 and 4, open hi-hat on the off-beats
  ("and"s). Quantize the kicks tight; leave the hat with a touch of swing
  if it feels human. Loop for at least 60 seconds and listen for the
  "tss-tss" pulse the cheat sheet describes.
- **Done criteria:**
  - [ ] 4 bars of MIDI on the kick track with hits on beats 1, 2, 3, 4
        (not 16th-resolution bounce — straight quarters)
  - [ ] Clap on beats 2 and 4 of every bar
  - [ ] Open hi-hat on every off-beat (the "and" of 1, 2, 3, 4)
  - [ ] Saved at projects/lesson-003-four-on-floor.als
- **Notes:**

## lesson-004: First sidechained bass — the tech-house signature [blocked]

- **Why blocked:** depends on lesson-003 (need the kick pattern as the sidechain trigger).
- **Why next once unblocked:** Sidechain compression is the single defining
  technique of tech house per `knowledge/genres/tech-house.md`. This is the
  payoff for the foundation work — the moment your project starts sounding
  like the genre you listen to.
- **Estimated time:** 60 min
- **Depends on:** lesson-003
- **Hardware:** MPK keys for the bass note; pads still drive the drums.
- **Practice task:** On a new MIDI track, play a single sustained bass note
  in C1 (use Operator with a simple sub-bass preset). Insert an Ableton
  Compressor on the bass track; in the compressor's sidechain panel, set
  the source to your kick track. Tune threshold + ratio until the bass
  ducks 3-6 dB on every kick hit. Reference: `knowledge/genres/tech-house.md`
  (sidechain section), `knowledge/ableton/the-mixer.md`. If you can't find
  the sidechain dropdown, use `knowledge/ableton/companion-mode.md`.
- **Done criteria:**
  - [ ] Bass track has a Compressor with sidechain input set to the kick track
  - [ ] Compressor's gain-reduction meter shows ~3-6 dB on every kick hit
  - [ ] You can hear the bass "pumping" in time with the kick
  - [ ] Saved at projects/lesson-004-sidechain.als
- **Notes:**

## lesson-005: Pick a key from your taste, write a 4-bar hook [blocked]

- **Why blocked:** depends on lesson-004 (we're adding melodic content on
  top of the rhythm + sidechain foundation).
- **Why next once unblocked:** Your taste profile's top Camelot keys come
  from your actual library — writing a hook in one of those keys means
  your project will mix harmonically with tracks you already love.
  References: `knowledge/theory/the-camelot-wheel.md`,
  `knowledge/theory/scales-and-keys.md`.
- **Estimated time:** 45 min
- **Depends on:** lesson-004
- **Hardware:** MPK keys for the hook; pads still drive the drums.
- **Practice task:** Open `taste/profile.md` and pick a Camelot key from
  the top of the Key bias section. Set up a new MIDI track with a simple
  lead synth (Operator preset or one from the browser). Using only notes
  in that key's scale (consult `knowledge/theory/scales-and-keys.md`),
  write a 4-bar melodic hook with at most 8 notes. Less is more — keep it
  sparse like the tech-house cheat sheet describes.
- **Done criteria:**
  - [ ] Project key is documented in a comment / clip note (e.g.,
        "key: 8A / A minor")
  - [ ] Lead MIDI track contains a 4-bar hook with all notes in the chosen scale
  - [ ] Hook has 8 or fewer notes
  - [ ] Saved at projects/lesson-005-hook.als
- **Notes:**

## lesson-006: Stack the groove — open hat + percussion loop [blocked]

- **Why blocked:** depends on lesson-005 (we're layering on a rhythmic +
  melodic foundation).
- **Why next once unblocked:** Tech house's texture comes from layered
  percussion in the gaps. Adding the open hat on the "and"s (already done
  in lesson-003) and a 1/16 percussion loop closes the rhythmic picture
  per `knowledge/genres/tech-house.md`. This is the lesson where the
  beat starts to feel like a real club track.
- **Estimated time:** 45 min
- **Depends on:** lesson-005
- **Hardware:** MPK pads for shaker / conga / processed claps.
- **Practice task:** On a new MIDI track in your lesson-005 project, load
  a percussion sample (shaker, conga, or processed clap) and program a
  1/16 loop that fills the off-beats. Optionally tap it in live on the
  pads for human feel. Listen back: the kick + clap + open-hat + perc
  layer should fill the beat without anyone instrument crowding.
- **Done criteria:**
  - [ ] New percussion track with a 1/16 pattern (shaker / conga / clap)
  - [ ] Beat sounds full but not muddy — perc fills gaps without competing
        with the kick
  - [ ] You can name out loud what each percussion element does in the mix
  - [ ] Saved as projects/lesson-006-groove.als
- **Notes:**

## lesson-007: Session view → Arrangement view: intro / drop / break / drop [blocked]

- **Why blocked:** depends on lesson-006 (need a complete drop loop to arrange).
- **Why next once unblocked:** The intro / drop A / break / drop B
  structure in `knowledge/genres/tech-house.md` is what turns a loop into
  a track. This lesson is the bridge from "I have a beat" to "I have an
  arrangement." References: `knowledge/ableton/session-vs-arrangement-view.md`.
- **Estimated time:** 60 min
- **Depends on:** lesson-006
- **Hardware:** mostly mouse work; pads optional.
- **Practice task:** Take your lesson-006 project. In Session view, set
  up clip slots for: Intro (32 bars), Drop A (32 bars), Break (16 bars),
  Drop B (32 bars), Outro (32 bars). Record into Arrangement view,
  building the structure by dropping clips on/off as the cheat sheet
  describes (intro = drums building, no bass yet; drop A = full;
  break = kick out + riser; drop B = back to full).
- **Done criteria:**
  - [ ] Arrangement view contains all five sections back-to-back
  - [ ] Drop A and Drop B both have kick + bass + sidechain
  - [ ] Break has the kick removed (riser / vocal sample optional)
  - [ ] Saved as projects/lesson-007-arrangement.als
- **Notes:**

## lesson-008: Save and bounce your first complete short track [blocked]

- **Why blocked:** depends on lesson-007 (arrangement must exist).
- **Why next once unblocked:** Closure. End of the foundation arc — you've
  got a 2-minute tech-house track that touches every primitive in
  `knowledge/genres/tech-house.md`. Bouncing it makes it real.
- **Estimated time:** 30 min
- **Depends on:** lesson-007
- **Hardware:** none.
- **Practice task:** Set Arrangement view's loop brace around the full
  arrangement (intro through outro). Use File → Export Audio/Video to
  bounce a wav. Listen to the wav outside Ableton (in your normal
  music-listening app) and notice what feels different vs. listening in
  the project.
- **Done criteria:**
  - [ ] Arrangement saved at projects/tech-house-drop-01.als
  - [ ] Bounced wav exists at projects/tech-house-drop-01.wav
  - [ ] You've listened to the wav at least once outside Ableton
- **Notes:**

## lesson-009: Half-time dubstep pattern at 140 BPM [blocked]

- **Why blocked:** depends on lesson-008 (foundation arc complete; tempo / groove switch is a meaningful step).
- **Stub — full lesson body authored when this becomes active.** Will draw
  from `knowledge/genres/dubstep.md` and the Subtronics / Zeds Dead artist
  pages.

## lesson-010: Wobble bass in Operator [blocked]

- **Why blocked:** depends on lesson-009 (need the half-time foundation in place to write a wobble line into).
- **Stub — full lesson body authored when this becomes active.** First
  synthesis-design lesson; teaches LFO routing in Operator.

## lesson-011: Melodic dubstep build — piano intro into a soft drop [blocked]

- **Why blocked:** depends on lesson-010 (sound design groundwork).
- **Stub — full lesson body authored when this becomes active.** Will
  draw from `knowledge/genres/melodic-dubstep.md` and the Wooli /
  Levity / nimino artist pages.

## lesson-012: Cross-genre tempo / key planning with the Camelot wheel [blocked]

- **Why blocked:** depends on lesson-011 (multiple genres now in your hands).
- **Stub — full lesson body authored when this becomes active.** Bridges
  back to `taste/profile.md`'s Camelot data and sets up DJ-adjacent
  thinking. References `knowledge/theory/the-camelot-wheel.md`.
