"""Tests for Krumhansl-Schmuckler key estimator (spec §3.8 step 7)."""

import numpy as np
import pytest

from teardown.key import estimate_key


def test_pure_c_major_chroma_returns_c_major():
    # Strong C, E, G; weak everything else (a C major triad's chroma profile).
    chroma_mean = np.zeros(12)
    chroma_mean[0] = 1.0   # C
    chroma_mean[4] = 0.7   # E
    chroma_mean[7] = 0.7   # G

    result = estimate_key(chroma_mean)

    assert result.standard == "C major"
    assert result.camelot == "8B"


def test_pure_a_minor_chroma_returns_a_minor():
    # A, C, E (A minor triad).
    chroma_mean = np.zeros(12)
    chroma_mean[9] = 1.0   # A
    chroma_mean[0] = 0.7   # C
    chroma_mean[4] = 0.7   # E

    result = estimate_key(chroma_mean)

    assert result.standard == "A minor"
    assert result.camelot == "8A"


def test_returns_camelot_string_format():
    chroma_mean = np.ones(12)  # uniform — degenerate but should still classify
    result = estimate_key(chroma_mean)
    # Camelot is 1A-12A or 1B-12B
    assert result.camelot[-1] in ("A", "B")
    assert 1 <= int(result.camelot[:-1]) <= 12


def test_method_label():
    result = estimate_key(np.ones(12))
    assert "krumhansl" in result.method.lower()


def test_chroma_mean_must_be_length_12():
    with pytest.raises(ValueError, match="length 12"):
        estimate_key(np.zeros(11))
