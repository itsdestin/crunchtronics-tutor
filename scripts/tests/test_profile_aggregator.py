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
        "artists": "Test Artist",
        "title": "Test Track",
        "album": "Test Album",
        "duration_s": "180",
        "bpm": "126.0",
        "key_camelot": "8A",
        "key_standard": "A minor",
        "mode": "0",
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
        _row(artists="Bravo"),
        _row(artists="Alpha"),
        _row(artists="Alpha"),
        _row(artists="Charlie"),
        _row(artists="Bravo"),
        _row(artists="Bravo"),
    ]
    result = top_artists(rows)
    assert result == [
        {"artist": "Bravo", "tracks": 3},
        {"artist": "Alpha", "tracks": 2},
        {"artist": "Charlie", "tracks": 1},
    ]


def test_top_artists_counts_every_credit_on_multi_artist_track():
    """A track with two credited artists counts once for each."""
    rows = [
        _row(artists="Subtronics;Wooli"),
        _row(artists="GRiZ;Wooli"),
        _row(artists="Wooli"),
    ]
    result = top_artists(rows)
    counts = {d["artist"]: d["tracks"] for d in result}
    assert counts["Wooli"] == 3
    assert counts["Subtronics"] == 1
    assert counts["GRiZ"] == 1


def test_top_artists_falls_back_to_artist_when_artists_missing():
    """Legacy rows with only `artist` populated still aggregate correctly."""
    rows = [
        {"artist": "Solo", "artists": ""},
        {"artist": "Solo", "artists": ""},
    ]
    result = top_artists(rows)
    assert result == [{"artist": "Solo", "tracks": 2}]


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
