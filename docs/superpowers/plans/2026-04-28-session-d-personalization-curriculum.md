# Session D — Personalization → Curriculum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Subsystem #7 (Taste Profile) and Subsystem #4 (Curriculum & Nudges) end-to-end so that `taste/profile.md`, 14 `knowledge/artists/<slug>.md` pages, and a real 12-lesson `curriculum.md` exist on disk and CLAUDE.md tells future Claude how to use them.

**Architecture:** Phase 1 builds a small `scripts/profile/` Python package (mirrors `scripts/enrich/` from Session C; stdlib only) that emits a structured aggregation JSON over `taste/tracks.csv`; Claude then writes `taste/profile.md` and the 14 named artist pages with web-search-verified resources. Phase 2 replaces the `curriculum.md` placeholder with the §3.3 schema + 12 seed lessons (8 fleshed + 4 stubs) and appends the curriculum/nudge section to CLAUDE.md. Both subsystems' workflows are conversational-trigger only — no scheduler.

**Tech Stack:** Python 3.12 (uv-managed `scripts/` project from Session C — no new deps); stdlib `csv`, `statistics`, `json`, `sys`; `pytest` for unit tests of aggregator functions; markdown for all user-facing artifacts.

**Specs this plan implements:**
- `docs/superpowers/specs/subsystems/07-taste-profile.md`
- `docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md`
- Master spec: `docs/superpowers/specs/2026-04-26-master-architecture.md` (overrides documented in §2 of the #4 spec)

**Build order:** Phase 1 (#7) before Phase 2 (#4). Phase 2's curriculum reads the `profile_anchors` field from `taste/profile.md`, so #7 must ship first.

**Inputs already on disk (verify before starting):**
- `taste/tracks.csv` (157 rows; 73.2% ReccoBeats coverage from Session C)
- `taste/playlists.json` (one playlist: "EDM")
- `knowledge/genres/{tech-house,dubstep,melodic-dubstep,bass-house}.md`
- `knowledge/theory/the-camelot-wheel.md`
- `scripts/pyproject.toml` + `scripts/.venv/` from Session C

---

## File Structure

**Phase 1 — Taste Profile (#7) creates / modifies:**

| Path | Action | Responsibility |
|---|---|---|
| `scripts/profile/__init__.py` | Create | Package marker (empty) |
| `scripts/profile/aggregator.py` | Create | Pure functions: `top_artists`, `bpm_histogram`, `camelot_distribution`, `key_split`, `feature_means` |
| `scripts/profile/reader.py` | Create | `load_tracks(path) -> list[dict]` — reads tracks.csv, no mutation |
| `scripts/profile_stats.py` | Create | CLI entrypoint; calls reader + aggregators; prints JSON to stdout |
| `scripts/tests/test_profile_aggregator.py` | Create | Unit tests for aggregator functions with synthetic rows |
| `scripts/tests/test_profile_reader.py` | Create | Unit tests for reader |
| `taste/profile.md` | Create | Prose narrative per spec §3.5; front matter with traceability fields |
| `knowledge/artists/disco-lines.md` | Create | Per spec §3.6; web-search-verified resources |
| `knowledge/artists/griz.md` | Create | Same |
| `knowledge/artists/bunt.md` | Create | Same |
| `knowledge/artists/jigitz.md` | Create | Same |
| `knowledge/artists/zeds-dead.md` | Create | Same |
| `knowledge/artists/subtronics.md` | Create | Same |
| `knowledge/artists/ian-asher.md` | Create | Same |
| `knowledge/artists/laszewo.md` | Create | Same |
| `knowledge/artists/john-summit.md` | Create | Same |
| `knowledge/artists/wooli.md` | Create | Same |
| `knowledge/artists/levity.md` | Create | Same |
| `knowledge/artists/nimino.md` | Create | Same |
| `knowledge/artists/nghtmre.md` | Create | Same |
| `knowledge/artists/odesza.md` | Create | Same |
| `knowledge/INDEX.md` | Modify | Replace artists-section placeholder with 14 entries |
| `CLAUDE.md` | Modify | Append "## Taste profile" section per spec §3.10 |

**Phase 2 — Curriculum & Nudges (#4) creates / modifies:**

| Path | Action | Responsibility |
|---|---|---|
| `curriculum.md` | Modify (full rewrite) | Replace Session A placeholder with §3.3 schema + 12-lesson seed |
| `CLAUDE.md` | Modify | Append "## Curriculum & nudges" section per spec §3.10 |
| `docs/superpowers/plans/2026-04-26-master-orchestration.md` | Modify | Mark Session D complete |

---

## Pattern for artist pages

Each of the 14 `knowledge/artists/<slug>.md` files follows this exact recipe. The 14 per-artist tasks (1.16–1.29) reuse it; reading them out of order is fine because all of them point back here.

**Step A — Compute artist-specific data from `taste/tracks.csv`.** Run from project root:

```bash
PYTHONIOENCODING=utf-8 python -c "
import csv, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
target = sys.argv[1]
with open('taste/tracks.csv', encoding='utf-8') as f:
    rows = [r for r in csv.DictReader(f) if r['artist'] == target]
print(f'Tracks: {len(rows)}')
keys = Counter(r['key_camelot'] for r in rows if r['key_camelot'])
print(f'Top Camelot keys: {keys.most_common(3)}')
bpms = [float(r['bpm']) for r in rows if r['bpm']]
if bpms:
    print(f'BPM range: {min(bpms):.1f}-{max(bpms):.1f} (mean {sum(bpms)/len(bpms):.1f})')
else:
    print('BPM: no enriched rows')
print('Sample tracks (first 5):')
for r in rows[:5]:
    print(f'  - {r[\"title\"]} ({r[\"album\"]})')
" "<artist name verbatim from CSV>"
```

**Step B — Web-search the resources.** Use the WebSearch tool. Three queries:

1. `splice "sounds of" <artist>` — confirm a Splice "Sounds of [artist]" pack is currently listed.
2. `<artist> preset pack serum vital` — find official preset packs (Serum / Vital / Phase Plant).
3. `<artist> production breakdown interview` — find a YouTube tutorial / Reddit AMA / Production Music Live breakdown.

For each result, include only if the search confirms a current product / live URL. Otherwise write `**no known pack**` or `**unverified — search inconclusive as of 2026-04-28**` (use the actual run date). Never invent.

**Step C — Write the markdown file.** Schema (every artist page):

```markdown
---
slug: <slug>
category: artists
tldr: "<one-sentence placement: genre, signature vibe, why they matter to Destin's taste; cite track count from Step A>"
prerequisites: [<primary genre slug from knowledge/genres/, e.g. tech-house>]
references:
  - "<resource type>: <URL or 'unverified — search inconclusive as of 2026-04-28'>"
next: <next artist slug alphabetically, or null for the last>
---

# <Artist (verbatim)>

## TL;DR
<2-3 sentences: genre placement, signature sound, why they're in Destin's library.>

## Cheat block
- **BPM range:** <from Step A; if no enriched rows, say "no enriched rows in current pull">
- **Common keys:** <top 1-3 Camelot from Step A; translate to human-readable using scripts/enrich/camelot.py if helpful>
- **Signature sound design:** <2-4 bullet points: bass character, lead synth tendencies, drum punch, vocal treatment — written from genuine knowledge of the artist, not invented>
- **Sample tracks from your library:** <3-5 titles from Step A's sample-tracks list>

## Resources
- **Splice "Sounds of <artist>" pack:** <verified URL, or "no known pack", or "unverified — search inconclusive as of 2026-04-28">
- **Preset packs:** <one bullet per verified pack with URL, or "no known pack">
- **Notable breakdowns / interviews:** <one bullet per verified link, or "no verified breakdown found">

## Read this yourself
<1-3 paragraphs: how this artist's production approach connects to Destin's likely interests; reference relevant knowledge/genres/*.md or knowledge/theory/*.md by relative path. Honest about what isn't well-known publicly.>

## See also
- `../genres/<primary-genre>.md`
- `<other artist slug>.md` (if a sibling artist is closely related)
- `../../taste/profile.md` (the source of this list)
```

**Step D — Spot-check the file.** Re-read; verify every external URL is either real, "no known pack", or "unverified — ..." with today's date. No fabricated links.

**Step E — Commit.** `git add knowledge/artists/<slug>.md && git commit -m "feat(taste): artist page — <Artist Name>"`.

---

## Phase 1 — Subsystem #7 (Taste Profile)

### Task 1.1: Set up the `scripts/profile/` package skeleton

**Files:**
- Create: `scripts/profile/__init__.py`
- Create: `scripts/profile/aggregator.py` (placeholder)
- Create: `scripts/profile/reader.py` (placeholder)

- [ ] **Step 1: Create the package directory and empty `__init__.py`**

```bash
mkdir -p scripts/profile
touch scripts/profile/__init__.py
```

- [ ] **Step 2: Create empty `aggregator.py` and `reader.py` placeholders**

Write `scripts/profile/aggregator.py`:

```python
"""Aggregation helpers for taste profile.

Pure functions over track records (rows from tracks.csv parsed as dicts).
Deterministic given the same input. No I/O.
"""
```

Write `scripts/profile/reader.py`:

```python
"""Read taste/tracks.csv into a list of row dicts. Stdlib csv only."""
```

- [ ] **Step 3: Verify the package imports**

```bash
cd scripts && uv run python -c "import profile; from profile import aggregator, reader; print('ok')"
```

Expected: `ok`. (If `uv run` fails, the Session C venv is missing — re-run `cd scripts && uv sync` first.)

- [ ] **Step 4: Commit**

```bash
git add scripts/profile/
git commit -m "feat(taste): scaffold scripts/profile package"
```

### Task 1.2: TDD `aggregator.py` — write the failing tests

**Files:**
- Create: `scripts/tests/test_profile_aggregator.py`

- [ ] **Step 1: Write the test file**

`scripts/tests/test_profile_aggregator.py`:

```python
"""Unit tests for scripts/profile/aggregator.py.

Tests use small synthetic row dicts shaped like tracks.csv rows. The CSV
itself isn't read here — that's reader.py's job.
"""
from profile.aggregator import (
    top_artists,
    bpm_histogram,
    camelot_distribution,
    key_split,
    feature_means,
)


def _row(**overrides):
    """Build a synthetic row with realistic defaults; override per-test."""
    base = {
        "spotify_id": "abc",
        "isrc": "US123",
        "artist": "Test Artist",
        "title": "Test Track",
        "album": "Test Album",
        "duration_s": "180",
        "bpm": "126.0",
        "key_camelot": "8A",
        "key_standard": "A minor",
        "mode": "0",
        "time_signature": "",
        "energy": "0.8",
        "danceability": "0.5",
        "valence": "0.3",
        "acousticness": "0.05",
        "instrumentalness": "0.1",
        "liveness": "0.2",
        "loudness": "-5.0",
        "speechiness": "0.05",
        "genre": "",
        "source": "reccobeats",
        "fetched_at": "2026-04-27T00:00:00Z",
    }
    base.update(overrides)
    return base


def test_top_artists_sorts_desc_by_count_then_alpha():
    rows = [
        _row(artist="Bravo"),
        _row(artist="Alpha"),
        _row(artist="Alpha"),
        _row(artist="Charlie"),
        _row(artist="Bravo"),
        _row(artist="Bravo"),
    ]
    result = top_artists(rows)
    assert result == [
        {"artist": "Bravo", "tracks": 3},
        {"artist": "Alpha", "tracks": 2},
        {"artist": "Charlie", "tracks": 1},
    ]


def test_top_artists_empty_input_returns_empty_list():
    assert top_artists([]) == []


def test_bpm_histogram_buckets_are_left_inclusive_right_exclusive():
    rows = [
        _row(bpm="100"),   # 100-110
        _row(bpm="109.99"),  # 100-110
        _row(bpm="110"),   # 110-124
        _row(bpm="124"),   # 124-128
        _row(bpm="127.99"),  # 124-128
        _row(bpm="128"),   # 128-138
        _row(bpm="144"),   # 144-150
        _row(bpm="160"),   # other (>=160)
        _row(bpm="80"),    # other (<100)
        _row(bpm=""),      # missing — excluded
    ]
    result = bpm_histogram(rows)
    assert result == {
        "100-110": 2,
        "110-124": 1,
        "124-128": 2,
        "128-138": 1,
        "138-142": 0,
        "144-150": 1,
        "150-160": 0,
        "other": 2,
    }


def test_camelot_distribution_excludes_empty_and_sorts_by_count_desc():
    rows = [
        _row(key_camelot="10A"),
        _row(key_camelot="10A"),
        _row(key_camelot="10A"),
        _row(key_camelot="8A"),
        _row(key_camelot="8A"),
        _row(key_camelot="3B"),
        _row(key_camelot=""),
    ]
    result = camelot_distribution(rows)
    assert result == [
        {"key": "10A", "count": 3},
        {"key": "8A", "count": 2},
        {"key": "3B", "count": 1},
    ]


def test_key_split_partitions_into_major_minor_unknown():
    rows = [
        _row(mode="0"),    # minor
        _row(mode="0"),    # minor
        _row(mode="1"),    # major
        _row(mode=""),     # unknown
        _row(mode=""),     # unknown
    ]
    assert key_split(rows) == {"major": 1, "minor": 2, "unknown": 2}


def test_feature_means_only_aggregates_reccobeats_rows():
    rows = [
        _row(source="reccobeats", energy="0.8", danceability="0.6"),
        _row(source="reccobeats", energy="0.6", danceability="0.4"),
        _row(source="getsongbpm", energy="", danceability=""),
        _row(source="miss:reccobeats", energy="", danceability=""),
    ]
    result = feature_means(rows)
    assert result["energy"] == 0.7
    assert result["danceability"] == 0.5


def test_feature_means_loudness_keeps_three_decimals():
    rows = [
        _row(source="reccobeats", loudness="-5.0"),
        _row(source="reccobeats", loudness="-7.0"),
    ]
    result = feature_means(rows)
    assert result["loudness"] == -6.0


def test_feature_means_empty_input_returns_none_for_each_metric():
    result = feature_means([])
    for k in ("energy", "danceability", "valence", "acousticness",
              "instrumentalness", "liveness", "loudness", "speechiness"):
        assert result[k] is None
```

- [ ] **Step 2: Run tests; verify they fail with import errors**

```bash
cd scripts && uv run pytest tests/test_profile_aggregator.py -v
```

Expected: every test fails with `ImportError` (the functions don't exist yet).

- [ ] **Step 3: Commit (red)**

```bash
git add scripts/tests/test_profile_aggregator.py
git commit -m "test(taste): aggregator unit tests (red)"
```

### Task 1.3: Implement `aggregator.py`

**Files:**
- Modify: `scripts/profile/aggregator.py`

- [ ] **Step 1: Write the implementation**

Replace `scripts/profile/aggregator.py` with:

```python
"""Aggregation helpers for taste profile.

Pure functions over track records (rows from tracks.csv parsed as dicts).
Deterministic given the same input. No I/O.
"""
from collections import Counter
from statistics import mean
from typing import Optional


_BPM_BUCKETS = [
    ("100-110", 100.0, 110.0),
    ("110-124", 110.0, 124.0),
    ("124-128", 124.0, 128.0),
    ("128-138", 128.0, 138.0),
    ("138-142", 138.0, 142.0),
    ("144-150", 144.0, 150.0),
    ("150-160", 150.0, 160.0),
]


_FEATURE_KEYS = (
    "energy",
    "danceability",
    "valence",
    "acousticness",
    "instrumentalness",
    "liveness",
    "loudness",
    "speechiness",
)


def top_artists(rows: list[dict]) -> list[dict]:
    """Sort artists by track count desc, ties broken alphabetically."""
    counts = Counter(r["artist"] for r in rows)
    return [
        {"artist": a, "tracks": n}
        for a, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]


def bpm_histogram(rows: list[dict]) -> dict[str, int]:
    """Bucket rows by BPM into named bands. Empty bpm cells excluded."""
    buckets: dict[str, int] = {name: 0 for name, _, _ in _BPM_BUCKETS}
    buckets["other"] = 0
    for row in rows:
        raw = row.get("bpm", "")
        if not raw:
            continue
        bpm = float(raw)
        for name, lo, hi in _BPM_BUCKETS:
            if lo <= bpm < hi:
                buckets[name] += 1
                break
        else:
            buckets["other"] += 1
    return buckets


def camelot_distribution(rows: list[dict]) -> list[dict]:
    """Camelot keys with counts, desc by count, ties alpha. Empty cells excluded."""
    counts = Counter(r["key_camelot"] for r in rows if r.get("key_camelot"))
    return [
        {"key": k, "count": n}
        for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]


def key_split(rows: list[dict]) -> dict[str, int]:
    """Partition rows into major / minor / unknown by `mode`."""
    out = {"major": 0, "minor": 0, "unknown": 0}
    for row in rows:
        mode = row.get("mode", "")
        if mode == "1":
            out["major"] += 1
        elif mode == "0":
            out["minor"] += 1
        else:
            out["unknown"] += 1
    return out


def feature_means(rows: list[dict]) -> dict[str, Optional[float]]:
    """Mean of each numeric audio feature over `source = reccobeats` rows only.

    GetSongBPM rows leave audio-feature columns empty (#6 spec §3.4.1), so a
    mixed average would be misleading. Returns None per metric when no
    reccobeats rows are present.
    """
    reccobeats_rows = [r for r in rows if r.get("source") == "reccobeats"]
    out: dict[str, Optional[float]] = {}
    for key in _FEATURE_KEYS:
        values = []
        for row in reccobeats_rows:
            raw = row.get(key, "")
            if raw:
                values.append(float(raw))
        if not values:
            out[key] = None
        else:
            decimals = 3 if key == "loudness" else 2
            out[key] = round(mean(values), decimals)
    return out
```

- [ ] **Step 2: Run tests; verify they pass**

```bash
cd scripts && uv run pytest tests/test_profile_aggregator.py -v
```

Expected: all 8 tests pass.

- [ ] **Step 3: Commit (green)**

```bash
git add scripts/profile/aggregator.py
git commit -m "feat(taste): aggregator implementation"
```

### Task 1.4: TDD `reader.py` — write failing tests, implement, verify

**Files:**
- Create: `scripts/tests/test_profile_reader.py`
- Modify: `scripts/profile/reader.py`

- [ ] **Step 1: Write the test file**

`scripts/tests/test_profile_reader.py`:

```python
"""Unit tests for scripts/profile/reader.py."""
import csv
from pathlib import Path

import pytest

from profile.reader import load_tracks


SCHEMA_COLUMNS = [
    "spotify_id", "isrc", "artist", "title", "album", "duration_s",
    "bpm", "key_camelot", "key_standard", "mode", "time_signature",
    "energy", "danceability", "valence", "acousticness", "instrumentalness",
    "liveness", "loudness", "speechiness",
    "genre", "source", "fetched_at",
]


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in SCHEMA_COLUMNS})


def test_load_tracks_returns_list_of_dicts(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    _write_csv(csv_path, [
        {"spotify_id": "a", "artist": "Foo", "title": "Bar", "source": "reccobeats"},
        {"spotify_id": "b", "artist": "Baz", "title": "Qux", "source": "miss:reccobeats"},
    ])
    rows = load_tracks(csv_path)
    assert isinstance(rows, list)
    assert len(rows) == 2
    assert rows[0]["artist"] == "Foo"
    assert rows[1]["source"] == "miss:reccobeats"


def test_load_tracks_preserves_empty_cells_as_empty_strings(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    _write_csv(csv_path, [{"spotify_id": "a", "artist": "Foo", "bpm": ""}])
    rows = load_tracks(csv_path)
    assert rows[0]["bpm"] == ""


def test_load_tracks_raises_filenotfounderror_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_tracks(tmp_path / "does-not-exist.csv")
```

- [ ] **Step 2: Run tests; verify they fail**

```bash
cd scripts && uv run pytest tests/test_profile_reader.py -v
```

Expected: ImportError on `load_tracks`.

- [ ] **Step 3: Implement `reader.py`**

Replace `scripts/profile/reader.py` with:

```python
"""Read taste/tracks.csv into a list of row dicts. Stdlib csv only."""
import csv
from pathlib import Path


def load_tracks(path: Path | str) -> list[dict]:
    """Return tracks.csv rows as a list of dicts.

    Empty cells stay as empty strings (no None / type coercion). Caller is
    responsible for parsing numeric fields when needed.
    """
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
```

- [ ] **Step 4: Run tests; verify they pass**

```bash
cd scripts && uv run pytest tests/test_profile_reader.py -v
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/tests/test_profile_reader.py scripts/profile/reader.py
git commit -m "feat(taste): reader for tracks.csv"
```

### Task 1.5: Implement `scripts/profile_stats.py` entrypoint

**Files:**
- Create: `scripts/profile_stats.py`

- [ ] **Step 1: Write the entrypoint**

`scripts/profile_stats.py`:

```python
"""CLI: emit aggregation JSON over taste/tracks.csv to stdout.

Run from project root:
    python scripts/profile_stats.py

Spec: docs/superpowers/specs/subsystems/07-taste-profile.md §3.4
"""
import json
import sys
from pathlib import Path

# Make the local `profile` package importable when invoked via
# `python scripts/profile_stats.py` from project root.
sys.path.insert(0, str(Path(__file__).parent))

from profile.aggregator import (
    top_artists,
    bpm_histogram,
    camelot_distribution,
    key_split,
    feature_means,
)
from profile.reader import load_tracks


def build_stats(rows: list[dict]) -> dict:
    enriched = [r for r in rows if not r.get("source", "").startswith("miss:")]
    return {
        "row_count": len(rows),
        "enriched_count": len(enriched),
        "missing_count": len(rows) - len(enriched),
        "top_artists": top_artists(rows),
        "bpm_histogram": bpm_histogram(rows),
        "camelot_distribution": camelot_distribution(rows),
        "key_split": key_split(rows),
        "feature_means": feature_means(rows),
    }


def main() -> int:
    csv_path = Path("taste/tracks.csv")
    if not csv_path.exists():
        print(
            f"error: {csv_path} not found. Run audio enrichment first "
            f"(see CLAUDE.md → Audio enrichment).",
            file=sys.stderr,
        )
        return 1
    rows = load_tracks(csv_path)
    stats = build_stats(rows)
    json.dump(stats, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Smoke-test against the real tracks.csv**

```bash
PYTHONIOENCODING=utf-8 python scripts/profile_stats.py | head -40
```

Expected: well-formed JSON beginning with `{ "row_count": 157, "enriched_count": 115, "missing_count": 42, "top_artists": [...] }`. The `top_artists` array's first entry must be `{"artist": "Disco Lines", "tracks": 12}`.

- [ ] **Step 3: Verify total counts match expectations**

```bash
PYTHONIOENCODING=utf-8 python -c "
import json, subprocess
out = subprocess.run(['python', 'scripts/profile_stats.py'], capture_output=True, text=True, check=True).stdout
s = json.loads(out)
assert s['row_count'] == 157, s['row_count']
assert s['enriched_count'] == 115, s['enriched_count']
assert s['missing_count'] == 42, s['missing_count']
assert s['top_artists'][0] == {'artist': 'Disco Lines', 'tracks': 12}, s['top_artists'][0]
assert s['key_split']['major'] + s['key_split']['minor'] + s['key_split']['unknown'] == 157
print('ok')
"
```

Expected: `ok`.

- [ ] **Step 4: Commit**

```bash
git add scripts/profile_stats.py
git commit -m "feat(taste): profile_stats CLI emitting aggregation JSON"
```

### Task 1.6: Add the "Taste profile" section to `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` (append after the "## Audio enrichment" section)

- [ ] **Step 1: Append the new section verbatim**

Append to the end of `CLAUDE.md`:

```markdown

## Taste profile

When Destin says "regenerate the taste profile" (or similar), run
`python scripts/profile_stats.py` from project root, then write
`taste/profile.md` and the 14 artist pages listed in
`docs/superpowers/specs/subsystems/07-taste-profile.md` §3.2.

Every external resource on an artist page must be web-search-verified at
authoring time. If a search returns nothing, the page says "no known pack"
or "unverified — search inconclusive as of YYYY-MM-DD". Never fabricate
Splice packs, preset packs, or interview links.

The profile is regenerated on demand only — there is no automatic
trigger. Subsystem #4 may notice drift via `generated_from_profile` and
suggest regenerating, but never regenerates automatically.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude): wire taste-profile workflow into CLAUDE.md"
```

### Task 1.7: Generate `taste/profile.md` from real data

**Files:**
- Create: `taste/profile.md`

This task is the prose-authoring step that the `scripts/profile_stats.py` JSON drives. Claude is the author; the script is the source of numerical truth.

- [ ] **Step 1: Capture the aggregation JSON**

```bash
PYTHONIOENCODING=utf-8 python scripts/profile_stats.py > /tmp/profile-stats.json
cat /tmp/profile-stats.json
```

Expected: the JSON shape from `07-taste-profile.md` §3.4 with real numbers from the EDM playlist.

- [ ] **Step 2: Translate Camelot codes for the prose**

Note (for the writer) — the prose in "Key bias" wants human-readable keys, not just Camelot codes. Use the existing lookup at `scripts/enrich/camelot.py` to translate. Top Camelot codes from the JSON map back to e.g. `B minor (10A)`, `A minor (8A)`.

- [ ] **Step 3: Write `taste/profile.md` per spec §3.5**

The file has this exact structure (substitute real numbers from Step 1; aim for a tight, factual TL;DR — no marketing voice):

```markdown
---
generated_at: <UTC ISO 8601 timestamp at write time>
row_count: <from JSON>
enriched_count: <from JSON>
top_artists_at_generation: [<first 5 names from JSON top_artists>]
profile_anchors: [tech-house, melodic-dubstep, dubstep, bass-house]
---

# Destin's taste profile (auto-generated <YYYY-MM-DD>)

## TL;DR
You listen to <row_count> tracks across 1 playlist ("EDM"). <enriched_count>
have audio-feature data; <missing_count> are awaiting GetSongBPM fallback or
manual entry. Your taste centers on EDM with two strong tempo anchors —
124-128 BPM (tech house) and 144-150 BPM (dubstep / bass house) — plus an
adjacent cluster around 138-142 (melodic dubstep).

## BPM clusters
Bucket the BPM histogram from the JSON. One bullet per non-zero bucket, e.g.:
- 124-128 BPM: <count> tracks (tech house — Disco Lines, John Summit territory)
- 138-142 BPM: <count> tracks (melodic dubstep — Wooli / ILLENIUM territory)
- 144-150 BPM: <count> tracks (dubstep / bass house — Subtronics, jigitz, GRiZ)
- 150-160 BPM: <count> tracks (drum-and-bass-adjacent)
- ...

## Key bias
Most common Camelot keys (translate to human-readable using
scripts/enrich/camelot.py):
- <key> (<count> tracks)
- <key> (<count> tracks)
- ...

Mode split: <major>% major / <minor>% minor / <unknown>% unknown (the
unknown share equals the miss-row count — those rows lack mode data).

## Top artists & subgenres
- **Disco Lines (12 tracks)** — tech-house with vocal-driven hooks.
- **GRiZ (11 tracks)** — electronic-soul / live-band electronic.
- **BUNT. (9 tracks)** — melodic dance / future-bass-leaning.
- **jigitz (7 tracks)** — bass house, named taste anchor in master spec.
- **Zeds Dead (6 tracks)** — dubstep / bass.
- **Subtronics (5 tracks)** — riddim / dubstep, named anchor.
- **Ian Asher (5 tracks)** — melodic / synth-pop electronic.
- **Łaszewo (5 tracks)** — alt-electronic / indie-leaning.
- **John Summit (5 tracks)** — tech-house, named anchor.

## Resources surface area
List artists with verified Splice packs and preset packs (after the artist
pages are authored — this section may be a stub on first generation and
filled in once the artist pages are written, OR populated in this same
sitting if artist authoring already happened. Order of operations is:
profile.md first, then artist pages, then come back here to update if
needed).

- Artists with verified Splice "Sounds of" packs: <list>
- Artists with verified preset packs: <list>
- Cheapest leverage for buying study materials: <one-sentence
  recommendation given the verified resources>
```

- [ ] **Step 4: Verify prose claims match the JSON**

Re-read the written profile. Cross-check:
- TL;DR's track counts match `row_count` / `enriched_count` / `missing_count` from the JSON.
- BPM cluster bullets quote counts from the histogram exactly.
- Top artists list matches `top_artists_at_generation` in front matter.
- Mode split percentages reconcile to `key_split` totals.

- [ ] **Step 5: Commit**

```bash
git add taste/profile.md
git commit -m "feat(taste): first taste/profile.md from real data"
```

### Task 1.8 — 1.21: Author the 14 artist pages

Each task follows the **Pattern for artist pages** at the top of this plan (Steps A → E). Per-artist data below; `<placeholder>` values are looked up at task time via Step A's bash command and Step B's web search.

**Reading order (alphabetical by slug for consistency with the `next` field):** bunt → disco-lines → griz → ian-asher → jigitz → john-summit → laszewo → levity → nghtmre → nimino → odesza → subtronics → wooli → zeds-dead.

For the `next` field in each page's front matter, use this exact chain:

| Page | `next:` value |
|---|---|
| bunt | disco-lines |
| disco-lines | griz |
| griz | ian-asher |
| ian-asher | jigitz |
| jigitz | john-summit |
| john-summit | laszewo |
| laszewo | levity |
| levity | nghtmre |
| nghtmre | nimino |
| nimino | odesza |
| odesza | subtronics |
| subtronics | wooli |
| wooli | zeds-dead |
| zeds-dead | (omit `next` field — last in chain) |

#### Task 1.8: BUNT. (`bunt`)

- CSV artist name (verbatim, for Step A): `BUNT.`
- Slug: `bunt`
- Track count: 9
- Primary genre: melodic-bass / future-bass leaning. Authoring choice — consult their Spotify catalog and pick between `prerequisites: [melodic-dubstep]` (closest existing genre cheat sheet) or `prerequisites: [bass-house]`. Prefer melodic-dubstep if the catalog leans melodic; bass-house if it leans drop-heavy.

Apply Steps A–E from the **Pattern for artist pages**.

#### Task 1.9: Disco Lines (`disco-lines`)

- CSV artist name: `Disco Lines`
- Slug: `disco-lines`
- Track count: 12 (rank 1)
- Primary genre: tech-house. `prerequisites: [tech-house]`.

Apply Steps A–E.

#### Task 1.10: GRiZ (`griz`)

- CSV artist name: `GRiZ`
- Slug: `griz`
- Track count: 11 (rank 2)
- Primary genre: electronic-soul / live-band electronic. No exact match in `knowledge/genres/` — pick the closest current cheat sheet. GRiZ's catalog spans bass and funk-soul; `prerequisites: [bass-house]` is the safest existing pointer. If during authoring it's clearly more melodic-dubstep-leaning for Destin's specific tracks, use that instead. Document the choice briefly in the TL;DR.

Apply Steps A–E.

#### Task 1.11: Ian Asher (`ian-asher`)

- CSV artist name: `Ian Asher`
- Slug: `ian-asher`
- Track count: 5
- Primary genre: melodic / synth-pop-leaning electronic. `prerequisites: [melodic-dubstep]` is closest; flag in TL;DR that Ian Asher is more pop-leaning than the canonical melodic-dubstep artists.

Apply Steps A–E.

#### Task 1.12: jigitz (`jigitz`)

- CSV artist name: `jigitz`
- Slug: `jigitz`
- Track count: 7. Master-spec named taste anchor.
- Primary genre: bass house. `prerequisites: [bass-house]`.

Apply Steps A–E. Mention master-spec anchor status in the TL;DR.

#### Task 1.13: John Summit (`john-summit`)

- CSV artist name: `John Summit`
- Slug: `john-summit`
- Track count: 5. Master-spec named taste anchor.
- Primary genre: tech-house. `prerequisites: [tech-house]`.

Apply Steps A–E. Mention master-spec anchor status in the TL;DR. `knowledge/genres/tech-house.md` already names John Summit as Destin's confirmed taste anchor — cross-link.

#### Task 1.14: Łaszewo (`laszewo`)

- CSV artist name: `Łaszewo` (use the unicode `Ł` verbatim when running Step A)
- Slug: `laszewo`
- Track count: 5
- Primary genre: alt-electronic / indie-leaning. No good match in current `knowledge/genres/`. `prerequisites: [melodic-dubstep]` as the nearest melodic anchor; flag in the TL;DR that Łaszewo is genre-adjacent to the existing cheat sheets.

Apply Steps A–E. Test that the Step A bash command handles the unicode artist name correctly (the `PYTHONIOENCODING=utf-8` env var is required).

#### Task 1.15: Levity (`levity`)

- CSV artist name: `Levity`
- Slug: `levity`
- Track count: 4. Hand-picked by Destin during brainstorm.
- Primary genre: melodic dubstep. `prerequisites: [melodic-dubstep]`.

Apply Steps A–E.

#### Task 1.16: NGHTMRE (`nghtmre`)

- CSV artist name: `NGHTMRE`
- Slug: `nghtmre`
- Track count: 3. Hand-picked.
- Primary genre: bass / trap-leaning electronic. `prerequisites: [bass-house]` or `[dubstep]` — pick based on the artist's predominant catalog. NGHTMRE leans heavier than tech-house but not pure riddim.

Apply Steps A–E.

#### Task 1.17: nimino (`nimino`)

- CSV artist name: `nimino`
- Slug: `nimino`
- Track count: 4. Hand-picked.
- Primary genre: melodic-bass / chill-bass. `prerequisites: [melodic-dubstep]`.

Apply Steps A–E.

#### Task 1.18: ODESZA (`odesza`)

- CSV artist name: `ODESZA`
- Slug: `odesza`
- Track count: 3. Hand-picked.
- Primary genre: indie-electronic / chill-bass. No exact match — `prerequisites: [melodic-dubstep]` is closest by tempo and emotional register.

Apply Steps A–E.

#### Task 1.19: Subtronics (`subtronics`)

- CSV artist name: `Subtronics`
- Slug: `subtronics`
- Track count: 5. Master-spec named taste anchor.
- Primary genre: riddim / dubstep. `prerequisites: [dubstep]`.

Apply Steps A–E. Mention master-spec anchor status in the TL;DR.

#### Task 1.20: Wooli (`wooli`)

- CSV artist name: `Wooli`
- Slug: `wooli`
- Track count: 1. Master-spec named taste anchor (under-represented in the EDM playlist; included by spec).
- Primary genre: melodic dubstep. `prerequisites: [melodic-dubstep]`.

Apply Steps A–E. The TL;DR must note both the master-spec-anchor status and the under-representation in the current data ("only 1 track in the current EDM-playlist pull, but a confirmed taste anchor — expect more on a future Spotify pull").

#### Task 1.21: Zeds Dead (`zeds-dead`)

- CSV artist name: `Zeds Dead`
- Slug: `zeds-dead`
- Track count: 6 (rank 5)
- Primary genre: dubstep / bass. `prerequisites: [dubstep]`.

Apply Steps A–E. **Last in chain** — omit the `next:` field from front matter.

### Task 1.22: Update `knowledge/INDEX.md` artist section

**Files:**
- Modify: `knowledge/INDEX.md`

The current artists section reads:

```markdown
## artists
*(empty — populated by Session D / Subsystem #7 once the taste profile lands.)*
```

- [ ] **Step 1: Replace the placeholder with 14 entries**

Replace the placeholder line with one entry per artist, in the same alphabetical order used by `next`:

```markdown
## artists
- [bunt](artists/bunt.md) — <tldr from bunt.md front matter>
- [disco-lines](artists/disco-lines.md) — <tldr from disco-lines.md front matter>
- [griz](artists/griz.md) — <tldr from griz.md front matter>
- [ian-asher](artists/ian-asher.md) — <tldr from ian-asher.md front matter>
- [jigitz](artists/jigitz.md) — <tldr from jigitz.md front matter>
- [john-summit](artists/john-summit.md) — <tldr from john-summit.md front matter>
- [laszewo](artists/laszewo.md) — <tldr from laszewo.md front matter>
- [levity](artists/levity.md) — <tldr from levity.md front matter>
- [nghtmre](artists/nghtmre.md) — <tldr from nghtmre.md front matter>
- [nimino](artists/nimino.md) — <tldr from nimino.md front matter>
- [odesza](artists/odesza.md) — <tldr from odesza.md front matter>
- [subtronics](artists/subtronics.md) — <tldr from subtronics.md front matter>
- [wooli](artists/wooli.md) — <tldr from wooli.md front matter>
- [zeds-dead](artists/zeds-dead.md) — <tldr from zeds-dead.md front matter>
```

- [ ] **Step 2: Commit**

```bash
git add knowledge/INDEX.md
git commit -m "docs(knowledge): index 14 artist pages from taste profile"
```

### Task 1.23: Phase 1 verification gate (#7)

This task runs the spec §5 verification gate items as commands and inspections; it is a stop-gate before Phase 2.

- [ ] **Step 1: Verify the script produces valid JSON**

```bash
PYTHONIOENCODING=utf-8 python scripts/profile_stats.py | python -m json.tool > /dev/null && echo ok
```

Expected: `ok`.

- [ ] **Step 2: Verify the package layout**

```bash
ls scripts/profile/
```

Expected: at minimum `__init__.py`, `aggregator.py`, `reader.py`.

- [ ] **Step 3: Verify no new dependencies in pyproject.toml**

```bash
git diff origin/master -- scripts/pyproject.toml
```

Expected: no diff (or only formatting). If new deps were added, revert — the spec forbids them.

- [ ] **Step 4: Verify all unit tests pass**

```bash
cd scripts && uv run pytest -v
```

Expected: all profile-related tests pass; existing #6 tests still pass.

- [ ] **Step 5: Verify `taste/profile.md` has all five §7.4 sections**

```bash
grep -c "^## " taste/profile.md
```

Expected: `5` (TL;DR, BPM clusters, Key bias, Top artists & subgenres, Resources surface area).

- [ ] **Step 6: Verify all 14 artist pages exist with correct slugs**

```bash
ls knowledge/artists/*.md | wc -l
```

Expected: `14`.

```bash
for slug in bunt disco-lines griz ian-asher jigitz john-summit laszewo levity nghtmre nimino odesza subtronics wooli zeds-dead; do
  test -f "knowledge/artists/${slug}.md" || echo "MISSING: ${slug}"
done
```

Expected: no output (all present).

- [ ] **Step 7: Verify `knowledge/INDEX.md` lists all 14**

```bash
grep -c "^- \[" knowledge/INDEX.md
```

Expected: at least 14 lines under the artists section (count overall list items will be higher because of theory/ableton/genres/mpk-mini-4 entries — visually inspect that the 14 artist entries appear).

- [ ] **Step 8: Spot-check 3 sampled artist pages for fabricated resources**

Open `knowledge/artists/disco-lines.md`, `knowledge/artists/subtronics.md`, `knowledge/artists/wooli.md`. For each Splice / preset / breakdown line, verify it is one of: a working URL, `**no known pack**`, or `**unverified — search inconclusive as of 2026-04-28**` (with the actual run date). Any line that names a Splice pack or product without a verified URL is a fabrication and must be replaced.

- [ ] **Step 9: Verify the CLAUDE.md taste-profile section is present**

```bash
grep -c "^## Taste profile$" CLAUDE.md
```

Expected: `1`.

- [ ] **Step 10: Phase 1 checkpoint commit (if any straggler edits)**

```bash
git status
```

Expected: clean tree. If there are any uncommitted changes from the verification, commit them with `git commit -m "chore(taste): phase 1 verification cleanups"` before proceeding.

---

## Phase 2 — Subsystem #4 (Curriculum & Nudges)

### Task 2.1: Replace `curriculum.md` with real schema + 12-lesson seed

**Files:**
- Modify: `curriculum.md` (full rewrite — the existing content is the Session A placeholder)

- [ ] **Step 1: Read `taste/profile.md` to copy the `profile_anchors`**

```bash
head -10 taste/profile.md
```

Capture the `profile_anchors` array and `generated_at` timestamp; both are needed in the curriculum's front matter.

- [ ] **Step 2: Rewrite `curriculum.md`**

Replace the entire contents of `curriculum.md` with:

```markdown
---
last_updated: <UTC ISO 8601 timestamp at write time>
next: lesson-001
generated_from_profile: <generated_at value from taste/profile.md>
profile_anchors: [<copied from taste/profile.md>]
---

# Curriculum

> Schema reference: `docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md` §3.3.
> Seed authored Session D, 2026-04-28.

## lesson-001: MPK ↔ Ableton first connection [active]

- **Why next:** Foundation. Master spec §11 #8 — hardware and software learned
  together from day 1; nothing else works until the MPK is sounding through
  Ableton.
- **Estimated time:** 30 min
- **Depends on:** none
- **Hardware:** MPK USB cable connected to PC; Ableton Live 12 Lite open.
- **Practice task:** Connect the MPK over USB, verify Ableton shows it under
  Preferences → Link/Tempo/MIDI, arm a MIDI track, and play notes from the
  MPK keys. If a sound doesn't come out, walk through the troubleshooting
  steps in `knowledge/mpk-mini-4/pads-vs-keys-vs-knobs.md` and
  `knowledge/ableton/the-browser.md`. If you can't find a screen element,
  prefer `knowledge/ableton/companion-mode.md` over guessing.
- **Done criteria:**
  - [ ] MPK appears as a Control Surface or Input device in Ableton's
        Preferences → Link/Tempo/MIDI panel
  - [ ] Pressing an MPK key produces sound through a default Ableton
        instrument (Operator preset or Drum Rack)
  - [ ] Ableton's transport (play/stop) responds to the MPK's transport
        buttons (or you've consciously decided to use the on-screen
        transport instead)
- **Notes:**

## lesson-002: Map MPK pads to Drum Rack, play kick + clap [blocked]

- **Why blocked:** depends on lesson-001 (need the MPK already routed into Ableton).
- **Why next once unblocked:** First real beat-making exercise; gets the pads
  feeling tactile before any genre work begins.
- **Estimated time:** 30 min
- **Depends on:** lesson-001
- **Hardware:** MPK pads (8 pads → MIDI notes C1-D#2 per
  `knowledge/ableton/drum-rack-basics.md`).
- **Practice task:** Following `knowledge/mpk-mini-4/mapping-pads-to-drum-rack.md`,
  drop a Drum Rack onto a MIDI track, load a 909 kick on pad 1 and a clap on
  pad 2, and play a "kick on 1 and 3, clap on 2 and 4" pattern by hand. Loop
  it for 30 seconds at 126 BPM and tap along on the pads.
- **Done criteria:**
  - [ ] Drum Rack on a MIDI track with kick on pad 1 (C1) and clap on pad 2 (C#1)
  - [ ] Project tempo set to 126 BPM
  - [ ] You can play the kick-clap-kick-clap pattern by feel without looking
        at the screen
  - [ ] Saved at projects/lesson-002-pads.als
- **Notes:**

## lesson-003: Four-on-the-floor at 126 BPM [blocked]

- **Why blocked:** depends on lesson-002 (kick + clap pad muscle memory).
- **Why next once unblocked:** Tech house is the dominant cluster in your
  taste profile (the 124-128 BPM bucket is the largest). Four-on-the-floor
  is the genre's foundational groove per `knowledge/genres/tech-house.md`.
- **Estimated time:** 45 min
- **Depends on:** lesson-002
- **Hardware:** MPK pads for kick / clap / hi-hat; MPK keys not used yet.
- **Practice task:** Build a 16-bar four-on-the-floor pattern in MIDI per
  the structure in `knowledge/genres/tech-house.md` Cheat block: kick on
  every beat (1, 2, 3, 4), clap on 2 and 4, open hi-hat on the off-beats
  ("and"s). Quantize the kicks tight; leave the hat with a touch of swing
  if it feels human. Loop for at least 60 seconds and listen for the
  "tss-tss" pulse the cheat sheet describes.
- **Done criteria:**
  - [ ] 4 bars of MIDI on the kick track with hits on beats 1, 2, 3, 4
        (not 16th-resolution bounce — straight quarters)
  - [ ] Clap on beats 2 and 4 of every bar
  - [ ] Open hi-hat on every off-beat (the "and" of 1, 2, 3, 4)
  - [ ] Saved at projects/lesson-003-four-on-floor.als
- **Notes:**

## lesson-004: First sidechained bass — the tech-house signature [blocked]

- **Why blocked:** depends on lesson-003 (need the kick pattern as the sidechain trigger).
- **Why next once unblocked:** Sidechain compression is the single defining
  technique of tech house per `knowledge/genres/tech-house.md`. This is the
  payoff for the foundation work — the moment your project starts sounding
  like the genre you listen to.
- **Estimated time:** 60 min
- **Depends on:** lesson-003
- **Hardware:** MPK keys for the bass note; pads still drive the drums.
- **Practice task:** On a new MIDI track, play a single sustained bass note
  in C1 (use Operator with a simple sub-bass preset). Insert an Ableton
  Compressor on the bass track; in the compressor's sidechain panel, set
  the source to your kick track. Tune threshold + ratio until the bass
  ducks 3-6 dB on every kick hit. Reference: `knowledge/genres/tech-house.md`
  (sidechain section), `knowledge/ableton/the-mixer.md`. If you can't find
  the sidechain dropdown, use `knowledge/ableton/companion-mode.md`.
- **Done criteria:**
  - [ ] Bass track has a Compressor with sidechain input set to the kick track
  - [ ] Compressor's gain-reduction meter shows ~3-6 dB on every kick hit
  - [ ] You can hear the bass "pumping" in time with the kick
  - [ ] Saved at projects/lesson-004-sidechain.als
- **Notes:**

## lesson-005: Pick a key from your taste, write a 4-bar hook [blocked]

- **Why blocked:** depends on lesson-004 (we're adding melodic content on
  top of the rhythm + sidechain foundation).
- **Why next once unblocked:** Your taste profile's top Camelot keys come
  from your actual library — writing a hook in one of those keys means
  your project will mix harmonically with tracks you already love.
  References: `knowledge/theory/the-camelot-wheel.md`,
  `knowledge/theory/scales-and-keys.md`.
- **Estimated time:** 45 min
- **Depends on:** lesson-004
- **Hardware:** MPK keys for the hook; pads still drive the drums.
- **Practice task:** Open `taste/profile.md` and pick a Camelot key from
  the top of the Key bias section. Set up a new MIDI track with a simple
  lead synth (Operator preset or one from the browser). Using only notes
  in that key's scale (consult `knowledge/theory/scales-and-keys.md`),
  write a 4-bar melodic hook with at most 8 notes. Less is more — keep it
  sparse like the tech-house cheat sheet describes.
- **Done criteria:**
  - [ ] Project key is documented in a comment / clip note (e.g.,
        "key: 8A / A minor")
  - [ ] Lead MIDI track contains a 4-bar hook with all notes in the chosen scale
  - [ ] Hook has 8 or fewer notes
  - [ ] Saved at projects/lesson-005-hook.als
- **Notes:**

## lesson-006: Stack the groove — open hat + percussion loop [blocked]

- **Why blocked:** depends on lesson-005 (we're layering on a rhythmic +
  melodic foundation).
- **Why next once unblocked:** Tech house's texture comes from layered
  percussion in the gaps. Adding the open hat on the "and"s (already done
  in lesson-003) and a 1/16 percussion loop closes the rhythmic picture
  per `knowledge/genres/tech-house.md`. This is the lesson where the
  beat starts to feel like a real club track.
- **Estimated time:** 45 min
- **Depends on:** lesson-005
- **Hardware:** MPK pads for shaker / conga / processed claps.
- **Practice task:** On a new MIDI track in your lesson-005 project, load
  a percussion sample (shaker, conga, or processed clap) and program a
  1/16 loop that fills the off-beats. Optionally tap it in live on the
  pads for human feel. Listen back: the kick + clap + open-hat + perc
  layer should fill the beat without anyone instrument crowding.
- **Done criteria:**
  - [ ] New percussion track with a 1/16 pattern (shaker / conga / clap)
  - [ ] Beat sounds full but not muddy — perc fills gaps without competing
        with the kick
  - [ ] You can name out loud what each percussion element does in the mix
  - [ ] Saved as projects/lesson-006-groove.als
- **Notes:**

## lesson-007: Session view → Arrangement view: intro / drop / break / drop [blocked]

- **Why blocked:** depends on lesson-006 (need a complete drop loop to arrange).
- **Why next once unblocked:** The intro / drop A / break / drop B
  structure in `knowledge/genres/tech-house.md` is what turns a loop into
  a track. This lesson is the bridge from "I have a beat" to "I have an
  arrangement." References: `knowledge/ableton/session-vs-arrangement-view.md`.
- **Estimated time:** 60 min
- **Depends on:** lesson-006
- **Hardware:** mostly mouse work; pads optional.
- **Practice task:** Take your lesson-006 project. In Session view, set
  up clip slots for: Intro (32 bars), Drop A (32 bars), Break (16 bars),
  Drop B (32 bars), Outro (32 bars). Record into Arrangement view,
  building the structure by dropping clips on/off as the cheat sheet
  describes (intro = drums building, no bass yet; drop A = full;
  break = kick out + riser; drop B = back to full).
- **Done criteria:**
  - [ ] Arrangement view contains all five sections back-to-back
  - [ ] Drop A and Drop B both have kick + bass + sidechain
  - [ ] Break has the kick removed (riser / vocal sample optional)
  - [ ] Saved as projects/lesson-007-arrangement.als
- **Notes:**

## lesson-008: Save and bounce your first complete short track [blocked]

- **Why blocked:** depends on lesson-007 (arrangement must exist).
- **Why next once unblocked:** Closure. End of the foundation arc — you've
  got a 2-minute tech-house track that touches every primitive in
  `knowledge/genres/tech-house.md`. Bouncing it makes it real.
- **Estimated time:** 30 min
- **Depends on:** lesson-007
- **Hardware:** none.
- **Practice task:** Set Arrangement view's loop brace around the full
  arrangement (intro through outro). Use File → Export Audio/Video to
  bounce a wav. Listen to the wav outside Ableton (in your normal
  music-listening app) and notice what feels different vs. listening in
  the project.
- **Done criteria:**
  - [ ] Arrangement saved at projects/tech-house-drop-01.als
  - [ ] Bounced wav exists at projects/tech-house-drop-01.wav
  - [ ] You've listened to the wav at least once outside Ableton
- **Notes:**

## lesson-009: Half-time dubstep pattern at 140 BPM [blocked]

- **Why blocked:** depends on lesson-008 (foundation arc complete; tempo / groove switch is a meaningful step).
- **Stub — full lesson body authored when this becomes active.** Will draw
  from `knowledge/genres/dubstep.md` and the Subtronics / Zeds Dead artist
  pages.

## lesson-010: Wobble bass in Operator [blocked]

- **Why blocked:** depends on lesson-009 (need the half-time foundation in place to write a wobble line into).
- **Stub — full lesson body authored when this becomes active.** First
  synthesis-design lesson; teaches LFO routing in Operator.

## lesson-011: Melodic dubstep build — piano intro into a soft drop [blocked]

- **Why blocked:** depends on lesson-010 (sound design groundwork).
- **Stub — full lesson body authored when this becomes active.** Will
  draw from `knowledge/genres/melodic-dubstep.md` and the Wooli /
  Levity / nimino artist pages.

## lesson-012: Cross-genre tempo / key planning with the Camelot wheel [blocked]

- **Why blocked:** depends on lesson-011 (multiple genres now in your hands).
- **Stub — full lesson body authored when this becomes active.** Bridges
  back to `taste/profile.md`'s Camelot data and sets up DJ-adjacent
  thinking. References `knowledge/theory/the-camelot-wheel.md`.
```

- [ ] **Step 3: Verify schema invariants**

```bash
PYTHONIOENCODING=utf-8 python -c "
import re, sys
text = open('curriculum.md', encoding='utf-8').read()
active = re.findall(r'## (lesson-\d+):.*\[active\]', text)
blocked = re.findall(r'## (lesson-\d+):.*\[blocked\]', text)
done = re.findall(r'## (lesson-\d+):.*\[done\]', text)
skipped = re.findall(r'## (lesson-\d+):.*\[skipped\]', text)
total = len(active) + len(blocked) + len(done) + len(skipped)
assert len(active) == 1, f'expected 1 active, got {len(active)}'
assert active == ['lesson-001'], active
assert total == 12, f'expected 12 lessons total, got {total}'
front = re.search(r'next: (\S+)', text).group(1)
assert front == 'lesson-001', front
print('ok')
"
```

Expected: `ok`. If anything fails, fix the file and rerun.

- [ ] **Step 4: Verify each fleshed lesson references a knowledge cheat sheet**

```bash
PYTHONIOENCODING=utf-8 python -c "
import re
text = open('curriculum.md', encoding='utf-8').read()
sections = re.split(r'^## ', text, flags=re.M)[1:]
for sec in sections:
    title = sec.split('\n',1)[0]
    if '[blocked]' in title and 'Stub' in sec:
        continue  # stubs don't require references
    if 'knowledge/' not in sec:
        print(f'MISSING: {title}')
print('done')
"
```

Expected: `done` with no `MISSING:` lines.

- [ ] **Step 5: Commit**

```bash
git add curriculum.md
git commit -m "feat(curriculum): seed 12 taste-aware lessons (8 fleshed + 4 stubs)"
```

### Task 2.2: Add the "Curriculum & nudges" section to `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` (append after "## Taste profile")

- [ ] **Step 1: Append the new section verbatim**

Append to the end of `CLAUDE.md`:

```markdown

## Curriculum & nudges

The living lesson plan is `curriculum.md`. Schema reference:
`docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md`. Per-session
logs live in `sessions/YYYY-MM-DD-<topic-slug>.md` (template in §3.7 of that
spec).

**Session-start nudge.** Before your first response in any session, list
`sessions/*.md` (excluding `.gitkeep`) and find the most recent by filename.
Parse the date from the filename. If no log exists or the delta to today is
≥ the nudge staleness threshold below, lead your first reply with a
3-sentence nudge per §3.8.2 of the spec: lesson identity, practice task +
time, offer to redirect. Skip the nudge if the most recent log is within
the threshold.

**Nudge staleness threshold:** 2 calendar days. (Adjust here to retune.)

**Session-end ritual.** When Destin signals end-of-session, write
`sessions/YYYY-MM-DD-<topic-slug>.md` per §3.7 of the spec and update
`curriculum.md` per the §3.4 end-of-session protocol. Confirm both in
chat. Do not commit — leave the diff in the working tree.

**Profile drift.** When you read `curriculum.md`, compare its
`generated_from_profile` front-matter to `taste/profile.md`'s `generated_at`.
If the profile is newer, run the §3.5 re-sync rule (reorder `[blocked]`
lessons to the new anchor order; insert lessons for newly-anchored genres
if missing). Surface the changes to Destin and offer to revert.

This subsystem overrides master spec §11 #4 and §8's nudge row — see
`docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md` §2.
```

- [ ] **Step 2: Verify CLAUDE.md is well-formed**

```bash
grep -c "^## " CLAUDE.md
```

Expected: at least 5 (the existing top-level sections plus the new one).

```bash
grep -c "^## Curriculum & nudges$" CLAUDE.md
```

Expected: `1`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude): wire curriculum & nudges into CLAUDE.md"
```

### Task 2.3: Rehearse the nudge mechanism end-to-end

This task is a manual rehearsal — verify that the documented nudge logic produces the right behavior given the current `sessions/` state.

- [ ] **Step 1: Confirm `sessions/` is empty (only `.gitkeep`)**

```bash
ls sessions/
```

Expected: only `.gitkeep`.

- [ ] **Step 2: Trace the staleness check by hand**

Given:
- Today's date: 2026-04-28 (or whatever today actually is)
- Most recent `sessions/*.md`: none

Per §3.8.1, the staleness check should fire because no log exists. The nudge per §3.8.2 should be exactly 3 sentences and should reference `lesson-001` (the `[active]` lesson per the curriculum's `next:` field).

Write the would-be nudge out:

```
Welcome back — it looks like this is your first session. You're on
lesson-001: MPK ↔ Ableton first connection. Today's practice (~30 min):
connect the MPK over USB, verify Ableton sees it, and play notes from
the keys. Want to dive in, switch lessons, or just chat?
```

Confirm the rehearsed text:
- Is exactly 3 sentences (excluding the optional "Welcome back" preamble; or 4 if you count the greeting — both are acceptable per §3.8.2 which prescribes structure rather than literal sentence count).
- References lesson-001 by ID + title from `curriculum.md`.
- Quotes the `Estimated time` and a paraphrase of the `Practice task`.
- Ends with the redirect offer.

- [ ] **Step 3: Trace the no-nudge case**

Imagine `sessions/2026-04-28-first-session.md` exists (it doesn't yet — this is a thought experiment). Per §3.8.1, if today is 2026-04-28 and the latest log is 2026-04-28, delta = 0, less than threshold (2). No nudge fires.

Confirm verbally that no nudge would fire in this case.

- [ ] **Step 4: Document the rehearsal in this plan**

Append to this plan file (`docs/superpowers/plans/2026-04-28-session-d-personalization-curriculum.md`) under a new "Rehearsal log" subsection at the end of Task 2.3:

```markdown
**Rehearsal log (filled in during execution):**

- Date of rehearsal: <YYYY-MM-DD>
- Sessions/ state: <empty / contents>
- Expected nudge fires: yes / no
- Drafted nudge text:
  > <three-sentence nudge text>
- Notes: <anything that surprised you during the rehearsal — these are
  signals that the nudge mechanics in the spec / CLAUDE.md need a tweak>
```

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-04-28-session-d-personalization-curriculum.md
git commit -m "test(curriculum): rehearse nudge mechanics on empty sessions/"
```

**Rehearsal log (filled in 2026-04-28 during Task 2.3 execution):**

- **Date of rehearsal:** 2026-04-28
- **Sessions/ state:** empty (only `.gitkeep` present)
- **Expected nudge fires:** yes (no log = stale per §3.8.1)
- **Drafted nudge text (would-be first response):**
  > Welcome back — it looks like this is your first session. You're on
  > `lesson-001: MPK ↔ Ableton first connection`. Today's practice (~30 min):
  > connect the MPK over USB, verify Ableton sees it under Preferences →
  > Link/Tempo/MIDI, and play notes from the keys. Want to dive in, switch
  > lessons, or just chat?
- **No-nudge counter-case (thought experiment):** if `sessions/2026-04-28-first-session.md`
  existed today, delta = 0 calendar days, threshold = 2, 0 < 2 → no nudge fires.
  Behavior matches spec §3.8.1.
- **Notes:** Mechanics traced cleanly with no surprises. The would-be nudge
  is 4 sentences if the "Welcome back" preamble is counted separately —
  spec §3.8.2 prescribes structure rather than literal sentence count, so
  the 3-sentence rule maps to the three semantic units (lesson identity,
  practice + time, redirect). Noted as a minor structural observation, not
  a spec gap.

### Task 2.4: Phase 2 verification gate (#4)

- [ ] **Step 1: Verify `curriculum.md` has the §3.3 schema**

```bash
head -10 curriculum.md
```

Expected: front matter with `last_updated`, `next: lesson-001`, `generated_from_profile`, `profile_anchors`.

- [ ] **Step 2: Verify all 12 lessons present**

```bash
grep -c "^## lesson-" curriculum.md
```

Expected: `12`.

- [ ] **Step 3: Verify schema invariants (re-run from Task 2.1 Step 3 for safety)**

```bash
PYTHONIOENCODING=utf-8 python -c "
import re
text = open('curriculum.md', encoding='utf-8').read()
active = re.findall(r'## (lesson-\d+):.*\[active\]', text)
blocked = re.findall(r'## (lesson-\d+):.*\[blocked\]', text)
assert len(active) == 1 and active == ['lesson-001']
assert len(blocked) == 11
print('ok')
"
```

Expected: `ok`.

- [ ] **Step 4: Verify CLAUDE.md has both the Taste profile and the Curriculum & nudges sections**

```bash
grep -c "^## Taste profile$\|^## Curriculum & nudges$" CLAUDE.md
```

Expected: `2`.

- [ ] **Step 5: Verify no `/schedule` entry exists for nudges**

The override gate (#4 spec §2.1) is satisfied by the *absence* of any nudge-related schedule entry. If a Routines list is queryable, list and confirm. If not, this gate is satisfied by inspection of the spec / CLAUDE.md (which document the override) and the absence of any code that registers a remote agent.

```bash
grep -ri "/schedule\|CronCreate" CLAUDE.md curriculum.md docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md | grep -v "override" | grep -v "no /schedule" || echo "no schedule entries — gate satisfied via override"
```

Expected: `no schedule entries — gate satisfied via override`.

- [ ] **Step 6: Verify no `nudges/` directory exists**

```bash
test ! -d nudges/ && echo "ok"
```

Expected: `ok`.

- [ ] **Step 7: Verify each fleshed lesson references at least one knowledge cheat sheet**

(Re-run the check from Task 2.1 Step 4 for safety.)

```bash
PYTHONIOENCODING=utf-8 python -c "
import re
text = open('curriculum.md', encoding='utf-8').read()
sections = re.split(r'^## ', text, flags=re.M)[1:]
missing = []
for sec in sections:
    title = sec.split('\n',1)[0]
    if 'Stub' in sec:
        continue
    if not title.startswith('lesson-'):
        continue
    if 'knowledge/' not in sec:
        missing.append(title)
print('missing:' if missing else 'ok')
for m in missing: print(' ', m)
"
```

Expected: `ok`.

### Task 2.5: Mark Session D complete in the orchestration plan

**Files:**
- Modify: `docs/superpowers/plans/2026-04-26-master-orchestration.md`

- [ ] **Step 1: Update the Session D status line**

Find the line `- **Status:** [ ] not started` under "### Session D: Personalization → curriculum (Subsystems #7, #4)" and change it to:

```
- **Status:** [x] complete (2026-04-28 — plan at `docs/superpowers/plans/2026-04-28-session-d-personalization-curriculum.md`; subsystems #7 + #4 shipped)
```

- [ ] **Step 2: Tick the three Session D step boxes**

Find this block at the end of the Session D section:

```
- [ ] **Step 1:** Open fresh session, paste hand-off prompt, complete the cycle
- [ ] **Step 2:** Both verification gates passed
- [ ] **Step 3:** Mark session `[x]` — unblocks Session E
```

Change to:

```
- [x] **Step 1:** Open fresh session, paste hand-off prompt, complete the cycle
- [x] **Step 2:** Both verification gates passed
- [x] **Step 3:** Mark session `[x]` — unblocks Session E
```

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-04-26-master-orchestration.md
git commit -m "chore(orchestration): mark Session D complete; subsystems #7 + #4 shipped"
```

### Task 2.6: Final sanity sweep + report

- [ ] **Step 1: Confirm clean tree**

```bash
git status
```

Expected: nothing to commit; working tree clean.

- [ ] **Step 2: Confirm both verification gates from spec §5 in #7 and #4 are satisfied**

Skim `docs/superpowers/specs/subsystems/07-taste-profile.md` §5 and `docs/superpowers/specs/subsystems/04-curriculum-and-nudges.md` §5; confirm every gate item is satisfied. If anything is unticked, return to the relevant task.

- [ ] **Step 3: Print the final report**

Surface to Destin:

> Session D complete. Subsystem #7 (Taste Profile) and Subsystem #4 (Curriculum & Nudges) are shipped. `taste/profile.md` is populated from real data; 14 artist pages live in `knowledge/artists/`; `curriculum.md` has 12 seed lessons (8 fleshed + 4 stubs); CLAUDE.md is wired up for both workflows. Session E (Teardown Pipeline) is now unblocked. Total commits in this session: <count>.

---

## Self-review

**Spec coverage (07-taste-profile.md):**
- §3.1 owns profile.md → Tasks 1.7 (write), 1.23 step 5 (verify sections)
- §3.2 owns 14 artist pages → Tasks 1.8–1.21, 1.23 step 6 (verify)
- §3.3 component layout → Task 1.1 (skeleton), 1.5 (entrypoint)
- §3.4 aggregator JSON shape → Task 1.2/1.3 (TDD), 1.5 step 3 (smoke check)
- §3.5 profile.md shape → Task 1.7
- §3.6 artist page shape → Pattern + 1.8–1.21
- §3.7 invocation pattern → CLAUDE.md edit Task 1.6
- §3.8 slug rules → Per-artist tasks (slugs explicit in each)
- §3.9 resource verification → Pattern Step B + 1.23 step 8 (spot-check)
- §3.10 CLAUDE.md edits → Task 1.6
- §4 prohibitions → enforced by Pattern (Step B / Step D), no script touches forbidden files
- §5 verification gate → Task 1.23

**Spec coverage (04-curriculum-and-nudges.md):**
- §3.1 owns curriculum.md → Task 2.1
- §3.2 owns sessions/ logs → Documented in CLAUDE.md (Task 2.2); Task 2.3 step 4 traces the file format
- §3.3 schema → Task 2.1 (full file)
- §3.4 end-of-session protocol → CLAUDE.md (Task 2.2)
- §3.5 re-sync → CLAUDE.md (Task 2.2)
- §3.6 12-lesson seed → Task 2.1
- §3.7 sessions/ template → CLAUDE.md (Task 2.2) + Task 2.3 (rehearsal references it)
- §3.8 nudge mechanics → CLAUDE.md (Task 2.2) + Task 2.3 rehearsal
- §3.9 session-end ritual → CLAUDE.md (Task 2.2)
- §3.10 CLAUDE.md edits → Task 2.2
- §4 prohibitions → enforced by absence of /schedule + nudges/ → Task 2.4 steps 5, 6
- §5 verification gate → Task 2.4

**Placeholder scan:** None. Every per-artist task has slug, CSV name, track count, primary genre. Curriculum lesson bodies are complete prose for 1–8 and explicit stubs for 9–12.

**Type consistency:** `top_artists`, `bpm_histogram`, `camelot_distribution`, `key_split`, `feature_means` are referenced consistently across Tasks 1.2 (tests), 1.3 (impl), 1.5 (entrypoint). `load_tracks` consistent across Tasks 1.4 (tests + impl) and 1.5 (caller). Spec §3.4 JSON shape ↔ Task 1.5 `build_stats` ↔ Task 1.7 prose all agree on the same field names.
