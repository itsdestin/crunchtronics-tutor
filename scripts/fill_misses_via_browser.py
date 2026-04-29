"""One-shot fill of taste/tracks.csv `miss:reccobeats` rows via GetSongBPM.

GetSongBPM's API sits behind a Cloudflare managed-challenge gate that
rejects raw HTTP requests regardless of headers / TLS impersonation.
The standard `enrich/getsongbpm.py` HTTP client is therefore unable to
reach the API in production. This script bypasses the gate by driving
a real Chromium via Playwright (with playwright-stealth patches) so the
Cloudflare JS challenge clears.

Run from project root:

    cd scripts
    uv run --with playwright --with tf-playwright-stealth python fill_misses_via_browser.py

Per-track expected outcomes:
- HIT  → row.source set to "getsongbpm"; bpm + key_* + mode populated
- MISS → row.source set to "miss:reccobeats,getsongbpm"; fetched_at refreshed
        so the 30-day TTL kicks in before another retry

GetSongBPM only returns BPM + key. The audio-feature columns
(`energy`, `danceability`, etc.) stay empty for these rows by design
(spec §3.4.1).

This script is intentionally separate from `enrich.py` because
GetSongBPM's per-track hit rate on niche EDM is very low (sanity-check
showed 1/15) and the Playwright dependency is heavy. Wiring it into
`enrich.py` proper would impose Playwright on every run for marginal
return.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import sys
import time
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# Local imports — make `enrich` package importable
sys.path.insert(0, str(Path(__file__).parent))
from enrich.camelot import camelot_from_int_key, key_standard_from_int

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRACKS_CSV = PROJECT_ROOT / "taste" / "tracks.csv"
SECRETS = Path.home() / ".crunchtronics-tutor-secrets" / "audio-enrichment.json"
BASE = "https://api.getsongbpm.com"
THROTTLE_S = 0.4  # between requests, after the page settles

# Pitch → 0..11 (Spotify-style key)
_PITCH_TO_INT = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10, "B": 11,
}


def parse_key_of(key_of: str) -> tuple[int | None, int | None]:
    """Parse GetSongBPM's `key_of` field, supporting long and short form.

    Long form: "F# minor", "C major"
    Short form: "F#m", "C", "Bbm"
    """
    s = (key_of or "").strip()
    if not s:
        return None, None
    parts = s.split()
    if len(parts) == 2:
        pitch, mode_str = parts[0], parts[1].lower()
        mode = 1 if mode_str.startswith("major") else 0 if mode_str.startswith("minor") else None
        return _PITCH_TO_INT.get(pitch), mode
    # Short form: optional 'm' suffix means minor
    if s.endswith("m"):
        pitch = s[:-1]
        return _PITCH_TO_INT.get(pitch), 0
    return _PITCH_TO_INT.get(s), 1


def load_api_key() -> str:
    if not SECRETS.exists():
        raise SystemExit(f"ERROR: {SECRETS} not found. Set up GetSongBPM first.")
    data = json.loads(SECRETS.read_text(encoding="utf-8"))
    key = (data.get("getsongbpm_api_key") or "").strip()
    if not key:
        raise SystemExit("ERROR: getsongbpm_api_key empty in audio-enrichment.json")
    return key


def fetch_one(page, api_key: str, artist: str, title: str) -> dict | None:
    """Returns the first matching search result dict, or None on no-result/no-match."""
    url = f"{BASE}/search/?type=both&lookup=song:{quote(title)}+artist:{quote(artist)}&api_key={api_key}"
    page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    # Wait for Cloudflare challenge to clear (title goes empty when raw-JSON page renders)
    for _ in range(25):
        if page.title() == "" and page.query_selector("pre"):
            break
        time.sleep(1)
    pre = page.query_selector("pre")
    if not pre:
        return None  # treat un-cleared challenge as a miss; caller will record as such
    try:
        payload = json.loads(pre.inner_text())
    except json.JSONDecodeError:
        return None
    search = payload.get("search", [])
    if isinstance(search, dict):  # error envelope, e.g. {"error": "no result"}
        return None
    if not search:
        return None
    first = search[0]
    # Defensive artist match — same rule as enrich/getsongbpm.py
    returned = ((first.get("artist") or {}).get("name") or "").strip().lower()
    if returned != artist.strip().lower():
        return None
    return first


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    api_key = load_api_key()

    with open(TRACKS_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        rows = list(reader)

    misses = [r for r in rows if r["source"].startswith("miss:")]
    print(f"Loaded {len(rows)} rows; {len(misses)} are misses to retry.")
    print()

    now_iso = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    hits, no_results = 0, 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()
        stealth_sync(page)

        for i, row in enumerate(misses, 1):
            try:
                hit = fetch_one(page, api_key, row["artist"], row["title"])
            except Exception as e:
                print(f"  [{i:2d}/{len(misses)}] ERR  {row['artist']} — {row['title']}: {e}")
                continue

            if hit is None:
                row["source"] = "miss:reccobeats,getsongbpm"
                row["fetched_at"] = now_iso
                no_results += 1
                print(f"  [{i:2d}/{len(misses)}] miss {row['artist']} — {row['title']}")
            else:
                tempo_str = hit.get("tempo", "")
                try:
                    bpm = float(tempo_str) if tempo_str else None
                except (TypeError, ValueError):
                    bpm = None
                key_int, mode_int = parse_key_of(hit.get("key_of", ""))
                if key_int is not None and mode_int is not None:
                    row["key_camelot"] = camelot_from_int_key(key_int, mode_int)
                    row["key_standard"] = key_standard_from_int(key_int, mode_int)
                    row["mode"] = str(mode_int)
                if bpm is not None:
                    row["bpm"] = f"{bpm:.3f}"
                row["source"] = "getsongbpm"
                row["fetched_at"] = now_iso
                hits += 1
                print(
                    f"  [{i:2d}/{len(misses)}] HIT  {row['artist']} — {row['title']}  "
                    f"→  {bpm} BPM | {row['key_camelot']} ({row['key_standard']})"
                )
            time.sleep(THROTTLE_S)

        browser.close()

    # Write CSV back atomically
    tmp = TRACKS_CSV.with_suffix(".csv.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    tmp.replace(TRACKS_CSV)

    print()
    print(f"Done: {hits} hit, {no_results} no-result. tracks.csv updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
