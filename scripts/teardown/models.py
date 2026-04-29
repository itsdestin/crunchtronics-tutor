"""Dataclasses for teardown pipeline results."""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class AnalysisResult:
    duration_s: float
    sample_rate: int
    bpm: float
    beat_times_s: np.ndarray
    chroma_mean: np.ndarray  # shape (12,)
    rms_values: np.ndarray   # 1-D
    rms_hop_length: int
    mfcc_means: np.ndarray   # shape (13,)
    mfcc_stds: np.ndarray    # shape (13,)
