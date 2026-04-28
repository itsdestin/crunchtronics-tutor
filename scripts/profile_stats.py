"""CLI: emit aggregation JSON over taste/tracks.csv to stdout.

Run from project root:
    python scripts/profile_stats.py

Spec: docs/superpowers/specs/subsystems/07-taste-profile.md §3.4
"""
import json
import sys
from pathlib import Path

# Make the local `profile` package importable when invoked via
# `python scripts/profile_stats.py` from project root.
sys.path.insert(0, str(Path(__file__).parent))

from profile.aggregator import (
    top_artists,
    bpm_histogram,
    camelot_distribution,
    key_split,
    feature_means,
)
from profile.reader import load_tracks


def build_stats(rows: list[dict]) -> dict:
    enriched = [r for r in rows if not r.get("source", "").startswith("miss:")]
    return {
        "row_count": len(rows),
        "enriched_count": len(enriched),
        "missing_count": len(rows) - len(enriched),
        "top_artists": top_artists(rows),
        "bpm_histogram": bpm_histogram(rows),
        "camelot_distribution": camelot_distribution(rows),
        "key_split": key_split(rows),
        "feature_means": feature_means(rows),
    }


def main() -> int:
    csv_path = Path("taste/tracks.csv")
    if not csv_path.exists():
        print(
            f"error: {csv_path} not found. Run audio enrichment first "
            f"(see CLAUDE.md → Audio enrichment).",
            file=sys.stderr,
        )
        return 1
    rows = load_tracks(csv_path)
    stats = build_stats(rows)
    json.dump(stats, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
