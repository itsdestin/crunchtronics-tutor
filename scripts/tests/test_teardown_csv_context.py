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
