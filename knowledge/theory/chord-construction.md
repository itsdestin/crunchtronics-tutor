---
slug: chord-construction
category: theory
tldr: "How triads and seventh chords are built from scale degrees."
prerequisites: [intervals, scales-and-keys]
references:
  - "MPK Manual: Chords Mode (configuration, inversions, transpose/ignore)"
next: the-camelot-wheel
---

# Chord construction

## TL;DR
How triads and seventh chords are built from scale degrees. A chord is two or more notes played at once; the most common one is the triad — three notes stacked in thirds. Add a seventh on top and you get the lush, jazzier chords that carry melodic dubstep and house breakdowns.

## Cheat block
- **Triad = root + 3rd + 5th**, three notes stacked in thirds (skipping every other scale note).
- **Major triad:** root + **M3** + **P5**. Bright and stable.
- **Minor triad:** root + **m3** + **P5**. Dark and stable.
- **Diminished triad:** root + m3 + diminished 5th. Tense.
- **Sus2 / sus4:** replace the 3rd with the 2nd or 4th. Open, unresolved.
- **Seventh chords:** triad + 7th note.
  - **maj7:** major triad + M7. Lush, dreamy.
  - **7 (dominant):** major triad + m7. Bluesy, wants to resolve.
  - **m7:** minor triad + m7. Mellow, jazzy.
- **Inversions:** same chord, different bass note. C major root position = C-E-G; first inversion = E-G-C; second = G-C-E.
- **The pop progression:** I-V-vi-IV. In C major: C - G - Am - F. You'll hear it in literally thousands of tracks.

## Read this yourself
Think of a triad like a three-rung ladder built from a scale: pick a starting note (the root), skip the next note, climb to the second rung (the 3rd), skip again, climb to the third rung (the 5th). That's it. The whole "is it major or minor" thing comes down to one note — whether the middle rung is a major third or a minor third above the root. Everything else is decoration.

The MPK's Chords Mode is the fastest way to internalize this. Turn it on, and one key on the keyboard plays a whole triad in your chosen key. Walk up the keyboard and you're walking through the chords of that key — i, ii, III, iv, v, VI, VII (capitals = major, lowercase = minor; natural minor goes minor, diminished, major, minor, minor, major, major). Once you can hear which positions feel like home and which feel like tension wanting resolution, you're writing chord progressions.

## See also
- `scales-and-keys.md` — where the notes come from
- `../mpk-mini-4/pads-vs-keys-vs-knobs.md` — where Chords Mode lives on the hardware
- Reference: *Chords Mode (configuration, inversions, transpose/ignore)* in `reference/INDEX.md`
