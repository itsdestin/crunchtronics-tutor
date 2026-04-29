"""Tests for matplotlib scrub-strip rendering (spec §3.10)."""

import numpy as np
import pytest

from teardown.analyze import analyze
from teardown.plot import render_scrub_strip


def test_scrub_strip_writes_png(tmp_path, teardown_fixture_wav):
    out_path = tmp_path / "scrub-strip.png"
    result = analyze(teardown_fixture_wav)
    paths = render_scrub_strip(
        audio_path=teardown_fixture_wav,
        result=result,
        out_dir=tmp_path,
    )
    assert out_path.exists()
    assert out_path.stat().st_size > 10_000  # non-trivial PNG
    assert paths == [out_path]


def test_scrub_strip_falls_back_to_per_panel_pngs(tmp_path, teardown_fixture_wav, monkeypatch):
    """When the multi-axis path fails, render each panel separately."""
    import teardown.plot as plot_mod
    original = plot_mod._render_combined

    def boom(*args, **kwargs):
        raise RuntimeError("simulated multi-axis failure")

    monkeypatch.setattr(plot_mod, "_render_combined", boom)

    result = analyze(teardown_fixture_wav)
    paths = render_scrub_strip(
        audio_path=teardown_fixture_wav,
        result=result,
        out_dir=tmp_path,
    )

    expected = [tmp_path / f"scrub-strip-{i}.png" for i in (1, 2, 3, 4)]
    for p in expected:
        assert p.exists(), f"expected fallback panel {p} missing"
    assert paths == expected
