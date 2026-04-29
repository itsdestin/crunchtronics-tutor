---
slug: john-summit-crystallized
recipe_for: "John Summit — crystallized (feat. Inéz)"
target: "Ableton Live 12 Lite (8 audio + 8 MIDI tracks, Simpler-only, 2 sends)"
generated_at: 2026-04-29T08:05:00Z
---

# Recipe — build something inspired by *crystallized (feat. Inéz)*

**Track budget at a glance:**

| Track | Type | Device | Role |
|---|---|---|---|
| MIDI 1 | MIDI | Drum Rack | Kick, clap, hat, perc |
| MIDI 2 | MIDI | Operator | Sub bass |
| MIDI 3 | MIDI | Operator | Lead/hook synth |
| MIDI 4 | MIDI | Simpler | Vocal chop / atmosphere |
| Audio 1 | Audio | (sample) | Percussion loop (optional bounce) |
| Return A | Return | Reverb | Shared long-tail reverb |
| Return B | Return | Delay | Shared 1/8 delay |

Total MIDI tracks used: 4 of 8. Total audio tracks used: 1 of 8. Well within Lite floor.

---

## Project setup

**Step 1.** Set the tempo to **128 BPM** (prefer the csv value: 128.049 rounds to 128). This is the tech-house pocket — see `knowledge/genres/tech-house.md` (BPM cheat block) for why 124–128 is the standard.

