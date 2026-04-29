"""librosa-based audio analysis (spec §3.8 steps 4-9)."""

from pathlib import Path

import librosa
import numpy as np

from teardown.models import AnalysisResult

_TARGET_SR = 22050
_ONSET_HOP_LENGTH = 256   # finer grid → better tempo resolution; hop=512 reads ~3 BPM low
_RMS_HOP_LENGTH = 512
_N_MFCC = 13

_BANDS_HZ = {
    "sub":      (20.0, 60.0),
    "bass":     (60.0, 250.0),
    "low_mids": (250.0, 2000.0),
    "highs":    (2000.0, 8000.0),
    "air":      (8000.0, None),  # open-top
}

_SIDECHAIN_THRESHOLD_DB = 3.0
_SIDECHAIN_THRESHOLD_CONSISTENCY_PCT = 60.0


def _per_band_rms(y: np.ndarray, sr: int, hop_length: int = _RMS_HOP_LENGTH) -> "PerBandRMS":
    """Compute per-band RMS curves via STFT magnitude binning.

    Spec §3.8 step 12, §3.9.per_band_rms.
    """
    from teardown.models import PerBandRMS

    n_fft = 2048  # standard
    stft = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    band_rms = {}
    for name, (lo, hi) in _BANDS_HZ.items():
        if hi is None:
            mask = freqs >= lo
        else:
            mask = (freqs >= lo) & (freqs < hi)
        if not mask.any():
            band_rms[name] = np.zeros(stft.shape[1])
            continue
        # RMS per time frame within the band.
        band_mag = stft[mask, :]
        band_rms[name] = np.sqrt(np.mean(band_mag ** 2, axis=0))

    return PerBandRMS(
        hop_length=hop_length,
        sub_rms=band_rms["sub"],
        bass_rms=band_rms["bass"],
        low_mids_rms=band_rms["low_mids"],
        highs_rms=band_rms["highs"],
        air_rms=band_rms["air"],
    )


def _hpss_split(y: np.ndarray, sr: int, hop_length: int = _RMS_HOP_LENGTH) -> "HPSSResult":
    """Harmonic-percussive source separation + per-component RMS.

    Spec §3.8 step 13, §3.9.hpss.
    """
    from teardown.models import HPSSResult

    y_h, y_p = librosa.effects.hpss(y)
    harmonic_rms = librosa.feature.rms(y=y_h, hop_length=hop_length).flatten()
    percussive_rms = librosa.feature.rms(y=y_p, hop_length=hop_length).flatten()
    return HPSSResult(
        hop_length=hop_length,
        harmonic_rms=harmonic_rms,
        percussive_rms=percussive_rms,
    )


def _spectral_centroid(y: np.ndarray, sr: int, hop_length: int = _RMS_HOP_LENGTH) -> "CentroidResult":
    """Spectral centroid curve over time, in Hz.

    Spec §3.8 step 14, §3.9.spectral_centroid.
    """
    from teardown.models import CentroidResult

    centroid = librosa.feature.spectral_centroid(
        y=y, sr=sr, hop_length=hop_length
    ).squeeze()
    return CentroidResult(hop_length=hop_length, values_hz=centroid)


