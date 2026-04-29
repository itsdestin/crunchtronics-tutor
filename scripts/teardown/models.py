"""Dataclasses for teardown pipeline results."""

from dataclasses import dataclass

import numpy as np


# eq=False because ndarray fields make auto-generated __eq__ raise.
# AnalysisResult is produced and consumed in a pipeline; equality and
# hashing aren't needed.
@dataclass(frozen=True, eq=False)
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
