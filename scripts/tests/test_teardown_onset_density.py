"""Tests for onset density per band per bar (spec §3.8 step 15, §3.9.onset_density)."""

import numpy as np
import librosa

from teardown.analyze import _onset_density_per_band, analyze
from teardown.models import OnsetDensity, OnsetDensityBar


def test_onset_density_returns_OnsetDensity(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    # Build a fake beat_times_s for a 30s 126 BPM track
    beat_interval_s = 60.0 / 126.0
    beat_times_s = np.arange(0.5, 30.0, beat_interval_s)
    result = _onset_density_per_band(y, sr, beat_times_s)
    assert isinstance(result, OnsetDensity)


def test_onset_density_bars_indexed_from_0(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    beat_interval_s = 60.0 / 126.0
    beat_times_s = np.arange(0.5, 30.0, beat_interval_s)
    result = _onset_density_per_band(y, sr, beat_times_s)
    assert len(result.bars) > 0
    assert result.bars[0].bar_index == 0


def test_onset_density_each_bar_has_all_5_bands(teardown_fixture_wav):
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    beat_interval_s = 60.0 / 126.0
    beat_times_s = np.arange(0.5, 30.0, beat_interval_s)
    result = _onset_density_per_band(y, sr, beat_times_s)
    expected_bands = {"sub", "bass", "low_mids", "highs", "air"}
    for bar in result.bars:
        assert set(bar.onsets_per_band.keys()) == expected_bands


def test_onset_density_bar_times_align_with_beats(teardown_fixture_wav):
    """Bar N starts at beat[N*4] and ends at beat[N*4+4]."""
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    beat_interval_s = 60.0 / 126.0
    beat_times_s = np.arange(0.5, 30.0, beat_interval_s)
    result = _onset_density_per_band(y, sr, beat_times_s)
    bar0 = result.bars[0]
    assert abs(bar0.start_s - beat_times_s[0]) < 0.01
    assert abs(bar0.end_s - beat_times_s[4]) < 0.01


def test_onset_density_clicks_land_in_at_least_one_band(teardown_fixture_wav):
    """The fixture has clicks at every beat — across the full track,
    onset density across all bands and bars must be > 0."""
    y, sr = librosa.load(str(teardown_fixture_wav), sr=22050, mono=True)
    beat_interval_s = 60.0 / 126.0
    beat_times_s = np.arange(0.5, 30.0, beat_interval_s)
    result = _onset_density_per_band(y, sr, beat_times_s)
    total = sum(
        sum(bar.onsets_per_band.values())
        for bar in result.bars
    )
    assert total > 0
