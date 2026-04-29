# Subsystem #8 — Teardown Pipeline

- **Date:** 2026-04-28
- **Status:** Approved (draft, pending implementation plan)
- **Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md`
- **Master-spec sections referenced:** §3.2 (Lite/Intro shared floor — recipes target Lite + Intro+ callouts), §3.5 (master-first; stems/multitracks not obtainable), §5.1 #8 (one-liner contract), §6 (data flow — reads `taste/tracks.csv` + user-supplied audio; writes `teardowns/<slug>/{...}`), §7.5 (artifact schema — **extended** by this spec; see §2), §8 (refresh cadence: on-demand only), §11 default decisions #6 (librosa) and #10 (yt-dlp), §12 (out-of-scope: `.als` generation requires Suite + M4L)
- **Companion specs:**
  - `docs/superpowers/specs/subsystems/06-audio-enrichment.md` — produces `taste/tracks.csv`, this subsystem's optional context input
  - `docs/superpowers/specs/subsystems/03-knowledge-base.md` — produces `knowledge/genres/*.md` and `knowledge/artists/*.md`, the priors Claude reads while authoring `teardown.md` / `recipe.md`
  - `docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md` — co-located target audience for the recipes (a recipe should be doable inside the curriculum's Lite-floor lesson framing)
- **Session:** E (capstone, solo subsystem)
- **Build order:** Last subsystem in the project per master-spec §9; depends on Session C (minimum) and ideally Session D
- **Depends on:**
  - Subsystem #6 (Audio Feature Enrichment — produces `taste/tracks.csv` for cross-check + lookup); soft dependency — the pipeline degrades cleanly when csv is absent
  - Subsystem #3 (Knowledge Base — `knowledge/genres/*.md` and `knowledge/artists/*.md`); soft dependency — recipes degrade cleanly when an artist or genre has no page
  - Subsystem #7 (Taste Profile — populates `knowledge/artists/*.md`); soft dependency, same as above
- **Blocks:** nothing downstream

## 1. One-liner contract

Given a track Destin loves (YouTube URL, local audio file, or a track-name lookup against `taste/tracks.csv`), produces a `teardowns/<slug>/` directory containing the source audio, a librosa-derived `analysis.json`, a `scrub-strip.png` visualization, a `teardown.md` narrative ("what's happening when"), and a `recipe.md` of numbered build steps targeting Ableton Live 12 Lite's track floor with Intro+ callouts where extra tracks/sends would help.

The pipeline owns the teardowns directory layout, the analysis JSON schema, the artifact templates, and the project-scoped `/teardown` skill.

## 2. Master-spec overrides

This subsystem extends §7.5 (artifact schema) and explicitly deviates on librosa section detection.

### 2.1 Extension of §7.5 — `analysis.json` shape

- **Original field list:** `{ tempo, beat_times, sections: [{start, duration, label}], chroma, mfcc_summary }`.
- **Extended to:** structured envelope with sub-objects (`source`, `audio`, `tempo`, `beats`, `key`, `energy`, `chroma_mean`, `mfcc_summary`, `sections`, `csv_context`); see §3.9 for the full schema.
- **Reason:** Claude is the primary downstream reader (writes `teardown.md` / `recipe.md` from the JSON). Sub-grouping reduces Claude's reading cost and makes the cross-check fields (e.g., `tempo.bpm_csv` vs `tempo.bpm_librosa`) trivially discoverable. The original §7.5 field set is preserved as a subset.

### 2.2 Extension of §7.5 — fourth artifact

- **Original artifact list:** three files per teardown (`analysis.json`, `teardown.md`, `recipe.md`).
- **Extended to:** four files plus the source audio — `source.wav`, `analysis.json`, `scrub-strip.png`, `teardown.md`, `recipe.md`.
- **Reason:** Claude can read images but cannot listen to audio. A pre-rendered scrub strip (waveform / RMS energy / chroma / beat grid, time-aligned via `subplots(sharex=True)`) is the cheapest way to give Claude a faithful visual proxy of the track's structure. Without it, Claude is writing the teardown narrative half-blind, relying only on numerical features.

### 2.3 Deviation from §7.5 — empty `sections[]`

- **Master-spec §7.5:** `sections: [{start, duration, label}]` — implies librosa's auto-segmenter populates this.
- **This subsystem:** `sections: []` always. librosa's segmenter (`librosa.segment.agglomerative` family) is unreliable on EDM masters — over-fragments breaks, misses drops on heavily-sidechained sections.
- **Replacement mechanism:** Claude derives section boundaries from the `scrub-strip.png` energy curve plus genre priors in `knowledge/genres/<slug>.md` (which describe canonical intro / build / drop / break shapes per subgenre). The teardown narrative *is* the section labeling — `sections[]` would duplicate it with worse confidence.
- **If a future analyzer (e.g., msaf with EDM-tuned features) ships better section detection, the field is already in the schema and re-population is non-disruptive.**

When the master spec is next revised, both extensions and the deviation should be reflected.

## 3. What this subsystem does

### 3.1 Owns `teardowns/<slug>/`

The directory's existence, layout, slug-derivation rule, and per-file schema are this subsystem's responsibility.

```
teardowns/<slug>/
├── source.wav        # yt-dlp output (or manually dropped). gitignored.
├── analysis.json     # librosa-derived numerical analysis. tracked.
├── scrub-strip.png   # 4-panel time-aligned visualization. tracked.
├── teardown.md       # Claude-authored narrative. tracked.
└── recipe.md         # Claude-authored Lite-floor build steps. tracked.
```

### 3.2 The user-facing skill

A project-scoped skill at `.claude/skills/teardown/SKILL.md`. Auto-discovered when Claude Code loads the project. Invoked by:

- `/teardown <input>` — slash form
- "teardown this track: <url>" / "teardown the John Summit one" — natural-language form
- bare `/teardown` — skill asks for input

Both routes execute the same flow. The skill body is Claude's instructions — it owns the user-facing flow, the artifact templates, and the read-list for narrative authoring. No code in the skill itself.

### 3.3 The analysis CLI

A pure-Python CLI at `scripts/teardown.py`. Given a slug + audio source, produces `source.wav`, `analysis.json`, and `scrub-strip.png`. Deterministic, re-runnable from the terminal, testable without Claude in the loop. Authors no markdown.

The seam between the skill and the CLI is the file system — the skill subprocess-invokes the CLI, the CLI writes artifacts, the skill reads them.

### 3.4 Data flow

```
User input (URL | file | track-name)
    │
    ▼
[Skill] Input normalization
        URL?            → use directly
        file path?      → verify exists; --local mode
        Spotify ID?     → look up tracks.csv → artist + title
        free text?      → fuzzy match tracks.csv; on miss → YouTube search query
    │
    ▼
[Skill] URL resolution + Destin confirmation
        yt-dlp ytsearch1: → resolved title + duration + channel → ask Destin
        Abort, accept, or paste replacement URL
    │
    ▼
[Skill] Slug derivation + idempotency check
        Default: <artist-kebab>-<title-kebab>
        If teardowns/<slug>/ exists non-empty → ask: overwrite / -v2 / abort
    │
    ▼
[CLI] python scripts/teardown.py --slug <slug> (--url <url> | --local <path>)
                                  [--csv-context <spotify-id>] [--force]
    │
    ▼
[CLI] yt-dlp → teardowns/<slug>/source.wav (44.1kHz stereo)
[CLI] librosa.load(..., sr=22050, mono=True)
[CLI] librosa.beat.beat_track → tempo + beats
[CLI] librosa.feature.chroma_cqt → chroma matrix → key estimate (Krumhansl-Schmuckler) + chroma_mean
[CLI] librosa.feature.rms → RMS curve
[CLI] librosa.feature.mfcc → mfcc_summary
[CLI] If --csv-context: read taste/tracks.csv row, embed as csv_context
[CLI] Write analysis.json (§3.9)
[CLI] Render scrub-strip.png (§3.10)
[CLI] Print artifact paths and exit 0
    │
    ▼
[Skill / Claude] Read analysis.json + scrub-strip.png + relevant knowledge pages
[Skill / Claude] Write teardowns/<slug>/teardown.md (§3.11)
[Skill / Claude] Write teardowns/<slug>/recipe.md (§3.12)
[Skill] One-line wrap-up summary back to Destin
```

### 3.5 Track input modes

The skill accepts four input shapes and resolves each to a `(slug, source-spec, csv-context)` triple before invoking the CLI.

| Input shape | How recognized | Resolution |
|---|---|---|
| YouTube URL | `^https?://(www\.)?(youtube\.com\|youtu\.be)/` | Use directly. Slug derived from `yt-dlp --print title`. csv_context: try to fuzzy-match resolved title against tracks.csv; on hit, set; on miss, omit. |
| Other URL | Any other URL | Pass to yt-dlp; if yt-dlp supports it, proceed; otherwise error. |
| Local file path | exists on disk and has audio extension (`.wav`, `.mp3`, `.flac`, `.m4a`, `.opus`) | Use as-is via `--local`. Slug: ask Destin (no good auto-derive). csv_context: omit. |
| Spotify track ID | matches Base-62 / 22-char track-id pattern | Look up in tracks.csv → resolved artist + title → fall through to free-text path |
| Free text | anything else | Fuzzy match against `tracks.csv` (artist + title columns); top-1 match → resolved track. On miss, treat as YouTube search query verbatim. |

All paths converge on the URL-confirmation step (§3.6) before the CLI runs.

### 3.6 URL resolution + confirmation

When the input doesn't already supply a URL (free-text, Spotify ID, or fuzzy-matched track name), the skill resolves:

```bash
yt-dlp --skip-download --print "%(title)s|%(duration_string)s|%(channel)s" \
       "ytsearch1:<artist> <title> official audio"
```

The skill then prompts:

> Found: **John Summit & HAYLA — Where You Are (Official Audio)** [3:42, John Summit]. Use this? (y / paste different URL / abort)

Destin's response gates the next step. No download happens until confirmation. This is the single most important UX-safety rule: yt-dlp's first hit can be a live cut, sped-up edit, or nightcore version — Destin's eye on the title prevents wasted analysis.

### 3.7 Slug derivation + idempotency

**Auto-derivation:** kebab-case `<artist>-<title>`. Casefold, strip diacritics, replace runs of non-`[a-z0-9]` with `-`, collapse repeated dashes, trim leading/trailing dashes. Truncate to 80 characters. Example: `John Summit & HAYLA — Where You Are` → `john-summit-and-hayla-where-you-are`.

**Override:** at the slug-confirmation prompt, Destin can supply any string matching `^[a-z0-9][a-z0-9-]{0,79}$`; the skill validates and uses it.

**Idempotency:** the CLI never overwrites an existing `teardowns/<slug>/` without `--force`. The skill never passes `--force` without explicit Destin confirmation. Three options at the prompt:

1. **Overwrite** — skill passes `--force` (re-downloads source, re-analyzes, re-renders, but does **not** automatically delete `teardown.md` / `recipe.md`; Claude rewrites them and the new authoring overwrites the file content)
2. **Append `-v2`** — skill computes next available `<slug>-v<N>` and proceeds
3. **Abort** — clean exit, no files touched

### 3.8 Analysis pipeline

Single CLI entrypoint. Linear pipeline; each step is a function returning a dataclass; failure at any step exits with a numbered code (§3.15).

```
1. ffmpeg presence check       (subprocess.run("ffmpeg -version"))
2. Resolve source              (--url → yt-dlp, --local → verify path)
3. yt-dlp download             (--extract-audio --audio-format wav --audio-quality 0)
   skip if source.wav already exists and not --force
4. librosa.load(sr=22050, mono=True)
5. tempo, beats = librosa.beat.beat_track(y, sr)
6. chroma = librosa.feature.chroma_cqt(y, sr) → chroma_mean (12-vector)
7. key = krumhansl_schmuckler(chroma_mean)  [helper module]
8. rms_curve = librosa.feature.rms(y).flatten()
9. mfcc = librosa.feature.mfcc(y, sr, n_mfcc=13) → mean + std vectors
10. If --csv-context: read tracks.csv row by spotify_id
11. Compose analysis.json (§3.9), write
12. Render scrub-strip.png (§3.10), write
13. Print artifact paths, exit 0
```

Step 3's skip-if-exists optimization lets re-runs iterate on analysis without re-paying the download cost. `--force` overrides the skip.

### 3.9 `analysis.json` schema

```json
{
  "tool_version": "0.1.0",
  "created_at": "<UTC ISO 8601>",
  "source": {
    "url": "https://www.youtube.com/watch?v=...",
    "title": "John Summit & HAYLA — Where You Are (Official Audio)",
    "channel": "John Summit",
    "duration_s": 222.4,
    "downloaded_to": "source.wav"
  },
  "audio": {
    "sample_rate": 22050,
    "duration_s": 222.4,
    "channels": 1,
    "loader": "librosa.load (resampled mono)"
  },
  "tempo": {
    "bpm_librosa": 126.05,
    "bpm_csv": 126.0,
    "agree_within_1bpm": true,
    "agree_within_4bpm": true
  },
  "beats": {
    "count": 467,
    "first_beat_s": 0.51,
    "beat_times_s": [0.51, 0.99, 1.47, ...]
  },
  "key": {
    "camelot_librosa": "5A",
    "standard_librosa": "F minor",
    "camelot_csv": "5A",
    "agree": true,
    "method": "krumhansl-schmuckler on chroma_cqt mean"
  },
  "energy": {
    "hop_length": 512,
    "rms_values": [0.012, 0.018, ...],
    "rms_summary": { "mean": 0.18, "p10": 0.04, "p50": 0.18, "p90": 0.31 }
  },
  "chroma_mean": [0.04, 0.07, 0.31, ..., 0.05],
  "mfcc_summary": {
    "n_coeffs": 13,
    "means": [-321.4, 95.2, -3.1, ...],
    "stds":  [22.1, 11.3, 4.7, ...]
  },
  "sections": [],
  "csv_context": {
    "spotify_id": "5n4erMKwoH0Bky4VKZWWCQ",
    "artist": "John Summit",
    "title": "Where You Are",
    "bpm": 126.0,
    "key_camelot": "5A",
    "key_standard": "F minor",
    "energy": 0.78,
    "danceability": 0.71,
    "valence": 0.32,
    "genre": ""
  }
}
```

**Field semantics:**

- `tool_version` — bumps when the schema changes. Readers can branch on it.
- `source.url` — the resolved URL (after yt-dlp search). Empty when `--local`.
- `source.title` — for `--local`, set to the file basename.
- `tempo.bpm_csv` — present only when `--csv-context` was provided. Omitted (key absent) otherwise.
- `tempo.agree_within_1bpm` / `agree_within_4bpm` — present only when both estimates exist. The 4 BPM threshold catches half-time / double-time cases gracefully.
- `beats.beat_times_s` — every detected beat. ~500 floats for a 4-min track at 126 BPM.
- `key.camelot_librosa` / `standard_librosa` — librosa estimate. `camelot_csv` / `agree` present only when both exist.
- `energy.rms_values` — full RMS curve (~10k floats). Loadable by Claude in JSON; also the underlying data for the scrub strip.
- `chroma_mean` — 12-vector (one float per pitch class). Full per-frame chroma is *not* serialized to JSON — it's rendered into the scrub strip directly.
- `mfcc_summary` — first 13 coefficients' per-frame mean + std. Sufficient for timbre comparison; full MFCC matrix not serialized.
- `sections` — always `[]` per §2.3. Reserved for a future better segmenter.
- `csv_context` — entire row from `taste/tracks.csv` keyed by `spotify_id`. Present only when `--csv-context` was provided and the row was found.

### 3.10 `scrub-strip.png` layout

One figure, ~1600×1200 pixels at 100 dpi. Four panels via `matplotlib.pyplot.subplots(nrows=4, sharex=True, figsize=(16, 12))`:

```
┌─────────────────────────────────────────────────────────────┐
│ Panel 1 — Waveform                                          │
│   librosa.display.waveshow(y, sr=22050, alpha=0.5)          │
│   Faint gray; orientation reference, not analytic.          │
├─────────────────────────────────────────────────────────────┤
│ Panel 2 — RMS energy curve                                  │
│   plt.plot(times, rms_values), color='black'                │
│   Thin gray ticks at every 16-bar boundary computed from    │
│   beats[0] + (16 * 4 * 60 / bpm) increments.                │
│   This is the panel Claude reads to identify drops/breaks.  │
├─────────────────────────────────────────────────────────────┤
│ Panel 3 — Chroma heatmap                                    │
│   librosa.display.specshow(chroma, x_axis='time',           │
│                             y_axis='chroma')                │
│   Reveals key changes and harmonic content over time.       │
├─────────────────────────────────────────────────────────────┤
│ Panel 4 — Beat grid                                         │
│   For each beat: plt.axvline(t, alpha=0.15, color='gray')   │
│   Bold every 4 (downbeats), bolder every 16 (bar-of-4).     │
│   Visual reference for the bar-level callouts in            │
│   teardown.md.                                              │
└─────────────────────────────────────────────────────────────┘
   x-axis (shared): time in seconds, mm:ss labels at multiples of 16 bars
```

**Fallback:** if matplotlib's multi-axis layout fails (font / dpi crash on Windows), the CLI re-renders each panel as a separate PNG (`scrub-strip-1.png` … `scrub-strip-4.png`). Claude reads whichever exist.

### 3.11 `teardown.md` template

```markdown
---
slug: john-summit-and-hayla-where-you-are
generated_at: 2026-04-28T...
source: https://www.youtube.com/watch?v=...
duration: 3:42
tempo: 126 BPM (librosa) / 126 BPM (csv) — agree
key: 5A — F minor (librosa) / 5A (csv) — agree
genre_inferred: tech-house
genre_page: knowledge/genres/tech-house.md
artist_page: knowledge/artists/john-summit.md
---

# Where You Are — teardown

## TL;DR
Two-to-three-sentence essence of the track: BPM, key, structure, and the
single production move that defines this version. Flag any tempo / key
disagreement with tracks.csv here.

## Sections

### 0:00 — 0:32 — Intro
<2-3 sentence section overview describing instrumentation, energy, what's
arriving and what's not yet>
- 0:08 — <bar-level callout: a specific production gesture worth replicating>
- 0:16 — <another callout>

### 0:32 — 1:04 — Drop A
<overview>
- ...

### 1:04 — 1:36 — Break
<overview>
- ...

(continue for each section Claude identifies from the scrub strip)

## Production techniques worth copying
- <technique 1, with reference into knowledge/...md>
- <technique 2>
- <technique 3>

## Listen-for next time
- <thing 1>
- <thing 2>
```

**Authoring rules** (encoded in SKILL.md):

- Every bar-level callout cites a specific timestamp (mm:ss).
- Production-technique references link to `knowledge/genres/<slug>.md` or `knowledge/theory/<slug>.md` when applicable. No invented technique names.
- If `tempo.agree_within_4bpm` is `false`, TL;DR explicitly explains the disagreement (likely half/double-time read).
- If `genre_page` is missing, TL;DR notes "no genre cheat sheet for <X>; writing from librosa features + general EDM intuition" — gap is visible, not papered over.

### 3.12 `recipe.md` template

```markdown
---
slug: john-summit-and-hayla-where-you-are
recipe_for: Where You Are — John Summit & HAYLA
target: Ableton Live 12 Lite (8 audio + 8 MIDI tracks, Simpler-only, 2 sends)
generated_at: 2026-04-28T...
---

# Recipe — build something inspired by *Where You Are*

## Project setup
1. Set tempo to 126 BPM.
2. Set project key to 5A (F minor) — write a note in your master clip.
3. <additional setup steps>

## Drum foundation (MIDI 1 — Drum Rack)
4. <numbered steps>
5. ...

## Bass + sidechain (MIDI 2 — Operator, audio compressor sidechain)
6. ...

## Melodic layer (MIDI 3 — Operator preset)
7. ...

## Texture + perc (MIDI 4 / Audio 1)
8. ...

## Arrangement
9. Build the section structure described in teardown.md:
   intro / drop A / break / drop B / outro.
   ...

## Artist-resource enhancement
*(Section omitted when `knowledge/artists/<slug>.md` does not exist;
 replaced with one line: "No artist page yet — recipe leans on genre
 conventions only.")*

- Splice "Sounds of John Summit" pack: <link from artist page>
- Preset packs / signature techniques: <from artist page>
- Specific samples to chase: kick character "<X>", lead character "<Y>"

## Intro+ notes
*(Inline `**Intro+ note:**` callouts attached to specific steps where
 Lite limits hurt, e.g.:)*

- **Intro+ note (step 6):** with a 9th MIDI track available, you could
  split the bass into a sub layer and a mid layer for independent
  processing.
- **Intro+ note (step 9):** with 4 sends instead of 2, you could route
  the perc and melody to separate reverb buses.
```

**Authoring rules** (encoded in SKILL.md):

- Recipe must fit the Lite floor (8 audio + 8 MIDI, Simpler-only, 2 sends). The track-budget plan (which devices on which tracks) appears at the top of each section header.
- At least one `**Intro+ note:**` callout per recipe. If the recipe genuinely doesn't bump against any Lite limit, an Intro+ note still calls out an upgrade-path enhancement (e.g., "with Standard's Sampler instead of Simpler, you could …").
- "Artist-resource enhancement" section reads from `knowledge/artists/<slug>.md` only — never invents Splice packs, preset packs, or interview links (mirrors the `knowledge/artists/` rule from Subsystem #7).
- Every step must be doable by Destin without external research. If a step requires consulting a knowledge page, the page is linked inline.

### 3.13 CLI flags

| Flag | Effect |
|---|---|
| `--slug <name>` | Required. Output directory under `teardowns/`. |
| `--url <url>` | Audio source (YouTube URL or any yt-dlp-supported URL). Mutually exclusive with `--local`. |
| `--local <path>` | Use an existing local audio file. Mutually exclusive with `--url`. |
| `--csv-context <spotify-id>` | Embed the matching `taste/tracks.csv` row in `analysis.json`. Skipped silently if csv missing or no row matches. |
| `--force` | Re-download (`yt-dlp --force-overwrites`), re-analyze, re-render. Existing `teardown.md` / `recipe.md` are left in place — Claude rewrites them in the next step. |
| `--check-deps` | Print versions of ffmpeg, librosa, yt-dlp, matplotlib; exit 0. No analysis. Used by `scripts/README.md` install walkthrough. |
| `--dry-run` | Print the planned operations and exit 0. No downloads, no writes. |

### 3.14 Component layout

```
.claude/skills/
└── teardown/
    └── SKILL.md            # the user-facing flow + artifact templates +
                            # narrative-authoring rules. Read by Claude on
                            # invocation; not code.

scripts/
├── teardown.py             # main CLI (arg parsing, top-level orchestration)
├── teardown/
│   ├── __init__.py
│   ├── ytdlp.py            # download wrapper (one function: download(url, dest) -> Path)
│   ├── analyze.py          # librosa orchestration (one function: analyze(wav_path) -> AnalysisResult)
│   ├── key.py              # krumhansl-schmuckler key estimator
│   ├── plot.py             # scrub strip rendering (one function: render(analysis, out_path))
│   ├── csv_context.py      # tracks.csv row lookup by spotify_id
│   └── slug.py             # kebab-case derivation
├── tests/
│   ├── fixtures/teardown/
│   │   └── conftest.py     # generates a 30s synthesized 126 BPM wav
│   ├── test_teardown_args.py
│   ├── test_teardown_slug.py
│   ├── test_teardown_csv_context.py
│   ├── test_teardown_analysis_schema.py
│   ├── test_teardown_disagreement.py
│   ├── test_teardown_idempotency.py
│   ├── test_teardown_ffmpeg_check.py
│   └── test_teardown_e2e.py    # gated by TEARDOWN_E2E=1
├── README.md               # extended with teardown section
└── pyproject.toml          # extended deps (§6)
```

**Module contracts:** every backend module exposes one function returning a typed dataclass result; raises a module-specific exception on transient failure. Keeps each module testable in isolation.

### 3.15 Error-handling matrix

| Failure | Exit code | Skill response |
|---|---|---|
| ffmpeg not on PATH | 6 | "Install ffmpeg: `winget install Gyan.FFmpeg`. Re-run when done." |
| yt-dlp 403 / video unavailable / age-gated | 2 | "yt-dlp couldn't fetch. Drop the audio file at `teardowns/<slug>/source.wav` and re-invoke `/teardown --local <slug>`, or paste a different URL." |
| Audio decode fails after download | 3 | Try once more via explicit ffmpeg transcode to 22050Hz mono wav; if that also fails, surface the underlying ffmpeg stderr. |
| `librosa.load` returns <30s | 3 | "audio is suspiciously short — likely a partial / DRM-blocked download." |
| `librosa.beat.beat_track` returns half/double-time tempo | (no error) | Recorded as `bpm_librosa`; `agree_within_4bpm` flag captures the disagreement. Claude flags it in the teardown TL;DR. |
| Scrub-strip render fails | 5 (only if all four panels also fail individually) | If any panel fell back to a separate PNG, exit 0 — Claude reads what's there. Skill notes the fallback in the wrap-up. |
| `--csv-context` set, csv missing | 0 (warn) | CLI omits `csv_context`, prints a warning, continues. Skill relays the warning to Destin. |
| `tracks.csv` row not found | 0 (warn) | Same as above. |
| Free-text track lookup misses csv | (skill-side) | Skill skips `--csv-context`, treats input as YouTube search query. |
| `knowledge/artists/<slug>.md` missing | (skill-side, in narrative) | recipe.md "Artist-resource enhancement" section replaced with the no-page sentence. |
| Inferred genre has no `knowledge/genres/<slug>.md` | (skill-side, in narrative) | teardown.md TL;DR notes the gap explicitly. |
| User aborts at URL or overwrite confirmation | (skill-side) | Clean exit, no files written. |
| Re-invocation on existing slug without `--force` | 0 (cli) — but skill never gets here | Skill always prompts before passing `--force`. |
| matplotlib font / dpi crash | (handled in §3.10 fallback) | Per-panel rendering; warning in summary. |

**Safety rule:** the source audio is downloaded directly to `teardowns/<slug>/source.wav` — not to a temp dir. A failed analysis leaves the audio for re-runs (yt-dlp can skip the download on retry). The skill's overwrite-confirmation prompt catches accidental re-invocation; manual cleanup is one `rm -rf teardowns/<slug>/`.

### 3.16 `CLAUDE.md` edits (the #8 section)

```markdown
## Teardowns

The teardown pipeline is invoked via the project-scoped `/teardown` skill
at `.claude/skills/teardown/SKILL.md`. Both `/teardown <input>` and
"teardown this track: <input>" route through the same flow. Inputs:
YouTube URL, local file path, Spotify track ID, or free-text track name
(fuzzy-matched against `taste/tracks.csv`).

Per-teardown artifacts land in `teardowns/<slug>/`:
- `source.wav` (gitignored) — yt-dlp output or manually-dropped file
- `analysis.json` — librosa-derived numerical analysis
- `scrub-strip.png` — 4-panel time-aligned visualization Claude reads
- `teardown.md` — narrative ("what's happening when")
- `recipe.md` — numbered build steps targeting Ableton Live 12 Lite

Recipe rules: target the Lite floor (8 audio + 8 MIDI, Simpler-only,
2 sends); include at least one `**Intro+ note:**` callout; reference
`knowledge/artists/<slug>.md` for study materials only when the page
exists (never fabricate Splice packs).

When Destin is in Ableton and asks how to execute a recipe step, prefer
companion mode (`knowledge/ableton/companion-mode.md`) over verbal-only
directions.

Full subsystem spec: `docs/superpowers/specs/subsystems/08-teardown-pipeline.md`.
```

### 3.17 `.gitignore` additions

```
# Teardown source audio (large; reproducible from URL)
teardowns/**/source.wav
teardowns/**/source.mp3
teardowns/**/source.flac
teardowns/**/source.m4a
teardowns/**/source.opus
```

The four committed artifacts (`analysis.json`, `scrub-strip.png`, `teardown.md`, `recipe.md`) collectively give a full record of the teardown without the audio. Destin (or future Claude) can re-derive the audio from `analysis.json.source.url` whenever needed.

## 4. What this subsystem must NOT do

- **No `.als` file generation.** Out of scope per master spec §12. Requires Suite + Max for Live.
- **No stem / multitrack acquisition.** Master spec §3.5 — these aren't realistically obtainable for commercial EDM. Pipeline is master-first only.
- **No DRM bypass.** yt-dlp on YouTube and similar publicly-streamable sources only. No Spotify-DRM extraction, no torrent integration, no any-other-DRM circumvention.
- **No background watch loops, no autonomous teardowns.** Pipeline is user-triggered per master spec §8. The skill never fires on its own; no `/schedule` entry.
- **No fabricated production techniques.** Every callout in `teardown.md` must be grounded in observable scrub-strip / analysis data plus referenced knowledge pages. Every "Splice pack" / "preset pack" reference in `recipe.md` must come from `knowledge/artists/<slug>.md` (which itself is web-search-verified per Subsystem #7's rule). When evidence is absent, the gap is named explicitly.
- **No silent overwrites.** Existing `teardowns/<slug>/` directories are never overwritten without an explicit `--force` flag, and the skill never passes `--force` without Destin's explicit confirmation.
- **No coupling to the curriculum.** Teardowns are standalone artifacts; the curriculum doesn't auto-generate lessons from them. (`recipe.md` may *reference* an existing curriculum lesson if the connection is natural — e.g., "this builds on lesson-004's sidechain technique" — but doesn't write to `curriculum.md`.)
- **No use of Spotify's `audio-features` / `audio-analysis` endpoints.** Deprecated for new apps per master spec §3.1; would 403 anyway. All audio characterization comes from local librosa.
- **No re-running ReccoBeats / GetSongBPM** to fill the `csv_context` field. The pipeline reads `taste/tracks.csv` as it stands; Subsystem #6 owns enrichment.
- **No fork of the Python environment.** Extends the existing `scripts/` uv project. No conda environment, no separate venv.

## 5. Verification gate

Before declaring this subsystem complete:

- [ ] `.claude/skills/teardown/SKILL.md` exists and is auto-discovered by Claude Code (visible in the skills list when the project is opened).
- [ ] `scripts/teardown.py --check-deps` runs and reports ffmpeg, librosa, yt-dlp, matplotlib versions cleanly.
- [ ] All unit tests (§3.14 component layout's `test_teardown_*.py`) pass: `cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_*.py -v` (excluding the e2e test).
- [ ] Integration test passes: `TEARDOWN_E2E=1 .venv/Scripts/python -m pytest tests/test_teardown_e2e.py -v` produces the four CLI artifacts (`source.wav`, `analysis.json`, `scrub-strip.png` *or* the four panel fallback PNGs) on the synthetic fixture wav, with tempo within 2 BPM of the fixture's 126 BPM.
- [ ] **End-to-end manual run** on a taste-anchor track. Recommended primary candidate: **John Summit & HAYLA — "Where You Are"** (tech house, in tracks.csv with Camelot 5A, has a `knowledge/artists/john-summit.md` page, `knowledge/genres/tech-house.md` exists — exercises every code path). Alternative candidates: a Subtronics track (riddim/dubstep, low-frequency stress test) or the top jigitz track (bass house, master-spec anchor).
- [ ] On the chosen end-to-end track, all five artifacts ship: `source.wav`, `analysis.json`, `scrub-strip.png` (or per-panel fallbacks), `teardown.md`, `recipe.md`.
- [ ] `analysis.json` validates against the §3.9 schema.
- [ ] `analysis.json.tempo.agree_within_4bpm` is `true` (or, if `false`, the disagreement is plausibly explained as half/double-time and Claude flagged it in the TL;DR).
- [ ] `scrub-strip.png` is human-readable: panels aligned on the time axis, energy curve clearly shows the track's drops and breaks.
- [ ] `teardown.md` has section overviews + at least 2 bar-level timestamp callouts; references `knowledge/genres/<inferred>.md` and `knowledge/artists/<slug>.md` when those pages exist.
- [ ] `recipe.md` targets the Lite floor (≤ 8 audio + ≤ 8 MIDI tracks, Simpler-only, ≤ 2 sends) and contains at least one `**Intro+ note:**` callout.
- [ ] **Beginner-comprehension check:** Destin reads `recipe.md` top-to-bottom and can do every step without external research or knowledge beyond what's in `knowledge/`.
- [ ] `CLAUDE.md` has the §3.16 section added.
- [ ] `.gitignore` has the §3.17 patterns added.
- [ ] `scripts/README.md` has a teardown subsection covering: how to run; ffmpeg dependency; `--check-deps`; troubleshooting common failures.

## 6. Implementation notes

- **Python environment.** Extends the existing `scripts/` uv project (Python 3.12). New deps in `pyproject.toml`:
  ```toml
  "librosa>=0.10.2",
  "yt-dlp>=2026.04.01",
  "matplotlib>=3.8",
  "soundfile>=0.12",  # transitive but pinned explicitly
  ```
  All have `win_amd64 + py312` wheels in current versions. If a wheel ever fails: fall back to `uv pip install --no-binary librosa librosa` (and document); not a design-time concern.
- **System dependency: ffmpeg.** Required by yt-dlp (postprocessing) and by librosa for non-wav decode. Install: `winget install Gyan.FFmpeg`. CLI's `--check-deps` and the run-start probe both verify presence and exit 6 with the install hint when absent.
- **yt-dlp pinning.** yt-dlp updates weekly, often with required-bump CVE / API fixes. Pin to a specific release in `pyproject.toml` and document the bump cadence in `scripts/README.md` (target: bump on each new teardown session if it's been > 1 month).
- **Audio working format.** yt-dlp's `--extract-audio --audio-format wav --audio-quality 0` produces 44.1kHz stereo wav. librosa loads via `librosa.load(path, sr=22050, mono=True)` — resampled-mono for analysis speed. The 44.1k/stereo source stays canonical in case Destin wants to re-listen; analysis works on the 22050-mono buffer in memory only.
- **Key estimator.** Krumhansl-Schmuckler is a 30-year-old standard; 24 reference profiles (12 major, 12 minor) correlated against the chroma_mean. ~50 lines of numpy. Don't pull a third-party key-detection library — the algorithm is small enough to ship in `scripts/teardown/key.py` with documented references.
- **Camelot conversion.** Reuse the existing 24-entry table in `scripts/enrich/camelot.py` — don't duplicate it. Import path: `from enrich.camelot import camelot_for(key_int, mode_int)` or equivalent.
- **TDD applied during implementation.** Per `superpowers:test-driven-development`, each unit test in §3.14 is written *before* its target code. Order: slug logic → schema validator (`test_teardown_analysis_schema.py` after composing a fixture analysis dict) → CSV-context lookup → disagreement detection → idempotency guard → ffmpeg-check stub. The integration test gets written once the linear pipeline can run end-to-end on the fixture wav.
- **Fixture audio.** Generated programmatically in `scripts/tests/fixtures/teardown/conftest.py`: a 30-second synthesized wav at 22050Hz mono, sine-bass at 65 Hz + click metronome at 126 BPM. Deterministic, fast, no copyright surface, validates the librosa pipeline returns sensible tempo + energy curve.
- **librosa version pin.** 0.10.x is the current stable line. 0.11 is in development; pin lower bound at 0.10.2 (the version with `librosa.feature.rms` returning consistent shape on stereo input). Bump only when a feature actually requires it.
- **matplotlib backend.** Use `matplotlib.use('Agg')` at module top — non-interactive backend, no display required, faster on Windows. The CLI never wants a window.
- **Slug collisions.** Two different tracks could derive the same slug after kebab-casing (e.g., a remix and an original both becoming `artist-track-name`). The skill's overwrite prompt is the safety net — Destin chooses `-v2` if he wants the second one. No global de-duplication needed in v1.
- **No spotify-services plugin dependency.** The pipeline reads `taste/tracks.csv` directly (file shape is owned by Subsystem #6); the plugin is not in the loop. This keeps the teardown pipeline runnable even when Destin's Spotify tokens have expired.
- **Out-of-coverage degradation.** Tracks where neither `knowledge/artists/<slug>.md` nor `knowledge/genres/<slug>.md` exist still ship a teardown — just with explicit "no page yet" notes in the artifacts. The pipeline is robust to gaps in the knowledge base; gaps are visible, not papered over.
- **Test track choice for verification gate.** John Summit's "Where You Are" is the recommended primary because every code path is exercised: in tracks.csv with full csv_context, has artist page, has genre page, has a clean tech-house structure that's friendly to a Lite-floor recipe. Fall back to a Subtronics or jigitz track if the John Summit URL goes 403.

## 7. Self-review checklist

- [x] **Placeholders / TBDs:** none. All field semantics, error behaviors, schemas, templates, and verification criteria are specified concretely.
- [x] **Internal consistency:** §3.4 data flow → §3.8 analysis pipeline → §3.9 analysis.json schema → §3.10 scrub-strip layout → §3.11/3.12 templates all describe the same end-to-end flow with consistent field names. The `--force` semantics in §3.7 (idempotency), §3.13 (CLI), and §3.15 (errors) agree. The "no fabricated data" rule appears in §3.11/3.12 (templates), §3.16 (CLAUDE.md), and §4 (must-not list) consistently.
- [x] **Scope:** narrowly bounded to the teardown of one user-supplied track. Out-of-scope items in §4 (no .als, no stems, no DRM, no autonomous behavior, no curriculum coupling). No drift into Subsystem #4 (curriculum), #6 (enrichment), or #7 (taste profile).
- [x] **Ambiguity:** the input-resolution table (§3.5), the URL-confirmation prompt copy (§3.6), the slug regex (§3.7), the CLI flag table (§3.13), and the error matrix (§3.15) are explicit. Three idempotency options (overwrite / -v2 / abort) are enumerated, not vague.
- [x] **Master-spec relationship:** §2 enumerates the two extensions and one deviation from §7.5 with reasons. §1 ties the contract to master-spec §3.2, §3.5, §5.1 #8, §6, §7.5, §8, §11 #6/#10, §12. The Lite-floor recipe constraint (§3.2) is honored throughout §3.12 / §4 / §5.
- [x] **Knowledge-base relationship:** §3.11 / §3.12 specify exactly when artist and genre pages are read, what the fallback is when they're absent, and the rule that fabricated resources are forbidden (mirroring the Subsystem #7 / CLAUDE.md rule).
- [x] **Subsystem #6 boundary:** clean — this spec reads `taste/tracks.csv` as input only, never writes it, never re-enriches.
- [x] **Subsystem #9 (Reactive Companion) relationship:** §3.16 defers in-Ableton execution help to companion mode. Recipe authoring doesn't try to replace the companion.
- [x] **Subsystem #4 (Curriculum) coupling:** intentionally absent. §4 explicitly forbids it. Recipes may reference existing lessons but never write to `curriculum.md`.
- [x] **Verification gate concreteness:** §5 lists 14 specific checks, including a named primary test track, file existence checks, schema validation, threshold checks, and a beginner-comprehension subjective gate. No gate is "TBD".
