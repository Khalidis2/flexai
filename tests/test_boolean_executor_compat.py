# tests/test_boolean_executor_compat.py

from __future__ import annotations

from pathlib import Path

from flexai.executor.blender_runner import BlenderRunResult
from flexai.executor import boolean_executor_v2


def test_boolean_executor_v2_delegates_to_primary_executor(monkeypatch, tmp_path) -> None:
    target_path = tmp_path / "target.stl"
    cutter_path = tmp_path / "cutter.stl"
    output_path = tmp_path / "output.stl"
    captured: dict[str, object] = {}

    def fake_subtract_cutter_with_blender(**kwargs):
        captured.update(kwargs)
        return BlenderRunResult(
            return_code=0,
            stdout="",
            stderr="",
            output_path=Path(kwargs["output_path"]),
        )

    monkeypatch.setattr(boolean_executor_v2, "subtract_cutter_with_blender", fake_subtract_cutter_with_blender)

    result = boolean_executor_v2.subtract_cutter_with_blender_v2(
        target_path=target_path,
        cutter_path=cutter_path,
        output_path=output_path,
        blender_path="blender-test",
    )

    assert result.return_code == 0
    assert captured == {
        "target_path": target_path,
        "cutter_path": cutter_path,
        "output_path": output_path,
        "blender_path": "blender-test",
    }
