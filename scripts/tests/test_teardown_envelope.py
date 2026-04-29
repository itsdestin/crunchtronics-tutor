"""Tests for analysis.json envelope composition (spec §3.9)."""

import json
import numpy as np
import pytest

from teardown.envelope import compose_envelope, write_envelope
from teardown.models import AnalysisResult
from teardown.key import KeyEstimate


def _make_result(**overrides) -> AnalysisResult:
    defaults = dict(
        duration_s=222.4,
        sample_rate=22050,
        bpm=126.05,
        beat_times_s=np.array([0.51, 0.99, 1.47]),
        chroma_mean=np.array([0.04, 0.07, 0.31, 0.05, 0.18, 0.09,
                              0.12, 0.06, 0.05, 0.21, 0.04, 0.05]),
        rms_values=np.array([0.012, 0.018, 0.21, 0.31, 0.18, 0.04]),
        rms_hop_length=512,
        mfcc_means=np.zeros(13),
        mfcc_stds=np.ones(13),
    )
    defaults.update(overrides)
    return AnalysisResult(**defaults)


def test_envelope_has_required_top_level_keys():
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="https://www.youtube.com/watch?v=xyz",
        source_title="John Summit & HAYLA — Where You Are",
        source_channel="John Summit",
        source_duration_s=222.4,
        source_basename="source.wav",
        csv_context=None,
    )
    for key in ["tool_version", "created_at", "source", "audio", "tempo",
                "beats", "key", "energy", "chroma_mean", "mfcc_summary",
                "sections", "csv_context"]:
        assert key in env, f"missing top-level key: {key}"


def test_envelope_sections_always_empty():
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    assert env["sections"] == []


def test_envelope_tempo_agreement_within_1bpm_true():
    env = compose_envelope(
        result=_make_result(bpm=126.0),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context={"bpm": 126.0, "key_camelot": "5A"},
    )
    assert env["tempo"]["agree_within_1bpm"] is True
    assert env["tempo"]["agree_within_4bpm"] is True


def test_envelope_tempo_disagreement_4bpm():
    env = compose_envelope(
        result=_make_result(bpm=63.0),  # half-time read of 126
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context={"bpm": 126.0, "key_camelot": "5A"},
    )
    assert env["tempo"]["agree_within_1bpm"] is False
    assert env["tempo"]["agree_within_4bpm"] is False


def test_envelope_tempo_agreement_keys_omitted_when_no_csv():
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    assert "agree_within_1bpm" not in env["tempo"]
    assert "agree_within_4bpm" not in env["tempo"]
    assert env["tempo"]["bpm_librosa"] == pytest.approx(126.05)
    assert "bpm_csv" not in env["tempo"]


def test_envelope_csv_context_omitted_when_none():
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    assert env["csv_context"] is None


