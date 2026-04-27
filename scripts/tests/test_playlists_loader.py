"""Tests for the playlists loader."""

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
    assert skipped["duplicates"] == 1  # track001 appears in pl1 and pl2


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
