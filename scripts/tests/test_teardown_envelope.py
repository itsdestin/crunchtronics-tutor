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
