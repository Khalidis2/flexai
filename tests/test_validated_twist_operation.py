# tests/test_validated_twist_operation.py

from __future__ import annotations

from pathlib import Path

import trimesh

from flexai.executor.blender_runner import BlenderRunResult
from flexai.models import CutterRecommendation
from flexai.operations import validated_twist_operation


def test_validated_twist_operation_reports_output_validation(monkeypatch, tmp_path) -> None:
    input_path = tmp_path / "input.stl"
    output_path = tmp_path / "output.stl"
    trimesh.creation.box(extents=(10.0, 10.0, 10.0)).export(input_path)

    def fake_apply_twist_operation(**kwargs):
        trimesh.creation.box(extents=(8.0, 8.0, 8.0)).export(output_path)
        from flexai.operations.twist_operation import TwistOperationResult

        return TwistOperationResult(
            input_path=Path(kwargs["input_path"]),
            cutter_path=tmp_path / "cutter.stl",
            output_path=Path(kwargs["output_path"]),
            blender_result=BlenderRunResult(
                return_code=0,
                stdout="",
                stderr="",
                output_path=Path(kwargs["output_path"]),
            ),
        )

    monkeypatch.setattr(validated_twist_operation, "apply_twist_operation", fake_apply_twist_operation)

    recommendation = CutterRecommendation(
        plugin_id="twist",
        plugin_name="Twist",
        score=96.0,
        reason="Test recommendation",
        parameters={"diameter_mm": 12.0, "height_mm": 12.0},
    )

    result = validated_twist_operation.apply_validated_twist_operation(
        input_path=input_path,
        output_path=output_path,
        recommendation=recommendation,
    )

    assert result.passed is True
    assert result.validation.exists is True
    assert result.validation.loadable is True
    assert result.validation.watertight is True
