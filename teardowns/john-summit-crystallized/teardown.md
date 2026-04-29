---
slug: john-summit-crystallized
generated_at: 2026-04-29T20:45:00Z
source: local (source.wav)
duration: 3:37
tempo: 128.049 BPM (csv) — 129.199 BPM (librosa). agree_within_4bpm: true.
key: 3B — Db major (csv) — librosa reads 4A — F minor. agree: false.
genre_inferred: tech-house
genre_page: knowledge/genres/tech-house.md
artist_page: knowledge/artists/john-summit.md
sidechain: 4.49 dB ducking on 65.3% of kicks (detected) — depth_db_p90: 8.54 dB
---

# crystallized (feat. Inéz) — teardown

## TL;DR

BPM 128.049 (csv); librosa reads 129.2 — agree within 4 BPM, csv is authoritative. Key 3B / Db major (csv); librosa reads 4A / F minor — a classic Krumhansl-Schmuckler bias toward the relative minor (F minor and Db major are adjacent on the Camelot wheel, 4A vs 3B). Valence 0.292 (csv): darker mood. Energy 0.857 (csv): high-energy. Danceability 0.529 (csv). Instrumentalness 4.85e-05 (csv): vocals or melodic samples are clearly present in the mix; per edm.com coverage ([edm.com](https://edm.com/music-releases/john-summit-inez-crystallized/), accessed 2026-04-29), Inéz is the credited featured vocalist. Sidechain detected: 4.49 dB average ducking on 65.3% of kick onsets; p90 depth 8.54 dB (per analysis.json). The HPSS panel shows a clear four-section structure: a ~42-second intro where percussive RMS climbs from 0.016 to 0.084 while sub-band RMS holds below 4, followed by Drop A (sub RMS jumping 14× to ~53–67), a break where sub onsets fall to 0/bar and percussive HPSS drops to 0.032–0.087, then Drop B restoring full-density levels.

## Sections

### 0:00 — 0:42 — Intro

Sub-band and bass-band per-panel values remain very low across bars 0–22: sub-band RMS mean per bar ranges 0.6–3.7 (vs. 40–65 in the drops), bass-band 12–22. Onset density confirms: sub onsets are 0/bar through bar 22, bass onsets 0–4/bar. Harmonic HPSS component climbs from ~0.078 at bar 0 to ~0.154 at bar 16; percussive HPSS rises from ~0.016 to ~0.081 over the same span — harmonic content is dominant throughout this section. Spectral centroid rises from ~836 Hz at bar 0 to ~2,695 Hz at bar 16, then peaks at ~3,271 Hz at bar 22 (Panel 4), indicating progressively brighter mid-high content building through the intro phase. Air-band RMS is near zero through bar 14 and begins a gradual increase from bar 16 onward.

- 0:08 (bar 3) — bass-band RMS first reaches 13.6; low-mids RMS at 6.8. Sub-band remains under 1.0. Per Panel 2 (per-band RMS).
- 0:29 (bar 16) — spectral centroid crosses 2,695 Hz. Percussive HPSS component reaches 0.081 — first significant percussive reading in the intro. Per Panels 3 and 4.
- 0:39 (bar 21) — onset density: air-band onsets reach 10/bar, highs 5/bar — highest air-band onset count before the drop. Sub still 0. Per Panel 5 (onset density heatmap).

### 0:42 — 1:42 — Drop A

Sub-band RMS jumps abruptly at bar 24 (~0:45): from ~3.7 (bar 22, last intro bar) to 53.2 — a 14× increase. Bass-band similarly climbs from ~18.8 to 67.4. Total RMS crosses 0.400. Percussive HPSS component holds between 0.106 and 0.145 across the drop; harmonic RMS simultaneously rises to 0.280–0.345, keeping the harmonic/percussive ratio roughly 2.1:1 (Panel 3). Onset density stabilizes: sub onsets hold at 7–13/bar, bass onsets 5–9/bar through bars 23–53. Spectral centroid settles at approximately 2,400–2,730 Hz — somewhat lower than the late-intro peak of 3,271 Hz, consistent with sub and bass energy shifting the spectral center of mass downward (Panel 4). Sidechain activity is most pronounced here: with sub and bass-band fully engaged and four-on-the-floor kick activity (genre prior — tech-house.md), the 4.49 dB mean ducking and 8.54 dB p90 depth (analysis.json) are driven primarily in this section.

- 0:42 (bar 23) — sub-band onset count: 4/bar; bass-band onsets: 7/bar. First bar where both sub and bass onset density exceed 3. Per Panel 5.
- 0:45 (bar 24) — sub-band RMS: 53.2; bass-band RMS: 67.4. Sharpest single-bar sub climb across the full track. Per Panel 2.
- 1:15 (bar 40) — highest total per-bar onset density in Drop A: 51 onsets/bar across all bands (sub: 13, bass: 8, low-mids: 9, highs: 10, air: 11). Per Panel 5.
- 1:26 (bar 46) — sub-band RMS: 56.6 (near-peak for Drop A). Total RMS: 0.414 — highest total RMS mean bar in Drop A. Per Panels 1 and 2.

### 1:42 — 2:48 — Break

Sub-band and bass-band RMS collapse starting at bar 54 (~1:42): sub drops from 31.7 (bar 52) to 18.5 (bar 54) to 5.8 (bar 56), then holds near-zero to oscillating-low through bar 89. Bass-band follows: 48.9 (bar 52) → 31.8 (bar 54) → 20.3 (bar 56) → ~17–26 for the break mid-section. Sub onset density falls from 9/bar (bar 53) to 0/bar (bars 56–59) and stays at 0–3 through bar 90. Percussive HPSS drops sharply: bars 60–62 show values of 0.032–0.063, the lowest sustained percussive readings outside the very beginning of the track (Panel 3 — the magenta curve visibly flattens in the break period). Harmonic HPSS component holds at 0.167–0.238 across bars 60–90 — mid-register harmonic content sustains while percussive content is reduced. Low-mids RMS remains elevated at 11–14 throughout the break — mid-range spectral activity continues even as the low end is stripped. At bars 90–92, sub and percussive RMS show brief spikes as the track prepares the return.

- 1:42 (bar 54) — sub-band onset density falls to 5/bar (from 9 the prior bar). Total RMS drops from 0.330 to 0.255. Per Panels 2 and 5.
- 1:53 (bar 57) — sub onset density: 0/bar. Percussive HPSS: 0.087. Harmonic HPSS: 0.162. Harmonic/percussive ratio widens to ~1.9:1. Per Panel 3.
- 2:44 (bar 90) — total RMS at its lowest sustained reading in the break: 0.099. Sub-band RMS 11.5, bass-band only 3.3 — most stripped-back moment in the track. Per Panel 2.
- 2:45 (bar 91) — onset density returns: sub 3/bar, low-mids 5/bar, highs 3/bar, air 3/bar. Percussive HPSS rises from ~0.005 (bar 90) to 0.034. Pre-drop energy accumulation begins. Per Panels 3 and 5.

### 2:48 — 3:32 — Drop B

Sub-band and bass-band RMS return to drop-level values at bar 93 (~2:48): sub 60.1, bass 56.3, total RMS 0.371 — comparable to Drop A peak levels. Onset density immediately restores: sub 10/bar, bass 8/bar, low-mids 11/bar at bar 93. Across bars 93–114, sub onsets average 9–13/bar, total onsets 35–47/bar. Harmonic HPSS settles at 0.289–0.315 and percussive HPSS holds 0.119–0.138 — the harmonic/percussive ratio in Drop B (~2.3:1) is slightly higher than Drop A's ~2.1:1, indicating a marginally more harmonic-heavy balance (Panel 3). Spectral centroid holds at 2,437–2,739 Hz — similar brightness range to Drop A. Low-mids RMS tracks 9–11 — slightly lower than Drop A's 10–13. At bar 114 (~3:30) total RMS begins a sudden collapse; bar 115 shows sub = 0, bass = 0, total RMS = 0.018. Full stop at ~3:32.

- 2:48 (bar 93) — sub-band RMS: 60.1. Onset density: 47 total/bar. Sharpest single-bar onset re-entry in the track outside the original drop. Per Panels 2 and 5.
- 3:07 (bar 101) — highest onset count in Drop B: 47 total/bar (sub: 13, low-mids: 10, highs: 8, air: 9). Per Panel 5.
- 3:30 (bar 114) — final full-density bar: sub 40.5, bass 54.3, onset total 36. Per Panel 2.
- 3:32 (bar 115) — total RMS: 0.018; sub and bass onsets both 0. Full stop. Per Panels 1 and 2.

## Production techniques worth copying

- **Sidechain compression.** Measured 4.49 dB average bass-band ducking on 65.3% of kick onsets; p90 depth 8.54 dB (per analysis.json). Reference: `knowledge/genres/tech-house.md` sidechain section for the Ableton Compressor routing and typical 3–6 dB target range.

- **Sub/bass withheld for 42 seconds.** The entire intro (0:00–0:42) maintains sub-band RMS below 4 and sub onset density of 0/bar. The drop's sub entry at bar 23 delivers a 14× sub-band RMS increase. The contrast is unusually large and is visible in Panel 2 as a near-flat sub trace that jumps to dominant. Withholding is the technique; the drop is the reward.

- **Percussive/harmonic ratio control across sections.** Panel 3 (HPSS) shows three clearly distinct percussive-RMS regimes: intro (rising 0.016→0.084), break (dropping to 0.032–0.087), drops (sustaining 0.106–0.151). Managing the HPSS balance — not just overall RMS — is what creates structural contrast without relying on element-by-element arrangement notation.

- **Spectral brightening through the intro.** Centroid climbs from ~836 Hz at bar 0 to ~3,271 Hz at bar 22 (Panel 4) — roughly a 4× increase over 42 seconds. On drop entry, centroid drops back to ~2,500 Hz as sub energy shifts the spectral center of mass. Centroid automation as a structural cue.

- **Sustained mid-range through the break.** Low-mids RMS (250–2k Hz) holds at 11–14 through the break even as sub-band collapses. Per Panel 2: the break does not go quiet — it shifts the spectral weight upward while sub content is removed.

## Listen-for next time

- The sub-band onset density transition at ~0:42 (bar 23): sub onsets go from 0 to 4/bar in one bar. Listen for what triggers that change in the low end.
- The p90 sidechain depth of 8.54 dB: there will be individual kicks where the pumping is nearly twice the average. Listen for those heavy downbeat moments.
- Lyric: "I loved you once, fire to ice / All of my teardrops, they all crystallized" (per [lyricsondemand.com](https://lyricsondemand.com/john_summit/crystallized), accessed 2026-04-29). The harmonic HPSS in the break (0.167–0.238) with low-mids sustained — listen for how the mid-range content carries during the break while the low end is absent.
- The centroid drop from ~3,093 Hz (bar 20, late intro) to ~2,664 Hz (bar 24, early drop). Brightness actually decreases slightly when sub arrives. Listen for that tonal-weight shift.

## Web-finding citations

- Per release coverage ([edm.com](https://edm.com/music-releases/john-summit-inez-crystallized/), accessed 2026-04-29): Inéz is the credited featured vocalist; reunion collaboration following their earlier "light years."
- Per lyrics site ([lyricsondemand.com](https://lyricsondemand.com/john_summit/crystallized), accessed 2026-04-29): confirmed lyric "I loved you once, fire to ice / All of my teardrops, they all crystallized."
- Per release announcement ([preludepress.com](https://preludepress.com/news/2025/09/11/john-summit-crystallized/), accessed 2026-04-29): confirmed release date September 11, 2025, on Experts Only label.
- Per Beatport listing ([beatport.com](https://www.beatport.com/track/crystallized-feat-inez/22095332), accessed 2026-04-29): track released on Experts Only label; house/tech-house genre classification consistent with csv and artist profile.
