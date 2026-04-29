"""Tests for HPSS split (spec §3.8 step 13, §3.9.hpss)."""

import numpy as np
import librosa

from teardown.analyze import _hpss_split
from teardown.models import HPSSResult


def test_hpss_returns_HPSSResult(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _hpss_split(y, sr)
    assert isinstance(result, HPSSResult)


def test_hpss_curves_same_length(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _hpss_split(y, sr)
    assert len(result.harmonic_rms) == len(result.percussive_rms)
    assert len(result.harmonic_rms) > 0


def test_hpss_sustained_sine_lands_in_harmonic():
    """A pure sine tone has all energy in the harmonic component."""
    sr = 22050
    t = np.arange(sr * 31) / sr
    y = 0.5 * np.sin(2 * np.pi * 440 * t)  # 31s of A4
    result = _hpss_split(y, sr)
    # Harmonic energy should dominate percussive
    assert result.harmonic_rms.mean() > result.percussive_rms.mean() * 5


def test_hpss_clicks_land_in_percussive():
    """Repeated transient clicks should land in percussive."""
    sr = 22050
    n = sr * 31
    y = np.zeros(n)
    # Click every 0.5s
    for i in range(int(31 / 0.5)):
        idx = int(i * 0.5 * sr)
        if idx + 100 < n:
            y[idx:idx + 100] = 0.7
    result = _hpss_split(y, sr)
    assert result.percussive_rms.mean() > result.harmonic_rms.mean()


def test_hpss_hop_length_is_512(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _hpss_split(y, sr)
    assert result.hop_length == 512
