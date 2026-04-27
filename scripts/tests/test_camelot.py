"""Tests for the Camelot wheel lookup."""

import pytest

from enrich.camelot import camelot_from_int_key, key_standard_from_int


@pytest.mark.parametrize(
    "key_int,mode_int,expected_camelot,expected_standard",
    [
        # (Spotify-style key int, mode int, expected camelot, expected standard)
        (0, 1, "8B", "C major"),
        (9, 0, "8A", "A minor"),
        (7, 1, "9B", "G major"),
        (4, 0, "9A", "E minor"),
        (2, 1, "10B", "D major"),
        (11, 0, "10A", "B minor"),
        (9, 1, "11B", "A major"),
        (6, 0, "11A", "F# minor"),
        (4, 1, "12B", "E major"),
        (1, 0, "12A", "C# minor"),
        (11, 1, "1B", "B major"),
        (8, 0, "1A", "G# minor"),
        (6, 1, "2B", "F# major"),
        (3, 0, "2A", "D# minor"),
        (1, 1, "3B", "Db major"),
        (10, 0, "3A", "Bb minor"),
        (8, 1, "4B", "Ab major"),
        (5, 0, "4A", "F minor"),
        (3, 1, "5B", "Eb major"),
        (0, 0, "5A", "C minor"),
        (10, 1, "6B", "Bb major"),
        (7, 0, "6A", "G minor"),
        (5, 1, "7B", "F major"),
        (2, 0, "7A", "D minor"),
    ],
)
def test_camelot_lookup_covers_all_24_keys(
    key_int, mode_int, expected_camelot, expected_standard
):
    assert camelot_from_int_key(key_int, mode_int) == expected_camelot
    assert key_standard_from_int(key_int, mode_int) == expected_standard


def test_invalid_key_int_raises():
    with pytest.raises(ValueError, match="key_int must be in"):
        camelot_from_int_key(12, 1)


def test_invalid_mode_int_raises():
    with pytest.raises(ValueError, match="mode_int must be 0 or 1"):
        camelot_from_int_key(0, 2)
