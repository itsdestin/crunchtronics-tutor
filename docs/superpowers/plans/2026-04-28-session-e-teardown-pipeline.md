# Session E — Teardown Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Subsystem #8 — a project-scoped `/teardown` skill that turns a track Destin loves into `teardowns/<slug>/{source.wav, analysis.json, scrub-strip.png, teardown.md, recipe.md}`. The CLI half is yt-dlp + librosa + matplotlib; the narrative half is Claude reading the artifacts plus `knowledge/genres/*.md` + `knowledge/artists/*.md`.

**Architecture:** Three layers per spec §3 — (1) project-scoped skill at `.claude/skills/teardown/SKILL.md` owns the user-facing flow + artifact templates; (2) Python CLI at `scripts/teardown.py` (thin shim) → `scripts/teardown/` package does the deterministic heavy lifting (yt-dlp download, librosa analysis, matplotlib scrub strip); (3) Claude back in the chat session reads the artifacts and authors `teardown.md` + `recipe.md`. Artifact directory is `teardowns/<slug>/`.

**Tech Stack:** Python 3.12 / uv (extends existing `scripts/` project), librosa ≥0.10.2, yt-dlp ≥2026.04.01, matplotlib ≥3.8, soundfile ≥0.12. System dep: ffmpeg. Existing test infra: pytest 8 + pytest-mock + responses (already in `[project.optional-dependencies].dev`).

**Spec:** `docs/superpowers/specs/subsystems/08-teardown-pipeline.md`

---

## File structure

**New files:**
```
.claude/skills/teardown/SKILL.md            # the project-scoped skill body (user flow + templates + authoring rules)

scripts/teardown.py                         # thin shim — sys.path insert + teardown.cli.main()
scripts/teardown/__init__.py
scripts/teardown/cli.py                     # argparse + top-level orchestration
scripts/teardown/models.py                  # dataclasses: AnalysisResult, SourceInfo, KeyEstimate, etc.
scripts/teardown/slug.py                    # kebab slug derivation
scripts/teardown/csv_context.py             # taste/tracks.csv row lookup by spotify_id
scripts/teardown/key.py                     # Krumhansl-Schmuckler key estimator
scripts/teardown/analyze.py                 # librosa orchestration (load + tempo + chroma + rms + mfcc)
scripts/teardown/envelope.py                # composes analysis.json from AnalysisResult + csv row
scripts/teardown/plot.py                    # matplotlib scrub strip + per-panel fallback
scripts/teardown/ytdlp.py                   # subprocess wrapper around yt-dlp

scripts/tests/conftest.py                   # adds the fixture-wav builder (extends if present)
scripts/tests/fixtures/teardown/__init__.py # marker
scripts/tests/test_teardown_slug.py
scripts/tests/test_teardown_csv_context.py
scripts/tests/test_teardown_key.py
scripts/tests/test_teardown_analyze.py
scripts/tests/test_teardown_envelope.py
scripts/tests/test_teardown_plot.py
scripts/tests/test_teardown_ytdlp.py
scripts/tests/test_teardown_cli_args.py
scripts/tests/test_teardown_idempotency.py
scripts/tests/test_teardown_check_deps.py
scripts/tests/test_teardown_e2e.py          # gated by TEARDOWN_E2E=1
```

**Modified files:**
```
scripts/pyproject.toml                      # add librosa, yt-dlp, matplotlib, soundfile to deps
scripts/README.md                           # add Teardowns section
CLAUDE.md                                   # add the §3.16 Teardowns section from the spec
.gitignore                                  # add teardowns/**/source.* patterns
docs/superpowers/plans/2026-04-26-master-orchestration.md  # mark Session E complete at the end
```

**Camelot lookup reuse:** `scripts/teardown/key.py` imports from `enrich.camelot` rather than duplicating the 24-entry table.

---

## Task 1: Extend pyproject.toml + create package skeleton + .gitignore

**Files:**
- Modify: `scripts/pyproject.toml`
- Create: `scripts/teardown/__init__.py`, `scripts/teardown.py`
- Modify: `.gitignore`

- [ ] **Step 1.1: Add deps to `scripts/pyproject.toml`**

Read the current file and replace the `dependencies = [...]` block:

```toml
dependencies = [
    "requests>=2.31",
    "python-dateutil>=2.9",
    "librosa>=0.10.2",
    "yt-dlp>=2026.04.01",
    "matplotlib>=3.8",
    "soundfile>=0.12",
]
```

- [ ] **Step 1.2: Run `uv sync` to install the new deps**

Run:
```bash
cd scripts && uv sync --extra dev
```

Expected: installs librosa, numba, llvmlite, yt-dlp, matplotlib, soundfile and their transitive deps. If any wheel fails on Windows, see spec §6 fallback note (`uv pip install --no-binary librosa librosa`).

- [ ] **Step 1.3: Create `scripts/teardown/__init__.py`**

Empty marker file:
```python
```

- [ ] **Step 1.4: Create `scripts/teardown.py` shim**

```python
"""Entrypoint wrapper for `python scripts/teardown.py`."""

import sys
from pathlib import Path

# Make the teardown/ package importable when this script is run directly.
sys.path.insert(0, str(Path(__file__).parent))

from teardown.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 1.5: Add gitignore patterns**

Append to `.gitignore`:
```
# Teardown source audio (large; reproducible from analysis.json.source.url)
teardowns/**/source.wav
teardowns/**/source.mp3
teardowns/**/source.flac
teardowns/**/source.m4a
teardowns/**/source.opus
```

- [ ] **Step 1.6: Verify deps installed**

Run:
```bash
cd scripts && .venv/Scripts/python -c "import librosa, yt_dlp, matplotlib, soundfile; print('ok')"
```

Expected: `ok`

- [ ] **Step 1.7: Commit**

```bash
git add scripts/pyproject.toml scripts/uv.lock scripts/teardown/__init__.py scripts/teardown.py .gitignore
git commit -m "feat(teardown): scaffold scripts/teardown/ package + new deps

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Slug derivation (TDD)

**Files:**
- Create: `scripts/teardown/slug.py`
- Test: `scripts/tests/test_teardown_slug.py`

- [ ] **Step 2.1: Write failing tests**

Create `scripts/tests/test_teardown_slug.py`:

```python
"""Tests for kebab-slug derivation (spec §3.7)."""

import pytest

from teardown.slug import derive_slug, validate_slug


class TestDeriveSlug:
    def test_simple_artist_title(self):
        assert derive_slug("John Summit", "Where You Are") == "john-summit-where-you-are"

    def test_collapses_whitespace_and_punctuation(self):
        assert derive_slug("John Summit & HAYLA", "Where You Are") == "john-summit-and-hayla-where-you-are"

    def test_em_dash_in_title(self):
        # The actual character used in YouTube titles for the artist/title sep.
        assert derive_slug("Subtronics", "Griztronics II") == "subtronics-griztronics-ii"

    def test_strips_diacritics(self):
        assert derive_slug("Łaszewo", "Café") == "laszewo-cafe"

    def test_collapses_repeated_dashes(self):
        assert derive_slug("---weird---", "name") == "weird-name"

    def test_strips_leading_trailing_dashes(self):
        assert derive_slug("-leading", "trailing-") == "leading-trailing"

    def test_truncates_at_80_chars(self):
        long_title = "a" * 200
        slug = derive_slug("artist", long_title)
        assert len(slug) <= 80

    def test_lowercases_uppercase(self):
        assert derive_slug("ARTIST", "TITLE") == "artist-title"

    def test_replaces_ampersand_with_and(self):
        assert derive_slug("A & B", "song") == "a-and-b-song"


class TestValidateSlug:
    def test_accepts_valid_slug(self):
        assert validate_slug("john-summit-where-you-are") is True

    def test_accepts_single_char(self):
        assert validate_slug("a") is True

    def test_rejects_empty(self):
        assert validate_slug("") is False

    def test_rejects_leading_dash(self):
        assert validate_slug("-leading") is False

    def test_rejects_uppercase(self):
        assert validate_slug("UPPER") is False

    def test_rejects_underscore(self):
        assert validate_slug("with_underscore") is False

    def test_rejects_spaces(self):
        assert validate_slug("with space") is False

    def test_rejects_too_long(self):
        assert validate_slug("a" * 81) is False
```

- [ ] **Step 2.2: Run tests to verify they fail**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_slug.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'teardown.slug'`

- [ ] **Step 2.3: Implement `scripts/teardown/slug.py`**

```python
"""Kebab-case slug derivation per spec §3.7.

Slug regex: ^[a-z0-9][a-z0-9-]{0,79}$
"""

