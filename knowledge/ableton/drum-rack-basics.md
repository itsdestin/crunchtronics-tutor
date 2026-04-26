---
slug: drum-rack-basics
category: ableton
tldr: "Drum Rack is a 16-pad device that hosts one Simpler/sample per pad, mapped to MIDI notes C1-D#2."
prerequisites: []
references:
  - "Ableton Manual: Instrument, Drum and Effect Racks (incl. Drum Rack)"
next: null
---

# Drum Rack basics

## TL;DR
Drum Rack is a 16-pad device that hosts one Simpler/sample per pad, mapped to MIDI notes C1-D#2. Drag samples onto pads to build a kit; each pad is its own chain with independent volume, pan, and send levels. The MPK Mini 4's eight pads default to that exact MIDI note range — drop a Drum Rack on a track, and you can play it from the controller without setup.

## Cheat block
- **16 pads = 16 chains.** A "chain" is a mini signal path: sample → optional Simpler controls → optional inserts → output.
- **Default pad-to-note mapping:** C1 = bottom-left pad. Walking right along the bottom row: C1, C#1, D1, D#1. Up to row 2: E1, F1, F#1, G1. Row 3: G#1, A1, A#1, B1. Top row: C2, C#2, D2, D#2.
- **Build a kit:** drag a sample onto an empty pad — Drum Rack auto-creates a Simpler-on-One-Shot chain for it.
- **Per-pad mixer (right side of Drum Rack):** volume, pan, send A/B, mute/solo, choke group.
- **Choke groups:** assign multiple pads to the same choke group (1-16) and only one of them plays at a time. Standard use: open hi-hat and closed hi-hat on the same choke group → closed hat cuts off the open hat.
- **MPK pad mapping:** the MPK's 8 pads in Notes mode default to C1-G1 (= the bottom-left 8 pads of a Drum Rack). Use the MPK pad bank A/B/C/D buttons to reach the other 24 effective pads.

## Read this yourself
A Drum Rack is just sixteen Simplers in a tidy box. The reason it exists as its own device is that drum kits have a particular shape — sixteen pads in a 4×4 grid — and every drum machine since the 80s has used roughly that layout. Ableton's Drum Rack copies the convention so muscle memory transfers from any other drum machine you've used (and from your MPK).

Building a kit by hand is genuinely fun. Open the Browser, hover over a kick — it previews at the project tempo. Drop one you like onto pad 1 (the bottom-left pad, C1). Now drag a snare to pad 5 (E1, second row left), an open hat to pad 9 (G#1, third row left), a closed hat to pad 8 (G1, second row right). Set pads 9 and 8 to the same choke group so the closed hat kills the open hat. Suddenly you have a custom kit with the personality of whatever samples you picked, and your MPK pads play it directly.

## See also
- `simpler-basics.md` — what each pad's chain actually contains
- `../mpk-mini-4/mapping-pads-to-drum-rack.md` — the end-to-end MPK setup recipe
- Reference: *Instrument, Drum and Effect Racks (incl. Drum Rack)* in `reference/INDEX.md`
