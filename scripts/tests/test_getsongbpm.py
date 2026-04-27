"""Tests for the GetSongBPM fallback client."""

import json
from pathlib import Path

import pytest
import responses

from enrich.getsongbpm import GETSONGBPM_BASE_URL, fetch

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@responses.activate
def test_fetch_returns_bpm_and_key_on_hit():
    fixture = json.loads((FIXTURE_DIR / "getsongbpm-search-hit.json").read_text())
    responses.get(
        f"{GETSONGBPM_BASE_URL}/search/",
        json=fixture,
        status=200,
    )

    result = fetch("Artist C", "Track Two", api_key="testkey")

    assert result is not None
    assert result.bpm == 128.0
    assert result.key_int == 6  # F#
    assert result.mode == 0  # minor
    # GetSongBPM doesn't return audio-feature dimensions
    assert result.energy is None
    assert result.valence is None


@responses.activate
def test_fetch_returns_none_on_empty_search():
    fixture = json.loads((FIXTURE_DIR / "getsongbpm-search-empty.json").read_text())
    responses.get(
        f"{GETSONGBPM_BASE_URL}/search/",
        json=fixture,
        status=200,
    )

    assert fetch("Nonexistent Artist", "Nonexistent Title", api_key="testkey") is None


@responses.activate
def test_fetch_returns_none_when_artist_doesnt_match():
    """Defensive: if GetSongBPM returns a match for a different artist, reject."""
    fixture = {
        "search": [
            {
                "id": "x",
                "title": "Track Two",
                "artist": {"name": "Wrong Artist"},
                "tempo": "120",
                "key_of": "C major",
            }
        ]
    }
    responses.get(
        f"{GETSONGBPM_BASE_URL}/search/",
        json=fixture,
        status=200,
    )

    assert fetch("Artist C", "Track Two", api_key="testkey") is None


def test_fetch_raises_when_no_api_key():
    with pytest.raises(ValueError, match="api_key required"):
        fetch("X", "Y", api_key="")
