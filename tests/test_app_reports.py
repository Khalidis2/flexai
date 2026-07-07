# tests/test_app_reports.py

from __future__ import annotations

import json
from pathlib import Path

from app import _resolve_report_path, _write_json_report


def test_write_json_report_creates_parent_directory(tmp_path) -> None:
    report_path = tmp_path / "nested" / "reports" / "operation.json"
    payload = {"passed": True, "score": {"value": 100}}

    written_path = _write_json_report(report_path, payload)

    assert written_path == report_path.resolve()
    assert json.loads(report_path.read_text(encoding="utf-8")) == payload
    assert report_path.read_text(encoding="utf-8").endswith("\n")


def test_resolve_report_path_prefers_explicit_report() -> None:
    assert _resolve_report_path("custom/report.json", "artifacts", "analysis.json") == Path("custom/report.json")


def test_resolve_report_path_uses_artifacts_dir_default_name() -> None:
    assert _resolve_report_path(None, "artifacts", "twist_operation.json") == Path("artifacts") / "twist_operation.json"


def test_resolve_report_path_returns_none_without_report_destination() -> None:
    assert _resolve_report_path(None, None, "analysis.json") is None
