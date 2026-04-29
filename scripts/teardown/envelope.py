"""Compose and write the analysis.json envelope (spec §3.9, v1.1 §2.4)."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np

from teardown.key import KeyEstimate
from teardown.models import AnalysisResult

TOOL_VERSION_V10 = "0.1.0"
TOOL_VERSION_V11 = "0.2.0"

_BAND_HZ = {
    "sub":      (20, 60),
    "bass":     (60, 250),
    "low_mids": (250, 2000),
    "highs":    (2000, 8000),
    "air":      (8000, None),
}


def _summary(arr: np.ndarray) -> dict[str, float]:
    a = np.asarray(arr)
    return {
        "mean": float(a.mean()),
        "p10": float(np.percentile(a, 10)),
        "p50": float(np.percentile(a, 50)),
        "p90": float(np.percentile(a, 90)),
    }


def compose_envelope(
    *,
    result: AnalysisResult,
    key_estimate: KeyEstimate,
    source_url: str,
    source_title: str,
    source_channel: str,
    source_duration_s: float,
    source_basename: str,
    csv_context: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """Build the JSON-serializable envelope per spec §3.9.

    When AnalysisResult v1.1 fields (per_band_rms, hpss, spectral_centroid,
    onset_density, sidechain) are present, output the v1.1 schema with
    tool_version="0.2.0" and the new top-level keys. When they're all None
    (v1.0 callers), output the v1.0 schema with tool_version="0.1.0" and
    the v1.1 keys absent.
    """
    rms = np.asarray(result.rms_values)
    rms_summary = _summary(rms)

    tempo: dict[str, Any] = {"bpm_librosa": float(result.bpm)}
    key: dict[str, Any] = {
        "camelot_librosa": key_estimate.camelot,
        "standard_librosa": key_estimate.standard,
        "method": key_estimate.method,
    }
    csv_block: Optional[dict[str, Any]] = None

    if csv_context is not None:
        csv_bpm = csv_context.get("bpm")
        if csv_bpm is not None:
            tempo["bpm_csv"] = float(csv_bpm)
            tempo["agree_within_1bpm"] = abs(result.bpm - csv_bpm) < 1.0
            tempo["agree_within_4bpm"] = abs(result.bpm - csv_bpm) < 4.0
        csv_camelot = csv_context.get("key_camelot")
        if csv_camelot:
            key["camelot_csv"] = csv_camelot
            key["agree"] = csv_camelot == key_estimate.camelot
        csv_block = csv_context

    is_v11 = (
        result.per_band_rms is not None
        or result.hpss is not None
        or result.spectral_centroid is not None
        or result.onset_density is not None
        or result.sidechain is not None
    )

    envelope: dict[str, Any] = {
        "tool_version": TOOL_VERSION_V11 if is_v11 else TOOL_VERSION_V10,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "url": source_url,
            "title": source_title,
            "channel": source_channel,
            "duration_s": source_duration_s,
            "downloaded_to": source_basename,
        },
        "audio": {
            "sample_rate": result.sample_rate,
            "duration_s": result.duration_s,
            "channels": 1,
            "loader": "librosa.load (resampled mono)",
        },
        "tempo": tempo,
        "beats": {
            "count": int(len(result.beat_times_s)),
            "first_beat_s": float(result.beat_times_s[0]) if len(result.beat_times_s) else 0.0,
            "beat_times_s": [float(t) for t in result.beat_times_s],
        },
        "key": key,
        "energy": {
            "hop_length": result.rms_hop_length,
            "rms_values": [float(v) for v in result.rms_values],
            "rms_summary": rms_summary,
        },
    }

    if result.per_band_rms is not None:
        pb = result.per_band_rms
        bands_out: dict[str, Any] = {}
        band_arrays = {
            "sub": pb.sub_rms,
            "bass": pb.bass_rms,
            "low_mids": pb.low_mids_rms,
            "highs": pb.highs_rms,
            "air": pb.air_rms,
        }
        for name, arr in band_arrays.items():
            lo, hi = _BAND_HZ[name]
            bands_out[name] = {
                "hz_low": lo,
                "hz_high": hi,
                "rms_values": [float(v) for v in arr],
                "rms_summary": _summary(arr),
            }
        envelope["per_band_rms"] = {"hop_length": pb.hop_length, "bands": bands_out}

    if result.hpss is not None:
        h = result.hpss
        envelope["hpss"] = {
            "hop_length": h.hop_length,
            "harmonic_rms_values": [float(v) for v in h.harmonic_rms],
            "percussive_rms_values": [float(v) for v in h.percussive_rms],
            "harmonic_rms_summary": _summary(h.harmonic_rms),
            "percussive_rms_summary": _summary(h.percussive_rms),
        }

    if result.spectral_centroid is not None:
        c = result.spectral_centroid
        c_arr = np.asarray(c.values_hz)
        envelope["spectral_centroid"] = {
            "hop_length": c.hop_length,
            "values_hz": [float(v) for v in c_arr],
            "summary_hz": {
                "mean": float(c_arr.mean()),
                "p10": float(np.percentile(c_arr, 10)),
                "p50": float(np.percentile(c_arr, 50)),
                "p90": float(np.percentile(c_arr, 90)),
            },
        }

    if result.onset_density is not None:
        envelope["onset_density"] = {
            "bars": [
                {
                    "bar_index": b.bar_index,
                    "start_s": b.start_s,
                    "end_s": b.end_s,
                    "onsets_per_band": dict(b.onsets_per_band),
                }
                for b in result.onset_density.bars
            ]
        }

    if result.sidechain is not None:
        sc = result.sidechain
        envelope["sidechain"] = {
            "detected": sc.detected,
            "depth_db_mean": sc.depth_db_mean,
            "depth_db_p90": sc.depth_db_p90,
            "consistency_pct": sc.consistency_pct,
            "kicks_examined": sc.kicks_examined,
            "threshold_db_for_detection": sc.threshold_db_for_detection,
            "threshold_consistency_for_detection": sc.threshold_consistency_for_detection,
            "method": sc.method,
        }

    envelope["chroma_mean"] = [float(v) for v in result.chroma_mean]
    envelope["mfcc_summary"] = {
        "n_coeffs": len(result.mfcc_means),
        "means": [float(v) for v in result.mfcc_means],
        "stds": [float(v) for v in result.mfcc_stds],
    }
    envelope["sections"] = []
    envelope["csv_context"] = csv_block
    return envelope


def write_envelope(envelope: dict[str, Any], out_path: Path) -> None:
    """Write the envelope as JSON with stable formatting."""
    out_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=False),
        encoding="utf-8",
    )
