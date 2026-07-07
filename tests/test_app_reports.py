# tests/test_app_reports.py

from __future__ import annotations

import json

from app import _write_json_report


def test_write_json_report_creates_parent_directory(tmp_path) -> None:
    report_path = tmp_path / "nested" / "reports" / "operation.json"
    payload = {"passed": True, "score": {"value": 100}}

    written_path = _write_json_report(report_path, payload)

    assert written_path == report_path.resolve()
    assert json.loads(report_path.read_text(encoding="utf-8")) == payload
    assert report_path.read_text(encoding="utf-8").endswith("\n")
