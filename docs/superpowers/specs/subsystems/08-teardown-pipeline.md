# Subsystem #8 — Teardown Pipeline

- **Date:** 2026-04-28 (v1.0 shipped); 2026-04-29 (v1.1 amendment — see §2.4–§2.6)
- **Status:** v1.0 shipped; v1.1 amendment approved, pending implementation plan
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

## 2. Master-spec overrides and v1.1 amendments

This subsystem extends §7.5 (artifact schema), explicitly deviates on librosa section detection, and (in v1.1) substantially expands the feature-extraction surface, redefines the trust hierarchy for narrative authoring, and adds a web-findings step.

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

### 2.4 v1.1 amendment — richer feature extraction

- **Original (v1.0) analysis pipeline:** load → tempo + beats → chroma_cqt mean → RMS curve → MFCC summary. Sufficient for structure, BPM, key. Insufficient for any time-localized claim about *what* makes the energy at a moment.
- **Extended to:** the v1.0 features plus **per-band RMS** (5 bands: sub 20–60 Hz / bass 60–250 / low-mids 250–2k / highs 2k–8k / air 8k+), **HPSS split** (`librosa.effects.hpss` → harmonic + percussive RMS curves), **spectral centroid** (`librosa.feature.spectral_centroid` over time), **onset density per band** (per-band onset envelopes → onsets-per-bar buckets), and **sidechain detection** (kick-onset-aligned bass-band RMS dip analysis with measured dB depth and consistency %).
- **Reason:** the v1.0 verification-gate teardown for John Summit — *crystallized (feat. Inéz)* exposed a hallucination failure mode. The narrative authored under v1.0 made specific instrument-level and production-technique claims (vocal lead, octave doubling, sidechained bass, reverb pre-delay automation, drum fills) that the v1.0 analysis surface didn't actually support — Claude was filling in genre-typical details rather than reporting what the artifacts measured. The v1.1 features give Claude *measured evidence* for the kinds of claims a producer-tutor narrative needs: which frequency bands light up when, how rhythmic vs harmonic content shifts across sections, where brightness peaks, and whether sidechain compression is present and how deep.
- **Sidechain detection method:** for each kick onset (sub-band onset detection on the loaded signal), measure the dip in bass-band RMS within ~100 ms of the onset versus a rolling local mean. Report measured dB depth and consistency %. Threshold for the "sidechain detected" flag: **≥3 dB ducking on ≥60% of kick onsets**. The measured dB depth and consistency % are always reported regardless of the flag — the threshold gates only the binary detection, not the data.
- **Cost:** moderate. HPSS adds ~5 s on a 4-min track (1 STFT + 1 ISTFT). Per-band RMS is a single STFT (cheap). Centroid, onset density, sidechain detection are cheap. Total expected analysis-step time on a 4-min track: ~12–20 s (was ~5–8 s in v1.0).
- **Spec lineage:** the original §3.8 pipeline list, §3.9 analysis.json schema, §3.10 scrub-strip layout, and §6 implementation notes are updated in place to reflect v1.1; v1.0 versions live in `git show 5b3ba2e:docs/superpowers/specs/subsystems/08-teardown-pipeline.md`.

### 2.5 v1.1 amendment — trust hierarchy for narrative authoring

The v1.0 SKILL.md authoring rules said "every callout cites a specific timestamp" and "no fabricated production techniques." Insufficiently specific — they didn't constrain *what kind* of claim could be made. v1.1 replaces them with an explicit four-tier trust hierarchy. Every claim in `teardown.md` and `recipe.md` must be traceable to one of these tiers, with the tier indicating its authority:

1. **`taste/tracks.csv` (ReccoBeats)** — authoritative for track-level facts. When a row exists for the track, its values for `bpm`, `key_camelot`, `key_standard`, `mode`, `time_signature`, `energy`, `danceability`, `valence`, `acousticness`, `instrumentalness`, `liveness`, `loudness`, `speechiness`, `genre` are the source of truth. Librosa estimates that disagree are explicitly named as cross-checks (*"librosa reads X, csv reads Y; csv is authoritative"*).
2. **Measured spectral features** (analysis.json + scrub-strip.png) — authoritative for time-localized observations. Claims must describe what the curves and panels show. The narrative may name *what the measurement is* ("sub-band RMS climbs from 0.04 to 0.42 at 0:40", "percussive HPSS component drops near-zero from 1:52 to 2:45", "spectral centroid mean is ~800 Hz higher in Drop B than Drop A") but **not** *what is causing the energy* without measurable support ("the bass enters" is a cause-inference; forbidden unless backed by per-band evidence and even then phrased as the measurement, e.g., "sub+bass band content arrives").
3. **Web findings** (see §2.6) — *supporting* only. Cite with source URL + access date. Can never override tier 1 or tier 2. When a web source contradicts measurement, the narrative reports both with attribution and flags the discrepancy.
4. **Genre/artist priors** (`knowledge/genres/*.md`, `knowledge/artists/*.md`) — background context. The narrative may use genre conventions for structural labeling ("kick-out break", "drop A → break → drop B") since the structural label is genre vocabulary, not a claim about this track. Priors may not introduce specific claims about this track that the measurement doesn't support.

