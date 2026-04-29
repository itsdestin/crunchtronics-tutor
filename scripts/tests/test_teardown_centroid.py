"""Tests for spectral centroid (spec §3.8 step 14, §3.9.spectral_centroid)."""

import numpy as np
import librosa

from teardown.analyze import _spectral_centroid
from teardown.models import CentroidResult


def test_centroid_returns_CentroidResult(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _spectral_centroid(y, sr)
    assert isinstance(result, CentroidResult)


def test_centroid_values_are_positive(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _spectral_centroid(y, sr)
    assert np.all(result.values_hz >= 0)


def test_centroid_low_for_bass_heavy_signal():
    """A pure 100 Hz sine should have centroid near 100 Hz."""
    sr = 22050
    t = np.arange(sr * 31) / sr
    y = 0.5 * np.sin(2 * np.pi * 100 * t)
    result = _spectral_centroid(y, sr)
    # Mean centroid should be in the low hundreds of Hz, not multiple kHz
    assert result.values_hz.mean() < 500


def test_centroid_high_for_bright_signal():
    """A 5 kHz sine should have centroid near 5 kHz."""
    sr = 22050
    t = np.arange(sr * 31) / sr
    y = 0.5 * np.sin(2 * np.pi * 5000 * t)
    result = _spectral_centroid(y, sr)
    assert result.values_hz.mean() > 4000


def test_centroid_hop_length_is_512(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _spectral_centroid(y, sr)
    assert result.hop_length == 512
