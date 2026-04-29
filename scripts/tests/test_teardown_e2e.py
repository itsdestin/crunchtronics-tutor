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

    Validates: source.wav exists, analysis.json schema, scrub-strip.png
    (or per-panel fallbacks).
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

        # analysis.json shape
        env = json.loads((target / "analysis.json").read_text(encoding="utf-8"))
        assert env["tool_version"]
        assert abs(env["tempo"]["bpm_librosa"] - 126.0) < 2.0
        assert env["sections"] == []
        assert len(env["chroma_mean"]) == 12
        assert env["audio"]["sample_rate"] == 22050

        # scrub strip (combined or per-panel)
        combined = target / "scrub-strip.png"
        per_panel = [target / f"scrub-strip-{i}.png" for i in (1, 2, 3, 4)]
        assert combined.exists() or all(p.exists() for p in per_panel)
    finally:
        if target.exists():
            shutil.rmtree(target)
