"""Phase 10 — scenario discovery primitive (SCEN-104).

Tests `get_scenario_discovery_roots()` validation and override behavior.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_config import (
    DEFAULT_SCENARIO_DISCOVERY_ROOTS,
    SCENARIO_FILE_PATTERN,
    _clear_project_config_cache,
    get_scenario_discovery_roots,
)


def _write_config(tmp_path, payload):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(exist_ok=True)
    (claude_dir / "config.json").write_text(json.dumps(payload), encoding="utf-8")


def test_defaults_include_ralph_and_docs_specs():
    assert ".ralph/specs" in DEFAULT_SCENARIO_DISCOVERY_ROOTS
    assert "docs/specs" in DEFAULT_SCENARIO_DISCOVERY_ROOTS


def test_pattern_matches_nested_scenario_files():
    assert SCENARIO_FILE_PATTERN == "**/scenarios/*.scenarios.md"


def test_returns_defaults_when_no_config(tmp_path):
    _clear_project_config_cache()
    assert get_scenario_discovery_roots(tmp_path) == DEFAULT_SCENARIO_DISCOVERY_ROOTS


def test_returns_defaults_when_cwd_is_none():
    assert get_scenario_discovery_roots(None) == DEFAULT_SCENARIO_DISCOVERY_ROOTS


def test_override_replaces_defaults(tmp_path):
    _clear_project_config_cache()
    _write_config(tmp_path, {"SCENARIO_DISCOVERY_ROOTS": ["custom/specs"]})
    assert get_scenario_discovery_roots(tmp_path) == ("custom/specs",)


def test_override_accepts_multiple_roots(tmp_path):
    _clear_project_config_cache()
    _write_config(tmp_path, {"SCENARIO_DISCOVERY_ROOTS": ["a/specs", "b/specs"]})
    assert get_scenario_discovery_roots(tmp_path) == ("a/specs", "b/specs")


def test_non_list_override_falls_back_to_defaults(tmp_path):
    _clear_project_config_cache()
    _write_config(tmp_path, {"SCENARIO_DISCOVERY_ROOTS": "not-a-list"})
    assert get_scenario_discovery_roots(tmp_path) == DEFAULT_SCENARIO_DISCOVERY_ROOTS


def test_absolute_path_entries_rejected(tmp_path):
    _clear_project_config_cache()
    _write_config(tmp_path, {"SCENARIO_DISCOVERY_ROOTS": ["/etc/evil", "ok/specs"]})
    # The absolute path is dropped; the relative one survives
    assert get_scenario_discovery_roots(tmp_path) == ("ok/specs",)


def test_traversal_entries_rejected(tmp_path):
    _clear_project_config_cache()
    _write_config(tmp_path, {"SCENARIO_DISCOVERY_ROOTS": ["../../etc", "ok/specs"]})
    assert get_scenario_discovery_roots(tmp_path) == ("ok/specs",)


def test_all_invalid_falls_back_to_defaults(tmp_path):
    _clear_project_config_cache()
    _write_config(tmp_path, {"SCENARIO_DISCOVERY_ROOTS": ["/bad", "../bad", ""]})
    assert get_scenario_discovery_roots(tmp_path) == DEFAULT_SCENARIO_DISCOVERY_ROOTS


def test_non_string_entries_skipped(tmp_path):
    _clear_project_config_cache()
    _write_config(tmp_path, {"SCENARIO_DISCOVERY_ROOTS": [123, None, "ok/specs"]})
    assert get_scenario_discovery_roots(tmp_path) == ("ok/specs",)
