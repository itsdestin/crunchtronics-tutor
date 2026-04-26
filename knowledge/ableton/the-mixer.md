---
slug: the-mixer
category: ableton
tldr: "The channel-strip view: per-track volume, pan, sends, plus master and return tracks."
prerequisites: []
references:
  - "Ableton Manual: Mixing (mixer view, sends, returns)"
next: null
---

# The mixer

## TL;DR
The channel-strip view: per-track volume, pan, sends, plus master and return tracks. Every track in your set has a vertical strip with the same controls — fader, pan knob, mute/solo, send knobs, output routing — and they all flow into a master strip on the right. Sends let you route a copy of any track into a "return" track that hosts shared effects.

## Cheat block
- **Per-track strip:** Volume fader, Pan knob, Mute / Solo / Arm, Sends (one knob per return track), Output routing (which bus the track sends to).
- **Master track:** rightmost strip. Final output before your speakers/headphones.
- **Return tracks:** lettered A, B, C... Hold shared effects (typical: A-Reverb, B-Delay).
- **Lite has 2 sends max** (so 2 return tracks — typically A-Reverb and B-Delay). Intro = 4. Standard = 12.
- **Sends are post-fader by default:** when you cut the channel volume, the send level cuts proportionally.
- **The send-and-return pattern:** put one big nice reverb on Return A, then dial Send A on every track that wants reverb. Better than putting a reverb on each track individually — saves CPU and keeps the spatial sound coherent.
- **Gain staging in one line:** keep individual track levels around -12 to -6 dB on the fader so the master doesn't clip. Mix with headroom.

## Read this yourself
The single biggest beginner mixing trap is putting a reverb on every single track. That works, but it eats CPU and produces a soupy, incoherent mix because each reverb has slightly different settings. The professional move is the send-and-return pattern: one nicely-tuned reverb sits on Return Track A; every track that wants reverb just turns up its Send A knob. Now everything shares the same room. Tweak that one reverb and the whole mix changes.

In Lite the limit is two return tracks — that's enough for one reverb and one delay, which covers 90% of what beginners need. Save your two slots for those. Effects that need to be track-specific (a saturator on the kick, an EQ on the bass) live as inserts on the track itself, not on a return.

Gain staging is the other beginner trap. New producers tend to push everything as loud as possible from the start; by the time they've got eight tracks playing, the master is clipping (the red square at the top of the master strip lights up). The fix is boring but works: keep every individual track around -12 to -6 dB on its fader, and the master will sit comfortably under 0 dB.

## See also
- `midi-vs-audio-tracks.md` — what's flowing into the mixer in the first place
- Reference: *Mixing (mixer view, sends, returns)* in `reference/INDEX.md`
