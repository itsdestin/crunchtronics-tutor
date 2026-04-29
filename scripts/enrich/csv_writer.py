"""Read and write taste/tracks.csv with the schema from spec §3.4."""

import csv
import datetime as dt
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Final, Optional

CSV_COLUMNS: Final[list[str]] = [
    "spotify_id", "isrc", "artist", "artists", "title", "album", "duration_s",
    "bpm", "key_camelot", "key_standard", "mode",
    "energy", "danceability", "valence", "acousticness", "instrumentalness",
    "liveness", "loudness", "speechiness",
    "genre", "source", "fetched_at",
]


@dataclass(frozen=True)
class EnrichedRow:
    spotify_id: str
    isrc: str
    artist: str
    artists: str
    title: str
    album: str
    duration_s: int
    bpm: Optional[float]
    key_camelot: str
    key_standard: str
    mode: Optional[int]
    energy: Optional[float]
    danceability: Optional[float]
    valence: Optional[float]
    acousticness: Optional[float]
    instrumentalness: Optional[float]
    liveness: Optional[float]
    loudness: Optional[float]
    speechiness: Optional[float]
    genre: str
    source: str
    fetched_at: str


def _row_to_csv_dict(row: EnrichedRow) -> dict[str, str]:
    """Render a row to the dict csv expects, with None -> empty string."""
    out = {}
    for col in CSV_COLUMNS:
        value = getattr(row, col)
        out[col] = "" if value is None else str(value)
    return out


def _csv_dict_to_row(d: dict[str, str]) -> EnrichedRow:
    def opt_float(s: str) -> Optional[float]:
        return float(s) if s else None

    def opt_int(s: str) -> Optional[int]:
        return int(s) if s else None

    return EnrichedRow(
        spotify_id=d["spotify_id"],
        isrc=d["isrc"],
        artist=d["artist"],
        artists=d["artists"],
        title=d["title"],
        album=d["album"],
        duration_s=int(d["duration_s"]) if d["duration_s"] else 0,
        bpm=opt_float(d["bpm"]),
        key_camelot=d["key_camelot"],
        key_standard=d["key_standard"],
        mode=opt_int(d["mode"]),
        energy=opt_float(d["energy"]),
        danceability=opt_float(d["danceability"]),
        valence=opt_float(d["valence"]),
        acousticness=opt_float(d["acousticness"]),
        instrumentalness=opt_float(d["instrumentalness"]),
        liveness=opt_float(d["liveness"]),
        loudness=opt_float(d["loudness"]),
        speechiness=opt_float(d["speechiness"]),
        genre=d["genre"],
        source=d["source"],
        fetched_at=d["fetched_at"],
    )


def read_existing(path: Path) -> dict[str, EnrichedRow]:
    """Read tracks.csv, return {spotify_id: EnrichedRow}.

    On schema mismatch (corrupt file), back the file up to
    tracks.csv.corrupt-<UTC-timestamp> and return {} so the next write
    rebuilds from scratch.
    """
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            # Access fieldnames inside the with-block so the header is read,
            # but collect everything before we decide to bail so the file is
            # closed before we try to rename it on Windows.
            fieldnames = reader.fieldnames
            rows_raw = list(reader)
    except (csv.Error, UnicodeDecodeError):
        _backup_corrupt(path)
        return {}

    if fieldnames != CSV_COLUMNS:
        _backup_corrupt(path)
        return {}

    try:
        out: dict[str, EnrichedRow] = {}
        for d in rows_raw:
            out[d["spotify_id"]] = _csv_dict_to_row(d)
        return out
    except KeyError:
        _backup_corrupt(path)
        return {}


def _backup_corrupt(path: Path) -> None:
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_name(f"{path.name}.corrupt-{timestamp}")
    path.rename(backup)
    print(f"WARNING: backed up unreadable {path.name} to {backup.name}; rebuilding fresh.")


def write_atomic(path: Path, rows: list[EnrichedRow]) -> None:
    """Write rows to a temp file, then rename to the final path."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.DictWriter(
            f, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(_row_to_csv_dict(row))
    tmp.replace(path)
