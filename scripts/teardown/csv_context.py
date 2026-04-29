"""Look up a row from taste/tracks.csv by spotify_id."""

import csv
from pathlib import Path
from typing import Any, Optional

_FLOAT_COLS = {"bpm", "energy", "danceability", "valence", "acousticness",
               "instrumentalness", "liveness", "loudness", "speechiness"}
_INT_COLS = {"duration_s", "mode", "time_signature"}
_STR_COLS = {"spotify_id", "isrc", "artist", "title", "album",
             "key_camelot", "key_standard", "genre", "source", "fetched_at"}


def _coerce(col: str, value: str) -> Any:
    if value == "":
        return None
    if col in _FLOAT_COLS:
        return float(value)
    if col in _INT_COLS:
        return int(value)
    return value  # _STR_COLS or unknown — pass through


def load_csv_context(csv_path: Path, spotify_id: str) -> Optional[dict[str, Any]]:
    """Return the matching row as a dict (with typed values), or None.

    None is returned when:
    - The CSV file does not exist
    - No row matches the given spotify_id
    """
    if not csv_path.exists():
        return None
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("spotify_id") == spotify_id:
                return {col: _coerce(col, val) for col, val in row.items()}
    return None
