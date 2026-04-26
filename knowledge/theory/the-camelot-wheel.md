---
slug: the-camelot-wheel
category: theory
tldr: "Camelot notation — a DJ-friendly map of which keys mix harmonically."
prerequisites: [scales-and-keys]
references: []
next: null
---

# The Camelot wheel

## TL;DR
Camelot notation — a DJ-friendly map of which keys mix harmonically. Instead of memorizing which Western keys sound good together (e.g., "C major and A minor share the same notes"), Camelot gives every key a number from 1 to 12 plus a letter (A or B). Keys with the same number, or numbers ±1 apart, mix without clashing.

## Cheat block
- **Codes:** 12 numbers (1-12) × {A, B} = 24 codes. **B = major**, **A = minor.**
- Examples: C major = 8B, A minor = 8A, G major = 9B, E minor = 9A.
- **Mixing rules:**
  - **Same code** (e.g., 8B → 8B): same key — guaranteed compatible.
  - **Same number, swap letter** (8A → 8B): relative major/minor swap. Mood shift, same notes.
  - **±1 number, same letter** (8B → 9B or 8B → 7B): adjacent keys on the wheel — closely related, smooth.
  - **±2** or further: increasingly different; possible but harder.
  - **Energy boost (+7 trick):** jump 7 numbers same letter for a "key-up" lift in the drop. DJs use this to ratchet energy.
- The wheel **wraps modulo 12**: 12 + 1 = 1, not 13.

## Read this yourself
DJs adopted Camelot because it does in arithmetic what classical theory does with memorization. You don't need to know that the relative minor of D major is B minor — you just need to know that D major is 10B and B minor is 10A, and they share a number, so they mix.

For producing, this same notation is your shortcut to using `taste/tracks.csv` intelligently. Once that file is populated with `key_camelot` per track, you can ask Claude things like "find me three tracks at 128 BPM in 8A or 9A" and get a coherent batch to study together. It also lets you spot patterns in your own taste — most listeners cluster heavily in three or four Camelot codes without realizing it.

## See also
- `scales-and-keys.md` — Western-notation foundation Camelot maps onto
- Reference: *Camelot Wheel reference* in `reference/ONLINE.md`
