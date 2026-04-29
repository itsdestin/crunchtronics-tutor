"""Compose and write the analysis.json envelope (spec §3.9)."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np

from teardown.key import KeyEstimate
from teardown.models import AnalysisResult

TOOL_VERSION = "0.1.0"


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
    """Build the JSON-serializable envelope per spec §3.9."""
    rms = np.asarray(result.rms_values)
    rms_summary = {
        "mean": float(rms.mean()),
        "p10": float(np.percentile(rms, 10)),
        "p50": float(np.percentile(rms, 50)),
        "p90": float(np.percentile(rms, 90)),
    }

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

    return {
        "tool_version": TOOL_VERSION,
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
        "chroma_mean": [float(v) for v in result.chroma_mean],
        "mfcc_summary": {
            "n_coeffs": len(result.mfcc_means),
            "means": [float(v) for v in result.mfcc_means],
            "stds": [float(v) for v in result.mfcc_stds],
        },
        "sections": [],
        "csv_context": csv_block,
    }


def write_envelope(envelope: dict[str, Any], out_path: Path) -> None:
    """Write the envelope as JSON with stable formatting."""
    out_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=False),
        encoding="utf-8",
    )
