"""Render the time-aligned scrub strip (spec §3.10).

Primary path: one figure with 4 sharex subplots.
Fallback: each panel rendered as a separate PNG.
"""

from pathlib import Path
from typing import List

import matplotlib

matplotlib.use("Agg")  # non-interactive backend; safe on Windows
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

from teardown.models import AnalysisResult


def render_scrub_strip(
    *,
    audio_path: Path,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    """Render the scrub strip to out_dir.

    Returns the list of PNG paths written. Normally 1 path
    (out_dir / 'scrub-strip.png'); if the combined render fails,
    returns 4 paths (scrub-strip-1.png … scrub-strip-4.png).
    """
    y, sr = librosa.load(str(audio_path), sr=result.sample_rate, mono=True)

    try:
        return _render_combined(y, sr, result, out_dir)
    except Exception:
        return _render_per_panel(y, sr, result, out_dir)


def _render_combined(
    y: np.ndarray,
    sr: int,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    out_path = out_dir / "scrub-strip.png"
    fig, axes = plt.subplots(nrows=4, sharex=True, figsize=(16, 12))

    # Panel 1 — waveform
    librosa.display.waveshow(y, sr=sr, ax=axes[0], alpha=0.5, color="gray")
    axes[0].set_ylabel("waveform")

    # Panel 2 — RMS energy curve
    rms_times = librosa.frames_to_time(
        np.arange(len(result.rms_values)),
        sr=sr,
        hop_length=result.rms_hop_length,
    )
    axes[1].plot(rms_times, result.rms_values, color="black", linewidth=0.7)
    axes[1].set_ylabel("RMS energy")
    _add_16bar_ticks(axes[1], result)

    # Panel 3 — chroma heatmap (recompute since envelope only stored mean)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    librosa.display.specshow(chroma, sr=sr, x_axis="time", y_axis="chroma", ax=axes[2])
    axes[2].set_ylabel("chroma")

    # Panel 4 — beat grid
    for i, t in enumerate(result.beat_times_s):
        is_downbeat = i % 4 == 0
        is_bar_of_4 = i % 16 == 0
        alpha = 0.6 if is_bar_of_4 else (0.35 if is_downbeat else 0.15)
        axes[3].axvline(t, color="gray", alpha=alpha, linewidth=0.5)
    axes[3].set_ylabel("beat grid")
    axes[3].set_xlabel("time (s)")
    axes[3].set_xlim(0, result.duration_s)
    axes[3].set_yticks([])

    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    return [out_path]


def _render_per_panel(
    y: np.ndarray,
    sr: int,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    """Fallback: each panel as its own PNG when combined render fails."""
    paths: List[Path] = []

    def _save(path: Path, render) -> None:
        fig, ax = plt.subplots(figsize=(16, 3))
        try:
            render(ax)
            fig.tight_layout()
            fig.savefig(path, dpi=100)
        finally:
            plt.close(fig)
        paths.append(path)

    _save(out_dir / "scrub-strip-1.png", lambda ax: librosa.display.waveshow(
        y, sr=sr, ax=ax, alpha=0.5, color="gray"))

    rms_times = librosa.frames_to_time(
        np.arange(len(result.rms_values)),
        sr=sr,
        hop_length=result.rms_hop_length,
    )
    _save(out_dir / "scrub-strip-2.png", lambda ax: ax.plot(
        rms_times, result.rms_values, color="black", linewidth=0.7))

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    _save(out_dir / "scrub-strip-3.png", lambda ax: librosa.display.specshow(
        chroma, sr=sr, x_axis="time", y_axis="chroma", ax=ax))

    def _beat_grid(ax):
        for i, t in enumerate(result.beat_times_s):
            alpha = 0.6 if i % 16 == 0 else (0.35 if i % 4 == 0 else 0.15)
            ax.axvline(t, color="gray", alpha=alpha, linewidth=0.5)
        ax.set_xlim(0, result.duration_s)
        ax.set_yticks([])

    _save(out_dir / "scrub-strip-4.png", _beat_grid)
    return paths


def _add_16bar_ticks(ax, result: AnalysisResult) -> None:
    if len(result.beat_times_s) == 0 or result.bpm <= 0:
        return
    bar_seconds = 16 * 4 * 60.0 / result.bpm
    t = result.beat_times_s[0]
    while t < result.duration_s:
        ax.axvline(t, color="gray", alpha=0.12, linewidth=0.4)
        t += bar_seconds
