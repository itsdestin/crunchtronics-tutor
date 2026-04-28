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
