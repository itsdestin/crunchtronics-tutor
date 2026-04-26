---
slug: simpler-basics
category: ableton
tldr: "Simpler plays a single sample as a melodic instrument — Lite/Intro's main sampler (no Sampler in those editions)."
prerequisites: []
references:
  - "Ableton Manual: Live Instrument Reference"
next: drum-rack-basics
---

# Simpler basics

## TL;DR
Simpler plays a single sample as a melodic instrument — Lite/Intro's main sampler (no Sampler in those editions). Drag a one-shot or loop onto Simpler and play it from the keyboard at any pitch. Three modes — Classic, One-Shot, Slice — cover almost everything you'd want to do with a sample short of full multi-sample sound design (which needs Sampler, which Lite/Intro don't ship).

## Cheat block
- **Three modes** (selectable in the device header):
  - **Classic:** chromatic playback. Every key plays the sample at a different pitch. Built-in **ADSR envelope** for shaping it like an instrument.
  - **One-Shot:** plays the whole sample once on any key trigger. No pitch-tracking. Good for vocal stabs and impact hits.
  - **Slice:** chops the sample at transients (or at fixed grid points). Each slice gets mapped to a pad. Good for chopping a vocal phrase or a drum loop.
- **ADSR envelope** (Classic mode): **A**ttack (fade-in), **D**ecay (fall to sustain), **S**ustain (held level), **R**elease (fade-out after key release). Knobs are at the right side of the device.
- **Warp toggle:** for samples longer than a one-shot, lets the sample lock to project tempo.
- **Lite limit:** Lite/Intro have **Simpler, not Sampler**. Sampler adds multi-sample zones and deeper modulation. For now, Simpler is plenty.

## Read this yourself
Drop a vocal one-shot onto Simpler in Classic mode and play it across the keyboard — you'll hear the sample pitch-shift. That's the simplest way to turn any audio file into a playable instrument. Tweak the Attack knob up and the sound fades in instead of starting instantly; tweak Release up and it lingers after you release the key. That's the whole envelope concept in three knobs.

One-Shot mode is the fastest way to fire a sample — load an impact or a sub bass hit, and any key triggers the full sample. Useful for build-ups where you want a "boom" you can place on any beat without worrying about pitch.

Slice mode is the secret weapon. Drop a four-bar drum loop on Simpler, switch to Slice, and Simpler chops the loop at every transient and lays the chops out across the keyboard. Now every drum hit in the loop is its own playable note — you can rearrange the loop into a totally different beat just by playing the keys in a new order.

## See also
- `drum-rack-basics.md` — when one Simpler isn't enough; rack 16 of them
- `the-browser.md` — where you find samples to drop on Simpler
- Reference: *Live Instrument Reference* in `reference/INDEX.md`
