"""Render the time-aligned scrub strip (spec §3.10, v1.1 6-panel layout).

Primary path: one figure with 6 sharex subplots.
Fallback: each panel rendered as a separate PNG (scrub-strip-1.png … -6.png).
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


_BAND_COLORS = {
    "sub":      "purple",
    "bass":     "blue",
    "low_mids": "green",
    "highs":    "orange",
    "air":      "red",
}


def render_scrub_strip(
    *,
    audio_path: Path,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    """Render the scrub strip to out_dir.

    Returns the list of PNG paths written. Normally 1 path
    (out_dir / 'scrub-strip.png'); if the combined render fails,
    returns 6 paths (scrub-strip-1.png … scrub-strip-6.png).
    """
    y, sr = librosa.load(str(audio_path), sr=result.sample_rate, mono=True)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    try:
        return _render_combined(y, sr, chroma, result, out_dir)
    except Exception:
        return _render_per_panel(y, sr, chroma, result, out_dir)


def _render_combined(
    y: np.ndarray,
    sr: int,
    chroma: np.ndarray,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    out_path = out_dir / "scrub-strip.png"
    fig, axes = plt.subplots(nrows=6, sharex=True, figsize=(16, 18))

    # Panel 1 — waveform
    librosa.display.waveshow(y, sr=sr, ax=axes[0], alpha=0.5, color="gray")
    axes[0].set_ylabel("waveform")

    # Panel 2 — per-band RMS (5 lines, log y)
    if result.per_band_rms is not None:
        pb = result.per_band_rms
        rms_times = librosa.frames_to_time(
            np.arange(len(pb.sub_rms)), sr=sr, hop_length=pb.hop_length,
        )
        band_arrays = {
            "sub": pb.sub_rms,
            "bass": pb.bass_rms,
            "low_mids": pb.low_mids_rms,
            "highs": pb.highs_rms,
            "air": pb.air_rms,
        }
        for name, arr in band_arrays.items():
            axes[1].plot(rms_times, arr + 1e-9, color=_BAND_COLORS[name],
                         linewidth=0.8, label=name)
        axes[1].set_yscale("log")
        axes[1].set_ylabel("per-band RMS (log)")
        axes[1].legend(loc="upper right", fontsize=8)
    else:
        # v1.0 fallback: overall RMS
        rms_times = librosa.frames_to_time(
            np.arange(len(result.rms_values)), sr=sr, hop_length=result.rms_hop_length,
        )
        axes[1].plot(rms_times, result.rms_values, color="black", linewidth=0.7)
        axes[1].set_ylabel("RMS energy")

    # Panel 3 — HPSS (harmonic + percussive)
    if result.hpss is not None:
        h = result.hpss
        h_times = librosa.frames_to_time(
            np.arange(len(h.harmonic_rms)), sr=sr, hop_length=h.hop_length,
        )
        axes[2].plot(h_times, h.harmonic_rms, color="teal", linewidth=0.9, label="harmonic")
        axes[2].plot(h_times, h.percussive_rms, color="magenta", linewidth=0.9, label="percussive")
        axes[2].set_ylabel("HPSS RMS")
        axes[2].legend(loc="upper right", fontsize=8)
    else:
        axes[2].set_ylabel("HPSS (not computed)")

    # Panel 4 — spectral centroid + total onset density per bar
    if result.spectral_centroid is not None:
        c = result.spectral_centroid
        c_times = librosa.frames_to_time(
            np.arange(len(c.values_hz)), sr=sr, hop_length=c.hop_length,
        )
        axes[3].plot(c_times, c.values_hz, color="gray", linewidth=0.8, label="centroid (Hz)")
        axes[3].set_ylabel("centroid (Hz)")
        axes[3].legend(loc="upper left", fontsize=8)
        if result.onset_density is not None:
            ax_b = axes[3].twinx()
            for bar in result.onset_density.bars:
                total = sum(bar.onsets_per_band.values())
                ax_b.bar(bar.start_s, total, width=(bar.end_s - bar.start_s),
                         align="edge", alpha=0.3, color="black")
            ax_b.set_ylabel("onsets/bar (total)")
    else:
        axes[3].set_ylabel("centroid (not computed)")

    # Panel 5 — chroma heatmap
    librosa.display.specshow(chroma, sr=sr, x_axis="time", y_axis="chroma", ax=axes[4])
    axes[4].set_ylabel("chroma")

    # Panel 6 — beat grid
    for i, t in enumerate(result.beat_times_s):
        is_downbeat = i % 4 == 0
        is_bar_of_4 = i % 16 == 0
        alpha = 0.6 if is_bar_of_4 else (0.35 if is_downbeat else 0.15)
        axes[5].axvline(t, color="gray", alpha=alpha, linewidth=0.5)
    axes[5].set_ylabel("beat grid")
    axes[5].set_xlabel("time (s)")
    axes[5].set_xlim(0, result.duration_s)
    axes[5].set_yticks([])

    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    return [out_path]


def _render_per_panel(
    y: np.ndarray,
    sr: int,
    chroma: np.ndarray,
    result: AnalysisResult,
    out_dir: Path,
) -> List[Path]:
    """Fallback: 6 separate PNGs when combined render fails."""
    paths: List[Path] = []

    def _save(path: Path, render: callable) -> None:
        fig, ax = plt.subplots(figsize=(16, 3))
        try:
            render(ax)
            fig.tight_layout()
            fig.savefig(path, dpi=100)
        finally:
            plt.close(fig)
        paths.append(path)

    # Panel 1: waveform
    _save(out_dir / "scrub-strip-1.png", lambda ax: librosa.display.waveshow(
        y, sr=sr, ax=ax, alpha=0.5, color="gray"))

    # Panel 2: per-band RMS
    if result.per_band_rms is not None:
        pb = result.per_band_rms
        rms_times = librosa.frames_to_time(
            np.arange(len(pb.sub_rms)), sr=sr, hop_length=pb.hop_length,
        )
        def _per_band(ax):
            for name, arr in (("sub", pb.sub_rms), ("bass", pb.bass_rms),
                              ("low_mids", pb.low_mids_rms), ("highs", pb.highs_rms),
                              ("air", pb.air_rms)):
                ax.plot(rms_times, arr + 1e-9, color=_BAND_COLORS[name],
                        linewidth=0.8, label=name)
            ax.set_yscale("log")
            ax.legend(loc="upper right", fontsize=8)
        _save(out_dir / "scrub-strip-2.png", _per_band)
    else:
        rms_times = librosa.frames_to_time(
            np.arange(len(result.rms_values)), sr=sr, hop_length=result.rms_hop_length,
        )
        _save(out_dir / "scrub-strip-2.png", lambda ax: ax.plot(
            rms_times, result.rms_values, color="black", linewidth=0.7))

    # Panel 3: HPSS
    if result.hpss is not None:
        h = result.hpss
        h_times = librosa.frames_to_time(
            np.arange(len(h.harmonic_rms)), sr=sr, hop_length=h.hop_length,
        )
        def _hpss_panel(ax):
            ax.plot(h_times, h.harmonic_rms, color="teal", linewidth=0.9, label="harmonic")
            ax.plot(h_times, h.percussive_rms, color="magenta", linewidth=0.9, label="percussive")
            ax.legend(loc="upper right", fontsize=8)
        _save(out_dir / "scrub-strip-3.png", _hpss_panel)
    else:
        _save(out_dir / "scrub-strip-3.png", lambda ax: ax.text(
            0.5, 0.5, "HPSS not computed", ha="center", va="center"))

    # Panel 4: centroid + onset density
    if result.spectral_centroid is not None:
        c = result.spectral_centroid
        c_times = librosa.frames_to_time(
            np.arange(len(c.values_hz)), sr=sr, hop_length=c.hop_length,
        )
        def _centroid_panel(ax):
            ax.plot(c_times, c.values_hz, color="gray", linewidth=0.8, label="centroid (Hz)")
            ax.legend(loc="upper left", fontsize=8)
            if result.onset_density is not None:
                ax_b = ax.twinx()
                for bar in result.onset_density.bars:
                    total = sum(bar.onsets_per_band.values())
                    ax_b.bar(bar.start_s, total, width=(bar.end_s - bar.start_s),
                             align="edge", alpha=0.3, color="black")
        _save(out_dir / "scrub-strip-4.png", _centroid_panel)
    else:
        _save(out_dir / "scrub-strip-4.png", lambda ax: ax.text(
            0.5, 0.5, "centroid not computed", ha="center", va="center"))

    # Panel 5: chroma
    _save(out_dir / "scrub-strip-5.png", lambda ax: librosa.display.specshow(
        chroma, sr=sr, x_axis="time", y_axis="chroma", ax=ax))

    # Panel 6: beat grid
    def _beat_grid(ax):
        for i, t in enumerate(result.beat_times_s):
            alpha = 0.6 if i % 16 == 0 else (0.35 if i % 4 == 0 else 0.15)
            ax.axvline(t, color="gray", alpha=alpha, linewidth=0.5)
        ax.set_xlim(0, result.duration_s)
        ax.set_yticks([])
    _save(out_dir / "scrub-strip-6.png", _beat_grid)

    return paths
