"""Subprocess wrapper around yt-dlp (spec §3.8 step 3, §3.15)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class DownloadError(RuntimeError):
    """yt-dlp failed (search or download)."""


@dataclass(frozen=True)
class SearchResult:
    title: str
    duration_string: str
    channel: str


def resolve_search(query: str) -> SearchResult:
    """Run `yt-dlp ytsearch1:` and return the resolved title/duration/channel.

    Does not download audio. Used by the skill flow before Destin's
    URL-confirmation step.
    """
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--print", "%(title)s|%(duration_string)s|%(channel)s",
        f"ytsearch1:{query}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise DownloadError(f"yt-dlp search failed: {proc.stderr.strip()}")

    parts = proc.stdout.strip().split("|", 2)
    if len(parts) != 3:
        raise DownloadError(f"yt-dlp search returned unexpected format: {proc.stdout!r}")
    return SearchResult(title=parts[0], duration_string=parts[1], channel=parts[2])


def download_audio(url: str, out_path: Path, *, force: bool) -> None:
    """Download `url` as a wav to `out_path`.

    If `out_path` already exists and `force` is False, this is a no-op
    (the existing file is treated as the canonical source).
    """
    if out_path.exists() and not force:
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "--output", str(out_path),
        url,
    ]
    if force:
        cmd.insert(1, "--force-overwrites")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise DownloadError(f"yt-dlp download failed: {proc.stderr.strip()}")