**Allowed (concrete examples):**
- *"BPM 128 (csv) — librosa reads 129; csv is authoritative."* — tier 1 with named cross-check
- *"Camelot 3B / Db major (csv); librosa estimate 4A (F minor) — adjacent on the wheel, common Krumhansl bias toward the relative minor."* — tier 1 with explicit disagreement framing
- *"Instrumentalness 0.011 (csv) — vocals or melodic samples are clearly present in the track."* — tier 1, csv field meaning made explicit
- *"Sub-band RMS climbs from 0.04 to 0.42 at 0:40."* — tier 2, describes the curve
- *"Sidechain detected: 4 dB average ducking on 87% of kick onsets (per analysis.json)."* — tier 2, measured + cited
- *"Percussive HPSS component drops near-zero from 1:52 to 2:45 while harmonic component holds — kick-out break (genre vocabulary)."* — tier 2 with tier 4 structural label
- *"Per Genius credits ([url], accessed 2026-04-29), Inéz performs lead vocal."* — tier 3, supporting claim with attribution

**Forbidden (concrete examples — these are what failed in the v1.0 verification gate):**
- *"The bass enters at 0:40."* — cause-inference; rewrite as the measurement
- *"Inéz's vocal hook arrives at 0:48."* — instrument-level claim with no measurement support; only allowed if a web finding (tier 3) supports it AND the per-band high-band activity is consistent
- *"The lead is doubled an octave up."* — un-measurable
- *"Reverb pre-delay automation on the 'crys-' syllable."* — un-measurable
- *"Drum fill at 2:42."* — cause-inference; describe percussive RMS spike
- *"The kick uses a Roland TR-909."* — un-measurable
- *"Vocal-formant-processed lead."* — un-measurable

### 2.6 v1.1 amendment — web findings as supporting evidence

A new step in the `/teardown` skill flow runs a focused batch of web searches between the CLI run and the narrative authoring. Findings are saved to a new tracked artifact `teardowns/<slug>/web_findings.md` and cited in `teardown.md` / `recipe.md` as tier-3 supporting evidence per §2.5.

- **Default search set** (run as a small batch, parallel where possible):
  | Search | Intent |
  |---|---|
  | `<artist> <title> stems` | stems / multitracks (rare but transformative — pivots `recipe.md` into "study the stems" mode if found) |
  | `<artist> <title> acapella` | vocal isolations |
  | `<artist> <title> breakdown` OR `how <artist> made <title>` | production breakdown videos / tutorials |
  | `<artist> <title> splice` | dedicated sample pack for this track (vs the artist-level packs already in `knowledge/artists/<slug>.md`) |
  | `<artist> <title>` (general) | context, interviews, Genius credits, mood tags |
- **`web_findings.md` schema (§3.10a):** a markdown file with frontmatter (slug, generated_at) and a section per search, each section listing each result's title, URL, source domain, and a one-paragraph relevance note. Tracked in git as a snapshot — auditable, and useful when re-running the teardown months later to see if the resource set has grown.
- **`recipe.md` stems-pivot:** when a search finds verified stems / multitracks, the recipe authoring switches modes — instead of "build a track that hits the csv profile + measured structure using genre conventions", it becomes "study the actual stems at <URL>" with steps like "load the drum stem into Audio 1 and sketch its kick attack envelope by ear" rather than "program a kick on MIDI 1." The genre-convention path is the fallback when no stems are found.
- **Failure handling:** web search timeouts, rate-limiting, or zero-result responses are recorded in `web_findings.md` (so the date-of-search audit is complete) but do not block the teardown — narrative authoring proceeds with `web_findings = []` if everything missed. The CLI is unaffected (web search lives in the skill, not the CLI).

When the master spec is next revised, the v1.0 extensions/deviation and the v1.1 amendments should both be reflected.

## 3. What this subsystem does

### 3.1 Owns `teardowns/<slug>/`

The directory's existence, layout, slug-derivation rule, and per-file schema are this subsystem's responsibility.

