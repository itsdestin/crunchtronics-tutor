"""Tests for --check-deps and the ffmpeg presence probe (spec §3.15)."""

from unittest.mock import MagicMock

import pytest

from teardown.cli import _ffmpeg_available, run_check_deps


def test_ffmpeg_available_returns_true_when_present(monkeypatch):
    fake_run = MagicMock(return_value=MagicMock(returncode=0))
    monkeypatch.setattr("teardown.cli.subprocess.run", fake_run)
    assert _ffmpeg_available() is True


def test_ffmpeg_available_returns_false_when_missing(monkeypatch):
    fake_run = MagicMock(side_effect=FileNotFoundError())
    monkeypatch.setattr("teardown.cli.subprocess.run", fake_run)
    assert _ffmpeg_available() is False


def test_run_check_deps_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr("teardown.cli._ffmpeg_available", lambda: True)
    rc = run_check_deps()
    captured = capsys.readouterr()
    assert rc == 0
    assert "ffmpeg" in captured.out.lower()
    assert "librosa" in captured.out.lower()
    assert "yt-dlp" in captured.out.lower()
    assert "matplotlib" in captured.out.lower()
