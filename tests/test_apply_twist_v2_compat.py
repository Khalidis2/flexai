# tests/test_apply_twist_v2_compat.py

from __future__ import annotations

import sys

from tools import apply_twist_v2


def test_apply_twist_v2_delegates_to_primary_twist_command(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_twist_command(**kwargs) -> int:
        captured.update(kwargs)
        return 7

    monkeypatch.setattr(apply_twist_v2, "twist_command", fake_twist_command)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "apply_twist_v2.py",
            "input.3mf",
            "output.stl",
            "--blender",
            "blender-test",
            "--keep-cutter",
            "--strict-recommendation",
            "--report",
            "reports/operation.json",
            "--artifacts-dir",
            "artifacts",
        ],
    )

    assert apply_twist_v2.main() == 7
    assert captured == {
        "input_path": "input.3mf",
        "output_path": "output.stl",
        "blender_path": "blender-test",
        "keep_cutter": True,
        "strict_recommendation": True,
        "report_path": "reports/operation.json",
        "artifacts_dir": "artifacts",
    }
