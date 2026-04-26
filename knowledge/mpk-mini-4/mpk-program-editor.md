---
slug: mpk-program-editor
category: mpk-mini-4
tldr: "Akai's free desktop app for creating custom MPK presets — what each pad, knob, and key does in your saved configuration."
prerequisites: [pads-vs-keys-vs-knobs]
references:
  - "MPK Manual: Program Edit (custom user presets)"
next: null
---

# MPK Program Editor

## TL;DR
Akai's free desktop app for creating custom MPK presets — what each pad, knob, and key does in your saved configuration. The MPK has eight onboard program slots; the Program Editor app is how you fill those slots with your own custom mappings (specific knob CC numbers, specific pad note assignments, specific MIDI channel) instead of relying on factory defaults.

## Cheat block
- **Where to get it:** akaipro.com → Downloads → MPK Mini 4 → Program Editor (free; macOS + Windows builds).
- **What it edits:**
  - **Knob CC numbers** (per knob, per program). Map knob 1 to CC #74 to control filter cutoff in Ableton; knob 2 to CC #71 for resonance; etc.
  - **Pad MIDI notes** (per pad, per bank, per program). Override the default C1-G1 mapping for non-Drum-Rack uses.
  - **MIDI channel** (per program). Useful when running multiple controllers and routing each to a specific track.
  - **Pad mode default per program** (Notes / CC# / Program Change).
- **Save up to 8 onboard programs.** Recall them with the Program button on the MPK.
- **Per-program presets** make sense when you have repeated workflows: one program for Drum Rack work, one for Operator/Wavetable knob mappings, one for live performance.

## Read this yourself
Most of the time, the factory defaults are exactly what you want — pads to MIDI notes that match Drum Rack, keys to standard 25-key layout, knobs to generic CC numbers Ableton's MIDI Map mode can absorb easily. You can produce for months without opening the Program Editor.

Where the editor pays off is when you keep doing the same workflow over and over and notice the friction. If every session you find yourself MIDI-mapping knob 1 to a synth's filter cutoff, save a program where knob 1 already sends CC #74 (the standard cutoff CC) and Ableton's MIDI Map mode will recognize it instantly. Or if you're using the pads to fire scene clips in Ableton's Session view, save a program where the pads send Program Change messages tied to scene numbers.

The friction-reduction pattern: notice a workflow you do three times in a row, then save a program for it. Don't pre-build programs you might use someday.

## See also
- `pads-vs-keys-vs-knobs.md` — what the surfaces do by default before you customize
- Reference: *Program Edit (custom user presets)* in `reference/INDEX.md`
