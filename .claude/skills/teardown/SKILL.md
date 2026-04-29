---
name: teardown
description: Tear down a track Destin loves — yt-dlp download, librosa analysis, scrub-strip render, then author teardown.md (narrative) and recipe.md (Ableton Lite-floor build steps). Use when Destin says "teardown this track", invokes /teardown, or pastes a YouTube URL asking how it's built.
---

# Teardown skill

This skill drives the teardown pipeline (Subsystem #8). Full spec at
`docs/superpowers/specs/subsystems/08-teardown-pipeline.md`.

## When to invoke

- `/teardown <input>` (slash form)
- "teardown this track: <url>" / "teardown the John Summit one" (natural language)
- bare `/teardown` — ask Destin what track

## The flow (seven steps)

### 1. Normalize the input

Classify what Destin gave you:

- **YouTube URL** (`youtube.com` / `youtu.be`) → use directly.
- **Other URL** → pass to yt-dlp, hope it's supported.
- **Local file path** that exists → use `--local` mode.
- **Spotify track ID** (Base-62, 22 chars) → look up `taste/tracks.csv`
  to get artist + title, then fall through to free-text path.
- **Free text** (e.g., "the John Summit one") → fuzzy-match against
  `taste/tracks.csv` (artist + title columns); on miss, treat as a
  YouTube search query.

### 2. Resolve the URL + ask Destin to confirm

When the input doesn't already supply a URL, run:

```bash
yt-dlp --skip-download --print "%(title)s|%(duration_string)s|%(channel)s" \
       "ytsearch1:<artist> <title> official audio"
```

Show Destin the resolved title + duration + channel and ask:

> Found: **<resolved title>** [<duration>, <channel>]. Use this? (y / paste different URL / abort)

Wait for Destin's response. **Do not download until confirmed.** First-hit
errors (live cuts, sped-up edits, nightcore versions) are real.

### 3. Derive a slug + check idempotency

Auto-derive: `<artist-kebab>-<title-kebab>` from the resolved title.

If `teardowns/<slug>/` already exists and is non-empty, ask:

> Existing teardown at `teardowns/<slug>/`. Overwrite, append `-v2`, or abort?

Three options:
1. **Overwrite** → invoke CLI with `--force`.
2. **`-v2`** → compute next free `<slug>-vN`, invoke without `--force`.
3. **Abort** → clean exit, no files touched.

Destin can also override the slug at this step if the auto-derived one
is awkward.

### 4. Run the analysis CLI

```bash
python scripts/teardown.py \
    --slug <slug> \
    (--url <url> | --local <path>) \
    [--csv-context <spotify-id>] \
    [--force]
```

Pass `--csv-context` only when you have a confirmed `tracks.csv` row
(spotify_id resolved through fuzzy match or direct ID input).

The CLI prints `[1/4] downloading…  [2/4] loading audio…` etc. and exits
with one of:

| Code | Meaning | Your response |
|---|---|---|
| 0 | OK | proceed to step 5 |
| 2 | yt-dlp download failed | tell Destin to drop the file at `teardowns/<slug>/source.wav` and retry with `--local` |
| 3 | audio decode / suspiciously short | likely DRM or partial download; suggest a different URL |
| 5 | scrub-strip render failed (all panels) | rare; surface the error |
| 6 | bad env (ffmpeg missing) | tell Destin to `winget install Gyan.FFmpeg` |

### 5. Read the artifacts + relevant knowledge pages

Read in this order:
1. `teardowns/<slug>/analysis.json`
2. `teardowns/<slug>/scrub-strip.png` (or the per-panel fallbacks)
3. `taste/tracks.csv` row matching `analysis.json.csv_context.spotify_id` if present
4. `knowledge/genres/<inferred-genre>.md` if it exists. Inference:
   - prefer `csv_context.genre` when populated
   - otherwise infer from artist + tempo: tech house ≈ 124-130, bass house ≈ 128-138,
     melodic dubstep ≈ 140-150, dubstep / riddim ≈ 140-150, trap ≈ 138-144
   - if no genre page exists, **note the gap explicitly** in the teardown TL;DR
5. `knowledge/artists/<artist-slug>.md` if it exists.

### 6. Author teardown.md and recipe.md

Write both files in a single message (use Write tool twice). Templates:

#### `teardown.md`

```markdown
---
slug: <slug>
generated_at: <iso UTC now>
source: <analysis.json source.url>
duration: <mm:ss from analysis.duration_s>
tempo: <bpm_librosa> BPM (librosa) / <bpm_csv> BPM (csv) — agree | DISAGREE
key: <camelot_librosa> — <standard_librosa> (librosa) / <camelot_csv> (csv) — agree | DISAGREE
genre_inferred: <slug-or-"unknown">
genre_page: knowledge/genres/<slug>.md (if exists)
artist_page: knowledge/artists/<slug>.md (if exists)
---

# <Track title> — teardown

## TL;DR
<2-3 sentences: BPM, key, structure, ONE production move that defines this track.
 If tempo or key disagrees with tracks.csv, explain (likely half/double-time read).>

## Sections
### 0:00 — 0:32 — Intro
<2-3 sentence section overview from scrub strip energy curve + genre prior>
- 0:08 — <bar-level callout: a specific production gesture worth replicating>
- 0:16 — <another callout>

### 0:32 — 1:04 — Drop A
<overview>
- ...

(continue for each section identified from the energy curve)

## Production techniques worth copying
- <technique 1, link to knowledge/genres/<slug>.md or knowledge/theory/<slug>.md>
- <technique 2>
- <technique 3>

## Listen-for next time
- <thing 1>
- <thing 2>
```

**Authoring rules:**
- Every bar-level callout cites a specific timestamp `mm:ss`.
- Production technique references LINK INTO `knowledge/`. Never invent technique
  names; only use what's in the knowledge pages.
- If `tempo.agree_within_4bpm` is `false`, TL;DR explicitly explains the
  disagreement (likely half or double-time read).
- If `genre_page` is missing, TL;DR notes "no genre cheat sheet for <X>;
  writing from librosa features + general EDM intuition" — gap visible.

#### `recipe.md`

```markdown
---
slug: <slug>
recipe_for: <track title>
target: Ableton Live 12 Lite (8 audio + 8 MIDI tracks, Simpler-only, 2 sends)
generated_at: <iso UTC now>
---

# Recipe — build something inspired by *<Track title>*

## Project setup
1. Set tempo to <bpm_librosa or bpm_csv preferring csv when available>.
2. Set project key to <camelot> (<standard>) — write a note in your master clip.
3. <other setup steps>

## Drum foundation (MIDI 1 — Drum Rack)
4. ...

## Bass + sidechain (MIDI 2 — Operator + audio compressor sidechain)
5. ...

## Melodic layer (MIDI 3 — Operator preset)
6. ...

## Texture + perc (MIDI 4 / Audio 1)
7. ...

## Arrangement
8. Build the section structure from teardown.md:
   intro / drop A / break / drop B / outro.

## Artist-resource enhancement
*(Section omitted with one-line note when knowledge/artists/<slug>.md does not
 exist: "No artist page yet — recipe leans on genre conventions only.")*

- Splice "Sounds of <artist>" pack: <link from artist page>
- Preset packs / signature techniques: <from artist page>
- Specific samples to chase: kick character "<X>", lead character "<Y>"

## Intro+ notes
- **Intro+ note (step <N>):** with a 9th MIDI track available, ...
- **Intro+ note (step <M>):** with 4 sends instead of 2, ...
```

**Authoring rules:**
- Recipe MUST fit the Lite floor (≤ 8 audio + ≤ 8 MIDI, Simpler-only, ≤ 2 sends).
  Track-budget header for each section names which device on which track.
- AT LEAST ONE `**Intro+ note:**` callout per recipe. If the recipe doesn't
  bump against any Lite limit, the Intro+ note still calls out an
  upgrade-path enhancement (e.g., "with Standard's Sampler instead of
  Simpler, you could …").
- "Artist-resource enhancement" section reads from `knowledge/artists/<slug>.md`
  ONLY. Never invent Splice packs, preset packs, or interview links. Mirrors
  the Subsystem #7 / CLAUDE.md rule.
- Every step must be doable by Destin without external research. If a step
  needs a knowledge page, link it inline.

### 7. Wrap up

After both files are written, end with one line:

> Done. `teardowns/<slug>/` has source.wav, analysis.json, scrub-strip.png,
> teardown.md, recipe.md. Want me to walk through the recipe with you?

If Destin is in Ableton, prefer companion mode (`knowledge/ableton/companion-mode.md`)
when he asks how to execute a recipe step.