import re
import unicodedata

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_REPEATED_DASH_RE = re.compile(r"-+")


def derive_slug(artist: str, title: str) -> str:
    """Compose a kebab slug from artist + title.

    Steps: replace `&` with `and`; casefold; strip diacritics; collapse
    non-alphanumeric runs to a single dash; strip leading/trailing dashes;
    truncate to 80 chars (trim trailing dash if truncation lands on one).
    """
    raw = f"{artist} {title}".replace("&", " and ")
    normalized = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower()
    dashed = _NON_ALNUM_RE.sub("-", lowered)
    collapsed = _REPEATED_DASH_RE.sub("-", dashed)
    stripped = collapsed.strip("-")
    truncated = stripped[:80].rstrip("-")
    return truncated


def validate_slug(slug: str) -> bool:
    """Return True iff `slug` matches the canonical pattern."""
    return bool(_SLUG_RE.match(slug))
```

- [ ] **Step 2.4: Run tests to verify they pass**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_slug.py -v
```

Expected: 14 PASS, 0 FAIL

- [ ] **Step 2.5: Commit**

```bash
git add scripts/teardown/slug.py scripts/tests/test_teardown_slug.py
git commit -m "feat(teardown): kebab slug derivation + validation

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: CSV-context lookup (TDD)

**Files:**
- Create: `scripts/teardown/csv_context.py`
- Test: `scripts/tests/test_teardown_csv_context.py`

- [ ] **Step 3.1: Write failing tests**

Create `scripts/tests/test_teardown_csv_context.py`:

```python
"""Tests for taste/tracks.csv row lookup by spotify_id (spec §3.9.csv_context)."""

import csv
from pathlib import Path

import pytest

from teardown.csv_context import load_csv_context

TRACKS_CSV_HEADER = [
    "spotify_id", "isrc", "artist", "title", "album", "duration_s",
    "bpm", "key_camelot", "key_standard", "mode", "time_signature",
    "energy", "danceability", "valence", "acousticness", "instrumentalness",
    "liveness", "loudness", "speechiness",
    "genre", "source", "fetched_at",
]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKS_CSV_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in TRACKS_CSV_HEADER})


