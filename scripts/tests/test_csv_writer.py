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
        "spotify_id", "isrc", "artist", "artists", "title", "album", "duration_s",
        "bpm", "key_camelot", "key_standard", "mode",
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
            artists="A;B",
            title="T",
            album="Al",
            duration_s=200,
            bpm=128.0,
            key_camelot="8B",
            key_standard="C major",
            mode=1,
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
    assert r.artists == "A;B"
    assert r.source == "reccobeats"
    assert r.fetched_at == "2026-04-26T00:00:00Z"


def test_read_existing_returns_empty_for_missing_file(tmp_path: Path):
    path = tmp_path / "nope.csv"
    assert read_existing(path) == {}


def test_write_atomic_preserves_column_order(tmp_path: Path):
    rows = [
        EnrichedRow(
            spotify_id="x", isrc="", artist="", artists="", title="", album="", duration_s=0,
            bpm=None, key_camelot="", key_standard="", mode=None,
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
