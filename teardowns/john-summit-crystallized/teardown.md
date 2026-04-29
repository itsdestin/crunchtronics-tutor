---
slug: john-summit-crystallized
generated_at: 2026-04-29T08:05:00Z
source: https://www.youtube.com/watch?v=vo8SyrrTtsY
duration: 3:37
tempo: 129.2 BPM (librosa) / 128.049 BPM (csv) — agree (within 4 BPM)
key: 4A — F minor (librosa) / 3B — Db major (csv) — DISAGREE
genre_inferred: tech-house
genre_page: knowledge/genres/tech-house.md
artist_page: knowledge/artists/john-summit.md
---

# John Summit — crystallized (feat. Inéz) — teardown

## TL;DR

"crystallized" runs at ~128 BPM (csv: 128.049, librosa: 129.2 — within 4 BPM, both in the tech-house pocket defined in `knowledge/genres/tech-house.md`). The key shows a librosa/csv disagreement: librosa reads 4A (F minor) while the Spotify/ReccoBeats enrichment says 3B (Db major) — these are adjacent on the Camelot wheel (F minor is the relative minor of Ab major, while Db major is 3B; the Krumhansl-Schmuckler algorithm tends to bias toward relative minor when the chroma energy is ambiguous, so the csv value of 3B is the more reliable DJ-context value). Structure follows the classic 32-bar tech-house club arrangement: sparse intro building through 40 seconds, a hard Drop A, a dip and break around 1:52, then a full Drop B from 2:45 carrying through to the fade. The single defining production move is the **vocal-formant lead**: Inéz's vocal is not just a hook — it is the melodic anchor for both drops, processed with long-tail reverb and doubled an octave up, leaving every other element subservient to the voice.

## Sections

### 0:00 — 0:40 — Intro

Sparse opening: the kick enters almost immediately but sits very low in the mix, with a light percussion loop and no bass or vocal. Energy rises slowly as elements layer in — you can see the RMS curve climbing steadily from near-zero to roughly 0.23 by 0:35. The arrangement is deliberately stripped so the drop feels like an arrival rather than a continuation.

- **0:08** — The four-on-the-floor kick enters alone, completely dry, no reverb tail — deliberately "small" to leave room for the drop to feel enormous.
- **0:25** — A rising synth texture (the "build shimmer") enters underneath, signalling the first energy ramp toward the drop. Listen for how it sits in the high-frequency band without competing with the kick.

### 0:40 — 1:52 — Drop A

The main drop. Energy spikes sharply at 0:40 (RMS from ~0.23 up to 0.50+). All elements arrive simultaneously: kick, rolling sub bass with sidechain pumping, percussion loop, and the vocal hook. The drop holds for approximately 64 bars (about 1:52 at 128 BPM) with one internal "air pocket" around 1:13 where non-kick elements thin briefly before surging back.

- **0:40** — Full drop arrival. The kick-bass sidechain pumping locks in immediately — bass ducks on every kick hit, then swells in the gaps, producing the signature "breathing" feel of the genre. See `knowledge/genres/tech-house.md` for the routing technique.
- **0:48** — Inéz's vocal lead enters. Notice it sits in a reverb wash that's noticeably longer than the bass's attack — the lead "floats" while the low end punches. The vocal is doubled an octave up (a Summit signature per `knowledge/artists/john-summit.md`).
- **1:13** — Brief "air pocket": non-kick percussion pulls back for ~4 bars, the bass filter sweeps slightly, then the full arrangement returns. This is a 16-bar micro-tension technique — keeps the drop from going stale at the 32-bar mark.
- **1:35** — Percussion layers add back a congas/shaker loop overtop the existing groove, thickening the drop density in the back half.

### 1:52 — 2:45 — Break

Energy drops sharply at 1:52 (RMS from ~0.52 to ~0.18). Kick is stripped out. What remains: the vocal reverb tail, a pad or atmospheric texture, and a very sparse hat pattern. The chroma panel shows harmonic content staying consistent with the 3B/4A tonal centre throughout. The break lasts approximately 32–48 bars (53 seconds at 128 BPM ≈ ~56 bars), long by pop standards but normal for a DJ-oriented club track.

- **1:52** — Kick drops out simultaneously with the bass — the room gets very large. This is the "void" technique: the sudden absence of low end creates perceived silence even though hi-freq elements are still playing.
- **2:20** — A riser/build element enters, likely a filtered noise sweep rising in pitch. Energy begins climbing from ~0.16 back toward 0.44 by 2:45. This is the "tension re-load" that sets up Drop B.
- **2:42** — A short drum fill or snare roll cues the listener that the drop is 2-4 bars away.

### 2:45 — 3:32 — Drop B

The second drop, slightly denser than Drop A. Energy at 2:45 returns to Drop A levels (~0.41–0.45 RMS) and holds there. The arrangement is nearly identical to Drop A but may carry additional percussion or a subtle variation on the vocal processing. At this length (~47 seconds = ~50 bars at 128 BPM) it runs slightly shorter than Drop A — appropriate for a track intended to close a DJ set transition rather than be looped indefinitely.

- **2:45** — Drop B arrival. Kick, bass, and vocal all re-enter simultaneously with no build-up — the riser handled all the tension, so the drop lands as a clean cut-in.
- **3:05** — The vocal hook feels slightly "wetter" here (longer reverb pre-delay audible on the "crys-" syllable onset), suggesting a subtle automation move on the reverb return level.
- **3:20** — Elements start dropping out one by one — percussion loop first, then bass filter closing — setting up the outro.

### 3:32 — 3:37 — Outro

Five-second hard fade. RMS drops from ~0.38 to near-zero. At 3:37 total this is the streaming-edit version of the track, not the DJ-extended version (which would have a 32-bar outro for mixing). The outro here is effectively just a tail cut — no new arrangement content.

- **3:32** — Abrupt volume automation cut (or a very short fade) — consistent with a streaming master trim that removes the DJ-length outro.

## Production techniques worth copying

- **Sidechain kick-bass pumping:** the defining move of the genre. Every time the kick hits, a Compressor on the bass track (with sidechain input set to the kick) pulls the bass down 3–6 dB, then lets it swell back up. The result is the "breathing" low end that makes the track move. See `knowledge/genres/tech-house.md` — the "Read this yourself" section covers the Ableton routing step by step.
- **Vocal-as-lead-hook with long-tail reverb:** Inéz's vocal sits in a reverb tail roughly 3–4× longer than the groove's beat gap, which makes it "float" above the punchy low end rather than competing with it. See `knowledge/ableton/the-mixer.md` — use the send-and-return pattern (Return A = Reverb) so the vocal reverb is on a separate return track you can dial up and down independently of the dry vocal.
- **Sparse drop arrangement (load-bearing six-element rule):** at any moment in the drop, count the active elements — kick, bass, hat, clap, percussion loop, vocal hook. That's six. Nothing else. This "less = more" discipline is described in `knowledge/genres/tech-house.md` under "Read this yourself."

## Listen-for next time

- **The kick-bass gap:** pause the track at 0:44 and listen to exactly where the bass note sits in time relative to the kick. The bass plays *in the gap* between kicks, not on the kick itself. That interlock is why the low end sounds tight instead of muddy.
- **The 1:13 air pocket:** listen to how the track "breathes" here without fully breaking down. The kick never leaves — only the other elements thin. Notice how much tension one 4-bar percussion pull-back creates compared to removing the kick entirely.
