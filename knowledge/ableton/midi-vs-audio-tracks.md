---
slug: midi-vs-audio-tracks
category: ableton
tldr: "MIDI tracks hold notes that drive instruments; audio tracks hold recorded sound — pick MIDI when you want to change the notes later."
prerequisites: []
references:
  - "Ableton Manual: Editing MIDI Notes and Velocities"
  - "Ableton Manual: Audio Clips, Tempo, and Warping"
next: the-mixer
---

# MIDI vs audio tracks

## TL;DR
MIDI tracks hold notes that drive instruments; audio tracks hold recorded sound — pick MIDI when you want to change the notes later. **MIDI** is musical instructions ("play C3 for half a beat at velocity 96") routed into an instrument plugin. **Audio** is a recorded waveform — the actual sound. They behave very differently once they're on the timeline.

## Cheat block
- **MIDI track:** holds note data. Needs an instrument plugin loaded on it (Simpler, Operator, third-party VST, etc.) for sound to come out.
- **Audio track:** holds a waveform. Plays it back; warps it (stretches/compresses to tempo) but can't easily change the notes inside it.
- **MIDI is fully editable post-recording.** Move notes, change pitches, alter velocity, quantize. Easy.
- **Audio is warp-editable but pitch-rigid.** You can stretch tempo and shift pitch by semitones, but you can't change *which* notes are inside a recorded chord.
- **Freezing + flattening:** Right-click track → Freeze. Right-click again → Flatten. Turns a MIDI track into an audio track (saves CPU; locks in the sound).
- **When to pick MIDI:** anything you might want to revise — drums, bass lines, melodies, chords.
- **When to pick audio:** recorded vocals, sampled loops you want to keep stable, finished bounces.

## Read this yourself
Think of MIDI as the sheet music and audio as the recording. Sheet music can be rewritten — change a note here, transpose the whole piece down a step — without re-recording anything. A recording is fixed: you can speed it up or slow it down, but you can't easily turn a C major chord into a D minor one without doing actual chemistry.

The practical rule for beginners: **start everything as MIDI** if there's any chance you'll want to change it later. That covers drums (programmed in a Drum Rack), basses, melodies, chords. The only things that need to be audio from the start are recordings of real instruments or vocals, and pre-made loops where the actual recording is the point. Once you're sure a part is final, freeze and flatten it to lock it in and free up CPU.

## See also
- `simpler-basics.md` — the instrument that turns audio samples into MIDI-playable notes
- `drum-rack-basics.md` — drums-as-MIDI on a single track
- Reference: *Editing MIDI Notes and Velocities* in `reference/INDEX.md`
- Reference: *Audio Clips, Tempo, and Warping* in `reference/INDEX.md`
