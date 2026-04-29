"""Tests for the yt-dlp wrapper (spec §3.8 step 3, §3.15 errors)."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from teardown.ytdlp import (
    DownloadError,
    SearchResult,
    download_audio,
    resolve_search,
)


def test_resolve_search_parses_yt_dlp_output(monkeypatch):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(
        returncode=0,
        stdout="John Summit & HAYLA — Where You Are (Official Audio)|3:42|John Summit\n",
        stderr="",
    )
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    result = resolve_search("John Summit Where You Are")

    assert isinstance(result, SearchResult)
    assert result.title.startswith("John Summit & HAYLA")
    assert result.duration_string == "3:42"
    assert result.channel == "John Summit"


def test_resolve_search_raises_on_yt_dlp_error(monkeypatch):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(returncode=1, stdout="", stderr="ERROR: nope")
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    with pytest.raises(DownloadError, match="search failed"):
        resolve_search("anything")


def test_download_audio_invokes_yt_dlp_with_wav_extraction(monkeypatch, tmp_path):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    out_path = tmp_path / "source.wav"
    # file does not exist yet — yt-dlp (mocked) would create it

    download_audio("https://x", out_path, force=False)

    args = fake_run.call_args[0][0]
    # Wrapper invokes via `python -m yt_dlp` so the module name appears as a
    # standalone token in the arg list (and args[0] is the Python exe).
    assert "yt_dlp" in args
    assert "-m" in args
    assert "--extract-audio" in args
    assert "--audio-format" in args
    assert "wav" in args
    assert "https://x" in args


def test_download_audio_skips_when_file_exists_and_not_force(monkeypatch, tmp_path):
    fake_run = MagicMock()
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    out_path = tmp_path / "source.wav"
    out_path.write_bytes(b"existing")

    download_audio("https://x", out_path, force=False)

    fake_run.assert_not_called()


def test_download_audio_overwrites_when_force(monkeypatch, tmp_path):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    out_path = tmp_path / "source.wav"
    out_path.write_bytes(b"existing")

    download_audio("https://x", out_path, force=True)

    fake_run.assert_called_once()
    args = fake_run.call_args[0][0]
    assert "--force-overwrites" in args


def test_download_audio_raises_on_yt_dlp_error(monkeypatch, tmp_path):
    fake_run = MagicMock()
    fake_run.return_value = MagicMock(returncode=1, stdout="", stderr="ERROR: 403")
    monkeypatch.setattr("teardown.ytdlp.subprocess.run", fake_run)

    with pytest.raises(DownloadError, match="download failed"):
        download_audio("https://x", tmp_path / "source.wav", force=False)