```
teardowns/<slug>/
├── source.wav        # yt-dlp output (or manually dropped). gitignored.
├── analysis.json     # librosa-derived numerical analysis (v1.1: per-band RMS,
│                     #   HPSS, centroid, onset density, sidechain detection).
│                     #   tracked.
├── scrub-strip.png   # 6-panel time-aligned visualization (v1.1: was 4 panels
│                     #   in v1.0). tracked.
├── web_findings.md   # v1.1: web-search snapshot — stems, breakdowns, credits,
│                     #   etc. with source URLs + access date. tracked.
├── teardown.md       # Claude-authored narrative. tracked.
└── recipe.md         # Claude-authored Lite-floor build steps (v1.1: pivots to
│                     #   "study the stems" mode if web_findings.md surfaces
│                     #   verified stems). tracked.
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
[CLI] onset_strength + feature.tempo + beat.plp → tempo + beat times
      (numba-free path; see §6 for the librosa.beat.beat_track segfault note)
[CLI] librosa.feature.chroma_cqt → chroma matrix → key estimate
      (Krumhansl-Schmuckler) + chroma_mean
[CLI] librosa.feature.rms → overall RMS curve
[CLI] librosa.feature.mfcc → mfcc_summary
[CLI] v1.1: STFT → per-band RMS curves (sub / bass / low-mids / highs / air)
[CLI] v1.1: librosa.effects.hpss → harmonic + percussive components → RMS each
[CLI] v1.1: librosa.feature.spectral_centroid → centroid curve
[CLI] v1.1: per-band onset detection → onset density per bar per band
[CLI] v1.1: sub-band onset detection + bass-band RMS dip analysis →
      sidechain detection (depth dB + consistency %)
[CLI] If --csv-context: read taste/tracks.csv row, embed as csv_context
[CLI] Write analysis.json (§3.9 — extended for v1.1)
[CLI] Render scrub-strip.png (§3.10 — 6 panels in v1.1)
[CLI] Print artifact paths and exit 0
    │
    ▼
[Skill] v1.1: Web-search batch (§3.10a) — stems / acapella / breakdown /
        splice / general queries. Capture results with URLs + access date.
[Skill] v1.1: Write teardowns/<slug>/web_findings.md
    │
    ▼
[Skill / Claude] Read analysis.json + scrub-strip.png + web_findings.md +
                 relevant knowledge pages
[Skill / Claude] Write teardowns/<slug>/teardown.md (§3.11) per §2.5 trust
                 hierarchy — every claim traces to tier 1/2/3/4
[Skill / Claude] Write teardowns/<slug>/recipe.md (§3.12) — stems-pivot mode
                 when web_findings.md has verified stems, otherwise
                 genre-convention "hit the csv profile" mode
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
 1. ffmpeg presence check       (only when --url; see §3.15)
 2. Resolve source              (--url → yt-dlp, --local → verify path)
 3. yt-dlp download             (--extract-audio --audio-format wav --audio-quality 0)
    skip if source.wav already exists and not --force
 4. librosa.load(sr=22050, mono=True)
 5. onset_env = librosa.onset.onset_strength(y, sr, hop=256)
 6. bpm = librosa.feature.tempo(onset_envelope=onset_env, ...)
 7. beat_times = via librosa.beat.plp(onset_env, tempo_min/max=bpm±20%) → localmax
    (avoids the librosa.beat.beat_track segfault on numba 0.65 / Py 3.12 Windows)
 8. chroma = librosa.feature.chroma_cqt(y, sr) → chroma_mean (12-vector)
 9. key = krumhansl_schmuckler(chroma_mean)  [helper module]
10. rms_curve = librosa.feature.rms(y).flatten()
11. mfcc = librosa.feature.mfcc(y, sr, n_mfcc=13) → mean + std vectors
12. v1.1: per_band_rms = STFT magnitude → sum bins per band → RMS per band
    Bands (Hz): sub 20–60, bass 60–250, low_mids 250–2000, highs 2000–8000, air 8000+
13. v1.1: y_h, y_p = librosa.effects.hpss(y); rms_harmonic, rms_percussive
14. v1.1: spectral_centroid = librosa.feature.spectral_centroid(y, sr) → curve
15. v1.1: per-band onset envelopes → librosa.onset.onset_detect → bin onsets
    by bar (using beat_times) → onsets_per_bar per band
16. v1.1: sidechain detection — for each kick onset (sub-band onset detect),
    measure dip in bass-band RMS within ~100 ms versus rolling local mean →
    dB depth + consistency %. Detected when ≥3 dB on ≥60% of kicks.
17. If --csv-context: read tracks.csv row by spotify_id
18. Compose analysis.json (§3.9), write
19. Render scrub-strip.png (§3.10), write
20. Print artifact paths, exit 0
```

Step 3's skip-if-exists optimization lets re-runs iterate on analysis without re-paying the download cost. `--force` overrides the skip.

Steps 12–16 are the v1.1 additions. They share the loaded waveform `y` from step 4 and the beat_times from step 7. Total expected analysis-step time on a 4-min track: ~12–20 s (was ~5–8 s in v1.0).

### 3.9 `analysis.json` schema

v1.1 schema. Bump `tool_version` to `"0.2.0"` to signal the new top-level keys (`per_band_rms`, `hpss`, `spectral_centroid`, `onset_density`, `sidechain`).

```json
{
  "tool_version": "0.2.0",
  "created_at": "<UTC ISO 8601>",
  "source": {
    "url": "https://www.youtube.com/watch?v=...",
    "title": "John Summit — crystallized (feat. Inéz) [Official Lyric Visualizer]",
    "channel": "John Summit",
    "duration_s": 217.8,
    "downloaded_to": "source.wav"
  },
  "audio": {
    "sample_rate": 22050,
    "duration_s": 217.8,
    "channels": 1,
    "loader": "librosa.load (resampled mono)"
  },
  "tempo": {
    "bpm_librosa": 129.2,
    "bpm_csv": 128.049,
    "agree_within_1bpm": false,
    "agree_within_4bpm": true
  },
  "beats": {
    "count": 467,
    "first_beat_s": 0.51,
    "beat_times_s": [0.51, 0.99, 1.47, ...]
  },
  "key": {
    "camelot_librosa": "4A",
    "standard_librosa": "F minor",
    "camelot_csv": "3B",
    "agree": false,
    "method": "krumhansl-schmuckler on chroma_cqt mean"
  },
  "energy": {
    "hop_length": 512,
    "rms_values": [0.012, 0.018, ...],
    "rms_summary": { "mean": 0.18, "p10": 0.04, "p50": 0.18, "p90": 0.31 }
  },

  "per_band_rms": {
    "hop_length": 512,
    "bands": {
      "sub":      { "hz_low": 20,   "hz_high": 60,   "rms_values": [...], "rms_summary": { "mean": ..., "p10": ..., "p90": ... } },
      "bass":     { "hz_low": 60,   "hz_high": 250,  "rms_values": [...], "rms_summary": {...} },
      "low_mids": { "hz_low": 250,  "hz_high": 2000, "rms_values": [...], "rms_summary": {...} },
      "highs":    { "hz_low": 2000, "hz_high": 8000, "rms_values": [...], "rms_summary": {...} },
      "air":      { "hz_low": 8000, "hz_high": null, "rms_values": [...], "rms_summary": {...} }
    }
  },

  "hpss": {
    "hop_length": 512,
    "harmonic_rms_values": [...],
    "percussive_rms_values": [...],
    "harmonic_rms_summary":  { "mean": ..., "p10": ..., "p90": ... },
    "percussive_rms_summary": { "mean": ..., "p10": ..., "p90": ... }
  },

  "spectral_centroid": {
    "hop_length": 512,
    "values_hz": [...],
    "summary_hz": { "mean": 2150.4, "p10": 850.0, "p50": 2050.1, "p90": 4120.7 }
  },

  "onset_density": {
    "bars": [
      { "bar_index": 0, "start_s": 0.51, "end_s": 2.39,
        "onsets_per_band": { "sub": 4, "bass": 5, "low_mids": 12, "highs": 18, "air": 9 } },
      { "bar_index": 1, "start_s": 2.39, "end_s": 4.27,
        "onsets_per_band": { "sub": 4, "bass": 5, "low_mids": 14, "highs": 22, "air": 11 } }
    ]
  },

  "sidechain": {
    "detected": true,
    "depth_db_mean": 4.2,
    "depth_db_p90": 6.8,
    "consistency_pct": 87.0,
    "kicks_examined": 152,
    "threshold_db_for_detection": 3.0,
    "threshold_consistency_for_detection": 60.0,
    "method": "sub-band onset detect + bass-band RMS dip within 100ms vs rolling mean"
  },

  "chroma_mean": [0.04, 0.07, 0.31, ..., 0.05],
  "mfcc_summary": {
    "n_coeffs": 13,
    "means": [-321.4, 95.2, -3.1, ...],
    "stds":  [22.1, 11.3, 4.7, ...]
  },
  "sections": [],
  "csv_context": {
    "spotify_id": "6YiIWuVXS4AqF1KvUGMwyx",
    "artist": "John Summit",
    "title": "crystallized (feat. Inéz)",
    "bpm": 128.049,
    "key_camelot": "3B",
    "key_standard": "Db major",
    "mode": 1,
    "energy": 0.857,
    "danceability": 0.857,
    "valence": 0.349,
    "acousticness": 0.292,
    "instrumentalness": 0.011,
    "liveness": 0.126,
    "loudness": -4.689,
    "speechiness": 0.075,
    "genre": ""
  }
}
```

