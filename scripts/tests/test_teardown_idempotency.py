"""Tests for the idempotency guard (spec §3.7)."""

import pytest

from teardown.cli import _check_idempotency


def test_empty_dir_is_ok(tmp_path):
    target = tmp_path / "empty-slug"
    # Does not exist yet; allowed.
    _check_idempotency(target, force=False)  # raises nothing


def test_nonexistent_dir_is_ok(tmp_path):
    target = tmp_path / "never-existed"
    _check_idempotency(target, force=False)


def test_populated_dir_without_force_raises(tmp_path):
    target = tmp_path / "exists"
    target.mkdir()
    (target / "analysis.json").write_text("{}")

    with pytest.raises(SystemExit) as exc:
        _check_idempotency(target, force=False)
    assert exc.value.code == 1


def test_populated_dir_with_force_is_ok(tmp_path):
    target = tmp_path / "exists"
    target.mkdir()
    (target / "analysis.json").write_text("{}")
    _check_idempotency(target, force=True)  # raises nothing
