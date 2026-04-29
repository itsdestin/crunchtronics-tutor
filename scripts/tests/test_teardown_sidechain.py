"""Tests for sidechain detection (spec §3.8 step 16, §3.9.sidechain)."""

import numpy as np
import librosa

from teardown.analyze import _sidechain_detection
from teardown.models import SidechainResult


def test_sidechain_returns_SidechainResult(teardown_fixture_sidechain_wav):
    y, sr = librosa.load(str(teardown_fixture_sidechain_wav), sr=22050, mono=True)
    result = _sidechain_detection(y, sr)
    assert isinstance(result, SidechainResult)


def test_sidechain_detected_on_sidechain_fixture(teardown_fixture_sidechain_wav):
    """The sidechain fixture has -6 dB ducking on every kick — must detect."""
    y, sr = librosa.load(str(teardown_fixture_sidechain_wav), sr=22050, mono=True)
    result = _sidechain_detection(y, sr)
    assert result.detected is True
    assert result.depth_db_mean >= 3.0
    assert result.consistency_pct >= 60.0


def test_sidechain_not_detected_on_non_sidechain_fixture(teardown_fixture_wav):
    """The base fixture has clicks but no bass ducking — must not detect."""
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _sidechain_detection(y, sr)
    assert result.detected is False


def test_sidechain_thresholds_recorded(teardown_fixture_sidechain_wav):
    """The thresholds are stored in the result so they can be re-tuned."""
    y, sr = librosa.load(str(teardown_fixture_sidechain_wav), sr=22050, mono=True)
    result = _sidechain_detection(y, sr)
    assert result.threshold_db_for_detection == 3.0
    assert result.threshold_consistency_for_detection == 60.0


def test_sidechain_method_label(teardown_fixture_sidechain_wav):
    y, sr = librosa.load(str(teardown_fixture_sidechain_wav), sr=22050, mono=True)
    result = _sidechain_detection(y, sr)
    assert "sub-band" in result.method.lower()
    assert "bass-band" in result.method.lower()


def test_sidechain_kicks_examined_positive(teardown_fixture_sidechain_wav):
    y, sr = librosa.load(str(teardown_fixture_sidechain_wav), sr=22050, mono=True)
    result = _sidechain_detection(y, sr)
    # 30s at 126 BPM ≈ 63 kicks
    assert 30 <= result.kicks_examined <= 80
