"""Top-level CLI for the teardown pipeline (spec §3.13)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from teardown import analyze as analyze_mod
from teardown import envelope as envelope_mod
from teardown import plot as plot_mod
from teardown.csv_context import load_csv_context
from teardown.key import estimate_key
from teardown.ytdlp import DownloadError, download_audio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEARDOWNS_DIR = PROJECT_ROOT / "teardowns"
TRACKS_CSV = PROJECT_ROOT / "taste" / "tracks.csv"


class _Parser(argparse.ArgumentParser):
    """ArgumentParser that enforces the cross-flag invariants."""

    def parse_args(self, args=None, namespace=None):
        ns = super().parse_args(args, namespace)
        if not getattr(ns, "check_deps", False):
            if not ns.slug:
                self.error("--slug is required (unless --check-deps)")
            if not (ns.url or ns.local):
                self.error("one of --url or --local is required (unless --check-deps)")
        return ns


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="teardown",
        description="Audio teardown pipeline (yt-dlp + librosa + scrub strip).",
    )
    parser.add_argument("--slug", help="Output directory name under teardowns/")
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--url", help="Audio source URL (yt-dlp will download it)")
    src.add_argument("--local", help="Path to an existing local audio file")
    parser.add_argument("--csv-context", dest="csv_context",
                        help="spotify_id to embed from taste/tracks.csv")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite an existing teardowns/<slug>/")
    parser.add_argument("--check-deps", dest="check_deps", action="store_true",
                        help="Print versions of ffmpeg/librosa/yt-dlp/matplotlib and exit")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true",
                        help="Print the planned operations and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.check_deps:
        return run_check_deps()

    if not _ffmpeg_available():
        print("ERROR: ffmpeg not found on PATH. Install: winget install Gyan.FFmpeg",
              file=sys.stderr)
        return 6

    target_dir = TEARDOWNS_DIR / args.slug
    _check_idempotency(target_dir, force=args.force)
    target_dir.mkdir(parents=True, exist_ok=True)

    source_path = target_dir / "source.wav"

    if args.dry_run:
        print(f"DRY RUN — would write: {source_path}, "
              f"{target_dir / 'analysis.json'}, {target_dir / 'scrub-strip.png'}")
        return 0

    try:
        if args.url:
            print(f"[1/4] downloading {args.url}…")
            download_audio(args.url, source_path, force=args.force)
            source_url = args.url
            source_title = args.slug
            source_channel = ""
        else:
            local_path = Path(args.local).resolve()
            if not local_path.exists():
                print(f"ERROR: --local path does not exist: {local_path}", file=sys.stderr)
                return 6
            print(f"[1/4] using local file {local_path}")
            if not source_path.exists() or args.force:
                import shutil
                shutil.copy(local_path, source_path)
            source_url = ""
            source_title = local_path.name
            source_channel = ""
    except DownloadError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        print("[2/4] loading audio…")
        result = analyze_mod.analyze(source_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    print("[3/4] librosa analysis + key estimate…")
    key_est = estimate_key(result.chroma_mean)

    csv_ctx = None
    if args.csv_context:
        csv_ctx = load_csv_context(TRACKS_CSV, args.csv_context)
        if csv_ctx is None:
            print(f"WARNING: --csv-context {args.csv_context} not in {TRACKS_CSV}",
                  file=sys.stderr)

    envelope = envelope_mod.compose_envelope(
        result=result,
        key_estimate=key_est,
        source_url=source_url,
        source_title=source_title,
        source_channel=source_channel,
        source_duration_s=result.duration_s,
        source_basename="source.wav",
        csv_context=csv_ctx,
    )
    envelope_mod.write_envelope(envelope, target_dir / "analysis.json")

    print("[4/4] rendering scrub strip…")
    try:
        png_paths = plot_mod.render_scrub_strip(
            audio_path=source_path,
            result=result,
            out_dir=target_dir,
        )
    except Exception as exc:
        print(f"ERROR: scrub strip rendering failed: {exc}", file=sys.stderr)
        return 5

    print("\nArtifacts:")
    print(f"  source.wav       {source_path}")
    print(f"  analysis.json    {target_dir / 'analysis.json'}")
    for p in png_paths:
        print(f"  {p.name:16s} {p}")
    return 0


def _check_idempotency(target_dir: Path, *, force: bool) -> None:
    """Exit 1 if target_dir exists and contains anything, unless force=True."""
    if force:
        return
    if not target_dir.exists():
        return
    if any(target_dir.iterdir()):
        print(f"ERROR: {target_dir} already exists and is non-empty. "
              "Re-run with --force to overwrite.", file=sys.stderr)
        sys.exit(1)


def _ffmpeg_available() -> bool:
    try:
        proc = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, text=True,
        )
        return proc.returncode == 0
    except FileNotFoundError:
        return False


def run_check_deps() -> int:
    """Print versions of all backend deps + ffmpeg. Always exits 0."""
    import importlib.metadata as md

    def _version(name: str) -> str:
        try:
            return md.version(name)
        except md.PackageNotFoundError:
            return "MISSING"

    print(f"librosa     {_version('librosa')}")
    print(f"yt-dlp      {_version('yt-dlp')}")
    print(f"matplotlib  {_version('matplotlib')}")
    print(f"soundfile   {_version('soundfile')}")
    print(f"ffmpeg      {'present' if _ffmpeg_available() else 'MISSING (install: winget install Gyan.FFmpeg)'}")
    return 0
