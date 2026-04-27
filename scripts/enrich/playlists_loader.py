"""Load taste/playlists.json, filter non-track items, dedupe by Spotify ID."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrackRecord:
    """Metadata extracted from a Spotify playlist item.

    Audio features are added later by the enrichment fetchers.
    """

    spotify_id: str
    isrc: str
    artist: str
    title: str
    album: str
    duration_s: int


def load_and_dedupe(path: Path) -> tuple[list[TrackRecord], dict[str, int]]:
    """Read a playlists.json file and return (records, skipped_counts).

    `records` is deduplicated by spotify_id; the first occurrence wins.
    `skipped_counts` reports how many items were filtered out and why,
    so the end-of-run summary can report them.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    seen: set[str] = set()
    records: list[TrackRecord] = []
    skipped = {"local_files": 0, "episodes_or_other": 0, "duplicates": 0}

    for playlist in data.get("playlists", []):
        for item in playlist.get("tracks", []):
            item_type = item.get("type", "track")
            if item_type != "track":
                skipped["episodes_or_other"] += 1
                continue
            if item.get("is_local") or item.get("id") is None:
                skipped["local_files"] += 1
                continue
            spotify_id = item["id"]
            if spotify_id in seen:
                skipped["duplicates"] += 1
                continue
            seen.add(spotify_id)
            artists = item.get("artists", [])
            primary_artist = artists[0]["name"] if artists else ""
            records.append(
                TrackRecord(
                    spotify_id=spotify_id,
                    isrc=item.get("external_ids", {}).get("isrc", ""),
                    artist=primary_artist,
                    title=item.get("name", ""),
                    album=item.get("album", {}).get("name", ""),
                    duration_s=item.get("duration_ms", 0) // 1000,
                )
            )

    return records, skipped
