"""End-to-end CLI test on the synthetic fixture wav.

Gated by TEARDOWN_E2E=1 so it isn't part of the default test run.
Exercises the full pipeline minus yt-dlp (--local).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("TEARDOWN_E2E") != "1",
    reason="TEARDOWN_E2E=1 not set",
)


def test_full_pipeline_on_fixture_wav(tmp_path, teardown_fixture_wav, monkeypatch):
    """Run scripts/teardown.py via subprocess against the fixture wav.

    Validates: source.wav exists, analysis.json v1.1 schema, scrub-strip.png
    (6-panel) or per-panel fallbacks.
    """
    project_root = Path(__file__).resolve().parents[2]
    teardown_script = project_root / "scripts" / "teardown.py"
    teardowns_dir = project_root / "teardowns"

    slug = "test-fixture-126bpm"
    target = teardowns_dir / slug
    if target.exists():
        shutil.rmtree(target)

    proc = subprocess.run(
        [sys.executable, str(teardown_script),
         "--slug", slug, "--local", str(teardown_fixture_wav)],
        capture_output=True, text=True,
    )
    try:
        assert proc.returncode == 0, f"CLI failed:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"

        # source.wav copied in
        assert (target / "source.wav").exists()

        # analysis.json v1.1 shape
        env = json.loads((target / "analysis.json").read_text(encoding="utf-8"))
        assert env["tool_version"] == "0.2.0", f"expected v0.2.0, got {env['tool_version']!r}"
        assert abs(env["tempo"]["bpm_librosa"] - 126.0) < 2.0
        assert env["sections"] == []
        assert len(env["chroma_mean"]) == 12
        assert env["audio"]["sample_rate"] == 22050

        # v1.1 keys
        assert "per_band_rms" in env
        assert set(env["per_band_rms"]["bands"].keys()) == {"sub", "bass", "low_mids", "highs", "air"}
        assert "hpss" in env
        assert "harmonic_rms_values" in env["hpss"]
        assert "percussive_rms_values" in env["hpss"]
        assert "spectral_centroid" in env
        assert "values_hz" in env["spectral_centroid"]
        assert "onset_density" in env
        assert "bars" in env["onset_density"]
        assert "sidechain" in env
        assert "detected" in env["sidechain"]
        # Fixture has clicks but no bass ducking — sidechain should be False here.
        assert env["sidechain"]["detected"] is False

        # scrub strip (combined or per-panel)
        combined = target / "scrub-strip.png"
        per_panel = [target / f"scrub-strip-{i}.png" for i in (1, 2, 3, 4, 5, 6)]
        assert combined.exists() or all(p.exists() for p in per_panel)
    finally:
        if target.exists():
            shutil.rmtree(target)
