# tests/test_twist_operation.py

from __future__ import annotations

from pathlib import Path

import pytest
import trimesh

from flexai.executor.blender_runner import BlenderRunResult
from flexai.models import CutterRecommendation, MeshAsset
from flexai.operations import twist_operation
from flexai.operations.twist_operation import apply_twist_operation, twist_parameters_from_recommendation


def test_twist_parameters_from_recommendation() -> None:
    recommendation = CutterRecommendation(
        plugin_id="twist",
        plugin_name="Twist",
        score=96.0,
        reason="Test recommendation",
        parameters={
            "diameter_mm": 44.0,
            "height_mm": 42.0,
            "core_hole_mm": 9.0,
            "turns": 1.25,
            "blade_count": 5,
            "segments": 64,
        },
    )

    params = twist_parameters_from_recommendation(recommendation)

    assert params.diameter_mm == 44.0
    assert params.height_mm == 42.0
    assert params.core_hole_mm == 9.0
    assert params.slot_width_mm == 1.2
    assert params.turns == 1.25
    assert params.blade_count == 5
    assert params.segments == 64


def test_twist_parameters_require_diameter() -> None:
    recommendation = CutterRecommendation(
        plugin_id="twist",
        plugin_name="Twist",
        score=96.0,
        reason="Test recommendation",
        parameters={"height_mm": 42.0},
    )

    with pytest.raises(KeyError):
        twist_parameters_from_recommendation(recommendation)


def test_twist_operation_converts_non_blender_input_without_losing_original_path(monkeypatch, tmp_path) -> None:
    input_path = tmp_path / "input.3mf"
    output_path = tmp_path / "output.stl"
    input_path.write_text("placeholder", encoding="utf-8")
    captured: dict[str, Path] = {}

    def fake_load_mesh(path: Path) -> MeshAsset:
        return MeshAsset(path=path, file_type="3mf", mesh=trimesh.creation.box(extents=(10.0, 10.0, 10.0)))

    def fake_subtract_cutter_with_blender(**kwargs):
        target_path = Path(kwargs["target_path"])
        captured["target_path"] = target_path
        assert target_path.suffix == ".stl"
        assert target_path.exists()
        trimesh.creation.box(extents=(9.0, 9.0, 9.0)).export(kwargs["output_path"])
        return BlenderRunResult(
            return_code=0,
            stdout="",
            stderr="",
            output_path=Path(kwargs["output_path"]),
        )

    monkeypatch.setattr(twist_operation, "load_mesh", fake_load_mesh)
    monkeypatch.setattr(twist_operation, "subtract_cutter_with_blender", fake_subtract_cutter_with_blender)

    recommendation = CutterRecommendation(
        plugin_id="twist",
        plugin_name="Twist",
        score=96.0,
        reason="Test recommendation",
        parameters={"diameter_mm": 12.0, "height_mm": 12.0},
    )

    result = apply_twist_operation(
        input_path=input_path,
        output_path=output_path,
        recommendation=recommendation,
    )

    assert result.input_path == input_path.resolve()
    assert result.blender_input_path == captured["target_path"]
    assert result.blender_input_path != result.input_path
    assert output_path.exists()