def _onset_density_per_band(
    y: np.ndarray,
    sr: int,
    beat_times_s: np.ndarray,
    hop_length: int = _RMS_HOP_LENGTH,
) -> "OnsetDensity":
    """Per-band onset detection, bucketed into bars (4 beats each).

    Spec §3.8 step 15, §3.9.onset_density.
    """
    from teardown.models import OnsetDensity, OnsetDensityBar

    # For each band, compute a band-filtered onset envelope and detect onsets.
    # Using STFT-magnitude band-slicing (cheaper than re-loading audio per band).
    n_fft = 2048
    stft = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    band_onset_times: dict[str, np.ndarray] = {}
    for name, (lo, hi) in _BANDS_HZ.items():
        if hi is None:
            mask = freqs >= lo
        else:
            mask = (freqs >= lo) & (freqs < hi)
        if not mask.any():
            band_onset_times[name] = np.array([])
            continue
        band_stft = stft[mask, :]
        # Reduce to a 1-D envelope per frame: sum across bins.
        env = band_stft.sum(axis=0)
        # librosa onset_detect on a precomputed envelope:
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=env, sr=sr, hop_length=hop_length, units="frames"
        )
        band_onset_times[name] = librosa.frames_to_time(
            onset_frames, sr=sr, hop_length=hop_length
        )

    # Bucket by bar (4 consecutive beats per bar).
    bars: list[OnsetDensityBar] = []
    n_bars = max(0, (len(beat_times_s) - 1) // 4)
    for bar_index in range(n_bars):
        start_s = float(beat_times_s[bar_index * 4])
        end_idx = bar_index * 4 + 4
        if end_idx >= len(beat_times_s):
            break
        end_s = float(beat_times_s[end_idx])
        counts: dict = {}
        for name in _BANDS_HZ.keys():
            ts = band_onset_times[name]
            counts[name] = int(np.sum((ts >= start_s) & (ts < end_s)))
        bars.append(OnsetDensityBar(
            bar_index=bar_index,
            start_s=start_s,
            end_s=end_s,
            onsets_per_band=counts,
        ))

    return OnsetDensity(bars=bars)


def _sidechain_detection(
    y: np.ndarray,
    sr: int,
    hop_length: int = _RMS_HOP_LENGTH,
) -> "SidechainResult":
    """Sidechain detection via kick-onset-aligned bass-band RMS dip analysis.

    Method:
    1. Detect kicks via librosa.onset.onset_detect on the sub-band onset envelope.
    2. For each kick onset time, find the bass-band RMS minimum within the next 100ms.
    3. Compute the rolling local mean of bass-band RMS in a [-250ms, +250ms] window.
    4. Dip depth in dB = 20 * log10(rolling_mean / dip_min), clamped at 0.
    5. Aggregate: depth_db_mean, depth_db_p90, consistency_pct.
    6. Detected when depth_db_mean >= 3.0 AND consistency_pct >= 60.0.

    Spec §3.8 step 16, §3.9.sidechain, §6 implementation note.
    """
    from teardown.models import SidechainResult

    n_fft = 2048
    stft = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    # Sub-band envelope for kick onset detection.
    sub_lo, sub_hi = _BANDS_HZ["sub"]
    sub_mask = (freqs >= sub_lo) & (freqs < sub_hi)
    if not sub_mask.any():
        return _empty_sidechain_result()
    sub_env = stft[sub_mask, :].sum(axis=0)
    kick_frames = librosa.onset.onset_detect(
        onset_envelope=sub_env, sr=sr, hop_length=hop_length, units="frames"
    )
    kick_times_s = librosa.frames_to_time(kick_frames, sr=sr, hop_length=hop_length)

    # Bass-band RMS curve for dip analysis.
    bass_lo, bass_hi = _BANDS_HZ["bass"]
    bass_mask = (freqs >= bass_lo) & (freqs < bass_hi)
    if not bass_mask.any():
        return _empty_sidechain_result()
    bass_band = stft[bass_mask, :]
    bass_rms = np.sqrt(np.mean(bass_band ** 2, axis=0))

    if len(kick_times_s) == 0:
        return _empty_sidechain_result()

    # Frame-level helpers.
    def time_to_frame(t: float) -> int:
        return int(round(t * sr / hop_length))

    dip_db_per_kick: list[float] = []
    eps = 1e-9
    for t_kick in kick_times_s:
        f_kick = time_to_frame(t_kick)
        f_dip_end = time_to_frame(t_kick + 0.100)  # 100ms window
        f_window_lo = time_to_frame(t_kick - 0.250)  # rolling mean window
        f_window_hi = time_to_frame(t_kick + 0.250)
        f_dip_end = min(f_dip_end, len(bass_rms) - 1)
        f_window_lo = max(0, f_window_lo)
        f_window_hi = min(len(bass_rms) - 1, f_window_hi)
        if f_kick >= len(bass_rms) - 1 or f_dip_end <= f_kick:
            continue
        dip_min = float(bass_rms[f_kick:f_dip_end + 1].min())
        rolling_mean = float(bass_rms[f_window_lo:f_window_hi + 1].mean())
        if rolling_mean <= eps or dip_min >= rolling_mean:
            dip_db_per_kick.append(0.0)
        else:
            depth = 20.0 * np.log10(rolling_mean / max(dip_min, eps))
            dip_db_per_kick.append(float(depth))

    if not dip_db_per_kick:
        return _empty_sidechain_result()

    arr = np.array(dip_db_per_kick)
    depth_mean = float(arr.mean())
    depth_p90 = float(np.percentile(arr, 90))
    consistency_pct = 100.0 * float(np.sum(arr >= _SIDECHAIN_THRESHOLD_DB)) / len(arr)
    detected = (
        depth_mean >= _SIDECHAIN_THRESHOLD_DB
        and consistency_pct >= _SIDECHAIN_THRESHOLD_CONSISTENCY_PCT
    )
    return SidechainResult(
        detected=detected,
        depth_db_mean=depth_mean,
        depth_db_p90=depth_p90,
        consistency_pct=consistency_pct,
        kicks_examined=len(arr),
        threshold_db_for_detection=_SIDECHAIN_THRESHOLD_DB,
        threshold_consistency_for_detection=_SIDECHAIN_THRESHOLD_CONSISTENCY_PCT,
    )


def _empty_sidechain_result() -> "SidechainResult":
    """Used when no kicks could be examined (no sub-band signal, no kicks, etc.)."""
    from teardown.models import SidechainResult
    return SidechainResult(
        detected=False,
        depth_db_mean=0.0,
        depth_db_p90=0.0,
        consistency_pct=0.0,
        kicks_examined=0,
        threshold_db_for_detection=_SIDECHAIN_THRESHOLD_DB,
        threshold_consistency_for_detection=_SIDECHAIN_THRESHOLD_CONSISTENCY_PCT,
    )


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

    per_band = _per_band_rms(y, sr)
    hpss_result = _hpss_split(y, sr)
    centroid_result = _spectral_centroid(y, sr)
    onset_density_result = _onset_density_per_band(y, sr, beat_times_s)
    sidechain_result = _sidechain_detection(y, sr)

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
        per_band_rms=per_band,
        hpss=hpss_result,
        spectral_centroid=centroid_result,
        onset_density=onset_density_result,
        sidechain=sidechain_result,
    )
