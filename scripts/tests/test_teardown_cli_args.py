"""Tests for CLI argument parsing (spec §3.13)."""

import pytest

from teardown.cli import build_parser


def test_url_and_local_are_mutually_exclusive():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--slug", "x", "--url", "https://x", "--local", "/y"])


def test_one_of_url_or_local_required_unless_check_deps_or_dry_run():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--slug", "x"])


def test_check_deps_alone_is_valid():
    parser = build_parser()
    args = parser.parse_args(["--check-deps"])
    assert args.check_deps is True


def test_dry_run_alone_with_url_is_valid():
    parser = build_parser()
    args = parser.parse_args(["--slug", "x", "--url", "https://x", "--dry-run"])
    assert args.dry_run is True


def test_csv_context_optional():
    parser = build_parser()
    args = parser.parse_args(["--slug", "x", "--url", "https://x", "--csv-context", "abc"])
    assert args.csv_context == "abc"


def test_force_flag_defaults_false():
    parser = build_parser()
    args = parser.parse_args(["--slug", "x", "--url", "https://x"])
    assert args.force is False
