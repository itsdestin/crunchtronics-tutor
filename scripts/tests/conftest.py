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


@pytest.fixture(scope="session")
def teardown_fixture_sidechain_wav(tmp_path_factory) -> Path:
    """Generate a deterministic 30s 126 BPM wav with sidechain-style bass ducking.

    Content: 4-on-the-floor kicks (5ms clicks at every beat) + 65 Hz sustained
    sine bass that ducks ~6 dB on every kick (50ms ramp down, 200ms ramp back up).
    Format: 22050 Hz mono, normalized.

    Used to validate sidechain detection — the detector should fire with
    measured depth ≈ 6 dB on ≈100% of kicks.
    """
    sr = 22050
    dur_s = 30.0
    bpm = 126.0
    n_samples = int(sr * dur_s)
    t = np.arange(n_samples) / sr

    # Sustained sine bass at 65 Hz
    bass = 0.5 * np.sin(2 * np.pi * 65.0 * t)

    # Kick clicks at every beat
    clicks = np.zeros(n_samples)
    beat_interval_s = 60.0 / bpm
    click_dur_samples = int(0.005 * sr)  # 5ms click
    n_beats = int(dur_s / beat_interval_s)

    # Sidechain envelope: 1.0 normally, drops to ~0.5 (≈ -6 dB) at each kick,
    # 50ms ramp down + 200ms ramp back up.
    envelope = np.ones(n_samples)
    ramp_down_samples = int(0.05 * sr)
    ramp_up_samples = int(0.2 * sr)
    duck_floor = 0.5  # ~ -6 dB

    for i in range(n_beats):
        beat_idx = int(i * beat_interval_s * sr)
        # Click
        end_idx = min(beat_idx + click_dur_samples, n_samples)
        clicks[beat_idx:end_idx] = 0.7
        # Sidechain dip on the bass envelope
        ramp_down_end = min(beat_idx + ramp_down_samples, n_samples)
        envelope[beat_idx:ramp_down_end] = np.linspace(
            envelope[beat_idx], duck_floor, ramp_down_end - beat_idx
        )
        ramp_up_end = min(ramp_down_end + ramp_up_samples, n_samples)
        envelope[ramp_down_end:ramp_up_end] = np.linspace(
            duck_floor, 1.0, ramp_up_end - ramp_down_end
        )

    audio = bass * envelope + clicks
    audio = audio / np.max(np.abs(audio))

    out_path = tmp_path_factory.mktemp("teardown") / "sidechain-126bpm.wav"
    sf.write(str(out_path), audio, sr)
    return out_path
