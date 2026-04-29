"""Shared pytest fixtures for the scripts test suite."""

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf


@pytest.fixture(scope="session")
def teardown_fixture_wav(tmp_path_factory) -> Path:
    """Generate a deterministic 30s 126 BPM wav for teardown tests.

    Content: 65 Hz sine bass + 5ms clicks at every 126-BPM beat.
    Format: 22050 Hz mono, normalized.
    """
    sr = 22050
    dur_s = 30.0
    bpm = 126.0
    n_samples = int(sr * dur_s)
    t = np.arange(n_samples) / sr

    # Sine bass at 65 Hz (~C2)
    bass = 0.3 * np.sin(2 * np.pi * 65.0 * t)

    # Click metronome at 126 BPM (interval = 60/126 ≈ 0.476 s)
    clicks = np.zeros(n_samples)
    beat_interval_s = 60.0 / bpm
    click_dur_samples = int(0.005 * sr)  # 5ms click
    n_beats = int(dur_s / beat_interval_s)
    for i in range(n_beats):
        beat_idx = int(i * beat_interval_s * sr)
        end_idx = min(beat_idx + click_dur_samples, n_samples)
        clicks[beat_idx:end_idx] = 0.7

    audio = bass + clicks
    audio = audio / np.max(np.abs(audio))  # normalize to [-1, 1]

    out_path = tmp_path_factory.mktemp("teardown") / "click-126bpm.wav"
    sf.write(str(out_path), audio, sr)
    return out_path
