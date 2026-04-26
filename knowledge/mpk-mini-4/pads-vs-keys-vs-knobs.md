---
slug: pads-vs-keys-vs-knobs
category: mpk-mini-4
tldr: "Pads (8) trigger drums or samples; keys (25) play melodies and chords; knobs (8) send MIDI CCs you can map onto plugin parameters."
prerequisites: []
references:
  - "MPK Manual: Features overview (top + rear panel callouts)"
  - "MPK Manual: Pad Modes (Notes / CC# / Program Change)"
next: transport-controls
---

# Pads vs keys vs knobs

## TL;DR
Pads (8) trigger drums or samples; keys (25) play melodies and chords; knobs (8) send MIDI CCs you can map onto plugin parameters. Three input surfaces, three different jobs. Each surface is velocity-sensitive (or, in the knobs' case, continuous), and each can be reconfigured per saved program.

## Cheat block
- **8 pads** in two rows of four. **Velocity-sensitive.** Default mode: **Notes**, mapped to MIDI notes C1-G1 (bottom-left = C1) — exactly matches the bottom-left 8 chains of an Ableton Drum Rack.
  - **Pad banks A / B / C / D:** four banks of 8 pads = **32 effective pads.** Bank button cycles through them.
  - **Pad modes:** Notes (default), CC# (each pad sends a CC), Program Change (each pad fires a program change).
- **25 keys** = two octaves + 1 (C to C). **Velocity-sensitive.** Octave +/- buttons shift the playable range up or down.
  - **Scales mode:** locks the keyboard to a chosen scale (root + scale type) so you can't play wrong notes.
  - **Chords mode:** one key triggers a full triad in your chosen key.
  - **Arpeggiator:** holds a chord, plays it as an up/down/random pattern at a chosen rate.
- **8 endless knobs.** Send MIDI CC messages. Two modes:
  - **Absolute:** knob position = CC value (jumps when you grab a knob whose physical position doesn't match the on-screen value).
  - **Relative:** sends "increment / decrement" — no jumps. Better for mapping to plugin parameters.

## Read this yourself
The MPK's three input surfaces map cleanly to three production jobs. Pads are for percussion, one-shots, and triggers — anything you'd hit, not hold. Keys are for played notes — melodies, chord stabs, bass lines. Knobs are for *changing things while they're playing* — the filter cutoff on a synth, the wet level on a reverb, the volume of a clip you're recording an automation for.

Two beginner-superpower features hide on the keyboard: **Scales mode** and **Chords mode**. Scales mode rearranges the keyboard so every key belongs to a chosen scale — pick A minor and you literally cannot play a wrong note. Chords mode makes every key trigger a full triad in your chosen key. Together they let a complete non-pianist write convincing chord progressions in twenty minutes.

The pad banks (A/B/C/D) take the eight physical pads and multiply them into 32 effective pads — perfect for triggering a full Drum Rack with sixteen kit pieces, or fifteen kit pieces and a pad reserved for an FX one-shot.

## See also
- `mapping-pads-to-drum-rack.md` — end-to-end MPK pads → Drum Rack recipe
- `../ableton/drum-rack-basics.md` — the Ableton side of that pairing
- Reference: *Features overview (top + rear panel callouts)* in `reference/INDEX.md`
- Reference: *Pad Modes (Notes / CC# / Program Change)* in `reference/INDEX.md`
