"""ReccoBeats client (two-step lookup).

Single public function: fetch(spotify_id) -> EnrichmentResult | None.

ReccoBeats does not accept Spotify IDs at the audio-features endpoint;
it has its own UUID-based identifiers. Going from a Spotify ID to
audio features is a two-step dance:

  1. GET /v1/track?ids=<spotify_id>  -> returns {"content": [{id: <uuid>, ...}, ...]}
  2. GET /v1/track/<uuid>/audio-features  -> returns the audio-features payload

Returns None if step 1's content is empty (track not in ReccoBeats DB).
Raises ReccoBeatsRateLimited on 429 (with Retry-After attached) from
either step. Raises requests.HTTPError on other non-2xx.
"""

from typing import Optional

import requests

from enrich.models import EnrichmentResult

RECCOBEATS_BASE_URL = "https://api.reccobeats.com"
_DEFAULT_TIMEOUT_S = 10


class ReccoBeatsRateLimited(Exception):
    def __init__(self, retry_after_s: int):
        super().__init__(f"ReccoBeats rate-limited; retry after {retry_after_s}s")
        self.retry_after_s = retry_after_s


def _check_429(response: requests.Response) -> None:
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", "60"))
        raise ReccoBeatsRateLimited(retry_after_s=retry_after)


def _resolve_spotify_id(spotify_id: str) -> Optional[str]:
    """Step 1: turn a Spotify track ID into a ReccoBeats UUID, or None if not in DB."""
    response = requests.get(
        f"{RECCOBEATS_BASE_URL}/v1/track",
        params={"ids": spotify_id},
        timeout=_DEFAULT_TIMEOUT_S,
        headers={"Accept": "application/json"},
    )
    _check_429(response)
    response.raise_for_status()
    content = response.json().get("content", [])
    if not content:
        return None
    return content[0]["id"]


def _fetch_features(uuid: str) -> EnrichmentResult:
    """Step 2: fetch audio features by ReccoBeats UUID."""
    response = requests.get(
        f"{RECCOBEATS_BASE_URL}/v1/track/{uuid}/audio-features",
        timeout=_DEFAULT_TIMEOUT_S,
        headers={"Accept": "application/json"},
    )
    _check_429(response)
    response.raise_for_status()
    payload = response.json()
    # Field names verified against the live API on 2026-04-26.
    return EnrichmentResult(
        bpm=payload.get("tempo"),
        key_int=payload.get("key"),
        mode=payload.get("mode"),
        energy=payload.get("energy"),
        danceability=payload.get("danceability"),
        valence=payload.get("valence"),
        acousticness=payload.get("acousticness"),
        instrumentalness=payload.get("instrumentalness"),
        liveness=payload.get("liveness"),
        loudness=payload.get("loudness"),
        speechiness=payload.get("speechiness"),
    )


def fetch(spotify_id: str) -> Optional[EnrichmentResult]:
    uuid = _resolve_spotify_id(spotify_id)
    if uuid is None:
        return None
    return _fetch_features(uuid)
