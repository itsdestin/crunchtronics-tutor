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
