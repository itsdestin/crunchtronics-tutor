"""Orchestrator: TTL retry decision, ReccoBeats fetch, summary."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path
from typing import Optional

from dateutil import parser as date_parser

from enrich.camelot import camelot_from_int_key, key_standard_from_int
from enrich.csv_writer import CSV_COLUMNS, EnrichedRow, read_existing, write_atomic
from enrich.models import EnrichmentResult
from enrich.playlists_loader import TrackRecord, load_and_dedupe
from enrich.reccobeats import ReccoBeatsRateLimited, fetch as fetch_reccobeats

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PLAYLISTS_PATH = PROJECT_ROOT / "taste" / "playlists.json"
TRACKS_CSV_PATH = PROJECT_ROOT / "taste" / "tracks.csv"

MISS_TTL_DAYS = 30
THROTTLE_SECONDS = 1.0


def needs_enrichment(
    track: TrackRecord,
    existing: Optional[EnrichedRow],
    now: dt.datetime,
) -> bool:
    """Decide if a track should be (re-)enriched on this run."""
    if existing is None:
        return True
    if not existing.source.startswith("miss:"):
        return False
    fetched = date_parser.isoparse(existing.fetched_at)
    age = now - fetched
    return age >= dt.timedelta(days=MISS_TTL_DAYS)


def plan_run(
    tracks: list[TrackRecord],
    existing: dict[str, EnrichedRow],
    now: dt.datetime,
    *,
    force_all: bool = False,
    retry_misses: bool = False,
    limit: Optional[int] = None,
) -> list[TrackRecord]:
    """Return the subset of tracks that should be enriched on this run."""
    out: list[TrackRecord] = []
    for track in tracks:
        existing_row = existing.get(track.spotify_id)
        if force_all:
            out.append(track)
        elif retry_misses and existing_row is not None and existing_row.source.startswith("miss:"):
            out.append(track)
        elif needs_enrichment(track, existing_row, now):
            out.append(track)
        if limit is not None and len(out) >= limit:
            break
    return out


def merge_for_write(
    final: dict[str, EnrichedRow],
    tracks_in_playlists: list[TrackRecord],
    *,
    force_all: bool,
) -> list[EnrichedRow]:
    """Decide which rows to write to tracks.csv.

    Default (cumulative): every row in `final` survives, including orphans
    whose source playlist is no longer in playlists.json (because #5 pulls
    are selective and the user's selection can change).

    --force-all: only rows currently in playlists.json survive — orphans
    get dropped, the csv is genuinely rebuilt from scratch.
    """
    if force_all:
        return [final[t.spotify_id] for t in tracks_in_playlists if t.spotify_id in final]
    return list(final.values())


def _to_enriched_row(
    track: TrackRecord,
    result: Optional[EnrichmentResult],
    source: str,
    now: dt.datetime,
) -> EnrichedRow:
    """Build an EnrichedRow from track metadata + (optional) audio features."""
    if result is None or result.key_int is None or result.mode is None:
        camelot, standard = "", ""
    else:
        camelot = camelot_from_int_key(result.key_int, result.mode)
        standard = key_standard_from_int(result.key_int, result.mode)

    return EnrichedRow(
        spotify_id=track.spotify_id,
        isrc=track.isrc,
        artist=track.artist,
        artists=track.artists,
        title=track.title,
        album=track.album,
        duration_s=track.duration_s,
        bpm=result.bpm if result else None,
        key_camelot=camelot,
        key_standard=standard,
        mode=result.mode if result else None,
        energy=result.energy if result else None,
        danceability=result.danceability if result else None,
        valence=result.valence if result else None,
        acousticness=result.acousticness if result else None,
        instrumentalness=result.instrumentalness if result else None,
        liveness=result.liveness if result else None,
        loudness=result.loudness if result else None,
        speechiness=result.speechiness if result else None,
        genre="",
        source=source,
        fetched_at=now.isoformat().replace("+00:00", "Z"),
    )


def _enrich_one(track: TrackRecord, now: dt.datetime) -> EnrichedRow:
    """Fetch one track from ReccoBeats and return an EnrichedRow.

    Raises:
        ReccoBeatsRateLimited: ReccoBeats returned 429. Propagated to the
            caller (main()) so the run can stop cleanly with partial
            progress preserved.
    """
    recco = fetch_reccobeats(track.spotify_id)
    if recco is not None:
        return _to_enriched_row(track, recco, source="reccobeats", now=now)
    return _to_enriched_row(track, result=None, source="miss:reccobeats", now=now)


def run_summary(
    *,
    total: int,
    candidates: int,
    newly_enriched: int,
    still_missed: int,
    skipped: dict[str, int],
) -> str:
    """Render the end-of-run summary.

    `total` is the row count in tracks.csv after this run (cumulative;
    includes orphans). `candidates` is the number of tracks the plan
    decided to enrich on this run. `newly_enriched` is how many of those
    actually got hits this run. `still_missed` is the count of `miss:*`
    rows in the final csv (cumulative — not just from this run).
    """
    lines = [
        f"Run complete: {newly_enriched}/{candidates} candidates newly enriched. "
        f"tracks.csv now has {total} rows; {still_missed} still missed cumulatively.",
    ]
    if any(skipped.values()):
        lines.append(
            f"  Skipped: {skipped['local_files']} local files, "
            f"{skipped['episodes_or_other']} episodes/other, "
            f"{skipped['duplicates']} duplicates."
        )
    return "\n".join(lines)


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="enrich",
        description="Enrich taste/tracks.csv from taste/playlists.json via ReccoBeats.",
    )
    p.add_argument("--retry-misses", action="store_true",
                   help="Skip the 30-day TTL; retry every row with source=miss:*.")
    p.add_argument("--force-all", action="store_true",
                   help="Re-enrich every track from scratch (rebuilds tracks.csv).")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would be done; make no API calls.")
    p.add_argument("--limit", type=int, default=None,
                   help="Cap the number of tracks enriched (testing).")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    # Track names + artist names contain arbitrary Unicode (e.g., Ł, ł, ñ, ★).
    # The default Windows console is cp1252 and crashes when asked to print them.
    # Reconfigure stdout/stderr to UTF-8 with backslashreplace so unprintable
    # characters degrade gracefully instead of aborting the run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

    if not PLAYLISTS_PATH.exists():
        print(
            f"ERROR: {PLAYLISTS_PATH.relative_to(PROJECT_ROOT)} not found. "
            "Run /pull-spotify-data first (or ask Claude to pull it).",
            file=sys.stderr,
        )
        return 2

    tracks, skipped = load_and_dedupe(PLAYLISTS_PATH)
    existing = read_existing(TRACKS_CSV_PATH)
    now = dt.datetime.now(dt.timezone.utc)

    plan = plan_run(
        tracks,
        existing,
        now=now,
        force_all=args.force_all,
        retry_misses=args.retry_misses,
        limit=args.limit,
    )

    print(f"Plan: {len(plan)} tracks to enrich (of {len(tracks)} total deduped).")

    if args.dry_run:
        for t in plan[:20]:
            print(f"  {t.spotify_id} — {t.artist} — {t.title}")
        if len(plan) > 20:
            print(f"  ... and {len(plan) - 20} more")
        return 0

    newly_enriched = 0

    # Merge: existing + new. Re-enriched rows override existing entries.
    final: dict[str, EnrichedRow] = dict(existing)
    for track in plan:
        try:
            row = _enrich_one(track, now=now)
        except ReccoBeatsRateLimited as e:
            print(
                f"\nReccoBeats rate-limited (Retry-After {e.retry_after_s}s). "
                "Stopping run; partial progress preserved. Resume with `python scripts/enrich.py`.",
                file=sys.stderr,
            )
            break
        final[track.spotify_id] = row
        if row.source == "reccobeats":
            newly_enriched += 1
        time.sleep(THROTTLE_SECONDS)

    rows_to_write = merge_for_write(final, tracks, force_all=args.force_all)

    write_atomic(TRACKS_CSV_PATH, rows_to_write)

    still_missed = sum(1 for r in rows_to_write if r.source.startswith("miss:"))
    print()
    print(
        run_summary(
            total=len(rows_to_write),
            candidates=len(plan),
            newly_enriched=newly_enriched,
            still_missed=still_missed,
            skipped=skipped,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
