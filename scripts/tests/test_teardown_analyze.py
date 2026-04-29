"""Tests for the librosa analysis pipeline (spec §3.8 steps 4-9).

Uses the teardown_fixture_wav from tests/conftest.py.
"""

import numpy as np
import pytest

from teardown.analyze import analyze
from teardown.models import AnalysisResult


def test_analyze_returns_AnalysisResult(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert isinstance(result, AnalysisResult)


def test_analyze_tempo_within_2bpm_of_126(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert abs(result.bpm - 126.0) < 2.0


def test_analyze_returns_at_least_50_beats(teardown_fixture_wav):
    # 30s at 126 BPM should yield ~63 beats; allow some slack.
    result = analyze(teardown_fixture_wav)
    assert len(result.beat_times_s) >= 50
    assert len(result.beat_times_s) <= 75


def test_analyze_first_beat_is_early(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert result.beat_times_s[0] < 1.0


def test_analyze_chroma_mean_length_12(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert result.chroma_mean.shape == (12,)


def test_analyze_rms_curve_non_empty(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert len(result.rms_values) > 100
    assert np.all(result.rms_values >= 0)


def test_analyze_mfcc_summary_13_coeffs(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert len(result.mfcc_means) == 13
    assert len(result.mfcc_stds) == 13


def test_analyze_duration_close_to_30s(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert abs(result.duration_s - 30.0) < 0.5


def test_analyze_sample_rate_22050(teardown_fixture_wav):
    result = analyze(teardown_fixture_wav)
    assert result.sample_rate == 22050


def test_analyze_short_audio_raises(tmp_path):
    """Audio under 30s of usable content raises (spec §3.15)."""
    import soundfile as sf
    short_wav = tmp_path / "short.wav"
    sf.write(str(short_wav), np.zeros(22050 * 5), 22050)  # 5 seconds
    with pytest.raises(ValueError, match="suspiciously short"):
        analyze(short_wav)


def test_analyze_beat_times_strictly_monotone(teardown_fixture_wav):
    """plp + localmax should always return strictly-increasing beat positions."""
    result = analyze(teardown_fixture_wav)
    assert np.all(np.diff(result.beat_times_s) > 0)
