"""Tests for kebab-slug derivation (spec §3.7)."""

import pytest

from teardown.slug import derive_slug, validate_slug


class TestDeriveSlug:
    def test_simple_artist_title(self):
        assert derive_slug("John Summit", "Where You Are") == "john-summit-where-you-are"

    def test_collapses_whitespace_and_punctuation(self):
        assert derive_slug("John Summit & HAYLA", "Where You Are") == "john-summit-and-hayla-where-you-are"

    def test_em_dash_in_title(self):
        # The actual character used in YouTube titles for the artist/title sep.
        assert derive_slug("Subtronics", "Griztronics II") == "subtronics-griztronics-ii"

    def test_strips_diacritics(self):
        assert derive_slug("Łaszewo", "Café") == "laszewo-cafe"

    def test_collapses_repeated_dashes(self):
        assert derive_slug("---weird---", "name") == "weird-name"

    def test_strips_leading_trailing_dashes(self):
        assert derive_slug("-leading", "trailing-") == "leading-trailing"

    def test_truncates_at_80_chars(self):
        long_title = "a" * 200
        slug = derive_slug("artist", long_title)
        assert len(slug) <= 80

    def test_lowercases_uppercase(self):
        assert derive_slug("ARTIST", "TITLE") == "artist-title"

    def test_replaces_ampersand_with_and(self):
        assert derive_slug("A & B", "song") == "a-and-b-song"


class TestValidateSlug:
    def test_accepts_valid_slug(self):
        assert validate_slug("john-summit-where-you-are") is True

    def test_accepts_single_char(self):
        assert validate_slug("a") is True

    def test_rejects_empty(self):
        assert validate_slug("") is False

    def test_rejects_leading_dash(self):
        assert validate_slug("-leading") is False

    def test_rejects_uppercase(self):
        assert validate_slug("UPPER") is False

    def test_rejects_underscore(self):
        assert validate_slug("with_underscore") is False

    def test_rejects_spaces(self):
        assert validate_slug("with space") is False

    def test_rejects_too_long(self):
        assert validate_slug("a" * 81) is False
