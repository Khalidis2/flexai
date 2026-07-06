# tests/test_operation_score.py

from __future__ import annotations

import trimesh

from flexai.validation.mesh_comparison import compare_mesh_files
from flexai.validation.operation_score import score_operation


def test_score_operation_passes_reasonable_change(tmp_path) -> None:
    input_path = tmp_path / "input.stl"
    output_path = tmp_path / "output.stl"
    trimesh.creation.box(extents=(10.0, 10.0, 10.0)).export(input_path)
    trimesh.creation.box(extents=(9.0, 9.0, 9.0)).export(output_path)

    comparison = compare_mesh_files(input_path, output_path)
    score = score_operation(comparison)

    assert score.passed is True
    assert score.score >= 90.0
    assert score.grade == "excellent"
    assert score.warnings == []


def test_score_operation_warns_for_no_change(tmp_path) -> None:
    input_path = tmp_path / "input.stl"
    output_path = tmp_path / "output.stl"
    mesh = trimesh.creation.box(extents=(10.0, 10.0, 10.0))
    mesh.export(input_path)
    mesh.export(output_path)

    comparison = compare_mesh_files(input_path, output_path)
    score = score_operation(comparison)

    assert score.passed is False
    assert score.score < 90.0
    assert any("too little material" in warning for warning in score.warnings)


def test_score_operation_warns_for_destructive_change(tmp_path) -> None:
    input_path = tmp_path / "input.stl"
    output_path = tmp_path / "output.stl"
    trimesh.creation.box(extents=(10.0, 10.0, 10.0)).export(input_path)
    trimesh.creation.box(extents=(2.0, 2.0, 2.0)).export(output_path)

    comparison = compare_mesh_files(input_path, output_path)
    score = score_operation(comparison)

    assert score.passed is False
    assert score.score < 70.0
    assert any("too much material" in warning for warning in score.warnings)
