"""Tests for per-band RMS computation (spec §3.8 step 12, §3.9.per_band_rms)."""

import numpy as np
import librosa

from teardown.analyze import _per_band_rms
from teardown.models import PerBandRMS


def test_per_band_rms_returns_PerBandRMS(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _per_band_rms(y, sr)
    assert isinstance(result, PerBandRMS)


def test_per_band_rms_hop_length_is_512(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _per_band_rms(y, sr)
    assert result.hop_length == 512


def test_per_band_rms_all_bands_same_length(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _per_band_rms(y, sr)
    n = len(result.sub_rms)
    assert len(result.bass_rms) == n
    assert len(result.low_mids_rms) == n
    assert len(result.highs_rms) == n
    assert len(result.air_rms) == n


def test_per_band_rms_sub_dominates_for_65hz_fixture(teardown_fixture_wav):
    """The fixture is 65 Hz sine bass + clicks. Sub band (20-60 Hz)
    or bass band (60-250 Hz) should carry more energy than air."""
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _per_band_rms(y, sr)
    # 65 Hz sits at the sub/bass boundary — both should dominate over air.
    assert result.bass_rms.mean() > result.air_rms.mean() * 5


def test_per_band_rms_air_band_near_zero_for_bass_only(teardown_fixture_wav):
    """A 65 Hz sine + transient clicks has very little 8 kHz+ content."""
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    result = _per_band_rms(y, sr)
    # Click transients spread some energy into highs but air should be tiny.
    assert result.air_rms.mean() < 0.051


def test_per_band_rms_handles_silence():
    """Pure silence should produce all-zero per-band RMS."""
    sr = 22050
    silence = np.zeros(sr * 31)  # 31s of silence (skip the <30s guard)
    result = _per_band_rms(silence, sr)
    assert np.all(result.sub_rms == 0)
    assert np.all(result.air_rms == 0)