**Field semantics:**

- `tool_version` — bumps when the schema changes. Readers can branch on it. v1.0 → `"0.1.0"`; v1.1 → `"0.2.0"`.
- `source.url` — the resolved URL (after yt-dlp search). Empty when `--local`.
- `source.title` — for `--local`, set to the file basename.
- `tempo.bpm_csv` — present only when `--csv-context` was provided. Omitted (key absent) otherwise.
- `tempo.agree_within_1bpm` / `agree_within_4bpm` — present only when both estimates exist. The 4 BPM threshold catches half-time / double-time cases gracefully.
- `beats.beat_times_s` — every detected beat (~500 floats for a 4-min track at 128 BPM).
- `key.camelot_librosa` / `standard_librosa` — librosa estimate. `camelot_csv` / `agree` present only when both exist.
- `energy.rms_values` — full overall RMS curve (~10k floats). Underlying data for the scrub strip's overall-energy reading.
- `per_band_rms.bands.<band>.rms_values` — per-band RMS curve. Same length and hop_length as `energy.rms_values`. The `air` band has `hz_high: null` (open-top above 8 kHz).
- `hpss.harmonic_rms_values` / `percussive_rms_values` — RMS computed on the HPSS-separated waveforms. Same length / hop_length as overall RMS.
- `spectral_centroid.values_hz` — centroid over time in Hz. Same length / hop_length.
- `onset_density.bars` — one entry per bar derived from `beats.beat_times_s` (each bar = 4 consecutive beats). Each entry counts onsets per band that fell within the bar's time range.
- `sidechain` — measurement always reported; `detected` is the binary flag gated by `threshold_db_for_detection` (3.0) AND `threshold_consistency_for_detection` (60.0). `depth_db_mean` / `depth_db_p90` are the measured ducking depth across all examined kicks. `consistency_pct` is the share of kicks where any dip exceeded the threshold. `kicks_examined` is the total number of kick onsets the detector evaluated.
- `chroma_mean` — 12-vector. Full per-frame chroma is *not* serialized; the scrub strip renders it directly.
- `mfcc_summary` — first 13 coefficients' per-frame mean + std.
- `sections` — always `[]` per §2.3. Reserved for a future better segmenter.
- `csv_context` — full row from `taste/tracks.csv` keyed by `spotify_id`. Present only when `--csv-context` was provided and the row was found.

### 3.10 `scrub-strip.png` layout

v1.1 layout: one figure, ~1600×1800 pixels at 100 dpi. **Six panels** via `matplotlib.pyplot.subplots(nrows=6, sharex=True, figsize=(16, 18))`:

```
┌─────────────────────────────────────────────────────────────┐
│ Panel 1 — Waveform                                          │
│   librosa.display.waveshow(y, sr=22050, alpha=0.5)          │
│   Faint gray; orientation reference, not analytic.          │
├─────────────────────────────────────────────────────────────┤
│ Panel 2 — Per-band RMS (5 lines)                            │
│   sub (purple) / bass (blue) / low_mids (green) /           │
│   highs (orange) / air (red), all on the same axis.         │
│   Use a log y-axis so the dynamic range across bands is     │
│   readable. Legend in the upper right.                      │
│   This is the panel Claude reads to know which bands light  │
│   up when (drops, kick-out breaks, riser sweeps).           │
├─────────────────────────────────────────────────────────────┤
│ Panel 3 — HPSS split (2 lines)                              │
│   harmonic_rms (teal) and percussive_rms (magenta) on the   │
│   same axis. Linear y-axis. Legend in the upper right.      │
│   Identifies kick-out breaks (percussive→0, harmonic holds) │
│   and harmony-stripped buildups.                            │
├─────────────────────────────────────────────────────────────┤
│ Panel 4 — Spectral centroid + total onset density           │
│   centroid (Hz, primary y-axis, gray line) and onset        │
│   density per bar summed across bands (secondary y-axis,    │
│   black bars). Tracks brightness shifts and rhythmic        │
│   density independently.                                    │
├─────────────────────────────────────────────────────────────┤
│ Panel 5 — Chroma heatmap                                    │
│   librosa.display.specshow(chroma, x_axis='time',           │
│                             y_axis='chroma')                │
│   Reveals key changes and harmonic content over time.       │
├─────────────────────────────────────────────────────────────┤
│ Panel 6 — Beat grid                                         │
│   For each beat: plt.axvline(t, alpha=0.15, color='gray')   │
│   Bold every 4 (downbeats), bolder every 16 (bar-of-4).     │
│   Visual reference for the bar-level callouts in            │
│   teardown.md.                                              │
└─────────────────────────────────────────────────────────────┘
   x-axis (shared): time in seconds, mm:ss labels at multiples of 16 bars
```

