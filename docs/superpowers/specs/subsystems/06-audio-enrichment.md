# Subsystem #6 — Audio Feature Enrichment

- **Date:** 2026-04-26
- **Status:** Shipped 2026-04-26 (Session C; plan at `docs/superpowers/plans/2026-04-26-session-c-data-pull.md`; first real run produced 73.2% ReccoBeats coverage on the EDM playlist)
- **Master spec:** `docs/superpowers/specs/2026-04-26-master-architecture.md`
- **Master-spec sections referenced:** §3.1 (Spotify deprecation context — the reason this subsystem exists), §5.1 #6 (one-liner contract), §6 (data flow), §7.2 (`taste/tracks.csv` shape — **extended** by this spec; see §2), §8 (refresh cadence: incremental, rate-limit aware), §11 default decision #2 (enrichment service — **overridden** by this spec; see §2)
- **Companion spec:** `docs/superpowers/specs/subsystems/05-spotify-integration.md` (this subsystem's input producer)
- **Session:** C (combined with #5)
- **Build order:** Second subsystem in Session C; depends on #5 having produced a populated `taste/playlists.json`
- **Depends on:**
  - Subsystem #5 (Spotify Integration — produces `taste/playlists.json`)
  - The `spotify-services` plugin (transitively, for #5's pull mechanism)
- **Blocks:**
  - Subsystem #7 (Taste Profile — reads `taste/tracks.csv`)
  - Subsystem #8 (Teardown Pipeline — reads `taste/tracks.csv` for track selection metadata)

## 1. One-liner contract

Reads `taste/playlists.json`, deduplicates tracks, queries third-party services to fill in BPM, key, and Spotify-style audio-feature dimensions per track, and incrementally maintains `taste/tracks.csv`. Owns the file and its schema. Service-swappable via the `source` column.

## 2. Master-spec overrides

This subsystem overrides two default decisions from the master spec:

### 2.1 Override of §11 #2 — Enrichment service

- **Original default:** GetSongBPM as primary.
- **Overridden to:** **ReccoBeats** is the sole enrichment service.
- **Reason:** ReccoBeats requires no API key, looks up by Spotify track ID (exact, no fuzzy artist+title matching), returns the Spotify-style audio-features vector (not just BPM + key), and has no attribution / backlink terms of use. The `source` column from §7.2 is the swap mechanism: a future service change can be added without disturbing already-enriched rows.
- **Architectural enabler:** `taste/playlists.json` from Subsystem #5 contains Spotify track IDs verbatim. ReccoBeats accepts these IDs as input.
- **API shape (verified against the live API on 2026-04-26 by Task 2.2):** ReccoBeats requires a **two-step lookup** — single-track ID-resolution doesn't accept Spotify IDs at the audio-features endpoint. Step 1: `GET /v1/track?ids=<spotify_id_csv>` resolves Spotify IDs to ReccoBeats internal UUIDs, returning a `content[]` array of `{id: <uuid>, href: <spotify_url>, isrc, ...}` for tracks they have (empty array for unknown IDs — this is also the "not in DB" signal, NOT an HTTP 404). Step 2: `GET /v1/track/<uuid>/audio-features` returns the audio-features payload using the UUID from step 1. The single-track client function (`fetch(spotify_id)`) hides this two-step pattern behind one call; the orchestrator's per-track loop is unchanged.
- **v1.2 revision (2026-04-29):** GetSongBPM was originally specified as a fallback. After integration, two findings led to its removal: (a) GetSongBPM's API now sits behind a Cloudflare managed-challenge gate that rejects all non-browser HTTP clients (verified across User-Agent rotation, curl_cffi Chrome120 TLS impersonation, Origin/Referer spoofing, and cloudscraper); (b) when fetched via Playwright + stealth as a workaround, the per-track hit rate on this catalog was 1/42 — GetSongBPM's database is light on niche/newer EDM. The cost of maintaining a Playwright-backed fallback was poor for the marginal coverage. The fallback path, the GetSongBPM client module, the secrets file slot, and the public-backlink obligation are all removed. A `manual` source value remains documented in §3.4.1 to record any data point the maintainer chooses to enter by hand.

### 2.2 Override of §7.2 — `tracks.csv` schema extension

- **Original column list:** `spotify_id, isrc, artist, title, album, duration_s, bpm, key_camelot, key_standard, energy, danceability, genre, source, fetched_at`.
- **Extended to:** original columns plus seven new audio-feature columns (`mode`, `valence`, `acousticness`, `instrumentalness`, `liveness`, `loudness`, `speechiness`) and one new credit column (`artists`). See §3.4 for the full ordered schema.
- **v1.1 revision (2026-04-29):** `time_signature` was dropped (always empty — ReccoBeats does not return it and no second backend filled it). `artists` was added (semicolon-delimited full-credit list) after a data audit showed 56% of pulled tracks had multi-artist credits and the original "primary only" rule mis-classified anchor artists. The `artist` column is retained as the primary credit.
- **Reason:** ReccoBeats returns the full vector for free in every response; capturing it now is cheap, and skipping it would force a re-enrichment of every track later when Subsystem #7 (Taste Profile) wants richer signal. Master spec §7.2 explicitly permits downstream subsystems to extend the column list.

When the master spec is next revised, both overrides should be reflected (or kept as the documented v1 defaults with this subsystem documenting the deviations).

## 3. What this subsystem does

### 3.1 Owns `taste/tracks.csv`

The file's existence, location, schema, and update lifecycle are this subsystem's responsibility. Schema in §3.4. The CSV is committed to git as a snapshot.

### 3.2 Implements an incremental enrichment script under `scripts/`

Single Python entrypoint: `scripts/enrich.py`. Run by Claude in-session when Destin asks ("enrich my tracks" or similar) — see §3.6. Default behavior is incremental: only enriches rows missing data plus misses older than 30 days. CLI flags allow forced / partial runs (§3.5).

### 3.3 Data flow

```
taste/playlists.json (raw Spotify shape, written by plugin)
    │
    ▼
[1] Load + flatten: walk every playlist, collect every track item
[2] Filter: drop items with no Spotify track ID (local files, podcasts, episodes)
[3] Dedupe by spotify_id (a track in 5 playlists = 1 row)
[4] Read taste/tracks.csv if present
[5] Build "needs enrichment" set:
      - rows not in csv yet
      - rows where source starts with "miss:" AND fetched_at older than 30 days
[6] For each needs-enrichment row:
      a. Try ReccoBeats by Spotify track ID
      b. On 200 → row source="reccobeats" (full audio-features vector)
      c. On empty content (not in DB) → row source="miss:reccobeats"
      d. Honor 429 Retry-After; client-side throttle ~1 req/sec
[7] Merge into taste/tracks.csv. tracks.csv is CUMULATIVE: existing rows are
    preserved even if their source playlist is no longer in the current
    playlists.json (which can happen since #5 pulls are selective and the
    user's selection can change between runs). Only --force-all rebuilds
    from scratch.
[8] Print end-of-run summary:
      - X tracks total / Y newly enriched / Z still missed
```

### 3.4 `taste/tracks.csv` schema (extended per §2.2)

Column order — fixed:

```
spotify_id, isrc, artist, artists, title, album, duration_s,
bpm, key_camelot, key_standard, mode,
energy, danceability, valence, acousticness, instrumentalness,
liveness, loudness, speechiness,
genre, source, fetched_at
```

Field semantics:

- `spotify_id` — Spotify track ID (Base-62). Always present (the dedup key).
- `isrc` — International Standard Recording Code, copied from the Spotify track payload when present. Empty if absent.
- `artist` — primary artist name (first artist in the Spotify track payload). Retained for use as a stable filename/slug seed (teardowns) and as a "lead credit" reference; consumers that need full credits read `artists`.
- `artists` — semicolon-delimited list of all credited artist names from the Spotify track payload, in payload order. Includes the primary. Example: `Subtronics;Wooli`. This is the source of truth for credit-counting (top-artist aggregation, artist-page eligibility). Master spec §7.2 explicitly permits column extension; this column was added in v1.1 (2026-04-29) after a data audit found 56% of pulled tracks had multi-artist credits and counting only the primary mis-classified anchor artists (e.g., Wooli).
- `title`, `album` — strings copied from the Spotify track payload.
- `duration_s` — integer seconds, computed from the Spotify `duration_ms`.
- `bpm` — float, tempo in beats per minute. Two decimals.
- `key_camelot` — string in Camelot notation (e.g., `8B`, `12A`). Computed from `key_standard` via the lookup in §3.7.
- `key_standard` — string like `C major`, `F# minor`. Derived from ReccoBeats `key` (0–11) + `mode` (0/1).
- `mode` — integer 0 (minor) or 1 (major). From ReccoBeats only.
- `energy`, `danceability`, `valence`, `acousticness`, `instrumentalness`, `liveness`, `speechiness` — floats in `[0, 1]`. From ReccoBeats only.
- `loudness` — float in dB (typically `-60` to `0`). From ReccoBeats only.
- `genre` — string. **Empty for v1** — neither service provides it. See §6 for a follow-up note on filling this column from Spotify's artist-genres endpoint or last.fm in a future iteration.
- `source` — string with one of the values defined in §3.4.1 below.
- `fetched_at` — ISO 8601 UTC timestamp. Set on every row, including miss rows, so the 30-day TTL works.

Empty cells are valid (per master spec §7.2: "enrichment is best-effort").

#### 3.4.1 `source` column value semantics

Track-metadata columns (`spotify_id`, `isrc`, `artist`, `artists`, `title`, `album`, `duration_s`) and bookkeeping columns (`source`, `fetched_at`) are populated on **every** row, sourced from `taste/playlists.json`. The audio-feature columns (`bpm`, `key_*`, `mode`, `energy`, …, `speechiness`) vary by `source`:

| Value | Meaning | Audio-feature columns populated |
|---|---|---|
| `reccobeats` | ReccoBeats returned a hit. | All of them (full audio-features vector). |
| `manual` | A maintainer entered values by hand (rare). | Whatever the maintainer filled in — typically `bpm`, `key_camelot`, `key_standard`, `mode`. |
| `miss:reccobeats` | ReccoBeats had no entry for this Spotify ID. | None. |

A reader can disambiguate empty cells by inspecting `source`: empty audio-feature cells in a `source = reccobeats` row would be a bug; empty cells in `source = manual` rows mean the maintainer didn't fill them in; empty cells in `miss:*` rows mean no service had data.

Future services can extend the value space (e.g., `last.fm`, `acousticbrainz`) without schema changes.

### 3.5 CLI flags

Default: incremental + 30-day TTL.

| Flag | Effect |
|---|---|
| (none) | Incremental: enrich rows not in csv + retry misses with `fetched_at` older than 30 days |
| `--retry-misses` | Skip TTL check; retry every row whose source starts with `miss:` |
| `--force-all` | Re-enrich every track from scratch; rebuild `tracks.csv` from `playlists.json` |
| `--dry-run` | Print the enrichment plan; make no API calls |
| `--limit N` | Enrich only the first N candidates (testing) |

### 3.6 Invocation pattern (Claude-mediated, not slash-command)

`CLAUDE.md` documents the conversational trigger: when Destin says "enrich my tracks" (or similar), Claude runs `python scripts/enrich.py` from the project root via Bash and surfaces the end-of-run summary verbatim. No slash command, no `/schedule` entry. This mirrors the pull-Spotify-data pattern in Subsystem #5 (Claude-invoked plugin tool).

If Destin wants a slash command later, it's an additive layer on top of the same script — no restructuring.

### 3.7 Camelot lookup

24 entries (12 keys × 2 modes). Deterministic, no theory computation:

```
C major   = 8B    A minor   = 8A
G major   = 9B    E minor   = 9A
D major   = 10B   B minor   = 10A
A major   = 11B   F# minor  = 11A
E major   = 12B   C# minor  = 12A
B major   = 1B    G# minor  = 1A
F# major  = 2B    D# minor  = 2A
Db major  = 3B    Bb minor  = 3A
Ab major  = 4B    F minor   = 4A
Eb major  = 5B    C minor   = 5A
Bb major  = 6B    G minor   = 6A
F major   = 7B    D minor   = 7A
```

Lives at `scripts/enrich/camelot.py` as a `dict[(key:int, mode:int), str]` keyed by the ReccoBeats integer encoding (0=C, 1=C#, …, 11=B; 0=minor, 1=major) and a parallel `dict[str, str]` keyed by the human-readable string for GetSongBPM compatibility.

### 3.8 Component layout

```
scripts/
├── enrich.py              # main entrypoint (CLI parsing, top-level flow)
├── enrich/
│   ├── __init__.py
│   ├── reccobeats.py      # ReccoBeats client (one function: enrich(spotify_id) -> EnrichmentResult | None)
│   ├── camelot.py         # 24-entry lookup
│   ├── playlists_loader.py  # parse playlists.json → list of deduped TrackRecord
│   └── csv_writer.py      # incremental tracks.csv merge logic
├── README.md              # how to run; troubleshooting
├── pyproject.toml         # uv-managed: requests, python-dateutil; dev: pytest
└── .python-version        # 3.12
```

**Service-client interface contract:** the backend module exposes one function returning a uniform `EnrichmentResult | None` dataclass (with all audio-feature fields as `Optional[float]`). Returns `None` on miss; raises a service-specific exception on transient errors (caller handles 429 retry, exponential backoff). Adding a second service later = one more file + a fallback branch in `cli.py`.

### 3.9 Error handling

| Failure | Behavior |
|---|---|
| ReccoBeats empty content (track not in DB) | Expected. Recorded as `miss:reccobeats`. |
| ReccoBeats 429 | Honor `Retry-After` header; back off and retry once. If second 429, surface a clear error and stop the run (better to resume tomorrow than burn the IP). |
| ReccoBeats 5xx / network | Exponential backoff: 3 attempts at 1s, 4s, 16s; then surface and stop. |
| `playlists.json` missing | Clear error: "Run /pull-spotify-data first (or ask me to pull it)." Exit non-zero. |
| `tracks.csv` malformed | Back up to `tracks.csv.corrupt-<UTC-timestamp>`, write fresh from `playlists.json`. Log the backup path. |
| ReccoBeats sustained outage | Stop the run cleanly; don't write a partial csv that drops rows. |

### 3.10 `CLAUDE.md` edits (the #6 section)

```markdown
## Audio enrichment
When Destin says "enrich my tracks" (or similar), run
`python scripts/enrich.py` from project root and surface the end-of-run
summary verbatim.

The script reads `taste/playlists.json` and writes `taste/tracks.csv`.
Incremental by default — only fetches missing rows + retries misses
older than 30 days. Flags: `--retry-misses`, `--force-all`, `--dry-run`,
`--limit N`. Service: ReccoBeats only (no API key required).
```

## 4. What this subsystem must NOT do

- **No Spotify-API calls.** All Spotify access goes through Subsystem #5 / the `spotify-services` plugin. This subsystem only reads the JSON file the plugin produced.
- **No transformation of `taste/playlists.json`.** Read-only. The plugin owns its production.
- **No writing of `taste/profile.md`.** That's Subsystem #7.
- **No `/schedule` entry.** Pulls and enrichment are on-demand only (mirrors §5's override of master spec §11 #12).
- **No use of Spotify's `audio-features` or `audio-analysis` endpoints** (deprecated for new apps per master spec §3.1; will return 403). All audio characterization comes from the third-party services.
- **No embedding of API keys in code.** ReccoBeats requires no key, so this subsystem holds no secrets at all.
- **No fabricated data.** When a service has no result, the row's audio-feature cells stay empty and `source` records the miss. Do not interpolate, guess, or pull from a different track.
- **No silent overwrites.** A row already populated with `source=reccobeats` is not re-enriched unless `--force-all` is passed.

## 5. Verification gate

Before declaring this subsystem complete:

- [ ] `scripts/enrich.py` exists and runs end-to-end on Destin's real `taste/playlists.json` (produced by Subsystem #5).
- [ ] `taste/tracks.csv` exists, populated with real data, and matches the schema in §3.4 exactly (column order, column count).
- [ ] At least 70% of deduped tracks have `source = "reccobeats"` (sanity check on coverage; if dramatically lower, investigate before declaring done).
- [ ] Re-running `enrich.py` immediately after a successful run is a no-op (incremental behavior verified).
- [ ] Re-running with `--retry-misses` attempts only `miss:*` rows.
- [ ] Camelot column populated correctly for at least 5 sampled rows (manual check against a reference table).
- [ ] `scripts/README.md` documents: how to run; troubleshooting for common errors.
- [ ] `CLAUDE.md` has the §3.10 section added.

## 6. Implementation notes

- **Python environment.** Sets the `scripts/` Python convention for the tutor repo; Subsystem #8 (Teardown Pipeline) will reuse the same venv. Use `uv` for environment management to match the `spotify-services` plugin's precedent.
- **Local files / podcasts in playlists.** Spotify allows users to add local-file uploads (no `id`) and podcast / episode items (`type != "track"`) to playlists. The dedupe step skips these silently and reports the count in the end-of-run summary so Destin sees they exist but understands they can't be enriched.
- **ReccoBeats track-ID format.** ReccoBeats accepts both its own UUID-based IDs and Spotify Base-62 IDs. We always use the Spotify ID — no extra lookup hop.
- **Genre column for v1.** Empty. A follow-up improvement could fill it from Spotify's `Get Artist` endpoint (returns artist-level genres), called via the `spotify-services` plugin. Adding this is a non-disruptive single-column backfill — it doesn't require re-running ReccoBeats. Defer until Subsystem #7 explicitly needs it.
- **Rate-limit posture.** ReccoBeats publishes no numeric rate limit but returns 429 on overage. We default to a polite ~1 req/sec client-side throttle. If a real run reveals headroom, dial up.
- **Test fixture.** Commit a small `scripts/tests/fixtures/playlists-mini.json` (5 tracks: 4 known-popular hits, 1 deliberately obscure) for fast unit / mocked-integration tests. The real-API smoke test uses the same fixture but with `SPOTIFY_E2E=1`.
- **CSV writing posture.** Use the stdlib `csv` module — quoting set to QUOTE_MINIMAL, line terminator forced to `\n`. No pandas dependency for v1; the dataset stays small enough that pandas is overhead.

## 7. Self-review checklist

- [x] **Placeholders / TBDs:** none. All field semantics, error behaviors, and overrides are specified.
- [x] **Internal consistency:** §3.3 data flow, §3.4 schema, §3.4.1 source values, §3.5 CLI flags, §3.9 error handling all describe the same incremental + TTL + fallback-chain system. The `genre` column is consistently described as v1-empty in §3.4, §6, and (by absence) the verification gate.
- [x] **Scope:** narrowly bounded to producing `taste/tracks.csv` from `taste/playlists.json`. Out-of-scope items in §4. No drift into profile-writing, taste-narrative generation, teardown, or curriculum.
- [x] **Ambiguity:** the fallback chain (ReccoBeats → GetSongBPM → miss) is explicit; the TTL semantics (30 days, applies only to `miss:*` rows) is explicit; the exact CLI flag behaviors are tabulated.
- [x] **Master-spec relationship:** §2 explicitly enumerates the two overrides (§11 #2, §7.2) and the reasons. §1 ties this subsystem's contract to master spec §3.1 (deprecation context), §5.1 #6, §6 (data flow), §7.2 (extended schema).
- [x] **Plugin-side boundary:** §4 prohibits any Spotify-API code; §3.3 only consumes the file the plugin writes.
- [x] **Subsystem #5 boundary:** clean — this spec doesn't touch `playlists.json` writing or pulling, only reading. The §5 spec already declares ownership of the file.