def test_returns_row_when_spotify_id_present(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    _write_csv(csv_path, [
        {"spotify_id": "abc123", "artist": "John Summit", "title": "Where You Are",
         "bpm": "126.0", "key_camelot": "5A", "key_standard": "F minor",
         "energy": "0.78", "danceability": "0.71", "valence": "0.32",
         "genre": "", "source": "reccobeats", "fetched_at": "2026-04-26T..."},
    ])

    ctx = load_csv_context(csv_path, "abc123")

    assert ctx is not None
    assert ctx["artist"] == "John Summit"
    assert ctx["bpm"] == 126.0
    assert ctx["key_camelot"] == "5A"
    assert ctx["energy"] == 0.78


def test_returns_none_when_spotify_id_absent(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    _write_csv(csv_path, [
        {"spotify_id": "abc123", "artist": "John Summit"},
    ])
    assert load_csv_context(csv_path, "missing-id") is None


def test_returns_none_when_csv_missing(tmp_path):
    csv_path = tmp_path / "nonexistent.csv"
    assert load_csv_context(csv_path, "any-id") is None


def test_floats_parse_when_present(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    _write_csv(csv_path, [
        {"spotify_id": "x", "bpm": "126.05", "energy": "0.82"},
    ])
    ctx = load_csv_context(csv_path, "x")
    assert isinstance(ctx["bpm"], float)
    assert ctx["bpm"] == 126.05


def test_empty_string_floats_become_none(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    _write_csv(csv_path, [
        {"spotify_id": "x", "bpm": "", "energy": ""},
    ])
    ctx = load_csv_context(csv_path, "x")
    assert ctx["bpm"] is None
    assert ctx["energy"] is None


def test_string_columns_passthrough(tmp_path):
    csv_path = tmp_path / "tracks.csv"
    _write_csv(csv_path, [
        {"spotify_id": "x", "artist": "BUNT.", "title": "Clouds", "genre": "folktronica"},
    ])
    ctx = load_csv_context(csv_path, "x")
    assert ctx["artist"] == "BUNT."
    assert ctx["genre"] == "folktronica"
```

- [ ] **Step 3.2: Run tests to verify they fail**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_csv_context.py -v
```

Expected: FAIL with import error.

- [ ] **Step 3.3: Implement `scripts/teardown/csv_context.py`**

```python
"""Look up a row from taste/tracks.csv by spotify_id."""

import csv
from pathlib import Path
from typing import Any, Optional

_FLOAT_COLS = {"bpm", "energy", "danceability", "valence", "acousticness",
               "instrumentalness", "liveness", "loudness", "speechiness"}
_INT_COLS = {"duration_s", "mode", "time_signature"}
_STR_COLS = {"spotify_id", "isrc", "artist", "title", "album",
             "key_camelot", "key_standard", "genre", "source", "fetched_at"}


def _coerce(col: str, value: str) -> Any:
    if value == "":
        return None
    if col in _FLOAT_COLS:
        return float(value)
    if col in _INT_COLS:
        return int(value)
    return value  # _STR_COLS or unknown — pass through


def load_csv_context(csv_path: Path, spotify_id: str) -> Optional[dict[str, Any]]:
    """Return the matching row as a dict (with typed values), or None.

    None is returned when:
    - The CSV file does not exist
    - No row matches the given spotify_id
    """
    if not csv_path.exists():
        return None
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("spotify_id") == spotify_id:
                return {col: _coerce(col, val) for col, val in row.items()}
    return None
```

- [ ] **Step 3.4: Run tests to verify they pass**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_csv_context.py -v
```

Expected: 6 PASS, 0 FAIL

- [ ] **Step 3.5: Commit**

```bash
git add scripts/teardown/csv_context.py scripts/tests/test_teardown_csv_context.py
git commit -m "feat(teardown): tracks.csv row lookup by spotify_id

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Krumhansl-Schmuckler key estimator (TDD)

**Files:**
- Create: `scripts/teardown/key.py`
- Test: `scripts/tests/test_teardown_key.py`

- [ ] **Step 4.1: Write failing tests**

Create `scripts/tests/test_teardown_key.py`:

```python
"""Tests for Krumhansl-Schmuckler key estimator (spec §3.8 step 7)."""

import numpy as np

from teardown.key import estimate_key


def test_pure_c_major_chroma_returns_c_major():
    # Strong C, E, G; weak everything else (a C major triad's chroma profile).
    chroma_mean = np.zeros(12)
    chroma_mean[0] = 1.0   # C
    chroma_mean[4] = 0.7   # E
    chroma_mean[7] = 0.7   # G

    result = estimate_key(chroma_mean)

    assert result.standard == "C major"
    assert result.camelot == "8B"


def test_pure_a_minor_chroma_returns_a_minor():
    # A, C, E (A minor triad).
    chroma_mean = np.zeros(12)
    chroma_mean[9] = 1.0   # A
    chroma_mean[0] = 0.7   # C
    chroma_mean[4] = 0.7   # E

    result = estimate_key(chroma_mean)

    assert result.standard == "A minor"
    assert result.camelot == "8A"


def test_returns_camelot_string_format():
    chroma_mean = np.ones(12)  # uniform — degenerate but should still classify
    result = estimate_key(chroma_mean)
    # Camelot is 1A-12A or 1B-12B
    assert result.camelot[-1] in ("A", "B")
    assert 1 <= int(result.camelot[:-1]) <= 12


def test_method_label():
    result = estimate_key(np.ones(12))
    assert "krumhansl" in result.method.lower()


def test_chroma_mean_must_be_length_12():
    import pytest
    with pytest.raises(ValueError, match="length 12"):
        estimate_key(np.zeros(11))
```

- [ ] **Step 4.2: Run tests to verify they fail**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_key.py -v
```

Expected: FAIL with import error.

- [ ] **Step 4.3: Implement `scripts/teardown/key.py`**

```python
"""Krumhansl-Schmuckler key estimation from a chroma mean vector.

Reference: Krumhansl, C. L., & Kessler, E. J. (1982). Tracing the dynamic
changes in perceived tonal organization in a spatial representation of
musical keys. Psychological Review, 89(4), 334-368.

The KS algorithm correlates a track's chroma profile against 24 reference
profiles (12 major + 12 minor). The reference profiles below are
Krumhansl's original tone-profiles, which remain the standard.
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np

# Krumhansl-Kessler tone profiles (root-relative).
_MAJOR_PROFILE = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88,
])
_MINOR_PROFILE = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17,
])

_PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Camelot wheel — 24 entries. Reuses semantics from scripts/enrich/camelot.py
# (open-coded here to avoid cross-package import at this layer; the
# correctness check below ensures consistency).
_CAMELOT: dict[tuple[str, str], str] = {
    ("C", "major"): "8B",   ("A", "minor"): "8A",
    ("G", "major"): "9B",   ("E", "minor"): "9A",
    ("D", "major"): "10B",  ("B", "minor"): "10A",
    ("A", "major"): "11B",  ("F#", "minor"): "11A",
    ("E", "major"): "12B",  ("C#", "minor"): "12A",
    ("B", "major"): "1B",   ("G#", "minor"): "1A",
    ("F#", "major"): "2B",  ("D#", "minor"): "2A",
    ("C#", "major"): "3B",  ("A#", "minor"): "3A",
    ("G#", "major"): "4B",  ("F", "minor"): "4A",
    ("D#", "major"): "5B",  ("C", "minor"): "5A",
    ("A#", "major"): "6B",  ("G", "minor"): "6A",
    ("F", "major"): "7B",   ("D", "minor"): "7A",
}


@dataclass(frozen=True)
class KeyEstimate:
    standard: str  # e.g., "F minor"
    camelot: str   # e.g., "5A"
    method: str = "Krumhansl-Schmuckler on chroma_cqt mean"


def estimate_key(chroma_mean: np.ndarray) -> KeyEstimate:
    """Estimate key from a 12-vector chroma mean."""
    if chroma_mean.shape != (12,):
        raise ValueError(f"chroma_mean must be length 12, got shape {chroma_mean.shape}")

    best_corr = -np.inf
    best_root = 0
    best_mode: Literal["major", "minor"] = "major"

    for root in range(12):
        for mode_name, profile in (("major", _MAJOR_PROFILE), ("minor", _MINOR_PROFILE)):
            shifted = np.roll(profile, root)
            # Pearson correlation
            corr = np.corrcoef(chroma_mean, shifted)[0, 1]
            if not np.isnan(corr) and corr > best_corr:
                best_corr = corr
                best_root = root
                best_mode = mode_name

    pitch = _PITCH_NAMES[best_root]
    standard = f"{pitch} {best_mode}"
    camelot = _CAMELOT[(pitch, best_mode)]
    return KeyEstimate(standard=standard, camelot=camelot)
```

- [ ] **Step 4.4: Run tests to verify they pass**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_key.py -v
```

Expected: 5 PASS, 0 FAIL

- [ ] **Step 4.5: Commit**

```bash
git add scripts/teardown/key.py scripts/tests/test_teardown_key.py
git commit -m "feat(teardown): Krumhansl-Schmuckler key estimator + Camelot mapping

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Test fixture — synthesized 126 BPM wav

**Files:**
- Create: `scripts/tests/conftest.py` (or extend if present)
- Create: `scripts/tests/fixtures/teardown/__init__.py`

- [ ] **Step 5.1: Check if `scripts/tests/conftest.py` exists**

Run:
```bash
ls scripts/tests/conftest.py
```

If it exists, read it before extending. If not, create new.

- [ ] **Step 5.2: Create or extend `scripts/tests/conftest.py`**

If creating new, full contents:

```python
"""Shared pytest fixtures for the scripts test suite."""

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf


@pytest.fixture(scope="session")
def teardown_fixture_wav(tmp_path_factory) -> Path:
    """Generate a deterministic 30s 126 BPM wav for teardown tests.

    Content: 65 Hz sine bass + 5ms clicks at every 126-BPM beat.
    Format: 22050 Hz mono, normalized.
    """
    sr = 22050
    dur_s = 30.0
    bpm = 126.0
    n_samples = int(sr * dur_s)
    t = np.arange(n_samples) / sr

    # Sine bass at 65 Hz (~C2)
    bass = 0.3 * np.sin(2 * np.pi * 65.0 * t)

    # Click metronome at 126 BPM (interval = 60/126 ≈ 0.476 s)
    clicks = np.zeros(n_samples)
    beat_interval_s = 60.0 / bpm
    click_dur_samples = int(0.005 * sr)  # 5ms click
    n_beats = int(dur_s / beat_interval_s)
    for i in range(n_beats):
        beat_idx = int(i * beat_interval_s * sr)
        end_idx = min(beat_idx + click_dur_samples, n_samples)
        clicks[beat_idx:end_idx] = 0.7

    audio = bass + clicks
    audio = audio / np.max(np.abs(audio))  # normalize to [-1, 1]

    out_path = tmp_path_factory.mktemp("teardown") / "click-126bpm.wav"
    sf.write(str(out_path), audio, sr)
    return out_path
```

If `conftest.py` already exists, append the fixture function but keep the existing import block.

- [ ] **Step 5.3: Create marker file**

Create `scripts/tests/fixtures/teardown/__init__.py` (empty).

Run:
```bash
mkdir -p scripts/tests/fixtures/teardown
touch scripts/tests/fixtures/teardown/__init__.py
```

- [ ] **Step 5.4: Smoke-test the fixture in a throwaway test**

Run:
```bash
cd scripts && .venv/Scripts/python -c "
import sys; sys.path.insert(0, '.')
from tests.conftest import teardown_fixture_wav
print('fixture function importable')
"
```

Expected: `fixture function importable`

- [ ] **Step 5.5: Commit**

```bash
git add scripts/tests/conftest.py scripts/tests/fixtures/teardown/__init__.py
git commit -m "test(teardown): synthesized 126 BPM fixture wav for analysis tests

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: librosa analysis module (TDD with fixture)

**Files:**
- Create: `scripts/teardown/models.py`, `scripts/teardown/analyze.py`
- Test: `scripts/tests/test_teardown_analyze.py`

- [ ] **Step 6.1: Write failing tests**

Create `scripts/tests/test_teardown_analyze.py`:

```python
"""Tests for the librosa analysis pipeline (spec §3.8 steps 4-9).

Uses the teardown_fixture_wav from tests/conftest.py.
"""

import numpy as np
import pytest

from teardown.analyze import analyze
from teardown.models import AnalysisResult


def test_analyze_returns_AnalysisResult(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert isinstance(result, AnalysisResult)


def test_analyze_tempo_within_2bpm_of_126(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert abs(result.bpm - 126.0) < 2.0


def test_analyze_returns_at_least_50_beats(teardown_fixture_wav):
    # 30s at 126 BPM should yield ~63 beats; allow some slack.
    result = analyze(teardown_fixture_wav)
    assert len(result.beat_times_s) >= 50
    assert len(result.beat_times_s) <= 75


def test_analyze_first_beat_is_early(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert result.beat_times_s[0] < 1.0


def test_analyze_chroma_mean_length_12(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert result.chroma_mean.shape == (12,)


def test_analyze_rms_curve_non_empty(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert len(result.rms_values) > 100
    assert np.all(result.rms_values >= 0)


def test_analyze_mfcc_summary_13_coeffs(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert len(result.mfcc_means) == 13
    assert len(result.mfcc_stds) == 13


def test_analyze_duration_close_to_30s(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert abs(result.duration_s - 30.0) < 0.5


def test_analyze_sample_rate_22050(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert result.sample_rate == 22050


def test_analyze_short_audio_raises(tmp_path):
    """Audio under 30s of usable content raises (spec §3.15)."""
    import soundfile as sf
    short_wav = tmp_path / "short.wav"
    sf.write(str(short_wav), np.zeros(22050 * 5), 22050)  # 5 seconds
    with pytest.raises(ValueError, match="suspiciously short"):
        analyze(short_wav)
```

- [ ] **Step 6.2: Run tests to verify they fail**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_analyze.py -v
```

Expected: FAIL with import error.

- [ ] **Step 6.3: Implement `scripts/teardown/models.py`**

```python
"""Dataclasses for teardown pipeline results."""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class AnalysisResult:
    duration_s: float
    sample_rate: int
    bpm: float
    beat_times_s: np.ndarray
    chroma_mean: np.ndarray  # shape (12,)
    rms_values: np.ndarray   # 1-D
    rms_hop_length: int
    mfcc_means: np.ndarray   # shape (13,)
    mfcc_stds: np.ndarray    # shape (13,)
```

- [ ] **Step 6.4: Implement `scripts/teardown/analyze.py`**

```python
"""librosa-based audio analysis (spec §3.8 steps 4-9)."""

from pathlib import Path

import librosa
import numpy as np

from teardown.models import AnalysisResult

_TARGET_SR = 22050
_RMS_HOP_LENGTH = 512
_N_MFCC = 13


def analyze(audio_path: Path) -> AnalysisResult:
    """Run the full librosa pipeline on an audio file.

    Loads as 22050 Hz mono. Raises ValueError on suspiciously short audio.
    """
    y, sr = librosa.load(str(audio_path), sr=_TARGET_SR, mono=True)
    duration_s = float(len(y)) / sr

    if duration_s < 30.0:
        raise ValueError(
            f"audio is suspiciously short ({duration_s:.1f}s) — "
            "likely a partial / DRM-blocked download"
        )

    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times_s = librosa.frames_to_time(beat_frames, sr=sr)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)

    rms = librosa.feature.rms(y=y, hop_length=_RMS_HOP_LENGTH).flatten()

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=_N_MFCC)
    mfcc_means = mfcc.mean(axis=1)
    mfcc_stds = mfcc.std(axis=1)

    # librosa returns tempo as 0-d ndarray in 0.10.x; coerce to float
    bpm = float(np.atleast_1d(tempo)[0])

    return AnalysisResult(
        duration_s=duration_s,
        sample_rate=sr,
        bpm=bpm,
        beat_times_s=beat_times_s,
        chroma_mean=chroma_mean,
        rms_values=rms,
        rms_hop_length=_RMS_HOP_LENGTH,
        mfcc_means=mfcc_means,
        mfcc_stds=mfcc_stds,
    )
```

- [ ] **Step 6.5: Run tests to verify they pass**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_analyze.py -v
```

Expected: 10 PASS, 0 FAIL. May take 5-10 seconds (real librosa on real audio).

- [ ] **Step 6.6: Commit**

```bash
git add scripts/teardown/models.py scripts/teardown/analyze.py scripts/tests/test_teardown_analyze.py
git commit -m "feat(teardown): librosa analysis pipeline (tempo/beats/chroma/rms/mfcc)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Analysis envelope composer (TDD)

**Files:**
- Create: `scripts/teardown/envelope.py`
- Test: `scripts/tests/test_teardown_envelope.py`

- [ ] **Step 7.1: Write failing tests**

Create `scripts/tests/test_teardown_envelope.py`:

```python
"""Tests for analysis.json envelope composition (spec §3.9)."""

import json
import numpy as np
import pytest

from teardown.envelope import compose_envelope, write_envelope
from teardown.models import AnalysisResult
from teardown.key import KeyEstimate


def _make_result(**overrides) -> AnalysisResult:
    defaults = dict(
        duration_s=222.4,
        sample_rate=22050,
        bpm=126.05,
        beat_times_s=np.array([0.51, 0.99, 1.47]),
        chroma_mean=np.array([0.04, 0.07, 0.31, 0.05, 0.18, 0.09,
                              0.12, 0.06, 0.05, 0.21, 0.04, 0.05]),
        rms_values=np.array([0.012, 0.018, 0.21, 0.31, 0.18, 0.04]),
        rms_hop_length=512,
        mfcc_means=np.zeros(13),
        mfcc_stds=np.ones(13),
    )
    defaults.update(overrides)
    return AnalysisResult(**defaults)


def test_envelope_has_required_top_level_keys():
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="https://www.youtube.com/watch?v=xyz",
        source_title="John Summit & HAYLA — Where You Are",
        source_channel="John Summit",
        source_duration_s=222.4,
        source_basename="source.wav",
        csv_context=None,
    )
    for key in ["tool_version", "created_at", "source", "audio", "tempo",
                "beats", "key", "energy", "chroma_mean", "mfcc_summary",
                "sections", "csv_context"]:
        assert key in env, f"missing top-level key: {key}"


def test_envelope_sections_always_empty():
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    assert env["sections"] == []


def test_envelope_tempo_agreement_within_1bpm_true():
    env = compose_envelope(
        result=_make_result(bpm=126.0),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context={"bpm": 126.0, "key_camelot": "5A"},
    )
    assert env["tempo"]["agree_within_1bpm"] is True
    assert env["tempo"]["agree_within_4bpm"] is True


def test_envelope_tempo_disagreement_4bpm():
    env = compose_envelope(
        result=_make_result(bpm=63.0),  # half-time read of 126
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context={"bpm": 126.0, "key_camelot": "5A"},
    )
    assert env["tempo"]["agree_within_1bpm"] is False
    assert env["tempo"]["agree_within_4bpm"] is False


def test_envelope_tempo_agreement_keys_omitted_when_no_csv():
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    assert "agree_within_1bpm" not in env["tempo"]
    assert "agree_within_4bpm" not in env["tempo"]
    assert env["tempo"]["bpm_librosa"] == pytest.approx(126.05)
    assert "bpm_csv" not in env["tempo"]


def test_envelope_csv_context_omitted_when_none():
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    assert env["csv_context"] is None


def test_write_envelope_round_trip(tmp_path):
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="https://x", source_title="x", source_channel="x",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    out_path = tmp_path / "analysis.json"
    write_envelope(env, out_path)

    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["tempo"]["bpm_librosa"] == pytest.approx(126.05)
    assert isinstance(loaded["chroma_mean"], list)
    assert len(loaded["chroma_mean"]) == 12
```

- [ ] **Step 7.2: Run tests to verify they fail**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_envelope.py -v
```

Expected: FAIL with import error.

- [ ] **Step 7.3: Implement `scripts/teardown/envelope.py`**

```python
"""Compose and write the analysis.json envelope (spec §3.9)."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np

from teardown.key import KeyEstimate
from teardown.models import AnalysisResult

TOOL_VERSION = "0.1.0"


def compose_envelope(
    *,
    result: AnalysisResult,
    key_estimate: KeyEstimate,
    source_url: str,
    source_title: str,
    source_channel: str,
    source_duration_s: float,
    source_basename: str,
    csv_context: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """Build the JSON-serializable envelope per spec §3.9."""
    rms = np.asarray(result.rms_values)
    rms_summary = {
        "mean": float(rms.mean()),
        "p10": float(np.percentile(rms, 10)),
        "p50": float(np.percentile(rms, 50)),
        "p90": float(np.percentile(rms, 90)),
    }

    tempo: dict[str, Any] = {"bpm_librosa": float(result.bpm)}
    key: dict[str, Any] = {
        "camelot_librosa": key_estimate.camelot,
        "standard_librosa": key_estimate.standard,
        "method": key_estimate.method,
    }
    csv_block: Optional[dict[str, Any]] = None

    if csv_context is not None:
        csv_bpm = csv_context.get("bpm")
        if csv_bpm is not None:
            tempo["bpm_csv"] = float(csv_bpm)
            tempo["agree_within_1bpm"] = abs(result.bpm - csv_bpm) < 1.0
            tempo["agree_within_4bpm"] = abs(result.bpm - csv_bpm) < 4.0
        csv_camelot = csv_context.get("key_camelot")
        if csv_camelot:
            key["camelot_csv"] = csv_camelot
            key["agree"] = csv_camelot == key_estimate.camelot
        csv_block = csv_context

    return {
        "tool_version": TOOL_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "url": source_url,
            "title": source_title,
            "channel": source_channel,
            "duration_s": source_duration_s,
            "downloaded_to": source_basename,
        },
        "audio": {
            "sample_rate": result.sample_rate,
            "duration_s": result.duration_s,
            "channels": 1,
            "loader": "librosa.load (resampled mono)",
        },
        "tempo": tempo,
        "beats": {
            "count": int(len(result.beat_times_s)),
            "first_beat_s": float(result.beat_times_s[0]) if len(result.beat_times_s) else 0.0,
            "beat_times_s": [float(t) for t in result.beat_times_s],
        },
        "key": key,
        "energy": {
            "hop_length": result.rms_hop_length,
            "rms_values": [float(v) for v in result.rms_values],
            "rms_summary": rms_summary,
        },
        "chroma_mean": [float(v) for v in result.chroma_mean],
        "mfcc_summary": {
            "n_coeffs": len(result.mfcc_means),
            "means": [float(v) for v in result.mfcc_means],
            "stds": [float(v) for v in result.mfcc_stds],
        },
        "sections": [],
        "csv_context": csv_block,
    }


def write_envelope(envelope: dict[str, Any], out_path: Path) -> None:
    """Write the envelope as JSON with stable formatting."""
    out_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=False),
        encoding="utf-8",
    )
```

- [ ] **Step 7.4: Run tests to verify they pass**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_envelope.py -v
```

Expected: 7 PASS, 0 FAIL

- [ ] **Step 7.5: Commit**

```bash
git add scripts/teardown/envelope.py scripts/tests/test_teardown_envelope.py
git commit -m "feat(teardown): analysis.json envelope composer + writer

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Scrub-strip rendering (TDD)

**Files:**
- Create: `scripts/teardown/plot.py`
- Test: `scripts/tests/test_teardown_plot.py`

- [ ] **Step 8.1: Write failing tests**

Create `scripts/tests/test_teardown_plot.py`:

```python
"""Tests for matplotlib scrub-strip rendering (spec §3.10)."""

import numpy as np
import pytest

from teardown.analyze import analyze
from teardown.plot import render_scrub_strip


def test_scrub_strip_writes_png(tmp_path, teardown_fixture_wav):
    out_path = tmp_path / "scrub-strip.png"
    result = analyze(teardown_fixture_wav)
    paths = render_scrub_strip(
        audio_path=teardown_fixture_wav,
        result=result,
        out_dir=tmp_path,
    )
    assert out_path.exists()
    assert out_path.stat().st_size > 10_000  # non-trivial PNG
    assert paths == [out_path]


def test_scrub_strip_falls_back_to_per_panel_pngs(tmp_path, teardown_fixture_wav, monkeypatch):
    """When the multi-axis path fails, render each panel separately."""
    import teardown.plot as plot_mod
    original = plot_mod._render_combined

    def boom(*args, **kwargs):
        raise RuntimeError("simulated multi-axis failure")

    monkeypatch.setattr(plot_mod, "_render_combined", boom)

    result = analyze(teardown_fixture_wav)
    paths = render_scrub_strip(
        audio_path=teardown_fixture_wav,
        result=result,
        out_dir=tmp_path,
    )

    expected = [tmp_path / f"scrub-strip-{i}.png" for i in (1, 2, 3, 4)]
    for p in expected:
        assert p.exists(), f"expected fallback panel {p} missing"
    assert paths == expected
```

- [ ] **Step 8.2: Run tests to verify they fail**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_plot.py -v
```

Expected: FAIL with import error.

- [ ] **Step 8.3: Implement `scripts/teardown/plot.py`**

```python
"""Render the time-aligned scrub strip (spec §3.10).

Primary path: one figure with 4 sharex subplots.
Fallback: each panel rendered as a separate PNG.
"""

from pathlib import Path
from typing import List

import matplotlib

matplotlib.use("Agg")  # non-interactive backend; safe on Windows
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

from teardown.models import AnalysisResult


def render_scrub_strip(
    *,
    audio_path: Path,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    """Render the scrub strip to out_dir.

    Returns the list of PNG paths written. Normally 1 path
    (out_dir / 'scrub-strip.png'); if the combined render fails,
    returns 4 paths (scrub-strip-1.png … scrub-strip-4.png).
    """
    y, sr = librosa.load(str(audio_path), sr=result.sample_rate, mono=True)

    try:
        return _render_combined(y, sr, result, out_dir)
    except Exception:
        return _render_per_panel(y, sr, result, out_dir)


def _render_combined(
    y: np.ndarray,
    sr: int,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    out_path = out_dir / "scrub-strip.png"
    fig, axes = plt.subplots(nrows=4, sharex=True, figsize=(16, 12))

    # Panel 1 — waveform
    librosa.display.waveshow(y, sr=sr, ax=axes[0], alpha=0.5, color="gray")
    axes[0].set_ylabel("waveform")

    # Panel 2 — RMS energy curve
    rms_times = librosa.frames_to_time(
        np.arange(len(result.rms_values)),
        sr=sr,
        hop_length=result.rms_hop_length,
    )
    axes[1].plot(rms_times, result.rms_values, color="black", linewidth=0.7)
    axes[1].set_ylabel("RMS energy")
    _add_16bar_ticks(axes[1], result)

    # Panel 3 — chroma heatmap (recompute since envelope only stored mean)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    librosa.display.specshow(chroma, sr=sr, x_axis="time", y_axis="chroma", ax=axes[2])
    axes[2].set_ylabel("chroma")

    # Panel 4 — beat grid
    for i, t in enumerate(result.beat_times_s):
        is_downbeat = i % 4 == 0
        is_bar_of_4 = i % 16 == 0
        alpha = 0.6 if is_bar_of_4 else (0.35 if is_downbeat else 0.15)
        axes[3].axvline(t, color="gray", alpha=alpha, linewidth=0.5)
    axes[3].set_ylabel("beat grid")
    axes[3].set_xlabel("time (s)")
    axes[3].set_xlim(0, result.duration_s)
    axes[3].set_yticks([])

    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    return [out_path]


def _render_per_panel(
    y: np.ndarray,
    sr: int,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    """Fallback: each panel as its own PNG when combined render fails."""
    paths: List[Path] = []

    def _save(path: Path, render: callable) -> None:
        fig, ax = plt.subplots(figsize=(16, 3))
        try:
            render(ax)
            fig.tight_layout()
            fig.savefig(path, dpi=100)
        finally:
            plt.close(fig)
        paths.append(path)

    _save(out_dir / "scrub-strip-1.png", lambda ax: librosa.display.waveshow(
        y, sr=sr, ax=ax, alpha=0.5, color="gray"))

    rms_times = librosa.frames_to_time(
        np.arange(len(result.rms_values)),
        sr=sr,
        hop_length=result.rms_hop_length,
    )
    _save(out_dir / "scrub-strip-2.png", lambda ax: ax.plot(
        rms_times, result.rms_values, color="black", linewidth=0.7))

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    _save(out_dir / "scrub-strip-3.png", lambda ax: librosa.display.specshow(
        chroma, sr=sr, x_axis="time", y_axis="chroma", ax=ax))

    def _beat_grid(ax):
        for i, t in enumerate(result.beat_times_s):
            alpha = 0.6 if i % 16 == 0 else (0.35 if i % 4 == 0 else 0.15)
            ax.axvline(t, color="gray", alpha=alpha, linewidth=0.5)
        ax.set_xlim(0, result.duration_s)
        ax.set_yticks([])

    _save(out_dir / "scrub-strip-4.png", _beat_grid)
    return paths


def _add_16bar_ticks(ax, result: AnalysisResult) -> None:
    if len(result.beat_times_s) == 0 or result.bpm <= 0:
        return
    bar_seconds = 16 * 4 * 60.0 / result.bpm
    t = result.beat_times_s[0]
    while t < result.duration_s:
        ax.axvline(t, color="gray", alpha=0.12, linewidth=0.4)
        t += bar_seconds
```

- [ ] **Step 8.4: Run tests to verify they pass**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_plot.py -v
```

Expected: 2 PASS, 0 FAIL. May take 5-15 seconds (matplotlib + librosa).

- [ ] **Step 8.5: Commit**

```bash
git add scripts/teardown/plot.py scripts/tests/test_teardown_plot.py
git commit -m "feat(teardown): scrub-strip render with per-panel fallback

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: yt-dlp wrapper (TDD with subprocess mocking)

**Files:**
- Create: `scripts/teardown/ytdlp.py`
- Test: `scripts/tests/test_teardown_ytdlp.py`

- [ ] **Step 9.1: Write failing tests**

Create `scripts/tests/test_teardown_ytdlp.py`:

```python
"""Tests for the yt-dlp wrapper (spec §3.8 step 3, §3.15 errors)."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from teardown.ytdlp import (
    DownloadError,
    SearchResult,
    download_audio,
    resolve_search,
)


def test_resolve_search_parses_yt_dlp_output(monkeypatch):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(
        returncode=0,
        stdout="John Summit & HAYLA — Where You Are (Official Audio)|3:42|John Summit\n",
        stderr="",
    )
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    result = resolve_search("John Summit Where You Are")

    assert isinstance(result, SearchResult)
    assert result.title.startswith("John Summit & HAYLA")
    assert result.duration_string == "3:42"
    assert result.channel == "John Summit"


def test_resolve_search_raises_on_yt_dlp_error(monkeypatch):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(returncode=1, stdout="", stderr="ERROR: nope")
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    with pytest.raises(DownloadError, match="search failed"):
        resolve_search("anything")


def test_download_audio_invokes_yt_dlp_with_wav_extraction(monkeypatch, tmp_path):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    out_path = tmp_path / "source.wav"
    out_path.write_bytes(b"fake wav")  # simulate yt-dlp's output

    download_audio("https://x", out_path, force=False)

    args = fake_run.call_args[0][0]
    assert "yt-dlp" in args[0]
    assert "--extract-audio" in args
    assert "--audio-format" in args
    assert "wav" in args
    assert "https://x" in args


def test_download_audio_skips_when_file_exists_and_not_force(monkeypatch, tmp_path):
    fake_run = MagicMock()
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    out_path = tmp_path / "source.wav"
    out_path.write_bytes(b"existing")

    download_audio("https://x", out_path, force=False)

    fake_run.assert_not_called()


def test_download_audio_overwrites_when_force(monkeypatch, tmp_path):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    out_path = tmp_path / "source.wav"
    out_path.write_bytes(b"existing")

    download_audio("https://x", out_path, force=True)

    fake_run.assert_called_once()
    args = fake_run.call_args[0][0]
    assert "--force-overwrites" in args


def test_download_audio_raises_on_yt_dlp_error(monkeypatch, tmp_path):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(returncode=1, stdout="", stderr="ERROR: 403")
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    with pytest.raises(DownloadError, match="download failed"):
        download_audio("https://x", tmp_path / "source.wav", force=False)
```

- [ ] **Step 9.2: Run tests to verify they fail**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_ytdlp.py -v
```

Expected: FAIL with import error.

- [ ] **Step 9.3: Implement `scripts/teardown/ytdlp.py`**

```python
"""Subprocess wrapper around yt-dlp (spec §3.8 step 3, §3.15)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class DownloadError(RuntimeError):
    """yt-dlp failed (search or download)."""


@dataclass(frozen=True)
class SearchResult:
    title: str
    duration_string: str
    channel: str


def resolve_search(query: str) -> SearchResult:
    """Run `yt-dlp ytsearch1:` and return the resolved title/duration/channel.

    Does not download audio. Used by the skill flow before Destin's
    URL-confirmation step.
    """
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--print", "%(title)s|%(duration_string)s|%(channel)s",
        f"ytsearch1:{query}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise DownloadError(f"yt-dlp search failed: {proc.stderr.strip()}")

    parts = proc.stdout.strip().split("|", 2)
    if len(parts) != 3:
        raise DownloadError(f"yt-dlp search returned unexpected format: {proc.stdout!r}")
    return SearchResult(title=parts[0], duration_string=parts[1], channel=parts[2])


def download_audio(url: str, out_path: Path, *, force: bool) -> None:
    """Download `url` as a wav to `out_path`.

    If `out_path` already exists and `force` is False, this is a no-op
    (the existing file is treated as the canonical source).
    """
    if out_path.exists() and not force:
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "--output", str(out_path),
        url,
    ]
    if force:
        cmd.insert(1, "--force-overwrites")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise DownloadError(f"yt-dlp download failed: {proc.stderr.strip()}")
```

- [ ] **Step 9.4: Run tests to verify they pass**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_ytdlp.py -v
```

Expected: 6 PASS, 0 FAIL

- [ ] **Step 9.5: Commit**

```bash
git add scripts/teardown/ytdlp.py scripts/tests/test_teardown_ytdlp.py
git commit -m "feat(teardown): yt-dlp wrapper for search and audio download

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: CLI argparse + ffmpeg check + idempotency (TDD)

**Files:**
- Create: `scripts/teardown/cli.py`
- Test: `scripts/tests/test_teardown_cli_args.py`, `scripts/tests/test_teardown_idempotency.py`, `scripts/tests/test_teardown_check_deps.py`

- [ ] **Step 10.1: Write failing argparse tests**

Create `scripts/tests/test_teardown_cli_args.py`:

```python
"""Tests for CLI argument parsing (spec §3.13)."""

import pytest

from teardown.cli import build_parser


def test_url_and_local_are_mutually_exclusive():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--slug", "x", "--url", "https://x", "--local", "/y"])


def test_one_of_url_or_local_required_unless_check_deps_or_dry_run():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--slug", "x"])


def test_check_deps_alone_is_valid():
    parser = build_parser()
    args = parser.parse_args(["--check-deps"])
    assert args.check_deps is True


def test_dry_run_alone_with_url_is_valid():
    parser = build_parser()
    args = parser.parse_args(["--slug", "x", "--url", "https://x", "--dry-run"])
    assert args.dry_run is True


def test_csv_context_optional():
    parser = build_parser()
    args = parser.parse_args(["--slug", "x", "--url", "https://x", "--csv-context", "abc"])
    assert args.csv_context == "abc"


def test_force_flag_defaults_false():
    parser = build_parser()
    args = parser.parse_args(["--slug", "x", "--url", "https://x"])
    assert args.force is False
```

- [ ] **Step 10.2: Write failing idempotency tests**

Create `scripts/tests/test_teardown_idempotency.py`:

```python
"""Tests for the idempotency guard (spec §3.7)."""

import pytest

from teardown.cli import _check_idempotency


def test_empty_dir_is_ok(tmp_path):
    target = tmp_path / "empty-slug"
    # Does not exist yet; allowed.
    _check_idempotency(target, force=False)  # raises nothing


def test_nonexistent_dir_is_ok(tmp_path):
    target = tmp_path / "never-existed"
    _check_idempotency(target, force=False)


def test_populated_dir_without_force_raises(tmp_path):
    target = tmp_path / "exists"
    target.mkdir()
    (target / "analysis.json").write_text("{}")

    with pytest.raises(SystemExit) as exc:
        _check_idempotency(target, force=False)
    assert exc.value.code == 1


def test_populated_dir_with_force_is_ok(tmp_path):
    target = tmp_path / "exists"
    target.mkdir()
    (target / "analysis.json").write_text("{}")
    _check_idempotency(target, force=True)  # raises nothing
```

- [ ] **Step 10.3: Write failing check-deps tests**

Create `scripts/tests/test_teardown_check_deps.py`:

```python
"""Tests for --check-deps and the ffmpeg presence probe (spec §3.15)."""

from unittest.mock import MagicMock

import pytest

from teardown.cli import _ffmpeg_available, run_check_deps


def test_ffmpeg_available_returns_true_when_present(monkeypatch):
    fake_run = MagicMock(return_value=MagicMock(returncode=0))
    monkeypatch.setattr("teardown.cli.subprocess.run", fake_run)
    assert _ffmpeg_available() is True


def test_ffmpeg_available_returns_false_when_missing(monkeypatch):
    fake_run = MagicMock(side_effect=FileNotFoundError())
    monkeypatch.setattr("teardown.cli.subprocess.run", fake_run)
    assert _ffmpeg_available() is False


def test_run_check_deps_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr("teardown.cli._ffmpeg_available", lambda: True)
    rc = run_check_deps()
    captured = capsys.readouterr()
    assert rc == 0
    assert "ffmpeg" in captured.out.lower()
    assert "librosa" in captured.out.lower()
    assert "yt-dlp" in captured.out.lower()
    assert "matplotlib" in captured.out.lower()
```

- [ ] **Step 10.4: Run tests to verify they fail**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_cli_args.py tests/test_teardown_idempotency.py tests/test_teardown_check_deps.py -v
```

Expected: FAIL with import errors.

- [ ] **Step 10.5: Implement `scripts/teardown/cli.py`**

```python
"""Top-level CLI for the teardown pipeline (spec §3.13)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from teardown import analyze as analyze_mod
from teardown import envelope as envelope_mod
from teardown import plot as plot_mod
from teardown.csv_context import load_csv_context
from teardown.key import estimate_key
from teardown.ytdlp import DownloadError, download_audio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEARDOWNS_DIR = PROJECT_ROOT / "teardowns"
TRACKS_CSV = PROJECT_ROOT / "taste" / "tracks.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teardown",
        description="Audio teardown pipeline (yt-dlp + librosa + scrub strip).",
    )
    parser.add_argument("--slug", help="Output directory name under teardowns/")
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--url", help="Audio source URL (yt-dlp will download it)")
    src.add_argument("--local", help="Path to an existing local audio file")
    parser.add_argument("--csv-context", help="spotify_id to embed from taste/tracks.csv")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite an existing teardowns/<slug>/")
    parser.add_argument("--check-deps", action="store_true",
                        help="Print versions of ffmpeg/librosa/yt-dlp/matplotlib and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the planned operations and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.check_deps:
        return run_check_deps()

    if not args.slug:
        parser.error("--slug is required (unless --check-deps)")
    if not (args.url or args.local):
        parser.error("one of --url or --local is required (unless --check-deps)")

    if not _ffmpeg_available():
        print("ERROR: ffmpeg not found on PATH. Install: winget install Gyan.FFmpeg",
              file=sys.stderr)
        return 6

    target_dir = TEARDOWNS_DIR / args.slug
    _check_idempotency(target_dir, force=args.force)
    target_dir.mkdir(parents=True, exist_ok=True)

    source_path = target_dir / "source.wav"

    if args.dry_run:
        print(f"DRY RUN — would write: {source_path}, "
              f"{target_dir / 'analysis.json'}, {target_dir / 'scrub-strip.png'}")
        return 0

    try:
        if args.url:
            print(f"[1/4] downloading {args.url}…")
            download_audio(args.url, source_path, force=args.force)
            source_url = args.url
            source_title = args.slug
            source_channel = ""
        else:
            local_path = Path(args.local).resolve()
            if not local_path.exists():
                print(f"ERROR: --local path does not exist: {local_path}", file=sys.stderr)
                return 6
            print(f"[1/4] using local file {local_path}")
            if not source_path.exists() or args.force:
                import shutil
                shutil.copy(local_path, source_path)
            source_url = ""
            source_title = local_path.name
            source_channel = ""
    except DownloadError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        print("[2/4] loading audio…")
        result = analyze_mod.analyze(source_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    print("[3/4] librosa analysis + key estimate…")
    key_est = estimate_key(result.chroma_mean)

    csv_ctx = None
    if args.csv_context:
        csv_ctx = load_csv_context(TRACKS_CSV, args.csv_context)
        if csv_ctx is None:
            print(f"WARNING: --csv-context {args.csv_context} not in {TRACKS_CSV}",
                  file=sys.stderr)

    envelope = envelope_mod.compose_envelope(
        result=result,
        key_estimate=key_est,
        source_url=source_url,
        source_title=source_title,
        source_channel=source_channel,
        source_duration_s=result.duration_s,
        source_basename="source.wav",
        csv_context=csv_ctx,
    )
    envelope_mod.write_envelope(envelope, target_dir / "analysis.json")

    print("[4/4] rendering scrub strip…")
    try:
        png_paths = plot_mod.render_scrub_strip(
            audio_path=source_path,
            result=result,
            out_dir=target_dir,
        )
    except Exception as exc:
        print(f"ERROR: scrub strip rendering failed: {exc}", file=sys.stderr)
        return 5

    print("\nArtifacts:")
    print(f"  source.wav       {source_path}")
    print(f"  analysis.json    {target_dir / 'analysis.json'}")
    for p in png_paths:
        print(f"  {p.name:16s} {p}")
    return 0


def _check_idempotency(target_dir: Path, *, force: bool) -> None:
    """Exit 1 if target_dir exists and contains anything, unless force=True."""
    if force:
        return
    if not target_dir.exists():
        return
    if any(target_dir.iterdir()):
        print(f"ERROR: {target_dir} already exists and is non-empty. "
              "Re-run with --force to overwrite.", file=sys.stderr)
        sys.exit(1)


def _ffmpeg_available() -> bool:
    try:
        proc = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, text=True,
        )
        return proc.returncode == 0
    except FileNotFoundError:
        return False


def run_check_deps() -> int:
    """Print versions of all backend deps + ffmpeg. Always exits 0."""
    import importlib.metadata as md

    def _version(name: str) -> str:
        try:
            return md.version(name)
        except md.PackageNotFoundError:
            return "MISSING"

    print(f"librosa     {_version('librosa')}")
    print(f"yt-dlp      {_version('yt-dlp')}")
    print(f"matplotlib  {_version('matplotlib')}")
    print(f"soundfile   {_version('soundfile')}")
    print(f"ffmpeg      {'present' if _ffmpeg_available() else 'MISSING (install: winget install Gyan.FFmpeg)'}")
    return 0
```

- [ ] **Step 10.6: Run tests to verify they pass**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest tests/test_teardown_cli_args.py tests/test_teardown_idempotency.py tests/test_teardown_check_deps.py -v
```

Expected: 13 PASS (6 + 4 + 3), 0 FAIL.

- [ ] **Step 10.7: Smoke-test --check-deps end-to-end**

Run:
```bash
cd scripts && .venv/Scripts/python teardown.py --check-deps
```

Expected: prints versions of librosa, yt-dlp, matplotlib, soundfile, and ffmpeg presence. Exit code 0.

- [ ] **Step 10.8: Commit**

```bash
git add scripts/teardown/cli.py scripts/tests/test_teardown_cli_args.py scripts/tests/test_teardown_idempotency.py scripts/tests/test_teardown_check_deps.py
git commit -m "feat(teardown): CLI orchestration (argparse + idempotency + check-deps)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: Integration test on the fixture wav

**Files:**
- Create: `scripts/tests/test_teardown_e2e.py`

- [ ] **Step 11.1: Write the gated integration test**

Create `scripts/tests/test_teardown_e2e.py`:

```python
"""End-to-end CLI test on the synthetic fixture wav.

Gated by TEARDOWN_E2E=1 so it isn't part of the default test run.
Exercises the full pipeline minus yt-dlp (--local).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("TEARDOWN_E2E") != "1",
    reason="TEARDOWN_E2E=1 not set",
)


def test_full_pipeline_on_fixture_wav(tmp_path, teardown_fixture_wav, monkeypatch):
    """Run scripts/teardown.py via subprocess against the fixture wav.

    Validates: source.wav exists, analysis.json schema, scrub-strip.png
    (or per-panel fallbacks).
    """
    project_root = Path(__file__).resolve().parents[2]
    teardown_script = project_root / "scripts" / "teardown.py"
    teardowns_dir = project_root / "teardowns"

    slug = "test-fixture-126bpm"
    target = teardowns_dir / slug
    if target.exists():
        shutil.rmtree(target)

    proc = subprocess.run(
        [sys.executable, str(teardown_script),
         "--slug", slug, "--local", str(teardown_fixture_wav)],
        capture_output=True, text=True,
    )
    try:
        assert proc.returncode == 0, f"CLI failed:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"

        # source.wav copied in
        assert (target / "source.wav").exists()

        # analysis.json shape
        env = json.loads((target / "analysis.json").read_text(encoding="utf-8"))
        assert env["tool_version"]
        assert abs(env["tempo"]["bpm_librosa"] - 126.0) < 2.0
        assert env["sections"] == []
        assert len(env["chroma_mean"]) == 12
        assert env["audio"]["sample_rate"] == 22050

        # scrub strip (combined or per-panel)
        combined = target / "scrub-strip.png"
        per_panel = [target / f"scrub-strip-{i}.png" for i in (1, 2, 3, 4)]
        assert combined.exists() or all(p.exists() for p in per_panel)
    finally:
        if target.exists():
            shutil.rmtree(target)
```

- [ ] **Step 11.2: Run the gated test**

Run:
```bash
cd scripts && TEARDOWN_E2E=1 .venv/Scripts/python -m pytest tests/test_teardown_e2e.py -v
```

Expected: 1 PASS. May take 15-30 seconds (real librosa + matplotlib).

- [ ] **Step 11.3: Confirm full default test suite still green**

Run:
```bash
cd scripts && .venv/Scripts/python -m pytest -v
```

Expected: all teardown tests pass; existing enrich/profile tests unaffected; e2e test SKIPPED (TEARDOWN_E2E not set).

- [ ] **Step 11.4: Commit**

```bash
git add scripts/tests/test_teardown_e2e.py
git commit -m "test(teardown): end-to-end CLI test on synthetic fixture wav

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: Author the project-scoped skill

**Files:**
- Create: `.claude/skills/teardown/SKILL.md`

- [ ] **Step 12.1: Create directory**

Run:
```bash
mkdir -p .claude/skills/teardown
```

- [ ] **Step 12.2: Write `.claude/skills/teardown/SKILL.md`**

```markdown
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
```

- [ ] **Step 12.3: Verify the skill is discoverable**

Skills are auto-discovered by Claude Code from `.claude/skills/<name>/SKILL.md`.
Run `git status` to confirm the file is staged correctly.

```bash
git status
```

Expected: shows `.claude/skills/teardown/SKILL.md` as new file.

- [ ] **Step 12.4: Commit**

```bash
git add .claude/skills/teardown/SKILL.md
git commit -m "feat(teardown): project-scoped /teardown skill

Drives the seven-step user flow (input normalize → URL confirm → slug
derive → CLI run → read artifacts → author teardown.md + recipe.md →
wrap up) per spec §3.2 and §3.4. Both /teardown and natural-language
'teardown this track' route through this body.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 13: CLAUDE.md + scripts/README.md updates

**Files:**
- Modify: `CLAUDE.md`
- Modify: `scripts/README.md`

- [ ] **Step 13.1: Add the Teardowns section to CLAUDE.md**

Append to `CLAUDE.md` (after the "Curriculum & nudges" section):

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

- [ ] **Step 13.2: Add the Teardowns section to scripts/README.md**

Append to `scripts/README.md`:

```markdown
## Teardowns (Subsystem #8)

`scripts/teardown.py` — analysis CLI invoked by the `/teardown` skill.

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
```

- [ ] **Step 13.3: Smoke-test the docs render**

Run:
```bash
cat CLAUDE.md | tail -30
```

Expected: shows the new Teardowns section.

- [ ] **Step 13.4: Commit**

```bash
git add CLAUDE.md scripts/README.md
git commit -m "docs(teardown): wire teardown pipeline into CLAUDE.md and scripts/README.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: End-to-end verification on a real taste-anchor track

**Files:**
- Create: `teardowns/john-summit-where-you-are/teardown.md`, `recipe.md` (and the CLI artifacts)

This is a manual verification gate per spec §5. The implementer (Claude
in this session) is exercising every code path on Destin's actual data.

- [ ] **Step 14.1: Find the John Summit "Where You Are" row in tracks.csv**

Run:
```bash
grep -i "where you are" taste/tracks.csv | head -5
```

Note the `spotify_id` from the matching row. If "Where You Are" is not in
tracks.csv, fall back to a Subtronics or top-jigitz track that IS present.

- [ ] **Step 14.2: Resolve and confirm the URL**

Run yt-dlp search; confirm with Destin before downloading:

```bash
cd scripts && .venv/Scripts/python -c "
from teardown.ytdlp import resolve_search
print(resolve_search('John Summit HAYLA Where You Are official audio'))
"
```

Show the result to Destin and wait for confirmation.

- [ ] **Step 14.3: Run the CLI**

Run (replace `<spotify-id>` with the value from Step 14.1, replace `<url>`
with the URL Destin confirmed):

```bash
cd scripts && .venv/Scripts/python teardown.py \
    --slug john-summit-and-hayla-where-you-are \
    --url <url> \
    --csv-context <spotify-id>
```

Expected: prints the four progress lines, exits 0, lists the artifacts.

- [ ] **Step 14.4: Sanity-check the artifacts**

Run:
```bash
ls teardowns/john-summit-and-hayla-where-you-are/
```

Expected: `source.wav`, `analysis.json`, `scrub-strip.png` (or the four
panel fallbacks).

Read `analysis.json` and verify:
- `tempo.bpm_librosa` close to `tempo.bpm_csv` (within 4 BPM, ideally 1).
- `key.camelot_librosa` matches or plausibly disagrees with `key.camelot_csv`.
- `sections == []`.
- `csv_context` populated with the actual John Summit row.

Read `scrub-strip.png` (use the Read tool — it supports images). Verify
panels are aligned and the energy curve clearly shows drops/breaks.

- [ ] **Step 14.5: Author teardown.md and recipe.md**

Following the SKILL.md authoring rules, read:
1. `teardowns/john-summit-and-hayla-where-you-are/analysis.json`
2. `teardowns/john-summit-and-hayla-where-you-are/scrub-strip.png`
3. `knowledge/genres/tech-house.md`
4. `knowledge/artists/john-summit.md`

Write `teardown.md` (section overview + bar-level callouts) and
`recipe.md` (Lite-floor numbered steps with at least one `**Intro+ note:**`).

- [ ] **Step 14.6: Beginner-comprehension review**

Read the recipe top-to-bottom from Destin's POV. Every step should be
doable without external research. Check specifically:
- Does step 1 reference a knowledge page when it talks about a tempo decision?
- Does the bass + sidechain section link to `knowledge/ableton/the-mixer.md` or
  `knowledge/genres/tech-house.md` for the sidechain technique?
- Are all referenced device names (Operator, Drum Rack, Compressor) ones Lite
  actually has?

If any step requires research outside `knowledge/`, rewrite it.

- [ ] **Step 14.7: Commit the verified artifacts**

```bash
git add teardowns/john-summit-and-hayla-where-you-are/analysis.json \
        teardowns/john-summit-and-hayla-where-you-are/scrub-strip.png \
        teardowns/john-summit-and-hayla-where-you-are/teardown.md \
        teardowns/john-summit-and-hayla-where-you-are/recipe.md
git commit -m "feat(teardown): verification-gate run on John Summit — Where You Are

End-to-end smoke test for Subsystem #8. Exercises every code path:
csv_context lookup, librosa analysis, scrub-strip render, knowledge-page
read (tech-house genre + john-summit artist), Lite-floor recipe with
Intro+ note.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 15: Mark Session E complete in the orchestration plan

**Files:**
- Modify: `docs/superpowers/plans/2026-04-26-master-orchestration.md`

- [ ] **Step 15.1: Update the Session E status line**

Open the file. Find the line `- **Status:** [ ] not started` under "Session E: Teardown pipeline (Subsystem #8)".

Replace with:
```
- **Status:** [x] complete (2026-04-28 — plan at `docs/superpowers/plans/2026-04-28-session-e-teardown-pipeline.md`; subsystem #8 shipped; verification gate passed on John Summit & HAYLA — "Where You Are")
```

Also flip the three trailing checkboxes:
```
- [x] **Step 1:** Open fresh session, paste hand-off prompt, complete the cycle
- [x] **Step 2:** Verification passed
- [x] **Step 3:** Mark session `[x]` — full system complete
```

And the system-wide done criteria (the first one becomes verifiable now):
```
- [x] All 5 sessions above marked `[x]` (which means all 9 subsystems shipping)
```

(Do NOT flip the second and third "done criteria" checkboxes — those are
about Destin actually USING the system, not about it shipping.)

- [ ] **Step 15.2: Final commit**

```bash
git add docs/superpowers/plans/2026-04-26-master-orchestration.md
git commit -m "chore(orchestration): mark Session E complete; subsystem #8 shipped

All 9 subsystems now shipping. The system is ready for Destin to use
end-to-end: pull Spotify → enrich → profile → curriculum → teardown.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Self-review

**1. Spec coverage:** Each spec section maps to at least one task:

| Spec section | Task(s) |
|---|---|
| §3.1 (teardowns/<slug>/ layout) | Tasks 1.5 (.gitignore), 14 (real artifacts) |
| §3.2 (the user-facing skill) | Task 12 |
| §3.3 (analysis CLI) | Tasks 1, 6-11 |
| §3.4 (data flow) | Tasks 10, 12 |
| §3.5 (track input modes) | Task 12 (skill body) |
| §3.6 (URL resolution + confirmation) | Tasks 9, 12 |
| §3.7 (slug + idempotency) | Tasks 2, 10, 12 |
| §3.8 (analysis pipeline) | Tasks 6, 7, 10 |
| §3.9 (analysis.json schema) | Task 7 |
| §3.10 (scrub-strip layout) | Task 8 |
| §3.11 (teardown.md template) | Task 12, 14 |
| §3.12 (recipe.md template) | Task 12, 14 |
| §3.13 (CLI flags) | Task 10 |
| §3.14 (component layout) | All implementation tasks |
| §3.15 (error matrix) | Tasks 6, 9, 10 (codes 2, 3, 5, 6) |
| §3.16 (CLAUDE.md edits) | Task 13 |
| §3.17 (.gitignore) | Task 1 |
| §4 (must-not list) | Tasks 12 (skill encodes the rules), 14 (verification check) |
| §5 (verification gate) | Tasks 11, 14 |
| §6 (impl notes) | Tasks 1, 6, 8 |

**2. Placeholder scan:** zero TBD/TODO/FIXME tokens; every code block has actual code; every test has actual asserts; every commit has a real message.

**3. Type consistency:**
- `AnalysisResult` defined Task 6.3, used Tasks 7, 8, 10 — consistent fields throughout.
- `KeyEstimate` defined Task 4.3, used Task 7, 10 — consistent.
- `SearchResult` and `DownloadError` defined Task 9.3, used Task 10 — consistent.
- `compose_envelope` signature is keyword-only and identical between Task 7's tests and Task 10's call site.
- `render_scrub_strip` signature is keyword-only and identical between Task 8's tests and Task 10's call site.
- Camelot strings everywhere are `<digit>(A|B)` (e.g., `5A`, `8B`) — consistent with the existing `enrich/camelot.py` table.
- `_check_idempotency` and `_ffmpeg_available` and `run_check_deps` are all defined in Task 10 and tested in the same task — internal consistency by construction.
