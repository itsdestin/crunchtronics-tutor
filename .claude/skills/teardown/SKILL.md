---
name: teardown
description: Tear down a track Destin loves — yt-dlp download, librosa analysis (per-band RMS, HPSS, centroid, onset density, sidechain), web-findings batch, then author teardown.md (narrative) and recipe.md (Ableton Lite-floor build steps) under a strict four-tier trust hierarchy. Use when Destin says "teardown this track", invokes /teardown, or pastes a YouTube URL asking how it's built.
---

# Teardown skill (v1.1)

This skill drives the teardown pipeline (Subsystem #8). Full spec at
`docs/superpowers/specs/subsystems/08-teardown-pipeline.md` (v1.1 amendment §2.4–§2.6).

## When to invoke

- `/teardown <input>` (slash form)
- "teardown this track: <url>" / "teardown the John Summit one" (natural language)
- bare `/teardown` — ask Destin what track

## Trust hierarchy for narrative authoring (the rule that prevents hallucination)

Every claim in `teardown.md` and `recipe.md` MUST be traceable to one of four tiers:

1. **`taste/tracks.csv` (ReccoBeats)** — authoritative for track-level facts (BPM, key, energy, danceability, valence, acousticness, instrumentalness, liveness, loudness, speechiness). When the librosa estimate disagrees, csv wins; the disagreement is named explicitly.
2. **Measured spectral features** (analysis.json + scrub-strip.png) — authoritative for time-localized observations. Describe what curves/panels show. Don't infer the cause.
3. **Web findings** (`web_findings.md`) — *supporting only*. Cite with source URL + access date. Never override tier 1 or 2.
4. **Genre/artist priors** (`knowledge/genres/`, `knowledge/artists/`) — background context. Genre vocabulary may be used for structural labels ("kick-out break", "drop A → break → drop B"); priors must NOT introduce specific claims about this track.

**Allowed examples:**
- *"BPM 128 (csv) — librosa reads 129; csv is authoritative."*
- *"Sub-band RMS climbs from 0.04 to 0.42 at 0:40."*
- *"Sidechain detected: 4 dB average ducking on 87% of kick onsets (per analysis.json)."*
- *"Percussive HPSS component drops near-zero from 1:52 to 2:45 while harmonic component holds — kick-out break."*
- *"Per Genius credits ([url], accessed 2026-04-29), Inéz performs lead vocal."*

**Forbidden examples (these are what failed in v1.0):**
- *"The bass enters at 0:40."* — cause-inference; rewrite as the measurement
- *"Inéz's vocal hook arrives at 0:48."* — instrument-level claim without measurement support
- *"The lead is doubled an octave up."* — un-measurable
- *"Reverb pre-delay automation on the 'crys-' syllable."* — un-measurable
- *"Drum fill at 2:42."* — cause-inference; describe percussive RMS spike
- *"The kick uses a Roland TR-909."* — un-measurable
- *"Vocal-formant-processed lead."* — un-measurable

## The flow (eight steps)

### 1. Normalize the input

- **YouTube URL** (`youtube.com` / `youtu.be`) → use directly.
- **Other URL** → pass to yt-dlp.
- **Local file path** that exists → use `--local` mode.
- **Spotify track ID** (Base-62, 22 chars) → look up `taste/tracks.csv` to get artist + title; fall through to free-text path.
- **Free text** → fuzzy-match against `taste/tracks.csv`; on miss, treat as YouTube search query.

### 2. Resolve the URL + ask Destin to confirm

When the input doesn't supply a URL, run yt-dlp:

```bash
python -m yt_dlp --skip-download --print "%(title)s|%(duration_string)s|%(channel)s" \
       "ytsearch1:<artist> <title> official audio"
```

Show resolved title + duration + channel. Ask:

> Found: **<title>** [<duration>, <channel>]. Use this? (y / paste different URL / abort)

**Do not download until confirmed.**

### 3. Derive a slug + check idempotency

Auto-derive: `<artist-kebab>-<title-kebab>`. If `teardowns/<slug>/` exists non-empty, ask:

> Existing teardown at `teardowns/<slug>/`. Overwrite, append `-v2`, or abort?

Three options: overwrite (skill passes `--force`); `-v2` (compute next free `<slug>-vN`); abort (clean exit).

### 4. Run the analysis CLI

```bash
python scripts/teardown.py \
    --slug <slug> \
    (--url <url> | --local <path>) \
    [--csv-context <spotify-id>] \
    [--force]
```

Pass `--csv-context` when you have a confirmed `tracks.csv` row.

Exit codes:

| Code | Meaning | Your response |
|---|---|---|
| 0 | OK | proceed to step 5 |
| 2 | yt-dlp download failed | tell Destin to drop the file at `teardowns/<slug>/source.wav` and retry with `--local` |
| 3 | audio decode / suspiciously short | likely DRM or partial download; suggest a different URL |
| 5 | scrub-strip render failed | rare; surface the error |
| 6 | bad env (ffmpeg missing or bad --local path) | tell Destin to `winget install Gyan.FFmpeg` |

### 5. Run the web-findings batch (NEW in v1.1)

After the CLI exits 0, derive `(artist, title)` from `analysis.json` (prefer `csv_context.artist` + `csv_context.title`; fall back to parsing `source.title`).

Run the default search batch using the `WebSearch` tool:

| Query | Intent |
|---|---|
| `<artist> <title> stems` | stems / multitracks |
| `<artist> <title> acapella` | vocal isolations |
| `<artist> <title> breakdown` | production breakdown videos / tutorials |
| `<artist> <title> splice` | dedicated sample pack for this track |
| `<artist> <title>` | context, interviews, Genius credits |

For each search, capture the top 3-5 relevant results: title, URL, source domain, and a one-paragraph relevance note authored from the result snippet. Discard obviously off-topic results (different artist, unrelated content).

### 6. Write `web_findings.md`

Use the `Write` tool to create `teardowns/<slug>/web_findings.md`:

```markdown
---
slug: <slug>
generated_at: <iso UTC now>
artist: <artist>
title: <title>
stems_found: <true|false — true only when at least one search returns a verified stems URL>
acapella_found: <true|false>
breakdown_found: <true|false>
---

# Web findings — *<title>*

> Tier 3 supporting evidence per spec §2.5. Cite with source URL + access date.
> Never override `taste/tracks.csv` (tier 1) or measured spectral features
> (tier 2). Discrepancies must be flagged in `teardown.md`.

## Stems / multitracks
- **<result title>** — <source domain> — `<URL>` — accessed <YYYY-MM-DD>
  <one-paragraph relevance note from snippet>
- ...

(or *No verified stems located in this search batch.* if zero hits)

## Acapella / vocal isolation
...

## Production breakdowns
...

## Splice / dedicated sample packs
...

## General context
...
```

Failure handling: if a search returns 0 results, write `*WebSearch returned 0 results for "<query>"*` under that section. If a search times out, write `*WebSearch timed out — query: "<query>"*`. Don't block the teardown.

### 7. Read all artifacts + relevant knowledge pages

Read in this order:
1. `teardowns/<slug>/analysis.json`
2. `teardowns/<slug>/scrub-strip.png` (or per-panel fallbacks)
3. `teardowns/<slug>/web_findings.md`
4. `taste/tracks.csv` row (already in `analysis.json.csv_context` if present)
5. `knowledge/genres/<inferred-genre>.md` if it exists. Inference: prefer `csv_context.genre` when populated; otherwise infer from artist + tempo (tech house ≈ 124-130, bass house ≈ 128-138, melodic dubstep ≈ 140-150, dubstep / riddim ≈ 140-150). If no genre page, **note the gap explicitly** in the teardown TL;DR.
6. `knowledge/artists/<artist-slug>.md` if it exists.

### 8. Author teardown.md and recipe.md

Write both files (use Write twice). Templates and authoring rules below.

#### `teardown.md` template

```markdown
---
slug: <slug>
generated_at: <iso UTC now>
source: <analysis.json source.url>
duration: <mm:ss from analysis.duration_s>
tempo: <bpm_csv> BPM (csv) — <bpm_librosa> BPM (librosa). agree_within_4bpm: <true|false>.
key: <camelot_csv> — <standard from csv> (csv) — librosa reads <camelot_librosa> — <standard_librosa>. agree: <true|false>.
genre_inferred: <slug-or-"unknown">
genre_page: knowledge/genres/<slug>.md (if exists)
artist_page: knowledge/artists/<slug>.md (if exists)
sidechain: <"<X> dB ducking on <Y>% of kicks (detected)" | "no sidechain detected (<X> dB on <Y>% — below threshold)">
---

# <Track title> — teardown

## TL;DR

(2-4 sentences. Lead with csv-grounded track-level facts: BPM, key, energy
band, instrumentalness, mood markers from csv. Then ONE structural note
from the scrub strip's per-band RMS or HPSS panels. If tempo or key
disagrees with csv, name it explicitly. If sidechain is detected, name
the measured depth + consistency. Do not name instruments. Do not infer
the cause of energy.)

## Sections

### 0:00 — 0:32 — Intro

(2-3 sentences describing what the scrub strip's per-band RMS / HPSS curves
show across this section: which bands are quiet, which carry the energy,
whether harmonic or percussive content dominates, brightness from centroid.
Use phrases like "sub-band RMS climbs" not "the bass enters". Name section
boundaries from the energy curve; the structural label ("intro") is a tier 4
genre prior.)

- 0:08 — sub-band RMS first crosses 0.05; bass-band joins at 0.04. Per scrub-strip Panel 2.
- 0:16 — percussive HPSS component crosses 0.10. Per Panel 3.
- ...

(continue per section identified from the scrub strip)

## Production techniques worth copying

- **Sidechain ducking.** Measured 4 dB ducking on 87% of kicks (per analysis.json.sidechain). Reference: `knowledge/genres/<inferred>.md`'s sidechain section.
- ...

## Listen-for next time

- <thing 1, grounded in measurement or web finding>
- <thing 2, ditto>

## Web-finding citations (when used)

- Per Genius credits ([genius.com](URL), accessed YYYY-MM-DD), <fact>.
- Per breakdown video ([youtube.com](URL), accessed YYYY-MM-DD), <fact>.
```

**Authoring rules for teardown.md:**

- Every bar-level callout cites a specific timestamp (mm:ss) AND the panel + measurement that supports it.
- TL;DR leads with csv facts before any time-localized claim.
- When `tempo.agree_within_4bpm` is `false` OR keys disagree, the disagreement is explained.
- Web findings cited inline `[<source domain>](<URL>) (accessed YYYY-MM-DD)`.
- **Forbidden phrasings (per §2.5):** cause-inference for energy ("the bass enters"), specific instrument identifications without measurement support ("vocal lead", "synth pad"), un-measurable production-technique claims (octave doubling, specific reverb settings, vocal-formant processing, drum fills).

#### `recipe.md` — TWO MODES

**Decide mode from `web_findings.md`:**

- If `stems_found: true` AND a verified stems URL exists → **stems-study mode**.
- Otherwise → **genre-rebuild mode** (default).

##### genre-rebuild mode (default)

```markdown
---
slug: <slug>
recipe_for: <track title>
target: Ableton Live 12 Lite (8 audio + 8 MIDI tracks, Simpler-only, 2 sends)
mode: genre-rebuild
generated_at: <iso UTC now>
---

# Recipe — build something inspired by *<Track title>*

> Builds a track that hits the csv profile (BPM <X>, key <camelot>,
> energy <E>, danceability <D>) and follows the section structure
> measured in teardown.md, using the genre conventions from
> `knowledge/genres/<inferred>.md`. Not a transcription; a guided
> rebuild that touches the same primitives.

## Project setup
1. Set tempo to <csv_bpm> BPM (preferring csv over librosa).
2. Set project key to <csv_camelot> (<csv_standard>) — write a note in your master clip.
3. <other setup steps>

## Drum foundation (MIDI 1 — Drum Rack)
4. ...

## Bass + sidechain (MIDI 2 — Operator + audio Compressor sidechain)
5. ... (when sidechain.detected is true: aim for the measured depth, e.g.,
   "set Compressor's gain reduction to ~4 dB on every kick — match the
   measured 4 dB ducking on 87% of kicks from the original")

## Melodic layer (MIDI 3 — Operator preset)
6. ...

## Texture + perc (MIDI 4 / Audio 1)
7. ...

## Arrangement
8. Build the section structure from teardown.md: intro / drop A / break / drop B / outro.

## Artist-resource enhancement
*(Section omitted with one-line note when knowledge/artists/<slug>.md does not exist:
 "No artist page yet — recipe leans on genre conventions only.")*

- Splice "Sounds of <artist>" pack: <link from artist page>
- ...

## Intro+ notes
- **Intro+ note (step <N>):** with a 9th MIDI track available, ...
```

##### stems-study mode (when verified stems are found)

```markdown
---
slug: <slug>
recipe_for: <track title>
target: Ableton Live 12 Lite (8 audio + 8 MIDI tracks, Simpler-only, 2 sends)
mode: stems-study
stems_url: <URL from web_findings.md>
generated_at: <iso UTC now>
---

# Recipe — study *<Track title>* via its stems

> Stems located: <URL> (accessed <YYYY-MM-DD>).
> Mode: stems-study. Steps focus on dissecting the actual stems and
> recording your observations, not programming new MIDI from scratch.

## Project setup
1. Set tempo to <csv_bpm> BPM. Set project key to <csv_camelot> (<csv_standard>).
2. Download the stems pack from <URL>. Drop the drum stem into Audio 1, bass stem into Audio 2, vocal stem into Audio 3, melodic stems into Audio 4-5 as you go.

## Drum stem study (Audio 1)
3. Solo the drum stem. Loop the drop section identified in teardown.md (<start>-<end>). Listen for ~5 cycles.
4. In a journal note (right-click the clip → Edit Info Text), record what you hear. Reference `knowledge/genres/<inferred>.md` for what to listen for.
5. ...

## Bass stem study (Audio 2)
N. Solo bass stem alongside the drum stem. ...

## Vocal stem study (Audio 3)
N. ...

## Melodic stems study (Audio 4-5)
N. ...

## Apply learnings
N. With those notes, sketch a new project that hits the same csv profile with your own samples. Keep the original stems-study project alongside for reference.

## Intro+ notes
- **Intro+ note:** with more audio tracks available, you could keep additional stems loaded for cross-reference instead of swapping.
```

**Authoring rules for recipe.md (both modes):**

- Recipe must fit the Lite floor (≤ 8 audio + ≤ 8 MIDI, Simpler-only, ≤ 2 sends).
- AT LEAST ONE `**Intro+ note:**` callout per recipe.
- Artist-resource enhancement section reads from `knowledge/artists/<slug>.md` ONLY. Never invent Splice packs.
- Every step doable by Destin without external research.
- For genre-rebuild mode: target the csv profile (BPM, key, energy band) using genre conventions. Don't claim to "rebuild this track."
- For stems-study mode: stems URL must be the one in `web_findings.md`. Don't fabricate a URL.

### Wrap up

End with one line:

> Done. `teardowns/<slug>/` has source.wav, analysis.json, scrub-strip.png, web_findings.md, teardown.md, recipe.md. Want me to walk through the recipe with you?

If Destin is in Ableton, prefer companion mode (`knowledge/ableton/companion-mode.md`) when he asks how to execute a step.
