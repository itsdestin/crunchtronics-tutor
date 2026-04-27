"""Camelot wheel lookup.

Maps a (key_int, mode_int) pair as ReccoBeats / Spotify return them
to a Camelot string ("8B") and a human-readable standard key ("C major").

Key ints: 0=C, 1=C#/Db, 2=D, 3=D#/Eb, 4=E, 5=F,
          6=F#/Gb, 7=G, 8=G#/Ab, 9=A, 10=A#/Bb, 11=B
Mode ints: 0=minor, 1=major
"""

from typing import Final

# Standard key spelling per (key_int, mode_int). The spelling follows the
# Camelot wheel convention (e.g., 12A is C# minor; 3B is Db major).
_KEY_STANDARD: Final[dict[tuple[int, int], str]] = {
    # major (mode=1)
    (0, 1): "C major",
    (1, 1): "Db major",
    (2, 1): "D major",
    (3, 1): "Eb major",
    (4, 1): "E major",
    (5, 1): "F major",
    (6, 1): "F# major",
    (7, 1): "G major",
    (8, 1): "Ab major",
    (9, 1): "A major",
    (10, 1): "Bb major",
    (11, 1): "B major",
    # minor (mode=0)
    (0, 0): "C minor",
    (1, 0): "C# minor",
    (2, 0): "D minor",
    (3, 0): "D# minor",
    (4, 0): "E minor",
    (5, 0): "F minor",
    (6, 0): "F# minor",
    (7, 0): "G minor",
    (8, 0): "G# minor",
    (9, 0): "A minor",
    (10, 0): "Bb minor",
    (11, 0): "B minor",
}

_CAMELOT: Final[dict[tuple[int, int], str]] = {
    # major (mode=1)
    (0, 1): "8B",
    (7, 1): "9B",
    (2, 1): "10B",
    (9, 1): "11B",
    (4, 1): "12B",
    (11, 1): "1B",
    (6, 1): "2B",
    (1, 1): "3B",
    (8, 1): "4B",
    (3, 1): "5B",
    (10, 1): "6B",
    (5, 1): "7B",
    # minor (mode=0)
    (9, 0): "8A",
    (4, 0): "9A",
    (11, 0): "10A",
    (6, 0): "11A",
    (1, 0): "12A",
    (8, 0): "1A",
    (3, 0): "2A",
    (10, 0): "3A",
    (5, 0): "4A",
    (0, 0): "5A",
    (7, 0): "6A",
    (2, 0): "7A",
}


def _validate(key_int: int, mode_int: int) -> None:
    if not 0 <= key_int <= 11:
        raise ValueError(f"key_int must be in 0..11, got {key_int}")
    if mode_int not in (0, 1):
        raise ValueError(f"mode_int must be 0 or 1, got {mode_int}")


def camelot_from_int_key(key_int: int, mode_int: int) -> str:
    _validate(key_int, mode_int)
    return _CAMELOT[(key_int, mode_int)]


def key_standard_from_int(key_int: int, mode_int: int) -> str:
    _validate(key_int, mode_int)
    return _KEY_STANDARD[(key_int, mode_int)]
