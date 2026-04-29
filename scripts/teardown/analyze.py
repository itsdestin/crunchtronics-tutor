"""librosa-based audio analysis (spec §3.8 steps 4-9)."""

from pathlib import Path

import librosa
import numpy as np

from teardown.models import AnalysisResult

_TARGET_SR = 22050
_ONSET_HOP_LENGTH = 256   # finer grid → better tempo resolution; hop=512 reads ~3 BPM low
_RMS_HOP_LENGTH = 512
_N_MFCC = 13


def analyze(audio_path: Path) -> AnalysisResult:
    """Run the full librosa pipeline on an audio file.

    Loads as 22050 Hz mono. Raises ValueError on suspiciously short audio.

    Beat tracking uses onset_strength + feature.tempo + plp instead of
    beat_track to avoid a numba JIT incompatibility on Windows
    (numba 0.65 / librosa 0.11 / Python 3.12).

    hop_length=256 is used for the onset envelope so that feature.tempo's
    autocorrelation grid resolves tempos near 126 BPM accurately (hop=512
    quantises to ~123 BPM for this tempo range).
    """
    y, sr = librosa.load(str(audio_path), sr=_TARGET_SR, mono=True)
    duration_s = float(len(y)) / sr

    if duration_s < 30.0:
        raise ValueError(
            f"audio is suspiciously short ({duration_s:.1f}s) — "
            "likely a partial / DRM-blocked download"
        )

    # Compute onset envelope once; reused for tempo + beat positions.
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=_ONSET_HOP_LENGTH)

    # Tempo via autocorrelation (numba-free path).
    tempo_arr = librosa.feature.tempo(
        onset_envelope=onset_env, sr=sr, hop_length=_ONSET_HOP_LENGTH
    )
    bpm = float(np.atleast_1d(tempo_arr)[0])

    # Beat positions via Predominant Local Pulse (numba-free).
    # Constrain plp to ±20% of estimated tempo so only on-beat peaks are kept;
    # an unconstrained plp at hop=256 finds sub-beat local maxima as well.
    pulse = librosa.beat.plp(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=_ONSET_HOP_LENGTH,
        tempo_min=bpm * 0.8,
        tempo_max=bpm * 1.2,
    )
    beat_frames = np.flatnonzero(librosa.util.localmax(pulse))
    beat_times_s = librosa.frames_to_time(beat_frames, sr=sr, hop_length=_ONSET_HOP_LENGTH)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)

    rms = librosa.feature.rms(y=y, hop_length=_RMS_HOP_LENGTH).flatten()

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=_N_MFCC)
    mfcc_means = mfcc.mean(axis=1)
    mfcc_stds = mfcc.std(axis=1)

    return AnalysisResult(
        duration_s=duration_s,
        sample_rate=sr,
        bpm=bpm,
        beat_times_s=beat_times_s,
        chroma_mean=chroma_mean,
        rms_values=rms,
        rms_hop_length=_RMS_HOP_LENGTH,
        mfcc_means=mfcc_means,
        mfcc_stds=mfcc_stds,
    )
