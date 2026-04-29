"""Shared data classes for the enrichment pipeline."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EnrichmentResult:
    """One backend's response for a single track.

    All fields are optional; ReccoBeats populates them all. Returned as
    None from the backend on a miss.
    """

    bpm: Optional[float] = None
    key_int: Optional[int] = None  # 0..11 (Spotify-style)
    mode: Optional[int] = None  # 0 minor, 1 major
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    loudness: Optional[float] = None
    speechiness: Optional[float] = None
