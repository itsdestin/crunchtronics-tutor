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
    """Sort artists by track count desc, ties broken alphabetically.

    Counts every credited artist on each track (splitting `artists` on `;`),
    not just the primary. A track with two credited artists counts once for
    each — mirrors how listeners experience a co-credited release. Falls
    back to the `artist` column for legacy rows that predate the `artists`
    column.
    """
    counts: Counter[str] = Counter()
    for r in rows:
        joined = r.get("artists", "") or r.get("artist", "")
        for name in joined.split(";"):
            name = name.strip()
            if name:
                counts[name] += 1
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

    Other source values (`manual`, `miss:*`) leave audio-feature columns
    empty or partial (#6 spec §3.4.1), so a mixed average would be
    misleading. Returns None per metric when no reccobeats rows are present.
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
