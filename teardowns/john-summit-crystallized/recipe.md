---
slug: john-summit-crystallized
recipe_for: "crystallized (feat. Inéz) — John Summit"
target: "Ableton Live 12 Lite (8 audio + 8 MIDI tracks, Simpler-only, 2 sends)"
mode: genre-rebuild
generated_at: 2026-04-29T20:55:00Z
---

# Recipe — build something inspired by *crystallized (feat. Inéz)*

> Builds a track that hits the csv profile (BPM 128, key 3B Db major,
> energy 0.857, danceability 0.529) and follows the section structure
> measured in teardown.md, using the genre conventions from
> `knowledge/genres/tech-house.md`. This is not a transcription; it is a
> guided rebuild that touches the same production primitives — sub
> withhold, HPSS contrast, sidechain depth, spectral brightening.

## Project setup

1. Set tempo to **128 BPM** (csv authoritative; librosa read 129.2 — ignore).
2. Set project key to **3B — Db major**. Write "3B / Db major" in a Master Clip info text box (right-click empty clip slot → Edit Info Text) so you remember it while tracking.
3. Create 4 MIDI tracks and 2 Audio tracks (staying well within the 8+8 Lite floor). Name them: `Drums`, `Sub/Bass`, `Mid Hook`, `Perc Loop`, `FX/Riser`, `Vocal Sample`.

## Drum foundation (MIDI 1 — Drum Rack)

4. Load a Drum Rack on the `Drums` MIDI track. Program a four-on-the-floor kick (beat 1, 2, 3, 4 every bar) per `knowledge/genres/tech-house.md` cheat block. Add a tight clap or rim on beats 2 and 4. Add an open hi-hat on the "and"s.
5. Add a 1/16th percussion loop in a second Drum Rack chain or layer. Tech house leaves space — keep it sparse (shaker or conga loop pattern, not more than 3–4 hits per bar on top of the groove skeleton).
6. Reference the onset density from teardown.md: in the drops, total onset density across bands was 35–51/bar. In the break, it dropped to 3–16/bar. Use this as a calibration target when you're deciding how busy your percussion loop is. You don't need to hit the number — use it as a sanity check.

**Intro+ note (step 4):** With an extra MIDI track available, split the kick into its own dedicated MIDI/Drum Rack track (separate from clap + hat). This makes sidechaining the bass to just the kick trivial — sidechain input receives the kick track only, not the full drum bus.

## Sub + bass (MIDI 2 — Operator)

7. Load Operator on the `Sub/Bass` MIDI track. Start with a sine wave on Oscillator A (Algorithm: A only). Tune it to Db2 or Db3 — the root of the 3B key. This is your sub layer.
8. **Do not play the sub in the intro.** Mute or automate the track volume to near-zero for bars 0–22 (0:00–0:42). The teardown measures sub-band RMS below 4 through the entire intro (vs. 53–67 in Drop A). The withheld sub is the main structural move of this track — enforcing 42 seconds of near-zero sub is not optional decoration.
9. At the drop entry (~0:42), bring the sub in. Program a rolling bassline with syncopation — bass plays in the gaps between kicks, not on the same beat (per tech-house.md). Keep the note pattern to 1–2 pitches; the motion comes from filter automation or the sidechain pumping, not from chord changes.
10. **Sidechain the bass to the kick.** Put a Compressor on the `Sub/Bass` track. Set Sidechain input to the kick channel. Target: **~4–5 dB of gain reduction on every kick** — match the measured 4.49 dB mean ducking from analysis.json. Dial threshold/ratio until the gain-reduction meter shows approximately 4 dB on each kick hit; allow p90 moments (heavy downbeats) to reach 8–9 dB per the measured 8.54 dB p90 depth.

## Mid-range hook (MIDI 3 — Operator or Simpler)

11. Load a second Operator or a Simpler on `Mid Hook`. This layer carries the sustained low-mids harmonic content (250–2k Hz band) that the teardown shows holding at RMS 11–14 throughout every section — including the break. Program a simple 2–4 note motif in Db major. Keep it sparse — tech house leaves space.
12. Unlike the sub, **keep this layer running through the break** (reducing its volume slightly but not muting it). This mirrors the teardown's measured behavior: low-mids RMS stays at 11–14 in the break even when sub collapses. The break's energy comes from mid harmonic sustain, not silence.

## Texture + perc layer (MIDI 4 / Audio 1)

13. On `Perc Loop`: load a Simpler with a tech-house percussion one-shot or loop sample. Layer additional 1/16th groove on top of the Drum Rack without duplicating hits — e.g., a shaker 8th running against the hi-hat "and"s.
14. On `Vocal Sample` (Audio 1): if you have a vocal chop or short sample, load it here. Keep the phrase to 2–4 syllables repeating — tech house vocal hooks are minimal. Confirm any sample used is cleared/royalty-free.

## FX and riser (Audio 2)

15. Load a white noise sweep or riser sample on `FX/Riser`. Automate its volume to rise over 8–16 bars before the drop (bar 8–22 roughly, corresponding to the spectral centroid climb from ~836 Hz to ~3,271 Hz measured in the intro — per teardown.md Panel 4). Automate a high-pass filter cutting from 20 Hz up to ~2k Hz over the same period to mirror the centroid brightening.

## Arrangement

16. Follow the section structure measured in teardown.md:
    - **Intro (0:00–0:42, bars 0–22):** Drums + mid hook only. Sub muted. FX riser active. Centroid/filter brightening in progress.
    - **Drop A (0:42–1:42, bars 23–53):** All tracks active. Sub enters. Sidechain pumping engaged.
    - **Break (1:42–2:48, bars 54–92):** Mute or near-mute sub. Reduce percussion to minimal. Keep mid hook running. Build tension through bars 90–92 with rising riser + percussion re-entry.
    - **Drop B (2:48–3:32, bars 93–114):** Same as Drop A. Consider one small twist on the mid hook pattern to differentiate — keep it subtle.
    - **Outro (3:30–3:37, bars 114–115):** Full stop or fade. The original cuts abruptly at bar 115 (RMS drops from 0.352 to 0.018 in one bar per teardown.md).
17. Use Ableton's **Session View** to build each section as a row of clips, then record into Arrangement View once the sections feel right.

## Artist-resource enhancement

- **Beatport "Go Back" (with Sub Focus) Track Breakdown** (per `knowledge/artists/john-summit.md`): covers kick layering, bass routing, and arrangement decisions on a specific Summit record — the most directly applicable resource for cross-referencing your build decisions: `https://www.beatportal.com/videos/646601-track-breakdown-john-summit-sub-focus-go-back-feat-julia-church`
- **Splice "Sounds of John Summit" pack:** listed as unverified in `knowledge/artists/john-summit.md` — do not purchase based on this recipe. Check Splice directly before buying.
- **Preset packs:** unverified per artist page — recipe leans on Operator + genre conventions only.

## Intro+ notes

- **Intro+ note (step 10):** With a 9th MIDI track (not available in Lite), you could run a dedicated "kick send" MIDI track that fires silent MIDI notes to feed the Compressor sidechain without the kick audio passing through — a cleaner routing that lets you tune the sidechain trigger independently of the kick's audio chain. In Lite, routing the kick Drum Rack output directly to the Compressor sidechain input on the bass track is the correct workaround.
- **Intro+ note (step 14):** With additional audio tracks, you could keep both a dry vocal sample and a heavily-reverbed version on separate tracks and crossfade between them across the drop/break transition — isolating reverb tail as a break technique. In Lite's 8-audio floor, use a single Send → Return chain with Reverb on the Return instead.
