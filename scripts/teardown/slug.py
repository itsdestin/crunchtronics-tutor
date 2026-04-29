"""Kebab-case slug derivation per spec §3.7.

Slug regex: ^[a-z0-9][a-z0-9-]{0,79}$
"""

import re
import unicodedata

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

# Transliteration map for characters that don't decompose via NFD/NFKD.
_TRANSLITERATION_MAP = {
    "Ł": "L",
    "ł": "l",
}


def derive_slug(artist: str, title: str) -> str:
    """Compose a kebab slug from artist + title.

    Steps: replace `&` with `and`; casefold; strip diacritics; collapse
    non-alphanumeric runs to a single dash; strip leading/trailing dashes;
    truncate to 80 chars (trim trailing dash if truncation lands on one).
    """
    raw = f"{artist} {title}".replace("&", " and ")

    # Apply transliteration mappings first.
    for char, replacement in _TRANSLITERATION_MAP.items():
        raw = raw.replace(char, replacement)

    # Normalize and remove combining marks.
    normalized = unicodedata.normalize("NFD", raw)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    lowered = normalized.lower()
    dashed = _NON_ALNUM_RE.sub("-", lowered)
    stripped = dashed.strip("-")
    truncated = stripped[:80].rstrip("-")
    if not truncated:
        raise ValueError(f"Cannot derive slug from artist={artist!r}, title={title!r}")
    return truncated


def validate_slug(slug: str) -> bool:
    """Return True iff `slug` matches the canonical pattern."""
    return bool(_SLUG_RE.match(slug))
