---
slug: transport-controls
category: mpk-mini-4
tldr: "Built-in play / stop / record / loop / tap-tempo buttons that drive Ableton's transport over MIDI."
prerequisites: []
references:
  - "MPK Manual: Setup with other DAWs (Ableton, Logic, FL, Cubase, GarageBand)"
next: mapping-pads-to-drum-rack
---

# Transport controls

## TL;DR
Built-in play / stop / record / loop / tap-tempo buttons that drive Ableton's transport over MIDI. Once the MPK and Ableton are talking to each other, those small black buttons on the top-left of the MPK become hands-free transport — you can start, stop, record, and loop without touching the mouse.

## Cheat block
- **Buttons:** Play, Stop, Record, Loop, plus Tap Tempo and metronome on the same panel.
- **Mapping path** (one-time setup):
  1. On the MPK, select the **Ableton preset** (the MPK ships with DAW-specific presets — pick the Ableton one).
  2. In Ableton: **Preferences → Link/Tempo/MIDI → MIDI** tab.
  3. Find the MPK in the Control Surface list, set Input + Output to MPK Mini 4.
  4. In the same MIDI panel, enable **Track / Sync / Remote** for the MPK input row.
- **Tap Tempo:** repeatedly tap the button at the speed you want; Ableton updates the project tempo to match. Useful for matching the BPM of an unknown audio loop.
- **Loop button:** toggles Arrangement Loop. Combine with the loop region brackets (in Arrangement view) to repeat a section while you tweak.

## Read this yourself
The first time the MPK transport buttons start Ableton playback without you touching the mouse is a small but real moment. It signals that the controller is fully integrated — that you can leave the keyboard and mouse and just play. Worth the five minutes of one-time setup in Preferences.

The Tap Tempo button is the other hidden gem. If you've got a sample or a YouTube reference track playing in your head and you want to know what BPM it is, just tap along — Ableton updates the project tempo each tap. Three or four taps and you're locked to that tempo. From there, every grid in your set syncs to it.

## See also
- `mapping-pads-to-drum-rack.md` — the next end-to-end recipe once transport is wired up
- `../ableton/session-vs-arrangement-view.md` — what the play button is launching
- Reference: *Setup with other DAWs (Ableton, Logic, FL, Cubase, GarageBand)* in `reference/INDEX.md`
