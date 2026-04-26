---
slug: mapping-pads-to-drum-rack
category: mpk-mini-4
tldr: "End-to-end recipe for triggering Ableton Drum Rack pads from your MPK pads."
prerequisites: [pads-vs-keys-vs-knobs]
references:
  - "MPK Manual: Pad Modes (Notes / CC# / Program Change)"
  - "Ableton Manual: Instrument, Drum and Effect Racks (incl. Drum Rack)"
next: mpk-program-editor
---

# Mapping pads to Drum Rack

## TL;DR
End-to-end recipe for triggering Ableton Drum Rack pads from your MPK pads. The default factory configuration already works — MPK pads in Notes mode emit MIDI notes C1-G1, which is exactly the lower row of any Ableton Drum Rack. Five steps and the first satisfying hit is yours.

## Cheat block
1. **MPK in Notes mode** (default). Confirm by checking the pad-mode indicator; if it's not Notes, hold Shift + the pad-mode button until it is.
2. **In Ableton, drop a Drum Rack on a MIDI track.** Browser → Drums → drag any preset kit to a MIDI track.
3. **Arm the track** — click the small round arm button at the bottom of the channel strip until it's red.
4. **Hit a pad.** The corresponding pad in the Drum Rack should light up and play.
5. **If nothing happens:** verify Track / Remote in Preferences → MIDI for the MPK row, check the MPK is sending on the channel Ableton is listening for, check the track's Input is "All Ins" or specifically the MPK.

**Common gotchas:**
- **Wrong octave.** Pad bank A = C1-G1 (matches Drum Rack lower row). Bank B = G#1-D#2 (upper row). Use Pad Bank button to switch.
- **Wrong MIDI channel.** Default is channel 1 on the MPK; default in Ableton track input is "All Channels". Don't change either if it's working.
- **Track not armed.** No red arm button = no MIDI in. The most common silent failure.

## Read this yourself
This is the recipe that makes the MPK feel like real production hardware. Up until this point the MPK is just a fancy keyboard; once it's triggering Drum Rack pads, you can program a beat without ever clicking the mouse. Drop a kit, arm the track, and start tapping out a four-on-the-floor pattern in record mode.

A subtle thing worth noticing: the MPK's bottom-row pads (1-4) map to MIDI notes C1, C#1, D1, D#1. The Drum Rack's bottom-row pads (1-4) map to those same notes. They line up because Akai (the company) helped Ableton (the company) standardize this exact mapping back when the original MPK launched in 2010. The convention has held for fifteen years and four MPK generations — your MPK Mini 4 still works the same way the OG did. Few hardware/software pairings are this stable.

## See also
- `../ableton/drum-rack-basics.md` — the Ableton-side primer
- `pads-vs-keys-vs-knobs.md` — what else the pads can do beyond Drum Rack
- Reference: *Pad Modes (Notes / CC# / Program Change)* in `reference/INDEX.md`
- Reference: *Instrument, Drum and Effect Racks (incl. Drum Rack)* in `reference/INDEX.md`