**Fallback:** if matplotlib's multi-axis layout fails (font / dpi crash on Windows), the CLI re-renders each panel as a separate PNG (`scrub-strip-1.png` … `scrub-strip-6.png`). Claude reads whichever exist.

### 3.10a Web findings flow + `web_findings.md` schema

After the CLI exits successfully, the skill (not the CLI) performs the web-findings batch. This separation keeps the deterministic CLI layer free of network-dependent behavior; the skill owns user-visible orchestration including web search.

**Flow:**

```
[Skill] After CLI exits 0, derive (artist, title) from analysis.json
        (csv_context.artist + csv_context.title when present, otherwise the
        resolved YouTube title parsed for "ARTIST - TITLE" form, otherwise
        the slug as a fallback identifier).
[Skill] Run the default search batch (§2.6 table) using the WebSearch tool.
[Skill] For each result, capture: title, URL, source_domain, one-paragraph
        relevance note authored from the result snippet.
[Skill] Compose web_findings.md (schema below) and write to
        teardowns/<slug>/web_findings.md.
[Skill] Note in the file whether any verified stems / acapella URL was
        found — this is what the recipe.md authoring step reads to decide
        whether to enter stems-pivot mode.
```

**`web_findings.md` schema:**

```markdown
---
slug: john-summit-crystallized
generated_at: 2026-04-29T08:30:00Z
artist: John Summit
title: crystallized (feat. Inéz)
stems_found: false
acapella_found: true
breakdown_found: true
---

# Web findings — *crystallized (feat. Inéz)*

> Tier 3 supporting evidence per spec §2.5. Cite with source URL + access date.
> Never override `taste/tracks.csv` (tier 1) or measured spectral features
> (tier 2). Discrepancies must be flagged in `teardown.md`.

## Stems / multitracks
*No verified stems located in this search batch.*

## Acapella / vocal isolation
- **Inéz – crystallized (Acapella)** — youtube.com — `<URL>` — accessed 2026-04-29
  Brief paragraph from the result snippet describing what's there and why
  it's relevant.

## Production breakdowns
- **How John Summit Made "crystallized"** — youtube.com (Channel: ProducerHub) — `<URL>` — accessed 2026-04-29
  Paragraph: "Tutorial walks through the kick + sub stack and the sidechain
  routing on the bass channel. Confirms a Splice sample for the kick."

## Splice / dedicated sample packs
*No track-specific Splice pack located. Artist-level pack is in `knowledge/artists/john-summit.md`.*

## General context
- **Genius credits page** — genius.com — `<URL>` — accessed 2026-04-29
  Paragraph: "Lists Inéz as featured vocalist; production credit John Summit; mixing engineer X."
- **Pitchfork review** — pitchfork.com — `<URL>` — accessed 2026-04-29
  Paragraph: "Notes the track's 'sparse' instrumentation; describes Inéz's
  vocal as 'breathy, processed with long delay tails'."
```

**Tracking:** `web_findings.md` is committed to git. It's a snapshot of what was findable at the run's date — useful for re-running the teardown later (resource sets grow) and for auditing what evidence the narrative was built on.

**Failure handling:** zero-result responses, timeouts, or rate-limits per search are recorded as a one-line note under the relevant section ("*WebSearch returned 0 results*", "*WebSearch timed out after 30s*"). The teardown proceeds with whatever findings landed; `web_findings = []` is a valid state.

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

**Authoring rules** (encoded in SKILL.md, v1.1 tightened per §2.5 trust hierarchy):

- Every claim must be traceable to a tier 1 (csv), tier 2 (measured spectral feature), tier 3 (web finding with citation), or tier 4 (genre prior, structural label only) source. Phrasing must reflect the tier — see §2.5 allowed/forbidden examples.
- Every bar-level callout cites a specific timestamp (mm:ss) AND cites the panel + measurement that supports it ("per scrub-strip Panel 2: sub-band RMS jumps from 0.04 to 0.42 at 0:40").
- TL;DR must lead with csv-grounded track-level facts (BPM, key, energy, danceability, valence, instrumentalness as relevant to mood/structure) before any time-localized claim. When `tempo.agree_within_4bpm` is `false`, the disagreement is explained explicitly. When the librosa key disagrees with the csv key, the csv value is named as authoritative and the disagreement framed (often relative-major/minor adjacency on the Camelot wheel).
- Production-technique references link to `knowledge/genres/<slug>.md` or `knowledge/theory/<slug>.md` when applicable. Genre vocabulary may be used for structural labels ("kick-out break", "drop A → break → drop B"). Specific instrument or production-technique claims about *this track* require tier 2 measurement support.
- Web findings (tier 3) cited inline with `[<source domain>](<URL>) (accessed YYYY-MM-DD)`. When a web source contradicts measurement, both are reported and the discrepancy flagged.
- If `genre_page` is missing, TL;DR notes "no genre cheat sheet for <X>; writing from librosa features + csv profile" — gap is visible, not papered over.
- **Forbidden** per §2.5: cause-inference for energy ("the bass enters"), specific instrument identifications without measurement support ("vocal lead", "synth pad", "Roland kick"), un-measurable production-technique claims (octave doubling, specific reverb settings, vocal-formant processing, drum-fill identification).

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

