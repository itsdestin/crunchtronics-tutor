"""Read taste/tracks.csv into a list of row dicts. Stdlib csv only."""
import csv
from pathlib import Path


def load_tracks(path: Path | str) -> list[dict]:
    """Return tracks.csv rows as a list of dicts.

    Empty cells stay as empty strings (no None / type coercion). Caller is
    responsible for parsing numeric fields when needed.
    """
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
