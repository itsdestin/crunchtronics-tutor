"""Tests for the orchestrator (TTL, fallback chain, summary)."""

import datetime as dt
from pathlib import Path
from unittest.mock import patch

import pytest

from enrich.cli import (
    merge_for_write,
    needs_enrichment,
    plan_run,
    run_summary,
)
from enrich.csv_writer import EnrichedRow
from enrich.playlists_loader import TrackRecord


def _make_track(sid: str = "t1") -> TrackRecord:
    return TrackRecord(
        spotify_id=sid, isrc="", artist="A", artists="A", title="T",
        album="Al", duration_s=200,
    )


def _make_row(sid: str, source: str, fetched_at: str) -> EnrichedRow:
    return EnrichedRow(
        spotify_id=sid, isrc="", artist="A", artists="A", title="T", album="Al", duration_s=200,
        bpm=None, key_camelot="", key_standard="", mode=None,
        energy=None, danceability=None, valence=None, acousticness=None,
        instrumentalness=None, liveness=None, loudness=None, speechiness=None,
        genre="", source=source, fetched_at=fetched_at,
    )


def test_needs_enrichment_includes_new_tracks():
    track = _make_track("new1")
    assert needs_enrichment(track, existing=None, now=dt.datetime.now(dt.timezone.utc)) is True


def test_needs_enrichment_skips_completed_rows():
    track = _make_track("done1")
    row = _make_row("done1", "reccobeats", "2026-04-25T00:00:00Z")
    now = dt.datetime(2026, 4, 26, tzinfo=dt.timezone.utc)
    assert needs_enrichment(track, existing=row, now=now) is False


def test_needs_enrichment_retries_old_misses():
    track = _make_track("oldmiss")
    row = _make_row("oldmiss", "miss:reccobeats", "2026-03-01T00:00:00Z")
    now = dt.datetime(2026, 4, 26, tzinfo=dt.timezone.utc)  # 56 days later
    assert needs_enrichment(track, existing=row, now=now) is True


def test_needs_enrichment_skips_recent_misses():
    track = _make_track("recentmiss")
    row = _make_row("recentmiss", "miss:reccobeats", "2026-04-20T00:00:00Z")
    now = dt.datetime(2026, 4, 26, tzinfo=dt.timezone.utc)  # 6 days later
    assert needs_enrichment(track, existing=row, now=now) is False


def test_run_summary_nudges_when_unenriched_and_no_getsongbpm():
    summary = run_summary(
        total=10,
        candidates=10,
        newly_enriched=7,
        still_missed=3,
        skipped={"local_files": 0, "episodes_or_other": 0, "duplicates": 0},
        getsongbpm_configured=False,
    )
    assert "10" in summary  # total / candidates
    assert "7" in summary  # newly enriched
    assert "3" in summary  # still missed
    assert "GetSongBPM" in summary  # nudge present


def test_run_summary_no_nudge_when_getsongbpm_configured():
    summary = run_summary(
        total=10,
        candidates=10,
        newly_enriched=10,
        still_missed=0,
        skipped={"local_files": 0, "episodes_or_other": 0, "duplicates": 0},
        getsongbpm_configured=True,
    )
    assert "GetSongBPM" not in summary


def test_plan_run_force_all_enriches_everything():
    tracks = [_make_track("a"), _make_track("b")]
    existing = {
        "a": _make_row("a", "reccobeats", "2026-04-25T00:00:00Z"),
        "b": _make_row("b", "reccobeats", "2026-04-25T00:00:00Z"),
    }
    now = dt.datetime(2026, 4, 26, tzinfo=dt.timezone.utc)
    plan = plan_run(tracks, existing, now=now, force_all=True)
    assert len(plan) == 2


def test_merge_for_write_default_preserves_orphans():
    """Cumulative behavior: rows whose track is no longer in playlists.json
    survive (because #5 pulls are selective and selection can change)."""
    tracks_in_playlists = [_make_track("a")]  # only "a" is in current playlists.json
    final = {
        "a": _make_row("a", "reccobeats", "2026-04-26T00:00:00Z"),
        "orphan": _make_row("orphan", "reccobeats", "2026-04-01T00:00:00Z"),  # was pulled in a previous selection
    }
    rows = merge_for_write(final, tracks_in_playlists, force_all=False)
    ids = {r.spotify_id for r in rows}
    assert ids == {"a", "orphan"}, "orphan row must survive cumulative writes"


def test_merge_for_write_force_all_drops_orphans():
    """--force-all rebuilds from scratch: rows not in current playlists.json get dropped."""
    tracks_in_playlists = [_make_track("a")]
    final = {
        "a": _make_row("a", "reccobeats", "2026-04-26T00:00:00Z"),
        "orphan": _make_row("orphan", "reccobeats", "2026-04-01T00:00:00Z"),
    }
    rows = merge_for_write(final, tracks_in_playlists, force_all=True)
    ids = {r.spotify_id for r in rows}
    assert ids == {"a"}, "orphan must be dropped under --force-all"
