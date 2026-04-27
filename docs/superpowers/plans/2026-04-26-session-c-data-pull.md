# Session C — Data Pull Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Subsystem #5 (Spotify Integration as plugin-consumer) and Subsystem #6 (Audio Feature Enrichment) end-to-end so that `taste/playlists.json` and `taste/tracks.csv` are populated with Destin's real Spotify data and ReccoBeats audio features.

**Architecture:** Phase 1 is documentation-only — declares the `spotify-services` plugin dependency in CLAUDE.md and runs the plugin's `export_all_playlists` tool once. Phase 2 builds a Python CLI (`scripts/enrich.py`) under a new `scripts/` Python project that reads `taste/playlists.json`, dedupes tracks, queries ReccoBeats (primary, no auth) by Spotify track ID for the full audio-features vector, falls back to GetSongBPM (artist+title, optional API key) on miss, writes/updates `taste/tracks.csv` incrementally with a 30-day TTL on miss retries.

**Tech Stack:** Python 3.12, `uv` for environment management, `requests` for HTTP, stdlib `csv` for output, `pytest` for tests. No pandas.

**Specs this plan implements:**
- `docs/superpowers/specs/subsystems/05-spotify-integration.md`
- `docs/superpowers/specs/subsystems/06-audio-enrichment.md`
- Master spec: `docs/superpowers/specs/2026-04-26-master-architecture.md` (overrides documented in §2 of each subsystem spec)