**Step 2.** Set the project key to **3B — Db major** (the csv/ReccoBeats value is more reliable than librosa's 4A here). In Ableton, open the clip's MIDI editor and write a single whole-note Db4 in a "master key clip" on a muted MIDI track — your personal breadcrumb so you always know what key you're working in. See `knowledge/theory/the-camelot-wheel.md` for the Camelot numbering system.

**Step 3.** On Return Track A, drop an **Audio Effect Rack → Reverb** (Ableton built-in). Set Decay Time to ~3.5 s, Pre-Delay to 25 ms, Dry/Wet to 100% (returns are always 100% wet). On Return Track B, drop a **Delay**: set Left/Right time to 1/8, Feedback ~25%. These are your shared effect buses — see `knowledge/ableton/the-mixer.md` for the send-and-return pattern.

---

## Drum foundation (MIDI 1 — Drum Rack)

**Step 4.** Create a MIDI track. Drop a **Drum Rack** device on it. You are building the four-on-the-floor + clap pattern from `knowledge/genres/tech-house.md`.

**Step 5.** Kick (pad C1 — bottom-left pad on your MPK): find a punchy tech-house kick in Ableton's built-in sample packs (Browser → Packs → search "kick tech"). Drag it onto pad C1. In the Simpler inside that chain, set Mode to **One-Shot**, with no loop. Aim for a kick with a short, tight tail (under 0.5 s).

**Intro+ note (step 5):** With a 9th MIDI track available (Ableton Intro or Standard), you could layer a second Drum Rack with *only* a sub-808 layer tuned to Db (the root key), then sidechain-duck it identically to the main kick. This layered-kick technique is described in `knowledge/artists/john-summit.md` — "kick: layered (sub-808 + transient-shaped click on top)." With Lite's 8-track MIDI ceiling you can approximate it by putting both samples on two separate pads within the same Drum Rack and triggering them simultaneously.

**Step 6.** Open a 1-bar MIDI clip on MIDI 1. Draw in the four-on-the-floor kick pattern: notes at every beat — steps 1, 5, 9, 13 on a 16-step grid (i.e., 1/4 notes at beats 1, 2, 3, 4).

**Step 7.** Clap (pad E1 — second row, first pad): drag a tight clap or snare sample onto pad E1. Draw clap notes on beats 2 and 4 only — steps 5 and 13 on the 16-step grid.

**Step 8.** Closed hi-hat (pad G1): find a short, bright closed hat. Draw 16th-note hi-hats on every step *except* the beats (to get the "and" feel, draw on steps 3, 7, 11, 15 — the up-beats between kicks). Velocity: vary between 80 and 100 for a human feel.

**Step 9.** Open hi-hat (pad G#1): drag a longer open hat. Draw sparse hits — every 2 bars, on the "and" of beat 4 (step 15 of the second bar). Set pads G1 and G#1 to **Choke Group 1** in the Drum Rack so the closed hat cuts the open hat. See `knowledge/ableton/drum-rack-basics.md` for choke group setup.

**Step 10.** Percussion shaker/conga (pad A1): find a shaker or conga one-shot. Draw a syncopated 16th-note pattern — e.g., hits on steps 2, 4, 10, 14. Keep velocity low (~60–70) so it sits under the kick and clap.

---

## Bass + sidechain (MIDI 2 — Operator)

**Step 11.** Create a second MIDI track. Drop **Operator** on it. Set Operator to a simple sine or triangle wave on Oscillator A only — turn off oscillators B, C, D. This is your sub bass. Tune it to Db2 (the root note, one octave below Db3).

**Step 12.** In the MIDI clip, draw a rolling bass line in Db. A simple starting pattern: hold Db2 for 3/16 beats, rest 1/16, repeat. The bass plays *in the gaps* between kicks — so your bass notes should start just after beats 1, 2, 3, 4, not on them. See `knowledge/genres/tech-house.md` — "bass plays in the gaps between kicks."

**Step 13 — Sidechain routing:** Drop a **Compressor** (Ableton built-in) on MIDI 2's device chain *after* Operator. In the Compressor, click the triangle ("Sidechain") button to expand the sidechain panel. Set **Audio From** to "MIDI 1" (your Drum Rack track). Set Threshold to around −18 dB, Ratio 4:1, Attack 1 ms, Release 80 ms. You should see 3–6 dB of gain reduction on every kick hit. See `knowledge/genres/tech-house.md` under "Sidechain compression" and `knowledge/ableton/the-mixer.md` for routing context.

---

## Melodic layer (MIDI 3 — Operator)

**Step 14.** Create a third MIDI track. Drop a second **Operator** on it. To approximate a "vocal formant / talky wavetable" sound (the Summit signature per `knowledge/artists/john-summit.md`): set Oscillator A to a sawtooth wave, add a resonant low-pass filter with Resonance ~40%, and automate the filter cutoff up over 4 bars to give it movement. Set the envelope attack to ~20 ms and release to ~300 ms.

**Step 15.** Tune the lead to **3B / Db major**. A simple 2-note motif: Db4 and Ab4 (the root and fifth). Loop a 4-bar motif and let it run through the drop. Keep the note rhythm sparse — held notes work better than busy runs in tech house (see `knowledge/genres/tech-house.md` — "melodic content: sparse").

**Step 16.** Dial up **Send A** (Return A Reverb) on this track to about 40–50%. The lead should feel like it "floats" in the room while the bass and kick are dry and punchy.

---

## Texture + perc (MIDI 4 — Simpler)

**Step 17.** Create a fourth MIDI track. Drop **Simpler** on it. In the Browser, find a short one-shot atmospheric pad or chord stab sample (Ableton's built-in Packs → "Ambient" or "Pad"). Load it into Simpler, set Mode to **One-Shot**. Tune the root key to Db.

**Step 18.** Draw in a sparse MIDI clip: a single long Db chord note held for 4 bars, then silence for 4 bars, then repeat. Keep velocity low (~55). Dial Send A (reverb) high on this track (~70%) — the pad should mostly be reverb wash, not dry attack.

**Intro+ note (step 18):** The 8-MIDI-track Lite floor is the tightest constraint on this recipe. MIDI 1 carries the full drum kit (kick, clap, hat, perc — all on one Drum Rack), MIDI 2 carries bass, MIDI 3 carries lead, MIDI 4 carries pad. That uses 4 of 8 MIDI tracks — leaving 4 more free. In a real John Summit production you'd expect at minimum: a dedicated percussion loop track, a separate vocal-chop track, an automation track for filter sweeps, and a riser/FX track for the build. If you hit Lite's 8-MIDI ceiling as the arrangement grows, a 9th MIDI track (Ableton Intro or Standard) is where you'd put the vocal-chop layer, since that's the hardest thing to fake inside an existing Drum Rack chain.

---

## Arrangement

**Step 19.** Build the section structure from `teardowns/john-summit-crystallized/teardown.md`:

| Section | Start | End | What's playing |
|---|---|---|---|
| Intro | 0:00 | 0:40 | Drum Rack (kick only at first, then full kit) — NO bass, NO lead |
| Drop A | 0:40 | 1:52 | All tracks: drums + bass + lead + pad |
| Break | 1:52 | 2:45 | Pad + reverb tail only — mute kick, bass, lead clips |
| Drop B | 2:45 | 3:32 | All tracks back — identical or +1 variation on lead velocity |
| Outro | 3:32 | 3:37 | Volume automation fade to silence |

In Ableton's **Arrangement View**, create scene clips for each section. Start with the Intro: only MIDI 1's drum clip active, all others silent. At 0:40 (bar 9 at 128 BPM, since each 4-bar phrase = ~1.875 s, so 0:40 ≈ bar 22 — use the bar ruler at the top of Arrangement View to find the right spot) drop all remaining clips in simultaneously.

**Step 20.** For the Break (1:52): deactivate all MIDI clips except MIDI 4 (pad). Automate the pad's reverb send (Return A) up to ~80% so the break sounds very spacious and empty.

**Step 21.** For Drop B (2:45): re-activate all clips. Consider automating the Operator filter cutoff on MIDI 3 (lead) slightly higher than in Drop A — a subtle brightness increase that makes the second drop feel "bigger" without adding new tracks.

---

## Artist-resource enhancement

Based on `knowledge/artists/john-summit.md`:

- **Splice "Sounds of John Summit" pack:** unverified — search inconclusive as of 2026-04-28. No pack to recommend.
- **Preset packs:** unverified — search inconclusive as of 2026-04-28.
- **Verified interviews and breakdowns:**
  - Beatport "Go Back" (with Sub Focus) track breakdown — direct producer commentary on kick layering and bass routing, which is directly relevant to this recipe: https://www.beatportal.com/videos/646601-track-breakdown-john-summit-sub-focus-go-back-feat-julia-church
  - MusicTech interview on production approach: https://musictech.com/features/interviews/john-summit-interview-comfort-in-chaos/
- **Sound-design hint from artist page:** when recreating the kick, layer two samples — a sub-heavy 808 with the transient cut, plus a separate clicky "tok" transient. Tune the sub layer to Db (the project root). See `knowledge/artists/john-summit.md` for the full description, and `knowledge/ableton/drum-rack-basics.md` for how to put both samples on separate pads within the same Drum Rack.