**v1.1 — stems-pivot mode:**

When `web_findings.md` (per §3.10a) reports `stems_found: true` with verified stem URLs, the recipe authoring switches modes. Instead of "build a track that hits the csv profile + measured structure using genre conventions", the recipe becomes:

```markdown
---
slug: <slug>
recipe_for: <track>
target: Ableton Live 12 Lite (8 audio + 8 MIDI tracks, Simpler-only, 2 sends)
mode: stems-study   # vs the default "genre-rebuild"
generated_at: <iso>
---

# Recipe — study *<Track>* via its stems

> Stems located: <URL from web_findings.md, accessed YYYY-MM-DD>.
> Mode: stems-study (vs the default genre-rebuild). Steps focus on
> dissecting the actual stems and recording your observations, not
> programming new MIDI from scratch.

## Project setup
1. Set tempo to <csv_bpm> BPM. Set project key to <csv_camelot> (<csv_standard>).
2. Download the stems pack from <URL>. Drop the drum stem into Audio 1,
   bass stem into Audio 2, vocal stem into Audio 3, melodic stems into
   Audio 4-5 as you go.

## Drum stem study (Audio 1)
3. Solo the drum stem. Loop the drop section identified in teardown.md
   (<start>-<end>). Listen for ~5 cycles.
4. In a journal note (right-click the clip → Edit Info Text), record:
   what frequencies the kick occupies, whether the clap has reverb tail,
   how the hi-hat sits in the off-beats. Reference
   `knowledge/genres/<inferred>.md` for what to listen for.
5. ...

## Bass stem study (Audio 2)
N. Solo bass stem alongside the drum stem. ...

## Vocal stem study (Audio 3)
N. ...

## Melodic stems study (Audio 4-5)
N. ...

## Apply learnings
N. With those notes, sketch a new project that hits the same csv profile
   with your own samples. Keep the original stems-study project alongside
   for reference.
```

The genre-rebuild path remains the default. Stems-pivot is taken only when `web_findings.md` confirms verified stems.

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

v1.0 component layout (shipped — see git history for actual file list, which evolved during implementation):

```
.claude/skills/
└── teardown/
    └── SKILL.md            # the user-facing flow + artifact templates +
                            # narrative-authoring rules. Read by Claude on
                            # invocation; not code.

scripts/
├── teardown.py             # thin entrypoint shim (sys.path + teardown.cli.main())
├── teardown/
│   ├── __init__.py
│   ├── cli.py              # argparse + top-level orchestration
│   ├── models.py           # AnalysisResult dataclass and friends
│   ├── ytdlp.py            # python -m yt_dlp wrapper (search + download)
│   ├── analyze.py          # librosa orchestration → AnalysisResult
│   ├── envelope.py         # compose + write analysis.json
│   ├── key.py              # krumhansl-schmuckler key estimator + Camelot map
│   ├── plot.py             # scrub strip rendering with per-panel fallback
│   ├── csv_context.py      # tracks.csv row lookup by spotify_id
│   └── slug.py             # kebab-case derivation
├── tests/
│   ├── conftest.py         # session-scoped synthesized 126 BPM fixture
│   └── test_teardown_*.py  # one test file per backend module
├── README.md               # teardown section appended
└── pyproject.toml          # librosa, yt-dlp, matplotlib, soundfile deps
```

**v1.1 component delta (what changes):**