**Build order:** Phase 1 (#5) before Phase 2 (#6). Phase 2 cannot start without `taste/playlists.json` populated by Phase 1.

---

## Phase 1 — Subsystem #5 (Spotify Integration as plugin-consumer)

Estimated time: ~30 minutes total. The plugin already ships; this phase declares the dependency in CLAUDE.md and runs one real pull.

### Task 1.1: Verify the plugin is installed and authenticated

**Files:** none (verification only)

- [ ] **Step 1: Run the plugin's smoke test**

```bash
bash ~/.claude/plugins/marketplaces/youcoded/plugins/spotify-services/setup/smoke-test.sh
```

Expected output:
```
  ✓ Authenticated as <name>
  ✓ Local backend (windows): <state>
```

If authentication fails, run `/spotify-services-setup` first and repeat. If it passes, proceed.

### Task 1.2: Add the Spotify-data section to project CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (append a new top-level section after "Pointers")

- [ ] **Step 1: Append the new section to CLAUDE.md**

Add this content at the end of `CLAUDE.md`:

```markdown

## Spotify data

This project depends on the `spotify-services` marketplace plugin. If it
isn't installed, run `/spotify-services-setup`.

Pulls are **selective with persisted choice**: Destin picks playlists once,
the choice is saved at `taste/.playlist-selection.json`, subsequent pulls
re-use it silently.

When Destin says "pull my Spotify data" (or similar):

1. Read `taste/.playlist-selection.json` if it exists.
2. **If it exists AND Destin did not say "fresh" / "reselect" / "pick again":**
   - Use the saved playlist IDs.
   - Tell Destin: *"Pulling your saved selection: <names>. Say 'pull my Spotify data fresh' to re-pick."*
3. **Otherwise:**
   1. Invoke the plugin's `mcp__spotify-services__playlists_list_mine` tool with `all=true` to get every playlist.
   2. Show Destin a numbered list with playlist names and track counts.
   3. Ask which playlists to include (number, name, comma-separated, or "all").
   4. Save the chosen playlist IDs + names to `taste/.playlist-selection.json`:
      ```json
      {
        "selected_at": "<UTC ISO timestamp>",
        "playlists": [{"id": "...", "name": "..."}]
      }
      ```
4. For each selected playlist ID, invoke `mcp__spotify-services__playlists_get_items` with `all=true` to get its tracks.
5. Assemble the per-playlist responses into `taste/playlists.json` matching master spec §7.1:
   ```json
   {
     "user_id": "<from playlists_list_mine response or user_profile call>",
     "fetched_at": "<UTC ISO timestamp>",
     "playlists": [{"id": "...", "name": "...", "tracks": [...]}]
   }
   ```
6. Report the playlist count, total track count, and any errors.

**Do NOT use `export_all_playlists`** — it dumps the entire library and bypasses selection.

Pull cadence is **on-demand only** (overrides master spec §11 #12 — no
`/schedule` entry). Taste evolves slowly; manual pulls are the right cadence.

Both `taste/playlists.json` and `taste/.playlist-selection.json` are committed
to git as snapshots. If `playlists.json` grows past ~5 MB it'll move to
`.gitignore` (the selection file stays tracked regardless).
```

- [ ] **Step 2: Verify the section reads cleanly in context**

Re-read `CLAUDE.md` end-to-end to make sure the new section flows after "Pointers" and doesn't duplicate or contradict anything earlier.

### Task 1.3: Walk Destin through the playlist picker and pull selected playlists

**Files:**
- Create: `taste/.playlist-selection.json`
- Create: `taste/playlists.json`

This task is interactive. The first run is the "pick playlists" path; subsequent runs use the saved selection. We're doing the first run here.

- [ ] **Step 1: List Destin's playlists**

Invoke `mcp__spotify-services__playlists_list_mine` with `all=true`. Capture the full list (id + name + track count per playlist).

- [ ] **Step 2: Show Destin the list and ask which to include**

Present a numbered list to Destin:

```
You have N playlists on Spotify:

  1. Bangers (47 tracks)
  2. Late-night drives (89 tracks)
  3. Workout (122 tracks)
  ...

Which would you like to pull for the tutor? (number, name, comma-separated list, or "all")
```

Wait for his answer. Resolve to a list of `{id, name}` records.

- [ ] **Step 3: Save the selection**

Write `taste/.playlist-selection.json`:

```json
{
  "selected_at": "<UTC ISO timestamp from datetime.now(timezone.utc).isoformat() with Z suffix>",
  "playlists": [
    {"id": "<playlist_id>", "name": "<playlist_name>"}
  ]
}
```

- [ ] **Step 4: Pull each selected playlist's tracks**

For each entry in `selection.playlists`, invoke `mcp__spotify-services__playlists_get_items` with the playlist ID and `all=true`. Collect the responses.

- [ ] **Step 5: Assemble `taste/playlists.json`**

Write `taste/playlists.json` matching master spec §7.1:

```json
{
  "user_id": "<destin's spotify user id>",
  "fetched_at": "<UTC ISO timestamp>",
  "playlists": [
    {
      "id": "<playlist_id>",
      "name": "<playlist_name>",
      "tracks": [<verbatim from playlists_get_items response>]
    }
  ]
}
```

If `user_id` isn't returned by the playlist tools, call `mcp__spotify-services__user_profile` once to get it.

- [ ] **Step 6: Verify schema and selection consistency**

```bash
python -c "
import json
with open('taste/playlists.json') as f:
    data = json.load(f)
with open('taste/.playlist-selection.json') as f:
    selection = json.load(f)

assert 'user_id' in data, 'missing user_id'
assert 'fetched_at' in data, 'missing fetched_at'
assert 'playlists' in data, 'missing playlists'
assert isinstance(data['playlists'], list), 'playlists is not a list'
assert len(data['playlists']) > 0, 'playlists is empty'

selected_ids = {p['id'] for p in selection['playlists']}
pulled_ids = {p['id'] for p in data['playlists']}
assert selected_ids == pulled_ids, f'selection/pull mismatch: in selection but not pulled: {selected_ids - pulled_ids}; pulled but not selected: {pulled_ids - selected_ids}'

total_tracks = sum(len(p.get('tracks', [])) for p in data['playlists'])
print(f'OK: user_id={data[\"user_id\"]}, playlists={len(data[\"playlists\"])}, tracks={total_tracks}')
"
```

Expected: prints `OK: user_id=..., playlists=N, tracks=M` where N matches the selection size and M >= 1.

If any assertion fails, investigate before proceeding to Phase 2. Common cause: token expiry — fix with `/spotify-services-reauth`.

### Task 1.4: Commit Phase 1

**Files:**
- Modify: `CLAUDE.md`
- Create: `taste/playlists.json`
- Create: `taste/.playlist-selection.json`

- [ ] **Step 1: Stage the changes**

```bash
git add CLAUDE.md taste/playlists.json taste/.playlist-selection.json
git status
```

- [ ] **Step 2: Commit**

```bash
git commit -m "$(cat <<'EOF'
feat(taste): subsystem #5 — selective spotify pull via spotify-services plugin

Adds the Spotify-data section to CLAUDE.md describing the
selective-with-persisted-choice pull workflow, runs the first
playlist pick, and ships the resulting taste/playlists.json plus the
saved taste/.playlist-selection.json.

Overrides master spec §11 #12: pull cadence is on-demand only,
no /schedule entry. Selection persists across pulls; "fresh"/--reselect
to re-pick.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Phase 1 Verification Gate

Before starting Phase 2:

- [ ] `CLAUDE.md` has the `## Spotify data` section with the selective-pull workflow
- [ ] `taste/.playlist-selection.json` exists with at least one playlist chosen
- [ ] `taste/playlists.json` exists, valid JSON, schema-correct, non-empty playlists, IDs consistent with the selection file
- [ ] No `export_all_playlists` invocation appears anywhere in the workflow (check CLAUDE.md doesn't mention it as a step)
- [ ] No Spotify-API code added to this repo: `grep -r "spotipy" scripts/ 2>/dev/null` returns nothing
- [ ] Phase 1 commit on local master

---

## Phase 2 — Subsystem #6 (Audio Feature Enrichment)

This phase builds the Python project. We follow strict TDD: every task starts with a failing test.

### Task 2.1: Bootstrap the Python project under `scripts/`

**Files:**
- Create: `scripts/.python-version`
- Create: `scripts/pyproject.toml`
- Create: `scripts/enrich/__init__.py`
- Modify: `.gitignore` (add Python venv + cache patterns; some may already exist)

- [ ] **Step 1: Pin Python version**

Create `scripts/.python-version`:

```
3.12
```

- [ ] **Step 2: Create the pyproject.toml**

Create `scripts/pyproject.toml`:

```toml
[project]
name = "crunchtronics-tutor-scripts"
version = "0.1.0"
description = "Local CLI tools for the Crunchtronics Tutor project."
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31",
    "python-dateutil>=2.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-mock>=3.12",
    "responses>=0.25",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["enrich"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-ra -q"
```

- [ ] **Step 3: Create the package init**

Create `scripts/enrich/__init__.py`:

```python
"""Audio feature enrichment for taste/tracks.csv."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Verify .gitignore covers Python artifacts**

Read `.gitignore` and confirm the following patterns are present (add any that are missing):

```
scripts/.venv/
scripts/__pycache__/
scripts/**/__pycache__/
scripts/.pytest_cache/
scripts/*.egg-info/
```

- [ ] **Step 5: Create the venv with uv**

```bash
cd scripts
uv venv .venv --python 3.12
uv pip install -e ".[dev]"
cd ..
```

Expected: venv created at `scripts/.venv/`; `pytest` available inside it.

- [ ] **Step 6: Verify pytest runs (with no tests yet)**

```bash
cd scripts
.venv/Scripts/python -m pytest --collect-only
cd ..
```

Expected: `no tests ran` (or similar) — confirms pytest is wired up.

- [ ] **Step 7: Commit**

```bash
git add scripts/.python-version scripts/pyproject.toml scripts/enrich/__init__.py .gitignore
git commit -m "$(cat <<'EOF'
chore(scripts): bootstrap Python 3.12 project for enrichment

uv-managed venv, requests + python-dateutil runtime deps, pytest +
responses for tests. Sets the precedent for scripts/ Python projects;
subsystem #8 will reuse this structure.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.2: Capture a real ReccoBeats response as a test fixture

This task is a research step — we don't know the exact ReccoBeats response field names from docs alone. We capture one real response so the parser is built against truth, not guessed shapes.

**Files:**
- Create: `scripts/tests/__init__.py`
- Create: `scripts/tests/fixtures/reccobeats-track-hit.json`
- Create: `scripts/tests/fixtures/reccobeats-track-404.json` (synthesized)

- [ ] **Step 1: Create the tests directory**

```bash
mkdir -p scripts/tests/fixtures
touch scripts/tests/__init__.py
```

- [ ] **Step 2: Pick a known-popular Spotify track ID**

Use a track guaranteed to be in ReccoBeats' DB. Default: `4uLU6hMCjMI75M1A2tKUQC` (Rick Astley, "Never Gonna Give You Up"). If you want to use a tutor-relevant track, pick any ID from the freshly-pulled `taste/playlists.json`.

- [ ] **Step 3: Make a real request and save the response**

```bash
curl -sS "https://api.reccobeats.com/v1/track/4uLU6hMCjMI75M1A2tKUQC/audio-features" \
  -H "Accept: application/json" \
  | python -m json.tool > scripts/tests/fixtures/reccobeats-track-hit.json
cat scripts/tests/fixtures/reccobeats-track-hit.json
```

Expected: a JSON object with audio-features fields. Print and read the actual field names — they may differ from spec assumptions (e.g., `tempo` vs `bpm`, `timeSignature` vs `time_signature`). **The actual field names from this fixture drive the parser implementation in Task 2.6.**

- [ ] **Step 4: Synthesize the 404 fixture**

Create `scripts/tests/fixtures/reccobeats-track-404.json`:

```json
{
  "error": "Track not found",
  "status": 404
}
```

(Adjust to match real 404 body if it differs — make a curl call to a fake ID like `0000000000000000000000` to verify.)

- [ ] **Step 5: Commit**

```bash
git add scripts/tests/__init__.py scripts/tests/fixtures/
git commit -m "$(cat <<'EOF'
test(enrich): capture real ReccoBeats response fixtures

Hit fixture from a real API call; 404 fixture for parser testing.
Drives the field-name decisions in the ReccoBeats client.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.3: Build the Camelot lookup

**Files:**
- Create: `scripts/tests/test_camelot.py`
- Create: `scripts/enrich/camelot.py`

- [ ] **Step 1: Write the failing test**

Create `scripts/tests/test_camelot.py`:

```python
"""Tests for the Camelot wheel lookup."""

import pytest

from enrich.camelot import camelot_from_int_key, key_standard_from_int


@pytest.mark.parametrize(
    "key_int,mode_int,expected_camelot,expected_standard",
    [
        # (Spotify-style key int, mode int, expected camelot, expected standard)
        (0, 1, "8B", "C major"),
        (9, 0, "8A", "A minor"),
        (7, 1, "9B", "G major"),
        (4, 0, "9A", "E minor"),
        (2, 1, "10B", "D major"),
        (11, 0, "10A", "B minor"),
        (9, 1, "11B", "A major"),
        (6, 0, "11A", "F# minor"),
        (4, 1, "12B", "E major"),
        (1, 0, "12A", "C# minor"),
        (11, 1, "1B", "B major"),
        (8, 0, "1A", "G# minor"),
        (6, 1, "2B", "F# major"),
        (3, 0, "2A", "D# minor"),
        (1, 1, "3B", "Db major"),
        (10, 0, "3A", "Bb minor"),
        (8, 1, "4B", "Ab major"),
        (5, 0, "4A", "F minor"),
        (3, 1, "5B", "Eb major"),
        (0, 0, "5A", "C minor"),
        (10, 1, "6B", "Bb major"),
        (7, 0, "6A", "G minor"),
        (5, 1, "7B", "F major"),
        (2, 0, "7A", "D minor"),
    ],
)
def test_camelot_lookup_covers_all_24_keys(
    key_int, mode_int, expected_camelot, expected_standard
):
    assert camelot_from_int_key(key_int, mode_int) == expected_camelot
    assert key_standard_from_int(key_int, mode_int) == expected_standard


def test_invalid_key_int_raises():
    with pytest.raises(ValueError, match="key_int must be in"):
        camelot_from_int_key(12, 1)


def test_invalid_mode_int_raises():
    with pytest.raises(ValueError, match="mode_int must be 0 or 1"):
        camelot_from_int_key(0, 2)
```

- [ ] **Step 2: Run the test, verify it fails**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_camelot.py -v
cd ..
```

Expected: FAIL with `ModuleNotFoundError: No module named 'enrich.camelot'`.

- [ ] **Step 3: Implement the camelot module**

Create `scripts/enrich/camelot.py`:

```python
"""Camelot wheel lookup.

Maps a (key_int, mode_int) pair as ReccoBeats / Spotify return them
to a Camelot string ("8B") and a human-readable standard key ("C major").

Key ints: 0=C, 1=C#/Db, 2=D, 3=D#/Eb, 4=E, 5=F,
          6=F#/Gb, 7=G, 8=G#/Ab, 9=A, 10=A#/Bb, 11=B
Mode ints: 0=minor, 1=major
"""

from typing import Final

# Standard key spelling per (key_int, mode_int). The spelling follows the
# Camelot wheel convention (e.g., 12A is C# minor; 3B is Db major).
_KEY_STANDARD: Final[dict[tuple[int, int], str]] = {
    # major (mode=1)
    (0, 1): "C major",
    (1, 1): "Db major",
    (2, 1): "D major",
    (3, 1): "Eb major",
    (4, 1): "E major",
    (5, 1): "F major",
    (6, 1): "F# major",
    (7, 1): "G major",
    (8, 1): "Ab major",
    (9, 1): "A major",
    (10, 1): "Bb major",
    (11, 1): "B major",
    # minor (mode=0)
    (0, 0): "C minor",
    (1, 0): "C# minor",
    (2, 0): "D minor",
    (3, 0): "D# minor",
    (4, 0): "E minor",
    (5, 0): "F minor",
    (6, 0): "F# minor",
    (7, 0): "G minor",
    (8, 0): "G# minor",
    (9, 0): "A minor",
    (10, 0): "Bb minor",
    (11, 0): "B minor",
}

_CAMELOT: Final[dict[tuple[int, int], str]] = {
    # major (mode=1)
    (0, 1): "8B",
    (7, 1): "9B",
    (2, 1): "10B",
    (9, 1): "11B",
    (4, 1): "12B",
    (11, 1): "1B",
    (6, 1): "2B",
    (1, 1): "3B",
    (8, 1): "4B",
    (3, 1): "5B",
    (10, 1): "6B",
    (5, 1): "7B",
    # minor (mode=0)
    (9, 0): "8A",
    (4, 0): "9A",
    (11, 0): "10A",
    (6, 0): "11A",
    (1, 0): "12A",
    (8, 0): "1A",
    (3, 0): "2A",
    (10, 0): "3A",
    (5, 0): "4A",
    (0, 0): "5A",
    (7, 0): "6A",
    (2, 0): "7A",
}


def _validate(key_int: int, mode_int: int) -> None:
    if not 0 <= key_int <= 11:
        raise ValueError(f"key_int must be in 0..11, got {key_int}")
    if mode_int not in (0, 1):
        raise ValueError(f"mode_int must be 0 or 1, got {mode_int}")


def camelot_from_int_key(key_int: int, mode_int: int) -> str:
    _validate(key_int, mode_int)
    return _CAMELOT[(key_int, mode_int)]


def key_standard_from_int(key_int: int, mode_int: int) -> str:
    _validate(key_int, mode_int)
    return _KEY_STANDARD[(key_int, mode_int)]
```

- [ ] **Step 4: Run the test, verify it passes**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_camelot.py -v
cd ..
```

Expected: 26 PASSED (24 parametrized + 2 error cases).

- [ ] **Step 5: Commit**

```bash
git add scripts/enrich/camelot.py scripts/tests/test_camelot.py
git commit -m "$(cat <<'EOF'
feat(enrich): camelot wheel lookup (24 keys)

Maps Spotify/ReccoBeats integer-encoded (key, mode) to Camelot string
and human-readable standard key. Pure data, no theory computation.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.4: Build the playlists loader (filter + dedupe)

**Files:**
- Create: `scripts/tests/fixtures/playlists-mini.json`
- Create: `scripts/tests/test_playlists_loader.py`
- Create: `scripts/enrich/playlists_loader.py`

- [ ] **Step 1: Create the test fixture**

Create `scripts/tests/fixtures/playlists-mini.json`:

```json
{
  "user_id": "testuser",
  "fetched_at": "2026-04-26T00:00:00Z",
  "playlists": [
    {
      "id": "pl1",
      "name": "Bangers",
      "tracks": [
        {
          "id": "track001",
          "type": "track",
          "name": "Track One",
          "artists": [{"id": "art1", "name": "Artist A"}, {"id": "art2", "name": "Artist B"}],
          "album": {"name": "Album X"},
          "duration_ms": 240000,
          "external_ids": {"isrc": "USRC12345601"}
        },
        {
          "id": "track002",
          "type": "track",
          "name": "Track Two",
          "artists": [{"id": "art3", "name": "Artist C"}],
          "album": {"name": "Album Y"},
          "duration_ms": 180500,
          "external_ids": {}
        },
        {
          "id": null,
          "type": "track",
          "is_local": true,
          "name": "Local File",
          "artists": [{"id": null, "name": "Unknown"}],
          "album": {"name": ""},
          "duration_ms": 200000
        }
      ]
    },
    {
      "id": "pl2",
      "name": "More Bangers",
      "tracks": [
        {
          "id": "track001",
          "type": "track",
          "name": "Track One",
          "artists": [{"id": "art1", "name": "Artist A"}],
          "album": {"name": "Album X"},
          "duration_ms": 240000,
          "external_ids": {"isrc": "USRC12345601"}
        },
        {
          "id": "ep001",
          "type": "episode",
          "name": "Some Podcast Ep",
          "duration_ms": 1800000
        },
        {
          "id": "track003",
          "type": "track",
          "name": "Track Three",
          "artists": [{"id": "art4", "name": "Artist D"}],
          "album": {"name": "Album Z"},
          "duration_ms": 210000,
          "external_ids": {"isrc": "USRC12345603"}
        }
      ]
    }
  ]
}
```

This fixture tests: dedup (track001 in two playlists), local-file filter (id=null), podcast-episode filter (type=episode), multi-artist primary-only, missing ISRC.

- [ ] **Step 2: Write the failing test**

Create `scripts/tests/test_playlists_loader.py`:

```python
"""Tests for the playlists loader."""

import json
from pathlib import Path

import pytest

from enrich.playlists_loader import TrackRecord, load_and_dedupe

FIXTURE = Path(__file__).parent / "fixtures" / "playlists-mini.json"


def test_load_and_dedupe_yields_three_tracks():
    records, skipped = load_and_dedupe(FIXTURE)

    # track001 appears in two playlists but should be deduped to one record.
    # Local file (id=null, is_local=True) should be skipped.
    # Podcast episode (type=episode) should be skipped.
    assert len(records) == 3
    ids = {r.spotify_id for r in records}
    assert ids == {"track001", "track002", "track003"}


def test_skipped_count_includes_local_and_episode():
    _, skipped = load_and_dedupe(FIXTURE)
    assert skipped["local_files"] == 1
    assert skipped["episodes_or_other"] == 1


def test_track_record_metadata_fields():
    records, _ = load_and_dedupe(FIXTURE)
    by_id = {r.spotify_id: r for r in records}

    t1 = by_id["track001"]
    assert t1.artist == "Artist A"  # primary artist only
    assert t1.title == "Track One"
    assert t1.album == "Album X"
    assert t1.duration_s == 240
    assert t1.isrc == "USRC12345601"

    t2 = by_id["track002"]
    assert t2.duration_s == 180  # 180500 ms rounds down
    assert t2.isrc == ""  # missing ISRC -> empty string


def test_load_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_and_dedupe(Path("nonexistent.json"))
```

- [ ] **Step 3: Run the test, verify it fails**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_playlists_loader.py -v
cd ..
```

Expected: FAIL with `ModuleNotFoundError: No module named 'enrich.playlists_loader'`.

- [ ] **Step 4: Implement the loader**

Create `scripts/enrich/playlists_loader.py`:

```python
"""Load taste/playlists.json, filter non-track items, dedupe by Spotify ID."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrackRecord:
    """Metadata extracted from a Spotify playlist item.

    Audio features are added later by the enrichment fetchers.
    """

    spotify_id: str
    isrc: str
    artist: str
    title: str
    album: str
    duration_s: int


def load_and_dedupe(path: Path) -> tuple[list[TrackRecord], dict[str, int]]:
    """Read a playlists.json file and return (records, skipped_counts).

    `records` is deduplicated by spotify_id; the first occurrence wins.
    `skipped_counts` reports how many items were filtered out and why,
    so the end-of-run summary can report them.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    seen: set[str] = set()
    records: list[TrackRecord] = []
    skipped = {"local_files": 0, "episodes_or_other": 0, "duplicates": 0}

    for playlist in data.get("playlists", []):
        for item in playlist.get("tracks", []):
            item_type = item.get("type", "track")
            if item_type != "track":
                skipped["episodes_or_other"] += 1
                continue
            if item.get("is_local") or item.get("id") is None:
                skipped["local_files"] += 1
                continue
            spotify_id = item["id"]
            if spotify_id in seen:
                skipped["duplicates"] += 1
                continue
            seen.add(spotify_id)
            artists = item.get("artists", [])
            primary_artist = artists[0]["name"] if artists else ""
            records.append(
                TrackRecord(
                    spotify_id=spotify_id,
                    isrc=item.get("external_ids", {}).get("isrc", ""),
                    artist=primary_artist,
                    title=item.get("name", ""),
                    album=item.get("album", {}).get("name", ""),
                    duration_s=item.get("duration_ms", 0) // 1000,
                )
            )

    return records, skipped
```

- [ ] **Step 5: Run the test, verify it passes**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_playlists_loader.py -v
cd ..
```

Expected: 4 PASSED.

- [ ] **Step 6: Commit**

```bash
git add scripts/enrich/playlists_loader.py scripts/tests/test_playlists_loader.py scripts/tests/fixtures/playlists-mini.json
git commit -m "$(cat <<'EOF'
feat(enrich): playlists.json loader with dedup + filter

Walks every playlist's tracks, drops local-file uploads and podcast
episodes, dedupes by spotify_id (first occurrence wins). Reports
skipped counts for the end-of-run summary.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.5: Define the EnrichmentResult dataclass

**Files:**
- Create: `scripts/tests/test_models.py`
- Create: `scripts/enrich/models.py`

- [ ] **Step 1: Write the failing test**

Create `scripts/tests/test_models.py`:

```python
"""Tests for shared data classes."""

from enrich.models import EnrichmentResult


def test_enrichment_result_defaults_to_all_none():
    r = EnrichmentResult()
    assert r.bpm is None
    assert r.key_int is None
    assert r.mode is None
    assert r.time_signature is None
    assert r.energy is None
    assert r.danceability is None
    assert r.valence is None
    assert r.acousticness is None
    assert r.instrumentalness is None
    assert r.liveness is None
    assert r.loudness is None
    assert r.speechiness is None


def test_enrichment_result_holds_full_vector():
    r = EnrichmentResult(
        bpm=128.5,
        key_int=7,
        mode=1,
        time_signature=4,
        energy=0.85,
        danceability=0.62,
        valence=0.42,
        acousticness=0.05,
        instrumentalness=0.0,
        liveness=0.12,
        loudness=-5.3,
        speechiness=0.04,
    )
    assert r.bpm == 128.5
    assert r.energy == 0.85
```

- [ ] **Step 2: Run the test, verify it fails**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_models.py -v
cd ..
```

Expected: FAIL with `ModuleNotFoundError: No module named 'enrich.models'`.

- [ ] **Step 3: Implement the models module**

Create `scripts/enrich/models.py`:

```python
"""Shared data classes for the enrichment pipeline."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EnrichmentResult:
    """One backend's response for a single track.

    All fields are optional. ReccoBeats populates everything; GetSongBPM
    populates only bpm + key_int + mode. Returned as None from the
    backend on a miss; the caller handles fallback.
    """

    bpm: Optional[float] = None
    key_int: Optional[int] = None  # 0..11 (Spotify-style)
    mode: Optional[int] = None  # 0 minor, 1 major
    time_signature: Optional[int] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    loudness: Optional[float] = None
    speechiness: Optional[float] = None
```

- [ ] **Step 4: Run the test, verify it passes**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_models.py -v
cd ..
```

Expected: 2 PASSED.

- [ ] **Step 5: Commit**

```bash
git add scripts/enrich/models.py scripts/tests/test_models.py
git commit -m "$(cat <<'EOF'
feat(enrich): EnrichmentResult dataclass — uniform backend return shape

Single record returned by every backend client. All audio-feature fields
optional; backends populate what they can; caller composes into csv.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.6: Build the ReccoBeats client (two-step lookup)

**Background (verified 2026-04-26 by Task 2.2):** ReccoBeats requires a two-step lookup — the audio-features endpoint takes ReccoBeats internal UUIDs, NOT Spotify IDs. To go from a Spotify track ID to audio features:

1. `GET /v1/track?ids=<spotify_id>` → returns `{"content": [{id, href, isrc, ...}, ...]}`. The `content` array contains a ReccoBeats track object for each Spotify ID they have. Empty `content` means the track isn't in their DB. **This is also how we detect "not in DB" — the audio-features endpoint never sees Spotify IDs in this design, so we don't get HTTP 404s on it for the "unknown track" case.**
2. `GET /v1/track/<reccobeats-uuid>/audio-features` → returns the audio-features payload for the resolved UUID.

The single-track client function (`fetch(spotify_id)`) hides this two-step pattern behind one call. Its return-shape contract is unchanged (`EnrichmentResult | None`).

The audio-features response shape (verified) is:

```json
{
  "id": "edd5003e-3d49-49ab-92ec-4f5439368e22",
  "href": "https://open.spotify.com/track/...",
  "isrc": "QM24S2501046",
  "acousticness": 0.00438,
  "danceability": 0.738,
  "energy": 0.785,
  "instrumentalness": 0.681,
  "key": 5,
  "liveness": 0.0799,
  "loudness": -7.25,
  "mode": 0,
  "speechiness": 0.0361,
  "tempo": 126.037,
  "valence": 0.331
}
```

Note: there is **no `time_signature` field**. The schema column for it stays empty in v1.

**Files:**
- Create: `scripts/tests/fixtures/reccobeats-resolve-hit.json` (real API capture)
- Create: `scripts/tests/fixtures/reccobeats-resolve-empty.json` (real API capture)
- Create: `scripts/tests/test_reccobeats.py`
- Create: `scripts/enrich/reccobeats.py`

- [ ] **Step 1: Capture the resolution-call fixtures**

```bash
# Hit: a known-good EDM Spotify ID (Disco Lines & GUDFELLA "Sunny")
curl -sS "https://api.reccobeats.com/v1/track?ids=7tZSQgFyzWAAtsb7OUUDbn" \
  -H "Accept: application/json" \
  | python -m json.tool > scripts/tests/fixtures/reccobeats-resolve-hit.json
cat scripts/tests/fixtures/reccobeats-resolve-hit.json

# Empty: a non-existent Spotify ID
curl -sS "https://api.reccobeats.com/v1/track?ids=0000000000000000000000" \
  -H "Accept: application/json" \
  | python -m json.tool > scripts/tests/fixtures/reccobeats-resolve-empty.json
cat scripts/tests/fixtures/reccobeats-resolve-empty.json
```

Verify the hit fixture has a non-empty `content` array with at least one object containing `id` (UUID), `href` (Spotify URL), `isrc`. Verify the empty fixture has `content: []`. The Spotify ID `7tZSQgFyzWAAtsb7OUUDbn` is the same one Task 2.2 used for `reccobeats-track-hit.json` — its UUID should match the `id` field there (`edd5003e-3d49-49ab-92ec-4f5439368e22`).

- [ ] **Step 2: Write the failing test**

Create `scripts/tests/test_reccobeats.py`:

```python
"""Tests for the ReccoBeats client (two-step lookup)."""

import json
from pathlib import Path

import pytest
import responses

from enrich.reccobeats import RECCOBEATS_BASE_URL, ReccoBeatsRateLimited, fetch

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _resolve_hit():
    return json.loads((FIXTURE_DIR / "reccobeats-resolve-hit.json").read_text())


def _resolve_empty():
    return json.loads((FIXTURE_DIR / "reccobeats-resolve-empty.json").read_text())


def _features_hit():
    return json.loads((FIXTURE_DIR / "reccobeats-track-hit.json").read_text())


@responses.activate
def test_fetch_returns_audio_features_on_resolved_track():
    spotify_id = "7tZSQgFyzWAAtsb7OUUDbn"
    resolve = _resolve_hit()
    features = _features_hit()
    uuid = resolve["content"][0]["id"]

    responses.get(
        f"{RECCOBEATS_BASE_URL}/v1/track",
        json=resolve,
        status=200,
        match=[responses.matchers.query_param_matcher({"ids": spotify_id})],
    )
    responses.get(
        f"{RECCOBEATS_BASE_URL}/v1/track/{uuid}/audio-features",
        json=features,
        status=200,
    )

    result = fetch(spotify_id)

    assert result is not None
    assert result.bpm == features["tempo"]
    assert result.key_int == features["key"]
    assert result.mode == features["mode"]
    assert result.energy == features["energy"]
    assert result.danceability == features["danceability"]
    assert result.valence == features["valence"]
    assert result.acousticness == features["acousticness"]
    assert result.instrumentalness == features["instrumentalness"]
    assert result.liveness == features["liveness"]
    assert result.loudness == features["loudness"]
    assert result.speechiness == features["speechiness"]
    assert result.time_signature is None  # ReccoBeats doesn't return this


@responses.activate
def test_fetch_returns_none_when_resolve_is_empty():
    spotify_id = "0000000000000000000000"
    responses.get(
        f"{RECCOBEATS_BASE_URL}/v1/track",
        json=_resolve_empty(),
        status=200,
        match=[responses.matchers.query_param_matcher({"ids": spotify_id})],
    )

    assert fetch(spotify_id) is None
    # Note: only one request was made — the audio-features endpoint
    # is never called when resolve returns empty content.
    assert len(responses.calls) == 1


@responses.activate
def test_fetch_raises_on_429_during_resolve():
    spotify_id = "7tZSQgFyzWAAtsb7OUUDbn"
    responses.get(
        f"{RECCOBEATS_BASE_URL}/v1/track",
        status=429,
        headers={"Retry-After": "30"},
        match=[responses.matchers.query_param_matcher({"ids": spotify_id})],
    )

    with pytest.raises(ReccoBeatsRateLimited) as exc_info:
        fetch(spotify_id)
    assert exc_info.value.retry_after_s == 30


@responses.activate
def test_fetch_raises_on_429_during_features():
    spotify_id = "7tZSQgFyzWAAtsb7OUUDbn"
    resolve = _resolve_hit()
    uuid = resolve["content"][0]["id"]

    responses.get(
        f"{RECCOBEATS_BASE_URL}/v1/track",
        json=resolve,
        status=200,
        match=[responses.matchers.query_param_matcher({"ids": spotify_id})],
    )
    responses.get(
        f"{RECCOBEATS_BASE_URL}/v1/track/{uuid}/audio-features",
        status=429,
        headers={"Retry-After": "10"},
    )

    with pytest.raises(ReccoBeatsRateLimited) as exc_info:
        fetch(spotify_id)
    assert exc_info.value.retry_after_s == 10


@responses.activate
def test_fetch_raises_on_5xx():
    spotify_id = "7tZSQgFyzWAAtsb7OUUDbn"
    responses.get(
        f"{RECCOBEATS_BASE_URL}/v1/track",
        status=500,
        match=[responses.matchers.query_param_matcher({"ids": spotify_id})],
    )

    with pytest.raises(Exception):
        fetch(spotify_id)
```

- [ ] **Step 3: Run the test, verify it fails**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_reccobeats.py -v
cd ..
```

Expected: FAIL with `ModuleNotFoundError: No module named 'enrich.reccobeats'`.

- [ ] **Step 4: Implement the ReccoBeats client**

Create `scripts/enrich/reccobeats.py`:

```python
"""ReccoBeats client (two-step lookup).

Single public function: fetch(spotify_id) -> EnrichmentResult | None.

ReccoBeats does not accept Spotify IDs at the audio-features endpoint;
it has its own UUID-based identifiers. Going from a Spotify ID to
audio features is a two-step dance:

  1. GET /v1/track?ids=<spotify_id>  -> returns {"content": [{id: <uuid>, ...}, ...]}
  2. GET /v1/track/<uuid>/audio-features  -> returns the audio-features payload

Returns None if step 1's content is empty (track not in ReccoBeats DB).
Raises ReccoBeatsRateLimited on 429 (with Retry-After attached) from
either step. Raises requests.HTTPError on other non-2xx.
"""

from typing import Optional

import requests

from enrich.models import EnrichmentResult

RECCOBEATS_BASE_URL = "https://api.reccobeats.com"
_DEFAULT_TIMEOUT_S = 10


class ReccoBeatsRateLimited(Exception):
    def __init__(self, retry_after_s: int):
        super().__init__(f"ReccoBeats rate-limited; retry after {retry_after_s}s")
        self.retry_after_s = retry_after_s


def _check_429(response: requests.Response) -> None:
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", "60"))
        raise ReccoBeatsRateLimited(retry_after_s=retry_after)


def _resolve_spotify_id(spotify_id: str) -> Optional[str]:
    """Step 1: turn a Spotify track ID into a ReccoBeats UUID, or None if not in DB."""
    response = requests.get(
        f"{RECCOBEATS_BASE_URL}/v1/track",
        params={"ids": spotify_id},
        timeout=_DEFAULT_TIMEOUT_S,
        headers={"Accept": "application/json"},
    )
    _check_429(response)
    response.raise_for_status()
    content = response.json().get("content", [])
    if not content:
        return None
    return content[0]["id"]


def _fetch_features(uuid: str) -> EnrichmentResult:
    """Step 2: fetch audio features by ReccoBeats UUID."""
    response = requests.get(
        f"{RECCOBEATS_BASE_URL}/v1/track/{uuid}/audio-features",
        timeout=_DEFAULT_TIMEOUT_S,
        headers={"Accept": "application/json"},
    )
    _check_429(response)
    response.raise_for_status()
    payload = response.json()
    # Field names verified against the live API on 2026-04-26.
    # time_signature is not in ReccoBeats' response — left None.
    return EnrichmentResult(
        bpm=payload.get("tempo"),
        key_int=payload.get("key"),
        mode=payload.get("mode"),
        time_signature=None,
        energy=payload.get("energy"),
        danceability=payload.get("danceability"),
        valence=payload.get("valence"),
        acousticness=payload.get("acousticness"),
        instrumentalness=payload.get("instrumentalness"),
        liveness=payload.get("liveness"),
        loudness=payload.get("loudness"),
        speechiness=payload.get("speechiness"),
    )


def fetch(spotify_id: str) -> Optional[EnrichmentResult]:
    uuid = _resolve_spotify_id(spotify_id)
    if uuid is None:
        return None
    return _fetch_features(uuid)
```

- [ ] **Step 5: Run the test, verify it passes**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_reccobeats.py -v
cd ..
```

Expected: 5 PASSED.

- [ ] **Step 6: Commit**

```bash
git add scripts/enrich/reccobeats.py scripts/tests/test_reccobeats.py scripts/tests/fixtures/reccobeats-resolve-hit.json scripts/tests/fixtures/reccobeats-resolve-empty.json
git commit -m "$(cat <<'EOF'
feat(enrich): ReccoBeats client with two-step lookup

ReccoBeats requires resolving Spotify ID -> internal UUID before
fetching audio features. Single fetch(spotify_id) hides the two
calls behind one return-shape contract. None when resolve returns
empty content (track not in DB); typed exception on 429 from either
step (Retry-After preserved). No auth required.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.7: Build the GetSongBPM client (fallback)

**Files:**
- Create: `scripts/tests/fixtures/getsongbpm-search-hit.json`
- Create: `scripts/tests/fixtures/getsongbpm-search-empty.json`
- Create: `scripts/tests/test_getsongbpm.py`
- Create: `scripts/enrich/getsongbpm.py`

The GetSongBPM API is artist+title based. Documented at https://getsongbpm.com/api. The endpoint we use is `/search/?type=both&lookup=song:<title>+artist:<artist>&api_key=<key>`. Returns a list of matches; we take the first if the artist+title both match (case-insensitive).

- [ ] **Step 1: Synthesize fixture for a hit**

Create `scripts/tests/fixtures/getsongbpm-search-hit.json`:

```json
{
  "search": [
    {
      "id": "abc123",
      "title": "Track Two",
      "artist": {"name": "Artist C"},
      "tempo": "128",
      "key_of": "F# minor",
      "time_sig": "4/4"
    }
  ]
}
```

- [ ] **Step 2: Synthesize fixture for empty results**

Create `scripts/tests/fixtures/getsongbpm-search-empty.json`:

```json
{
  "search": []
}
```

(The actual GetSongBPM "no results" shape may differ; verify by making a real query later in Task 2.13. The implementation gracefully handles missing/empty `search`.)

- [ ] **Step 3: Write the failing test**

Create `scripts/tests/test_getsongbpm.py`:

```python
"""Tests for the GetSongBPM fallback client."""

import json
from pathlib import Path

import pytest
import responses

from enrich.getsongbpm import GETSONGBPM_BASE_URL, fetch

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@responses.activate
def test_fetch_returns_bpm_and_key_on_hit():
    fixture = json.loads((FIXTURE_DIR / "getsongbpm-search-hit.json").read_text())
    responses.get(
        f"{GETSONGBPM_BASE_URL}/search/",
        json=fixture,
        status=200,
    )

    result = fetch("Artist C", "Track Two", api_key="testkey")

    assert result is not None
    assert result.bpm == 128.0
    assert result.key_int == 6  # F#
    assert result.mode == 0  # minor
    # GetSongBPM doesn't return audio-feature dimensions
    assert result.energy is None
    assert result.valence is None


@responses.activate
def test_fetch_returns_none_on_empty_search():
    fixture = json.loads((FIXTURE_DIR / "getsongbpm-search-empty.json").read_text())
    responses.get(
        f"{GETSONGBPM_BASE_URL}/search/",
        json=fixture,
        status=200,
    )

    assert fetch("Nonexistent Artist", "Nonexistent Title", api_key="testkey") is None


@responses.activate
def test_fetch_returns_none_when_artist_doesnt_match():
    """Defensive: if GetSongBPM returns a match for a different artist, reject."""
    fixture = {
        "search": [
            {
                "id": "x",
                "title": "Track Two",
                "artist": {"name": "Wrong Artist"},
                "tempo": "120",
                "key_of": "C major",
            }
        ]
    }
    responses.get(
        f"{GETSONGBPM_BASE_URL}/search/",
        json=fixture,
        status=200,
    )

    assert fetch("Artist C", "Track Two", api_key="testkey") is None


def test_fetch_raises_when_no_api_key():
    with pytest.raises(ValueError, match="api_key required"):
        fetch("X", "Y", api_key="")
```

- [ ] **Step 4: Run the test, verify it fails**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_getsongbpm.py -v
cd ..
```

Expected: FAIL with `ModuleNotFoundError: No module named 'enrich.getsongbpm'`.

- [ ] **Step 5: Implement the GetSongBPM client**

Create `scripts/enrich/getsongbpm.py`:

```python
"""GetSongBPM fallback client.

Used only when ReccoBeats misses. Looks up by artist + title (fuzzy);
returns BPM and key only. Audio-feature columns stay empty.

Free API requires registration + a public backlink to getsongbpm.com.
This project includes the attribution in scripts/README.md and
taste/profile.md (when generated by Subsystem #7).
"""

from typing import Optional

import requests

from enrich.models import EnrichmentResult

GETSONGBPM_BASE_URL = "https://api.getsongbpm.com"
_DEFAULT_TIMEOUT_S = 10

# Map GetSongBPM's "key_of" string format ("F# minor", "C major") to
# (key_int, mode_int) pairs that match the camelot lookup.
_KEY_TO_INT = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10, "B": 11,
}


def _parse_key_of(key_of: str) -> tuple[Optional[int], Optional[int]]:
    """Parse 'F# minor' / 'C major' into (key_int, mode_int)."""
    if not key_of:
        return None, None
    parts = key_of.strip().split()
    if len(parts) != 2:
        return None, None
    pitch, mode_str = parts[0], parts[1].lower()
    key_int = _KEY_TO_INT.get(pitch)
    mode_int = 1 if mode_str.startswith("major") else 0 if mode_str.startswith("minor") else None
    return key_int, mode_int


def fetch(artist: str, title: str, api_key: str) -> Optional[EnrichmentResult]:
    if not api_key:
        raise ValueError("api_key required for GetSongBPM")

    response = requests.get(
        f"{GETSONGBPM_BASE_URL}/search/",
        params={
            "type": "both",
            "lookup": f"song:{title}+artist:{artist}",
            "api_key": api_key,
        },
        timeout=_DEFAULT_TIMEOUT_S,
    )
    response.raise_for_status()
    payload = response.json()

    matches = payload.get("search", []) if isinstance(payload, dict) else []
    if not matches:
        return None

    # Defensive artist match — reject if GetSongBPM returns a different artist.
    first = matches[0]
    returned_artist = (first.get("artist") or {}).get("name", "")
    if returned_artist.strip().lower() != artist.strip().lower():
        return None

    tempo_str = first.get("tempo", "")
    try:
        bpm = float(tempo_str) if tempo_str else None
    except (TypeError, ValueError):
        bpm = None

    key_int, mode_int = _parse_key_of(first.get("key_of", ""))

    return EnrichmentResult(bpm=bpm, key_int=key_int, mode=mode_int)
```

- [ ] **Step 6: Run the test, verify it passes**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_getsongbpm.py -v
cd ..
```

Expected: 4 PASSED.

- [ ] **Step 7: Commit**

```bash
git add scripts/enrich/getsongbpm.py scripts/tests/test_getsongbpm.py scripts/tests/fixtures/getsongbpm-search-hit.json scripts/tests/fixtures/getsongbpm-search-empty.json
git commit -m "$(cat <<'EOF'
feat(enrich): GetSongBPM fallback client (artist + title lookup)

Defensive artist-match check rejects mismatched results from the fuzzy
search endpoint. Returns BPM and key only; audio-feature columns left
empty for downstream csv writer.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.8: Build the CSV writer (incremental merge)

**Files:**
- Create: `scripts/tests/test_csv_writer.py`
- Create: `scripts/enrich/csv_writer.py`

- [ ] **Step 1: Write the failing test**

Create `scripts/tests/test_csv_writer.py`:

```python
"""Tests for the tracks.csv writer."""

import csv
from pathlib import Path

from enrich.csv_writer import (
    CSV_COLUMNS,
    EnrichedRow,
    read_existing,
    write_atomic,
)


def test_csv_columns_match_spec():
    """The exact column order from spec §3.4."""
    expected = [
        "spotify_id", "isrc", "artist", "title", "album", "duration_s",
        "bpm", "key_camelot", "key_standard", "mode", "time_signature",
        "energy", "danceability", "valence", "acousticness", "instrumentalness",
        "liveness", "loudness", "speechiness",
        "genre", "source", "fetched_at",
    ]
    assert CSV_COLUMNS == expected


def test_write_then_read_roundtrip(tmp_path: Path):
    rows = [
        EnrichedRow(
            spotify_id="track001",
            isrc="USRC1",
            artist="A",
            title="T",
            album="Al",
            duration_s=200,
            bpm=128.0,
            key_camelot="8B",
            key_standard="C major",
            mode=1,
            time_signature=4,
            energy=0.8,
            danceability=0.6,
            valence=0.5,
            acousticness=0.1,
            instrumentalness=0.0,
            liveness=0.1,
            loudness=-5.0,
            speechiness=0.05,
            genre="",
            source="reccobeats",
            fetched_at="2026-04-26T00:00:00Z",
        )
    ]
    path = tmp_path / "tracks.csv"
    write_atomic(path, rows)

    read_back = read_existing(path)
    assert "track001" in read_back
    r = read_back["track001"]
    assert r.bpm == 128.0
    assert r.source == "reccobeats"
    assert r.fetched_at == "2026-04-26T00:00:00Z"


def test_read_existing_returns_empty_for_missing_file(tmp_path: Path):
    path = tmp_path / "nope.csv"
    assert read_existing(path) == {}


def test_write_atomic_preserves_column_order(tmp_path: Path):
    rows = [
        EnrichedRow(
            spotify_id="x", isrc="", artist="", title="", album="", duration_s=0,
            bpm=None, key_camelot="", key_standard="", mode=None, time_signature=None,
            energy=None, danceability=None, valence=None, acousticness=None,
            instrumentalness=None, liveness=None, loudness=None, speechiness=None,
            genre="", source="miss:reccobeats", fetched_at="2026-04-26T00:00:00Z",
        )
    ]
    path = tmp_path / "tracks.csv"
    write_atomic(path, rows)

    with open(path, "r", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == CSV_COLUMNS


def test_corrupt_csv_is_backed_up(tmp_path: Path):
    path = tmp_path / "tracks.csv"
    path.write_text("this,is,not,a,valid,header\nrandomgarbage\n")

    # read_existing should not raise; it returns {} and renames the corrupt file.
    result = read_existing(path)
    assert result == {}
    backups = list(tmp_path.glob("tracks.csv.corrupt-*"))
    assert len(backups) == 1
```

- [ ] **Step 2: Run the test, verify it fails**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_csv_writer.py -v
cd ..
```

Expected: FAIL with `ModuleNotFoundError: No module named 'enrich.csv_writer'`.

- [ ] **Step 3: Implement the csv writer**

Create `scripts/enrich/csv_writer.py`:

```python
"""Read and write taste/tracks.csv with the schema from spec §3.4."""

import csv
import datetime as dt
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Final, Optional

CSV_COLUMNS: Final[list[str]] = [
    "spotify_id", "isrc", "artist", "title", "album", "duration_s",
    "bpm", "key_camelot", "key_standard", "mode", "time_signature",
    "energy", "danceability", "valence", "acousticness", "instrumentalness",
    "liveness", "loudness", "speechiness",
    "genre", "source", "fetched_at",
]


@dataclass(frozen=True)
class EnrichedRow:
    spotify_id: str
    isrc: str
    artist: str
    title: str
    album: str
    duration_s: int
    bpm: Optional[float]
    key_camelot: str
    key_standard: str
    mode: Optional[int]
    time_signature: Optional[int]
    energy: Optional[float]
    danceability: Optional[float]
    valence: Optional[float]
    acousticness: Optional[float]
    instrumentalness: Optional[float]
    liveness: Optional[float]
    loudness: Optional[float]
    speechiness: Optional[float]
    genre: str
    source: str
    fetched_at: str


def _row_to_csv_dict(row: EnrichedRow) -> dict[str, str]:
    """Render a row to the dict csv expects, with None -> empty string."""
    out = {}
    for col in CSV_COLUMNS:
        value = getattr(row, col)
        out[col] = "" if value is None else str(value)
    return out


def _csv_dict_to_row(d: dict[str, str]) -> EnrichedRow:
    def opt_float(s: str) -> Optional[float]:
        return float(s) if s else None

    def opt_int(s: str) -> Optional[int]:
        return int(s) if s else None

    return EnrichedRow(
        spotify_id=d["spotify_id"],
        isrc=d["isrc"],
        artist=d["artist"],
        title=d["title"],
        album=d["album"],
        duration_s=int(d["duration_s"]) if d["duration_s"] else 0,
        bpm=opt_float(d["bpm"]),
        key_camelot=d["key_camelot"],
        key_standard=d["key_standard"],
        mode=opt_int(d["mode"]),
        time_signature=opt_int(d["time_signature"]),
        energy=opt_float(d["energy"]),
        danceability=opt_float(d["danceability"]),
        valence=opt_float(d["valence"]),
        acousticness=opt_float(d["acousticness"]),
        instrumentalness=opt_float(d["instrumentalness"]),
        liveness=opt_float(d["liveness"]),
        loudness=opt_float(d["loudness"]),
        speechiness=opt_float(d["speechiness"]),
        genre=d["genre"],
        source=d["source"],
        fetched_at=d["fetched_at"],
    )


def read_existing(path: Path) -> dict[str, EnrichedRow]:
    """Read tracks.csv, return {spotify_id: EnrichedRow}.

    On schema mismatch (corrupt file), back the file up to
    tracks.csv.corrupt-<UTC-timestamp> and return {} so the next write
    rebuilds from scratch.
    """
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != CSV_COLUMNS:
                _backup_corrupt(path)
                return {}
            out: dict[str, EnrichedRow] = {}
            for d in reader:
                out[d["spotify_id"]] = _csv_dict_to_row(d)
            return out
    except (KeyError, csv.Error, UnicodeDecodeError):
        _backup_corrupt(path)
        return {}


def _backup_corrupt(path: Path) -> None:
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_name(f"{path.name}.corrupt-{timestamp}")
    path.rename(backup)
    print(f"WARNING: backed up unreadable {path.name} to {backup.name}; rebuilding fresh.")


def write_atomic(path: Path, rows: list[EnrichedRow]) -> None:
    """Write rows to a temp file, then rename to the final path."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.DictWriter(
            f, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(_row_to_csv_dict(row))
    tmp.replace(path)
```

- [ ] **Step 4: Run the test, verify it passes**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_csv_writer.py -v
cd ..
```

Expected: 5 PASSED.

- [ ] **Step 5: Commit**

```bash
git add scripts/enrich/csv_writer.py scripts/tests/test_csv_writer.py
git commit -m "$(cat <<'EOF'
feat(enrich): tracks.csv reader/writer with corrupt-file recovery

Atomic write via temp+rename. Corrupt file (schema mismatch or unreadable)
is backed up to tracks.csv.corrupt-<timestamp> and we rebuild fresh.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.9: Build the orchestrator (`enrich/cli.py`)

**Files:**
- Create: `scripts/tests/test_cli.py`
- Create: `scripts/enrich/cli.py`
- Create: `scripts/enrich.py` (3-line wrapper)

The orchestrator owns: CLI parsing, the TTL retry decision, the fallback chain (Recco → GetSongBPM → miss), the rate-limit throttle, and the end-of-run summary.

- [ ] **Step 1: Write the failing test**

Create `scripts/tests/test_cli.py`:

```python
"""Tests for the orchestrator (TTL, fallback chain, summary)."""

import datetime as dt
from pathlib import Path
from unittest.mock import patch

import pytest

from enrich.cli import (
    merge_for_write,
    needs_enrichment,
    plan_run,
    run_summary,
)
from enrich.csv_writer import EnrichedRow
from enrich.playlists_loader import TrackRecord


def _make_track(sid: str = "t1") -> TrackRecord:
    return TrackRecord(
        spotify_id=sid, isrc="", artist="A", title="T",
        album="Al", duration_s=200,
    )


def _make_row(sid: str, source: str, fetched_at: str) -> EnrichedRow:
    return EnrichedRow(
        spotify_id=sid, isrc="", artist="A", title="T", album="Al", duration_s=200,
        bpm=None, key_camelot="", key_standard="", mode=None, time_signature=None,
        energy=None, danceability=None, valence=None, acousticness=None,
        instrumentalness=None, liveness=None, loudness=None, speechiness=None,
        genre="", source=source, fetched_at=fetched_at,
    )


def test_needs_enrichment_includes_new_tracks():
    track = _make_track("new1")
    assert needs_enrichment(track, existing=None, now=dt.datetime.now(dt.timezone.utc)) is True


def test_needs_enrichment_skips_completed_rows():
    track = _make_track("done1")
    row = _make_row("done1", "reccobeats", "2026-04-25T00:00:00Z")
    now = dt.datetime(2026, 4, 26, tzinfo=dt.timezone.utc)
    assert needs_enrichment(track, existing=row, now=now) is False


def test_needs_enrichment_retries_old_misses():
    track = _make_track("oldmiss")
    row = _make_row("oldmiss", "miss:reccobeats", "2026-03-01T00:00:00Z")
    now = dt.datetime(2026, 4, 26, tzinfo=dt.timezone.utc)  # 56 days later
    assert needs_enrichment(track, existing=row, now=now) is True


def test_needs_enrichment_skips_recent_misses():
    track = _make_track("recentmiss")
    row = _make_row("recentmiss", "miss:reccobeats", "2026-04-20T00:00:00Z")
    now = dt.datetime(2026, 4, 26, tzinfo=dt.timezone.utc)  # 6 days later
    assert needs_enrichment(track, existing=row, now=now) is False


def test_run_summary_nudges_when_unenriched_and_no_getsongbpm():
    summary = run_summary(
        total=10,
        newly_enriched=7,
        still_missed=3,
        skipped={"local_files": 0, "episodes_or_other": 0, "duplicates": 0},
        getsongbpm_configured=False,
    )
    assert "10" in summary  # total
    assert "7" in summary  # newly enriched
    assert "3" in summary  # still missed
    assert "GetSongBPM" in summary  # nudge present


def test_run_summary_no_nudge_when_getsongbpm_configured():
    summary = run_summary(
        total=10,
        newly_enriched=10,
        still_missed=0,
        skipped={"local_files": 0, "episodes_or_other": 0, "duplicates": 0},
        getsongbpm_configured=True,
    )
    assert "GetSongBPM" not in summary


def test_plan_run_force_all_enriches_everything():
    tracks = [_make_track("a"), _make_track("b")]
    existing = {
        "a": _make_row("a", "reccobeats", "2026-04-25T00:00:00Z"),
        "b": _make_row("b", "reccobeats", "2026-04-25T00:00:00Z"),
    }
    now = dt.datetime(2026, 4, 26, tzinfo=dt.timezone.utc)
    plan = plan_run(tracks, existing, now=now, force_all=True)
    assert len(plan) == 2


def test_merge_for_write_default_preserves_orphans():
    """Cumulative behavior: rows whose track is no longer in playlists.json
    survive (because #5 pulls are selective and selection can change)."""
    tracks_in_playlists = [_make_track("a")]  # only "a" is in current playlists.json
    final = {
        "a": _make_row("a", "reccobeats", "2026-04-26T00:00:00Z"),
        "orphan": _make_row("orphan", "reccobeats", "2026-04-01T00:00:00Z"),  # was pulled in a previous selection
    }
    rows = merge_for_write(final, tracks_in_playlists, force_all=False)
    ids = {r.spotify_id for r in rows}
    assert ids == {"a", "orphan"}, "orphan row must survive cumulative writes"


def test_merge_for_write_force_all_drops_orphans():
    """--force-all rebuilds from scratch: rows not in current playlists.json get dropped."""
    tracks_in_playlists = [_make_track("a")]
    final = {
        "a": _make_row("a", "reccobeats", "2026-04-26T00:00:00Z"),
        "orphan": _make_row("orphan", "reccobeats", "2026-04-01T00:00:00Z"),
    }
    rows = merge_for_write(final, tracks_in_playlists, force_all=True)
    ids = {r.spotify_id for r in rows}
    assert ids == {"a"}, "orphan must be dropped under --force-all"
```

- [ ] **Step 2: Run the test, verify it fails**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_cli.py -v
cd ..
```

Expected: FAIL with `ModuleNotFoundError: No module named 'enrich.cli'`.

- [ ] **Step 3: Implement the orchestrator**

Create `scripts/enrich/cli.py`:

```python
"""Orchestrator: TTL retry decision, fallback chain, summary."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path
from typing import Optional

from dateutil import parser as date_parser

from enrich.camelot import camelot_from_int_key, key_standard_from_int
from enrich.csv_writer import CSV_COLUMNS, EnrichedRow, read_existing, write_atomic
from enrich.getsongbpm import fetch as fetch_getsongbpm
from enrich.models import EnrichmentResult
from enrich.playlists_loader import TrackRecord, load_and_dedupe
from enrich.reccobeats import ReccoBeatsRateLimited, fetch as fetch_reccobeats

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PLAYLISTS_PATH = PROJECT_ROOT / "taste" / "playlists.json"
TRACKS_CSV_PATH = PROJECT_ROOT / "taste" / "tracks.csv"
SECRETS_PATH = Path.home() / ".crunchtronics-tutor-secrets" / "audio-enrichment.json"

MISS_TTL_DAYS = 30
THROTTLE_SECONDS = 1.0


def needs_enrichment(
    track: TrackRecord,
    existing: Optional[EnrichedRow],
    now: dt.datetime,
) -> bool:
    """Decide if a track should be (re-)enriched on this run."""
    if existing is None:
        return True
    if not existing.source.startswith("miss:"):
        return False
    fetched = date_parser.isoparse(existing.fetched_at)
    age = now - fetched
    return age >= dt.timedelta(days=MISS_TTL_DAYS)


def plan_run(
    tracks: list[TrackRecord],
    existing: dict[str, EnrichedRow],
    now: dt.datetime,
    *,
    force_all: bool = False,
    retry_misses: bool = False,
    limit: Optional[int] = None,
) -> list[TrackRecord]:
    """Return the subset of tracks that should be enriched on this run."""
    out: list[TrackRecord] = []
    for track in tracks:
        existing_row = existing.get(track.spotify_id)
        if force_all:
            out.append(track)
        elif retry_misses and existing_row is not None and existing_row.source.startswith("miss:"):
            out.append(track)
        elif needs_enrichment(track, existing_row, now):
            out.append(track)
        if limit is not None and len(out) >= limit:
            break
    return out


def _to_enriched_row(
    track: TrackRecord,
    result: Optional[EnrichmentResult],
    source: str,
    now: dt.datetime,
) -> EnrichedRow:
    """Build an EnrichedRow from track metadata + (optional) audio features."""
    if result is None or result.key_int is None or result.mode is None:
        camelot, standard = "", ""
    else:
        camelot = camelot_from_int_key(result.key_int, result.mode)
        standard = key_standard_from_int(result.key_int, result.mode)

    return EnrichedRow(
        spotify_id=track.spotify_id,
        isrc=track.isrc,
        artist=track.artist,
        title=track.title,
        album=track.album,
        duration_s=track.duration_s,
        bpm=result.bpm if result else None,
        key_camelot=camelot,
        key_standard=standard,
        mode=result.mode if result else None,
        time_signature=result.time_signature if result else None,
        energy=result.energy if result else None,
        danceability=result.danceability if result else None,
        valence=result.valence if result else None,
        acousticness=result.acousticness if result else None,
        instrumentalness=result.instrumentalness if result else None,
        liveness=result.liveness if result else None,
        loudness=result.loudness if result else None,
        speechiness=result.speechiness if result else None,
        genre="",
        source=source,
        fetched_at=now.isoformat().replace("+00:00", "Z"),
    )


def _enrich_one(
    track: TrackRecord, now: dt.datetime, getsongbpm_key: Optional[str]
) -> EnrichedRow:
    """Run the fallback chain for one track and return an EnrichedRow."""
    # ReccoBeats first
    recco = fetch_reccobeats(track.spotify_id)
    if recco is not None:
        return _to_enriched_row(track, recco, source="reccobeats", now=now)

    # GetSongBPM fallback (only if configured)
    if getsongbpm_key:
        gsb = fetch_getsongbpm(track.artist, track.title, api_key=getsongbpm_key)
        if gsb is not None:
            return _to_enriched_row(track, gsb, source="getsongbpm", now=now)
        miss_source = "miss:reccobeats,getsongbpm"
    else:
        miss_source = "miss:reccobeats"

    return _to_enriched_row(track, result=None, source=miss_source, now=now)


def merge_for_write(
    final: dict[str, EnrichedRow],
    tracks_in_playlists: list[TrackRecord],
    *,
    force_all: bool,
) -> list[EnrichedRow]:
    """Decide which rows to write to tracks.csv.

    Default (cumulative): every row in `final` survives, including orphans
    whose source playlist is no longer in playlists.json (because #5 pulls
    are selective and the user's selection can change).

    --force-all: only rows currently in playlists.json survive — orphans
    get dropped, the csv is genuinely rebuilt from scratch.
    """
    if force_all:
        return [final[t.spotify_id] for t in tracks_in_playlists if t.spotify_id in final]
    return list(final.values())


def run_summary(
    *,
    total: int,
    newly_enriched: int,
    still_missed: int,
    skipped: dict[str, int],
    getsongbpm_configured: bool,
) -> str:
    lines = [
        f"Run complete: {total} tracks total / {newly_enriched} newly enriched / {still_missed} still missed.",
    ]
    if any(skipped.values()):
        lines.append(
            f"  Skipped: {skipped['local_files']} local files, "
            f"{skipped['episodes_or_other']} episodes/other, "
            f"{skipped['duplicates']} duplicates."
        )
    if still_missed > 0 and not getsongbpm_configured:
        lines.append(
            f"\n{still_missed} tracks unenriched. Set up GetSongBPM as a fallback to "
            f"fill more rows. Walkthrough in scripts/README.md (#GetSongBPM-setup)."
        )
    return "\n".join(lines)


def _load_getsongbpm_key() -> Optional[str]:
    if not SECRETS_PATH.exists():
        return None
    try:
        data = json.loads(SECRETS_PATH.read_text(encoding="utf-8"))
        key = data.get("getsongbpm_api_key", "").strip()
        return key or None
    except (json.JSONDecodeError, OSError):
        return None


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="enrich",
        description="Enrich taste/tracks.csv from taste/playlists.json (ReccoBeats primary, GetSongBPM fallback).",
    )
    p.add_argument("--retry-misses", action="store_true",
                   help="Skip the 30-day TTL; retry every row with source=miss:*.")
    p.add_argument("--force-all", action="store_true",
                   help="Re-enrich every track from scratch (rebuilds tracks.csv).")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the enrichment plan; make no API calls.")
    p.add_argument("--limit", type=int, default=None,
                   help="Cap the number of tracks enriched (testing).")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    if not PLAYLISTS_PATH.exists():
        print(
            f"ERROR: {PLAYLISTS_PATH.relative_to(PROJECT_ROOT)} not found. "
            "Run /pull-spotify-data first (or ask Claude to pull it).",
            file=sys.stderr,
        )
        return 2

    tracks, skipped = load_and_dedupe(PLAYLISTS_PATH)
    existing = read_existing(TRACKS_CSV_PATH)
    now = dt.datetime.now(dt.timezone.utc)

    plan = plan_run(
        tracks,
        existing,
        now=now,
        force_all=args.force_all,
        retry_misses=args.retry_misses,
        limit=args.limit,
    )

    print(f"Plan: {len(plan)} tracks to enrich (of {len(tracks)} total deduped).")

    if args.dry_run:
        for t in plan[:20]:
            print(f"  {t.spotify_id} — {t.artist} — {t.title}")
        if len(plan) > 20:
            print(f"  ... and {len(plan) - 20} more")
        return 0

    getsongbpm_key = _load_getsongbpm_key()
    newly_enriched = 0

    # Merge: existing + new. Re-enriched rows override existing entries.
    final: dict[str, EnrichedRow] = dict(existing)
    for track in plan:
        try:
            row = _enrich_one(track, now=now, getsongbpm_key=getsongbpm_key)
        except ReccoBeatsRateLimited as e:
            print(
                f"\nReccoBeats rate-limited (Retry-After {e.retry_after_s}s). "
                "Stopping run; partial progress preserved. Resume with `python scripts/enrich.py`.",
                file=sys.stderr,
            )
            break
        final[track.spotify_id] = row
        if row.source in ("reccobeats", "getsongbpm"):
            newly_enriched += 1
        time.sleep(THROTTLE_SECONDS)

    # tracks.csv is CUMULATIVE by default — keep all enriched rows even if
    # their source playlist is no longer in playlists.json. #5 pulls are
    # selective and the user's selection can change between runs; orphaned
    # rows shouldn't be silently dropped. --force-all is the only flag that
    # rebuilds from scratch — under it we keep only rows present in the
    # current playlists.json.
    rows_to_write = merge_for_write(final, tracks, force_all=args.force_all)

    write_atomic(TRACKS_CSV_PATH, rows_to_write)

    still_missed = sum(1 for r in rows_to_write if r.source.startswith("miss:"))
    print()
    print(
        run_summary(
            total=len(rows_to_write),
            newly_enriched=newly_enriched,
            still_missed=still_missed,
            skipped=skipped,
            getsongbpm_configured=bool(getsongbpm_key),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Create the entrypoint wrapper**

Create `scripts/enrich.py`:

```python
"""Entrypoint wrapper for `python scripts/enrich.py`."""

import sys
from pathlib import Path

# Make the enrich/ package importable when this script is run directly.
sys.path.insert(0, str(Path(__file__).parent))

from enrich.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run the unit tests, verify they pass**

```bash
cd scripts
.venv/Scripts/python -m pytest tests/test_cli.py -v
cd ..
```

Expected: 9 PASSED.

- [ ] **Step 6: Run the full test suite for regressions**

```bash
cd scripts
.venv/Scripts/python -m pytest -v
cd ..
```

Expected: all tests pass (camelot 28 + playlists_loader 4 + models 2 + reccobeats 6 + getsongbpm 4 + csv_writer 5 + cli 9 = 58).

- [ ] **Step 7: Commit**

```bash
git add scripts/enrich/cli.py scripts/enrich.py scripts/tests/test_cli.py
git commit -m "$(cat <<'EOF'
feat(enrich): orchestrator — TTL retry, fallback chain, end-of-run summary

ReccoBeats first; GetSongBPM fallback only if api key configured;
miss otherwise. 30-day TTL on miss retries. ~1 req/sec throttle.
Stops cleanly on second 429; partial progress preserved.

scripts/enrich.py is a thin wrapper that imports enrich.cli.main —
keeps the spec-mandated entrypoint name without sys.path conflicts.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.10: Write `scripts/README.md`

**Files:**
- Create: `scripts/README.md`

- [ ] **Step 1: Write the README**

Create `scripts/README.md`:

```markdown
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

## Enrichment services

### ReccoBeats (primary, no setup)

Free, no API key required, accepts Spotify track IDs natively, returns the full Spotify-style audio-features vector. The script uses ReccoBeats first for every track.

### GetSongBPM (fallback, optional)

Used only when ReccoBeats misses. Provides BPM + key only. **Requires registration and a backlink to getsongbpm.com on a public site as a free-API condition** — this project includes the attribution in `taste/profile.md` (when generated by Subsystem #7) and in this README.

#### GetSongBPM setup walkthrough

If the script reports `X tracks unenriched. Set up GetSongBPM as a fallback…`, follow these steps:

1. Visit `https://getsongbpm.com/api` and register with an email address.
2. They send you an API key.
3. Open `C:\Users\desti\.crunchtronics-tutor-secrets\audio-enrichment.json`.
4. Set the `getsongbpm_api_key` field to your key:
   ```json
   { "getsongbpm_api_key": "your-key-here" }
   ```
5. Re-run `python scripts/enrich.py` (the script picks up the key automatically).

**Attribution: data via [getsongbpm.com](https://getsongbpm.com).**

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
```

- [ ] **Step 2: Commit**

```bash
git add scripts/README.md
git commit -m "$(cat <<'EOF'
docs(scripts): README with setup, CLI flags, GetSongBPM walkthrough

Includes the GetSongBPM attribution backlink as the ToS requires for
free-tier API access.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.11: Update CLAUDE.md with the audio-enrichment section

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Append the audio-enrichment section**

Add to the end of `CLAUDE.md` (after the "Spotify data" section from Task 1.2):

```markdown

## Audio enrichment

When Destin says "enrich my tracks" (or similar), run
`python scripts/enrich.py` from project root and surface the end-of-run
summary verbatim.

The script reads `taste/playlists.json` and writes `taste/tracks.csv`.
Incremental by default — only fetches missing rows + retries misses
older than 30 days. Flags: `--retry-misses`, `--force-all`, `--dry-run`,
`--limit N`. Full docs in `scripts/README.md`.

Primary service: **ReccoBeats** (no API key needed). Fallback:
**GetSongBPM** (key in
`C:\Users\desti\.crunchtronics-tutor-secrets\audio-enrichment.json` —
optional, see `scripts/README.md` for the setup walkthrough). If
unenriched count > 0 and GetSongBPM isn't configured, the script's
end-of-run summary will recommend setting it up; relay that summary
verbatim to Destin.

This subsystem overrides master spec §11 #2 (was: GetSongBPM primary)
and §7.2 (extends the column list with eight audio-feature columns).
See `docs/superpowers/specs/subsystems/06-audio-enrichment.md` §2.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude): wire audio-enrichment workflow into CLAUDE.md

Conversational trigger ("enrich my tracks"), invocation pattern,
service overview, and pointer to the subsystem spec for the master-spec
overrides documented in this subsystem.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 2.12: Update the secrets-dir README

**Files:**
- Modify: `C:\Users\desti\.crunchtronics-tutor-secrets\README.txt`

- [ ] **Step 1: Update the audio-enrichment.json section**

Read the current `C:\Users\desti\.crunchtronics-tutor-secrets\README.txt`. Replace the `audio-enrichment.json` section with:

```
audio-enrichment.json
  Holds the GetSongBPM API key (fallback enrichment service). Used by
  Subsystem #6 (Audio Feature Enrichment).

  Optional — Subsystem #6's primary service is ReccoBeats, which needs
  no key. GetSongBPM only fills coverage gaps. The script silently
  skips it if this file is missing or the key is empty.

  Expected shape:
    {
      "getsongbpm_api_key": "..."
    }

  Setup walkthrough: scripts/README.md (#GetSongBPM-setup) inside the
  Crunchtronics Tutor project.
```

(No commit step here — the secrets dir lives outside any git repo.)

### Task 2.13: Real end-to-end run against Destin's data

This is the verification gate. We run the enricher against the real `taste/playlists.json` from Phase 1 and confirm the verification gates from spec §5.

**Files:**
- Create: `taste/tracks.csv` (real data)

- [ ] **Step 1: Run the enricher dry to see the plan**

```bash
cd scripts
.venv/Scripts/python enrich.py --dry-run --limit 5
cd ..
```

Expected: prints "Plan: N tracks to enrich" with N >= 1, and lists 5 sample tracks.

- [ ] **Step 2: Run the enricher on a small batch first**

```bash
cd scripts
.venv/Scripts/python enrich.py --limit 5
cd ..
```

Expected: completes in ~10 seconds (5 tracks × ~1s throttle + API time). Prints "Run complete" summary. `taste/tracks.csv` exists with 5 rows.

- [ ] **Step 3: Spot-check tracks.csv**

```bash
head -1 taste/tracks.csv
head -6 taste/tracks.csv | column -t -s,
```

Verify: header line matches `CSV_COLUMNS` exactly; each data row has values in the metadata columns (artist/title/album); `source` is `reccobeats` for hits or `miss:reccobeats` for misses.

- [ ] **Step 4: Verify Camelot for 5 sampled rows**

For each enriched row, manually verify the Camelot value matches the standard key + the wheel:

```bash
awk -F, 'NR > 1 && $7 != "" {print $9, $8, $1}' taste/tracks.csv | head -5
```

Expected: prints `<key_standard> <key_camelot> <spotify_id>`. Cross-check at least 3 against the wheel:
- C major → 8B; A minor → 8A
- D major → 10B; B minor → 10A
- E major → 12B; C# minor → 12A

If all sampled rows match, the lookup is correct.

- [ ] **Step 5: Run the full enrichment**

Remove `--limit` and run end-to-end:

```bash
cd scripts
.venv/Scripts/python enrich.py
cd ..
```

This may take several minutes (1 sec per track × N tracks). Note the end-of-run summary numbers.

- [ ] **Step 6: Verify the verification gates from spec §5**

```bash
# Coverage: ReccoBeats hit rate >= 70%
python -c "
import csv
with open('taste/tracks.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
total = len(rows)
recco = sum(1 for r in rows if r['source'] == 'reccobeats')
pct = 100 * recco / total if total else 0
print(f'Total: {total}, ReccoBeats hits: {recco} ({pct:.1f}%)')
assert pct >= 70, f'Coverage {pct:.1f}% < 70% threshold'
print('Coverage gate PASSED')
"
```

If coverage is below 70%, investigate before declaring done. Common causes: many deep-cut/unreleased tracks; many local files (should have been filtered); ReccoBeats temporarily down for some IDs.

- [ ] **Step 7: Verify incremental behavior (re-run is a no-op)**

```bash
cd scripts
.venv/Scripts/python enrich.py
cd ..
```

Expected: `Plan: 0 tracks to enrich (of N total deduped).` — confirms incremental-skip works.

- [ ] **Step 8: Verify --retry-misses targets only miss rows**

```bash
cd scripts
.venv/Scripts/python enrich.py --retry-misses --dry-run
cd ..
```

Expected: `Plan: M tracks to enrich (of N total deduped).` where M equals the count of `miss:*` rows from Step 6.

- [ ] **Step 9: Commit `taste/tracks.csv`**

```bash
git add taste/tracks.csv
git commit -m "$(cat <<'EOF'
feat(taste): subsystem #6 — first real enrichment of tracks.csv

ReccoBeats covers <pct>% of deduped tracks via Spotify track ID lookup.
Remaining rows recorded as miss:reccobeats for 30-day TTL retry.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

(Replace `<pct>` with the actual percentage from Step 6.)

### Task 2.14: Final regression check

- [ ] **Step 1: Run the full test suite one more time**

```bash
cd scripts
.venv/Scripts/python -m pytest -v
cd ..
```

Expected: all 58 tests pass. No skips, no errors.

- [ ] **Step 2: Verify scope boundaries**

```bash
# No spotipy in the repo
grep -r "spotipy" scripts/ 2>/dev/null
# No /schedule entry created
grep -r "schedule" .claude/ 2>/dev/null
```

Expected: both return nothing.

- [ ] **Step 3: Commit any cleanup if needed**

If the prior steps surfaced anything that needs fixing, fix it and commit. Otherwise, this task is a no-op verification.

### Phase 2 Verification Gate (from subsystem spec §5)

- [ ] `scripts/enrich.py` exists and runs end-to-end on real `taste/playlists.json`
- [ ] `taste/tracks.csv` exists with the schema from §3.4 (header verified to match CSV_COLUMNS)
- [ ] At least 70% of deduped tracks have `source = "reccobeats"`
- [ ] Re-running `enrich.py` immediately after a successful run is a no-op
- [ ] Re-running with `--retry-misses` attempts only `miss:*` rows
- [ ] Camelot values verified correct against the wheel for 5 sampled rows
- [ ] `scripts/README.md` documents how to run, GetSongBPM setup walkthrough, and troubleshooting
- [ ] `CLAUDE.md` has the `## Audio enrichment` section
- [ ] `audio-enrichment.json` documented in the secrets-dir README (key not populated unless Destin opts in)

---

## Done criteria (Session C as a whole)

- [ ] Phase 1 verification gate passed
- [ ] Phase 2 verification gate passed
- [ ] All commits clean and atomic (no WIP / fixup commits)
- [ ] `git log --oneline | head -20` shows the Session C arc clearly
- [ ] Update `docs/superpowers/plans/2026-04-26-master-orchestration.md` Session C status to `[x] complete (2026-04-26 — N commits, plan at docs/superpowers/plans/2026-04-26-session-c-data-pull.md)` and check the three Step boxes — separate commit
- [ ] Subsystems #5 and #6 specs each get a final commit changing their `Status:` line from "Drafted (via brainstorm; awaiting user review)" to "Shipped 2026-04-26" — separate commit

---

## Self-review notes

**1. Spec coverage check:**

| Spec section | Implementing task |
|---|---|
| #5 §3.1 plugin dependency in CLAUDE.md | Task 1.2 |
| #5 §3.2 owns playlists.json | Task 1.3 |
| #5 §3.3 on-demand pull mechanism in CLAUDE.md | Task 1.2 |
| #5 §3.4 first-run verification | Task 1.3 |
| #6 §2.1 override of §11 #2 (ReccoBeats primary) | Tasks 2.6 + 2.9 |
| #6 §2.2 override of §7.2 (extended schema) | Task 2.8 (`CSV_COLUMNS` constant) |
| #6 §3.1 owns tracks.csv | Task 2.8 |
| #6 §3.2 incremental enrichment script | Task 2.9 |
| #6 §3.3 data flow (load → filter → dedupe → fallback chain → merge → summary) | Tasks 2.4 + 2.9 |
| #6 §3.4 schema | Task 2.8 |
| #6 §3.4.1 source values | Task 2.9 (`_enrich_one`) |
| #6 §3.5 CLI flags | Task 2.9 (`_build_arg_parser`) |
| #6 §3.6 invocation pattern | Task 2.11 (CLAUDE.md edit) |
| #6 §3.7 Camelot lookup | Task 2.3 |
| #6 §3.8 component layout | Tasks 2.1, 2.3–2.9 (each file maps to a task) |
| #6 §3.9 error handling | Tasks 2.6 (rate-limit + 5xx), 2.8 (corrupt csv), 2.9 (missing playlists.json + rate-limit stop) |
| #6 §3.10 audio-enrichment.json shape | Task 2.12 |
| #6 §3.11 CLAUDE.md edit | Task 2.11 |
| #6 §5 verification gates | Task 2.13 |

All spec sections have an implementing task. ✓

**2. Placeholder scan:** Searched for "TBD", "TODO", "implement later", "similar to". One reference to `<pct>` in Task 2.13 Step 9 commit message — that's literally the engineer filling in a real number from the prior step, not a placeholder for unspecified work. ✓

**3. Type consistency:**

- `EnrichmentResult` defined in Task 2.5; consumed by `reccobeats.fetch` (2.6), `getsongbpm.fetch` (2.7), and `cli._enrich_one` (2.9). Field names consistent across all three.
- `TrackRecord` defined in Task 2.4; consumed by `cli.plan_run` (2.9), `cli._enrich_one` (2.9). Consistent.
- `EnrichedRow` defined in Task 2.8; consumed by `cli.main` (2.9), `csv_writer.write_atomic` (2.8). Consistent.
- `CSV_COLUMNS` defined in Task 2.8; tested against the spec column list in `test_csv_writer::test_csv_columns_match_spec`. ✓
- `camelot_from_int_key` and `key_standard_from_int` defined in 2.3; called from `cli._to_enriched_row` (2.9). Consistent.
- `fetch` named identically in `reccobeats` and `getsongbpm` modules; imported with aliases in `cli.py` to disambiguate. ✓
- `ReccoBeatsRateLimited.retry_after_s` attribute used in test (Task 2.6) and caught in `cli.main` (Task 2.9). Consistent.