def test_write_envelope_round_trip(tmp_path):
    env = compose_envelope(
        result=_make_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="https://x", source_title="x", source_channel="x",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    out_path = tmp_path / "analysis.json"
    write_envelope(env, out_path)

    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["tempo"]["bpm_librosa"] == pytest.approx(126.05)
    assert isinstance(loaded["chroma_mean"], list)
    assert len(loaded["chroma_mean"]) == 12


# v1.1 schema tests


def _make_per_band_rms(n=10):
    from teardown.models import PerBandRMS
    return PerBandRMS(
        hop_length=512,
        sub_rms=np.linspace(0.0, 0.5, n),
        bass_rms=np.linspace(0.0, 0.4, n),
        low_mids_rms=np.linspace(0.0, 0.3, n),
        highs_rms=np.linspace(0.0, 0.2, n),
        air_rms=np.linspace(0.0, 0.05, n),
    )


def _make_hpss(n=10):
    from teardown.models import HPSSResult
    return HPSSResult(
        hop_length=512,
        harmonic_rms=np.linspace(0.1, 0.4, n),
        percussive_rms=np.linspace(0.05, 0.3, n),
    )


def _make_centroid(n=10):
    from teardown.models import CentroidResult
    return CentroidResult(hop_length=512, values_hz=np.linspace(500, 3000, n))


def _make_onset_density():
    from teardown.models import OnsetDensity, OnsetDensityBar
    return OnsetDensity(bars=[
        OnsetDensityBar(bar_index=0, start_s=0.5, end_s=2.4,
                        onsets_per_band={"sub": 4, "bass": 5, "low_mids": 12,
                                         "highs": 18, "air": 9}),
        OnsetDensityBar(bar_index=1, start_s=2.4, end_s=4.3,
                        onsets_per_band={"sub": 4, "bass": 5, "low_mids": 14,
                                         "highs": 22, "air": 11}),
    ])


def _make_sidechain():
    from teardown.models import SidechainResult
    return SidechainResult(
        detected=True,
        depth_db_mean=4.2,
        depth_db_p90=6.8,
        consistency_pct=87.0,
        kicks_examined=152,
        threshold_db_for_detection=3.0,
        threshold_consistency_for_detection=60.0,
    )


def _make_v11_result():
    return _make_result(
        per_band_rms=_make_per_band_rms(),
        hpss=_make_hpss(),
        spectral_centroid=_make_centroid(),
        onset_density=_make_onset_density(),
        sidechain=_make_sidechain(),
    )


def test_envelope_tool_version_bumped_to_0_2_0():
    env = compose_envelope(
        result=_make_v11_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    assert env["tool_version"] == "0.2.0"


def test_envelope_includes_per_band_rms():
    env = compose_envelope(
        result=_make_v11_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    pb = env["per_band_rms"]
    assert pb["hop_length"] == 512
    assert set(pb["bands"].keys()) == {"sub", "bass", "low_mids", "highs", "air"}
    sub = pb["bands"]["sub"]
    assert sub["hz_low"] == 20
    assert sub["hz_high"] == 60
    assert isinstance(sub["rms_values"], list)
    assert "rms_summary" in sub
    air = pb["bands"]["air"]
    assert air["hz_low"] == 8000
    assert air["hz_high"] is None  # open-top


def test_envelope_includes_hpss():
    env = compose_envelope(
        result=_make_v11_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    h = env["hpss"]
    assert h["hop_length"] == 512
    assert isinstance(h["harmonic_rms_values"], list)
    assert isinstance(h["percussive_rms_values"], list)
    assert "harmonic_rms_summary" in h
    assert "percussive_rms_summary" in h


def test_envelope_includes_spectral_centroid():
    env = compose_envelope(
        result=_make_v11_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    c = env["spectral_centroid"]
    assert c["hop_length"] == 512
    assert isinstance(c["values_hz"], list)
    assert "summary_hz" in c
    assert all(k in c["summary_hz"] for k in ("mean", "p10", "p50", "p90"))


def test_envelope_includes_onset_density():
    env = compose_envelope(
        result=_make_v11_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    od = env["onset_density"]
    assert "bars" in od
    assert len(od["bars"]) == 2
    bar0 = od["bars"][0]
    assert bar0["bar_index"] == 0
    assert "start_s" in bar0
    assert "end_s" in bar0
    assert set(bar0["onsets_per_band"].keys()) == {"sub", "bass", "low_mids", "highs", "air"}


def test_envelope_includes_sidechain():
    env = compose_envelope(
        result=_make_v11_result(),
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    sc = env["sidechain"]
    assert sc["detected"] is True
    assert sc["depth_db_mean"] == pytest.approx(4.2)
    assert sc["consistency_pct"] == pytest.approx(87.0)
    assert sc["threshold_db_for_detection"] == 3.0
    assert "method" in sc


def test_envelope_v1_0_result_omits_v1_1_keys():
    """When v1.1 fields on AnalysisResult are None (v1.0 callers), envelope
    keeps the new top-level keys absent from output. Forward-compatible:
    readers that branch on tool_version=="0.1.0" still work."""
    env = compose_envelope(
        result=_make_result(),  # v1.0 fields only
        key_estimate=KeyEstimate(standard="F minor", camelot="5A"),
        source_url="", source_title="x", source_channel="",
        source_duration_s=222.4, source_basename="source.wav",
        csv_context=None,
    )
    # v1.0 schema reverts when no v1.1 features are present
    assert env["tool_version"] == "0.1.0"
    assert "per_band_rms" not in env
    assert "hpss" not in env
    assert "spectral_centroid" not in env
    assert "onset_density" not in env
    assert "sidechain" not in env