- `scripts/teardown/models.py` — extend `AnalysisResult` with new fields: `per_band_rms`, `hpss`, `spectral_centroid_hz`, `onset_density_per_bar`, `sidechain`. Each is its own typed nested structure (probably a small dataclass per group, all under the existing `AnalysisResult` umbrella).
- `scripts/teardown/analyze.py` — add the v1.1 pipeline steps (12–16 in §3.8). Each step lives in its own helper function for testability: `_per_band_rms`, `_hpss_split`, `_spectral_centroid`, `_onset_density_per_band`, `_sidechain_detection`. The top-level `analyze()` function calls them in sequence and assembles into the extended `AnalysisResult`.
- `scripts/teardown/envelope.py` — add serialization for the new fields. Schema bump `tool_version` to `"0.2.0"`.
- `scripts/teardown/plot.py` — change `_render_combined` from 4 panels to 6. Update `_render_per_panel` fallback to also produce 6 PNGs (`scrub-strip-1.png` … `scrub-strip-6.png`). The waveform / chroma / beat-grid panels are unchanged; the existing single RMS panel is replaced with the new per-band RMS panel; HPSS and centroid/density panels are inserted between RMS and chroma.
- `scripts/tests/test_teardown_per_band.py` — new test file: per-band RMS correctness on the fixture wav (sub-band should dominate the 65 Hz sine bass; air-band should be near-zero).
- `scripts/tests/test_teardown_hpss.py` — new test file: HPSS split correctness (the click metronome should land in percussive; the sustained sine bass should land in harmonic).
- `scripts/tests/test_teardown_centroid.py` — new test file: spectral centroid sanity (low for the bass-heavy fixture; doesn't crash on edge cases).
- `scripts/tests/test_teardown_onset_density.py` — new test file: onset density per bar (fixture has 4 clicks per bar at 126 BPM → expected onset count per bar in the appropriate band).
- `scripts/tests/test_teardown_sidechain.py` — new test file: sidechain detection on a synthesized fixture (a fixture with simulated kick + ducked bass should detect; a fixture with non-ducked bass should not detect).
- `scripts/tests/test_teardown_envelope.py` — extend with assertions for the new envelope fields.
- `scripts/tests/test_teardown_plot.py` — update for 6-panel layout; per-panel fallback now produces 6 PNGs.
- `scripts/tests/test_teardown_e2e.py` — extend asserts to validate the new analysis.json fields and the 6-panel scrub strip.
- `scripts/tests/conftest.py` — extend the fixture builder, OR add a second fixture (`teardown_fixture_sidechain_wav`) that simulates a sidechained bass for the sidechain detection tests.
- `.claude/skills/teardown/SKILL.md` — substantially rewritten authoring rules per §2.5 trust hierarchy; added §3.10a web-findings step in the flow; updated `recipe.md` template with stems-pivot mode.

**Not added in v1.1:** no new Python modules for web search. The web-findings step lives entirely in the skill layer (Claude using the `WebSearch` tool and writing `web_findings.md` via the `Write` tool). Keeps the deterministic CLI free of network-dependent behavior.

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

v1.1 update of the Teardowns section (replaces the v1.0 version):

```markdown
## Teardowns

The teardown pipeline is invoked via the project-scoped `/teardown` skill
at `.claude/skills/teardown/SKILL.md`. Both `/teardown <input>` and
"teardown this track: <input>" route through the same flow. Inputs:
YouTube URL, local file path, Spotify track ID, or free-text track name
(fuzzy-matched against `taste/tracks.csv`).

Per-teardown artifacts land in `teardowns/<slug>/`:
- `source.wav` (gitignored) — yt-dlp output or manually-dropped file
- `analysis.json` — librosa-derived numerical analysis (per-band RMS,
  HPSS, spectral centroid, onset density, sidechain detection)
- `scrub-strip.png` — 6-panel time-aligned visualization Claude reads
- `web_findings.md` — web-search snapshot (stems, breakdowns, credits)
- `teardown.md` — narrative ("what's happening when")
- `recipe.md` — numbered build steps targeting Ableton Live 12 Lite
  (or stems-study mode when web_findings.md surfaces verified stems)

**Trust hierarchy for narrative authoring** (per spec §2.5):
1. `taste/tracks.csv` (ReccoBeats) — authoritative for track-level facts
2. Measured spectral features — authoritative for time-localized claims
3. Web findings — supporting only, cited with source URL + access date
4. Genre/artist priors — background context, structural labels only

Forbidden: cause-inference for energy ("the bass enters"), specific
instrument identifications without measurement support ("vocal lead"),
un-measurable production-technique claims (octave doubling, specific
reverb settings).

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

v1.0 (shipped 2026-04-28):

- [x] `.claude/skills/teardown/SKILL.md` exists and is auto-discovered.
- [x] `scripts/teardown.py --check-deps` reports versions cleanly.
- [x] All v1.0 unit tests pass.
- [x] Synthetic-fixture e2e test passes.
- [x] End-to-end on John Summit — *crystallized (feat. Inéz)* — but the v1.0 narrative authoring exhibited a hallucination failure mode (see §2.4 reason). Drove the v1.1 amendment.

v1.1 verification gate (this amendment):

- [ ] `analysis.json` `tool_version` is `"0.2.0"` and contains all new top-level keys: `per_band_rms`, `hpss`, `spectral_centroid`, `onset_density`, `sidechain`.
- [ ] All v1.1 unit tests pass: per-band RMS sanity (sub-band dominates the 65 Hz fixture, air-band near-zero), HPSS split sanity (clicks land in percussive, sine in harmonic), spectral centroid doesn't crash, onset density per bar matches expectation on the fixture, sidechain detection fires correctly on the synthesized sidechain fixture and not on the unmodulated one.
- [ ] `scrub-strip.png` renders 6 panels at 16×18 (combined) OR 6 separate panel PNGs on fallback. Each panel reads cleanly: per-band RMS curves are color-distinguishable on log y-axis; HPSS panel shows harmonic + percussive curves clearly; centroid + onset density panel uses dual y-axes; chroma + beat grid unchanged from v1.0.
- [ ] `web_findings.md` exists in the verification-gate teardown's directory and is non-empty (or contains a clean "no results in this batch" note for searches that legitimately missed). Tracked in git.
- [ ] **End-to-end manual rerun** on John Summit — *crystallized (feat. Inéz)* (slug `john-summit-crystallized`, source.wav reused). Re-runs analysis (CLI), runs the new web-findings step, re-authors `teardown.md` and `recipe.md` under the new §2.5 trust hierarchy. **Beginner-comprehension check:** Destin reads `teardown.md` while listening to the actual track and confirms claims correspond to what's audible — the failure mode that drove this amendment must not recur. Specifically: no instrument-level claim ("vocal lead enters", "bass at X") that lacks a tier 2 measurement OR tier 3 web-citation backing it.
- [ ] If `web_findings.md.stems_found` is `true` for the verification track, `recipe.md` is in stems-pivot mode (per §3.12 v1.1 addition). If `false`, `recipe.md` is in genre-rebuild mode and the Splice/preset references trace exclusively to `knowledge/artists/john-summit.md`.
- [ ] `CLAUDE.md` Teardowns section is updated to the v1.1 version (per §3.16 above).
- [ ] `.claude/skills/teardown/SKILL.md` is rewritten to encode the §2.5 trust hierarchy, the §3.10a web-findings flow, and the §3.12 stems-pivot recipe mode.
- [ ] `scripts/README.md` Teardowns section notes the v1.1 schema bump (`tool_version: 0.2.0`) and the new analysis surface (per-band RMS / HPSS / centroid / onset density / sidechain detection).

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

**v1.1 implementation notes (additions):**

- **Per-band RMS implementation.** Single STFT on the loaded waveform, then sum the magnitude bins corresponding to each band's frequency range, then take RMS along the time axis. Reuse the same `hop_length=512` as the existing overall RMS so the output curves time-align with `energy.rms_values`. The "air" band has no upper cutoff (open-top above the Nyquist limit at sr=22050 → 11025 Hz upper bound effectively).
- **HPSS implementation.** `librosa.effects.hpss(y)` returns `(y_h, y_p)`. Compute RMS on each at `hop_length=512`. Cost is dominated by the internal STFT + median filter + ISTFT — ~5 s on a 4-min track on the user's hardware; not a UX problem given the existing 5-15 s analysis baseline.
- **Spectral centroid.** Single call: `librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=512)`. Returns shape `(1, n_frames)` — squeeze to 1-D. Cheap.
- **Onset density per band.** For each band, run `librosa.onset.onset_strength` on the band-filtered signal (cheaper) or on the band's STFT magnitude slice (cheaper still since we already have the STFT for per-band RMS). Then `librosa.onset.onset_detect`. Bucket the resulting onset frames into bars using `beats.beat_times_s` (each bar = consecutive 4 beats). Output is a list of `{bar_index, start_s, end_s, onsets_per_band: {<band>: count}}`. Same structure for every track regardless of length.
- **Sidechain detection.** Algorithm: (a) detect kick onsets via `librosa.onset.onset_detect` on the sub-band onset envelope (kicks dominate sub). (b) For each kick onset time `t_kick`, compute the bass-band RMS minimum within `[t_kick, t_kick + 100ms]`. (c) Compute the rolling local mean of bass-band RMS in a `[t_kick - 250ms, t_kick + 250ms]` window. (d) The dip depth in dB is `20 * log10(rolling_mean / dip_min)` (clamped at 0 if dip_min ≥ rolling_mean). (e) Aggregate across all kicks: `depth_db_mean`, `depth_db_p90`, `consistency_pct = 100 * (count of kicks with dip_db ≥ 3.0) / total kicks`. (f) `detected = depth_db_mean ≥ 3.0 AND consistency_pct ≥ 60.0`. The numerical thresholds are stored in the schema (`threshold_db_for_detection`, `threshold_consistency_for_detection`) so the detector's bar can be re-tuned without a schema bump.
- **Why no separate sidechain panel in the scrub strip.** The detection result is a small structured fact (boolean + a few numbers), not a time-series. Cite it in narrative; visualize the underlying bass-band-vs-kicks story via Panel 2 (per-band RMS) + Panel 6 (beat grid) read together.
- **Web search budget.** The default search batch (§2.6) is 5 searches. The skill should run them sequentially or with a small batch concurrency (e.g., 2–3 at a time via the WebSearch tool's natural sequential model). Total wall-clock for the web step: ~10–30 s on a typical run. The skill should not block the teardown if any individual search times out — record the timeout and proceed.
- **Crystallized rewrite.** The v1.0 verification-gate teardown at `teardowns/john-summit-crystallized/` (committed at `5b3ba2e`) is rewritten under v1.1: source.wav is reused (no re-download), analysis.json is regenerated by the upgraded analyzer, web_findings.md is created, scrub-strip.png is regenerated as 6-panel, teardown.md and recipe.md are re-authored from scratch under the §2.5 trust hierarchy. The v1.0 versions remain in git history as the "before" example.

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
- [x] **Verification gate concreteness:** §5 lists 14 specific v1.0 checks plus 8 v1.1 checks, including a named primary test track, file existence checks, schema validation, threshold checks, and a beginner-comprehension subjective gate. No gate is "TBD".

**v1.1 self-review additions (2026-04-29):**

- [x] **Failure mode driving the amendment is named.** §2.4 reason explicitly says: "the v1.0 verification-gate teardown for John Summit — *crystallized (feat. Inéz)* exposed a hallucination failure mode" and lists the specific Tier 3 violations from the v1.0 narrative (vocal lead, octave doubling, sidechained bass without measurement, reverb pre-delay automation, drum fills).
- [x] **Trust hierarchy is exhaustive.** §2.5 lists exactly four tiers, names each tier's authority and citation requirements, gives 7 allowed-example phrasings and 7 forbidden-example phrasings drawn directly from the v1.0 failure cases.
- [x] **Schema bump is signaled.** §3.9 names the schema version bump (`tool_version: 0.2.0`) and lists every new top-level key. Existing v1.0 keys are preserved exactly.
- [x] **Web findings boundary is clean.** §3.10a specifies that web search lives in the skill layer (not the CLI), `web_findings.md` is tracked in git, and the failure-handling posture (zero results, timeouts) is explicit. The CLI's contract is unchanged — it neither knows about nor depends on web search.
- [x] **Stems-pivot mode boundaries.** §3.12 v1.1 addition specifies the `mode: stems-study` frontmatter key, gives a complete template, and names the trigger condition (`web_findings.md.stems_found: true` AND a verified URL is present). The default genre-rebuild path is preserved.
- [x] **Implementation surface is delta-only.** §3.14 v1.1 addition lists exactly which Python modules and tests change, and explicitly states that no new modules are introduced for web search.
- [x] **Verification gate distinguishes v1.0 vs v1.1.** §5 marks v1.0 checkboxes as `[x]` complete and v1.1 checkboxes as `[ ]` pending. The crystallized rewrite is named as the verification driver.
- [x] **Spec lineage is preserved.** §2.4 names the v1.0 commit (`5b3ba2e`) so a reader can `git show` the prior version. The amendment is additive/replacing-in-place; no v1.0 sections are deleted (only updated).
