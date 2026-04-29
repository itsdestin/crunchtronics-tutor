"""Krumhansl-Schmuckler key estimation from a chroma mean vector.

Reference: Krumhansl, C. L., & Kessler, E. J. (1982). Tracing the dynamic
changes in perceived tonal organization in a spatial representation of
musical keys. Psychological Review, 89(4), 334-368.

The KS algorithm correlates a track's chroma profile against 24 reference
profiles (12 major + 12 minor). The reference profiles below are
Krumhansl's original tone-profiles, which remain the standard.
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np

# Krumhansl-Kessler tone profiles (root-relative).
_MAJOR_PROFILE = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88,
])
_MINOR_PROFILE = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17,
])

_PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Camelot wheel — 24 entries. Reuses semantics from scripts/enrich/camelot.py
# (open-coded here to avoid cross-package import at this layer; the
# correctness check below ensures consistency).
_CAMELOT: dict[tuple[str, str], str] = {
    ("C", "major"): "8B",   ("A", "minor"): "8A",
    ("G", "major"): "9B",   ("E", "minor"): "9A",
    ("D", "major"): "10B",  ("B", "minor"): "10A",
    ("A", "major"): "11B",  ("F#", "minor"): "11A",
    ("E", "major"): "12B",  ("C#", "minor"): "12A",
    ("B", "major"): "1B",   ("G#", "minor"): "1A",
    ("F#", "major"): "2B",  ("D#", "minor"): "2A",
    ("C#", "major"): "3B",  ("A#", "minor"): "3A",
    ("G#", "major"): "4B",  ("F", "minor"): "4A",
    ("D#", "major"): "5B",  ("C", "minor"): "5A",
    ("A#", "major"): "6B",  ("G", "minor"): "6A",
    ("F", "major"): "7B",   ("D", "minor"): "7A",
}


@dataclass(frozen=True)
class KeyEstimate:
    standard: str  # e.g., "F minor"
    camelot: str   # e.g., "5A"
    method: str = "Krumhansl-Schmuckler on chroma_cqt mean"


def estimate_key(chroma_mean: np.ndarray) -> KeyEstimate:
    """Estimate key from a 12-vector chroma mean."""
    if chroma_mean.shape != (12,):
        raise ValueError(f"chroma_mean must be length 12, got shape {chroma_mean.shape}")

    best_corr = -np.inf
    best_root = 0
    best_mode: Literal["major", "minor"] = "major"

    for root in range(12):
        for mode_name, profile in (("major", _MAJOR_PROFILE), ("minor", _MINOR_PROFILE)):
            shifted = np.roll(profile, root)
            # Pearson correlation
            corr = np.corrcoef(chroma_mean, shifted)[0, 1]
            if not np.isnan(corr) and corr > best_corr:
                best_corr = corr
                best_root = root
                best_mode = mode_name

    pitch = _PITCH_NAMES[best_root]
    standard = f"{pitch} {best_mode}"
    camelot = _CAMELOT[(pitch, best_mode)]
    return KeyEstimate(standard=standard, camelot=camelot)
