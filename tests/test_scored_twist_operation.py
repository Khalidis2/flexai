# tests/test_scored_twist_operation.py

from __future__ import annotations

from pathlib import Path

import trimesh

from flexai.executor.blender_runner import BlenderRunResult
from flexai.models import CutterRecommendation
from flexai.operations import compared_twist_operation
from flexai.operations.scored_twist_operation import apply_scored_twist_operation


def test_scored_twist_operation_returns_quality_score(monkeypatch, tmp_path) -> None:
    input_path = tmp_path / "input.stl"
    output_path = tmp_path / "output.stl"
    trimesh.creation.box(extents=(10.0, 10.0, 10.0)).export(input_path)

    def fake_apply_twist_operation(**kwargs):
        trimesh.creation.box(extents=(9.0, 9.0, 9.0)).export(output_path)
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

    monkeypatch.setattr(compared_twist_operation, "apply_twist_operation", fake_apply_twist_operation)

    recommendation = CutterRecommendation(
        plugin_id="twist",
        plugin_name="Twist",
        score=96.0,
        reason="Test recommendation",
        parameters={"diameter_mm": 12.0, "height_mm": 12.0},
    )

    result = apply_scored_twist_operation(
        input_path=input_path,
        output_path=output_path,
        recommendation=recommendation,
    )

    assert result.passed is True
    assert result.score.passed is True
    assert result.score.grade == "excellent"
    assert result.score.score >= 90.0
