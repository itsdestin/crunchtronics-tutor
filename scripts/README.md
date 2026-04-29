# Crunchtronics Tutor — local CLI tools

Python 3.12 project under `uv`. Currently houses one tool:

- `enrich.py` — Audio Feature Enrichment for `taste/tracks.csv` (Subsystem #6).

Subsystem #8 (Teardown Pipeline) will reuse this same project shell.

## First-time setup

```bash
cd scripts
uv venv .venv --python 3.12
uv pip install -e ".[dev]"
```

## Running the enricher

From a Claude Code session, just say "enrich my tracks." Claude runs the script and surfaces the end-of-run summary.

To run it manually:

```bash
cd scripts
.venv/Scripts/python enrich.py
```

The script reads `taste/playlists.json` (produced by Subsystem #5 / the spotify-services plugin) and writes `taste/tracks.csv`. Default behavior is incremental — only fetches missing rows + retries misses older than 30 days.

### CLI flags

| Flag | Effect |
|---|---|
| (none) | Incremental: enrich rows not in csv + retry misses older than 30 days |
| `--retry-misses` | Skip TTL; retry every row with `source=miss:*` |
| `--force-all` | Rebuild tracks.csv from scratch |
| `--dry-run` | Print plan; no API calls |
| `--limit N` | Enrich only first N candidates (testing) |

## Enrichment service

### ReccoBeats (no setup)

Free, no API key required, accepts Spotify track IDs natively, returns the full Spotify-style audio-features vector. The script uses ReccoBeats for every track. Tracks ReccoBeats has no entry for are recorded as `source=miss:reccobeats` and not retried for 30 days.

A v1.0 GetSongBPM fallback was specified and integrated, then removed in v1.2 — see `docs/superpowers/specs/subsystems/06-audio-enrichment.md` §2.1 for the post-mortem.

## Tests

```bash
cd scripts
.venv/Scripts/python -m pytest -v
```

Real-API integration test (gated by env var):

```bash
cd scripts
SPOTIFY_E2E=1 .venv/Scripts/python -m pytest tests/test_real_api.py -v
```

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `ERROR: taste/playlists.json not found` | Subsystem #5 hasn't pulled yet. Ask Claude to "pull my Spotify data" or run the plugin's `export_all_playlists` tool. |
| `ReccoBeats rate-limited` | The script stops cleanly with partial progress preserved. Wait a few minutes; re-run. |
| Coverage suspiciously low (<70% from ReccoBeats) | Check that you're enriching real Spotify track IDs (not local files). Open `taste/tracks.csv` and look at the `source` column distribution. |
| `tracks.csv` got corrupted somehow | The script auto-backs-up to `tracks.csv.corrupt-<timestamp>` and rebuilds. Check for a backup file in `taste/`. |

## Teardowns (Subsystem #8)

`scripts/teardown.py` — analysis CLI invoked by the `/teardown` skill.

**Schema version:** `analysis.json.tool_version` is `"0.2.0"` as of v1.1 (2026-04-29). v0.2.0 adds these top-level keys to the v1.0 envelope: `per_band_rms` (5 EDM-tuned bands: sub 20-60Hz / bass 60-250 / low_mids 250-2k / highs 2k-8k / air 8k+), `hpss` (harmonic + percussive RMS curves), `spectral_centroid`, `onset_density` (per band per bar), `sidechain` (kick-aligned bass dip detection with measured dB depth + consistency %). The scrub strip is now 6 panels (or 6 separate PNGs on the per-panel fallback). See `docs/superpowers/specs/subsystems/08-teardown-pipeline.md` §3.9 for the full schema.

### Pre-requisites

- ffmpeg on PATH. Install:
  ```bash
  winget install Gyan.FFmpeg
  ```
  Verify with:
  ```bash
  cd scripts && .venv/Scripts/python teardown.py --check-deps
  ```

### Running manually

Normally invoked through the `/teardown` skill (see `.claude/skills/teardown/`).
Manual usage:

```bash
cd scripts
.venv/Scripts/python teardown.py --slug john-summit-where-you-are \
    --url https://www.youtube.com/watch?v=... \
    --csv-context 5n4erMKwoH0Bky4VKZWWCQ
```

CLI flags:

| Flag | Effect |
|---|---|
| `--slug <name>` | Output directory under `teardowns/`. Required. |
| `--url <url>` | Audio source URL (yt-dlp downloads it). Mutually exclusive with `--local`. |
| `--local <path>` | Use an existing local audio file. Mutually exclusive with `--url`. |
| `--csv-context <spotify-id>` | Embed the matching `taste/tracks.csv` row in `analysis.json`. |
| `--force` | Overwrite an existing `teardowns/<slug>/`. |
| `--check-deps` | Print versions of ffmpeg / librosa / yt-dlp / matplotlib and exit. |
| `--dry-run` | Print the planned operations and exit. |

### Tests

Default suite (no real audio downloads):

```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_*.py -v
```

End-to-end on synthetic fixture (slow; no network):

```bash
cd scripts && TEARDOWN_E2E=1 .venv/Scripts/python -m pytest tests/test_teardown_e2e.py -v
```

### Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `ERROR: ffmpeg not found on PATH` | `winget install Gyan.FFmpeg`, restart shell, re-run. |
| `ERROR: yt-dlp download failed: ... 403` | Video is age-gated or geo-blocked. Drop the audio file at `teardowns/<slug>/source.wav` and re-invoke with `--local`. |
| `ERROR: audio is suspiciously short` | Partial / DRM-blocked download. Try a different URL. |
| Scrub strip ships as 4 separate `scrub-strip-N.png` files | Combined-axis render failed (Windows matplotlib quirk). Functional fallback; Claude reads them individually. |
| yt-dlp itself feels stale | Bump `yt-dlp` in `pyproject.toml` to the latest release; re-run `uv sync --extra dev`. |
