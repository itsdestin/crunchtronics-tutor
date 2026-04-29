"""Dataclasses for teardown pipeline results."""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass(frozen=True, eq=False)
class PerBandRMS:
    """Per-band RMS curves over time. Five EDM-tuned bands."""
    hop_length: int
    sub_rms: np.ndarray         # 20-60 Hz
    bass_rms: np.ndarray        # 60-250 Hz
    low_mids_rms: np.ndarray    # 250-2000 Hz
    highs_rms: np.ndarray       # 2000-8000 Hz
    air_rms: np.ndarray         # 8000+ Hz


@dataclass(frozen=True, eq=False)
class HPSSResult:
    """RMS curves of the harmonic and percussive components after librosa.effects.hpss."""
    hop_length: int
    harmonic_rms: np.ndarray
    percussive_rms: np.ndarray


@dataclass(frozen=True, eq=False)
class CentroidResult:
    """Spectral centroid curve over time (Hz)."""
    hop_length: int
    values_hz: np.ndarray


@dataclass(frozen=True, eq=False)
class OnsetDensityBar:
    """Onset counts per band for a single bar."""
    bar_index: int
    start_s: float
    end_s: float
    onsets_per_band: dict  # {"sub": int, "bass": int, "low_mids": int, "highs": int, "air": int}


@dataclass(frozen=True, eq=False)
class OnsetDensity:
    """Onset density per bar across all bars in the track."""
    bars: list  # list[OnsetDensityBar]


@dataclass(frozen=True, eq=False)
class SidechainResult:
    """Sidechain detection: kick-aligned bass-band RMS dip analysis."""
    detected: bool
    depth_db_mean: float
    depth_db_p90: float
    consistency_pct: float
    kicks_examined: int
    threshold_db_for_detection: float
    threshold_consistency_for_detection: float
    method: str = (
        "sub-band onset detect + bass-band RMS dip "
        "within 100ms vs rolling mean"
    )


@dataclass(frozen=True, eq=False)
class AnalysisResult:
    duration_s: float
    sample_rate: int
    bpm: float
    beat_times_s: np.ndarray
    chroma_mean: np.ndarray   # shape (12,)
    rms_values: np.ndarray    # 1-D
    rms_hop_length: int
    mfcc_means: np.ndarray    # shape (13,)
    mfcc_stds: np.ndarray     # shape (13,)

    # v1.1 additions — optional with None defaults so v1.0 test code still works.
    per_band_rms: Optional[PerBandRMS] = None
    hpss: Optional[HPSSResult] = None
    spectral_centroid: Optional[CentroidResult] = None
    onset_density: Optional[OnsetDensity] = None
    sidechain: Optional[SidechainResult] = None
