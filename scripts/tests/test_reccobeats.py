"""Tests for the ReccoBeats client (two-step lookup)."""

import json
from pathlib import Path

import pytest
import requests
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
def test_fetch_raises_on_5xx_during_resolve():
    spotify_id = "7tZSQgFyzWAAtsb7OUUDbn"
    responses.get(
        f"{RECCOBEATS_BASE_URL}/v1/track",
        status=500,
        match=[responses.matchers.query_param_matcher({"ids": spotify_id})],
    )

    with pytest.raises(requests.HTTPError):
        fetch(spotify_id)


@responses.activate
def test_fetch_raises_on_5xx_during_features():
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
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        fetch(spotify_id)
