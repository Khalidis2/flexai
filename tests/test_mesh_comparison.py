# tests/test_mesh_comparison.py

from __future__ import annotations

import trimesh

from flexai.validation.mesh_comparison import compare_mesh_files


def test_compare_mesh_files_detects_reasonable_volume_removal(tmp_path) -> None:
    input_path = tmp_path / "input.stl"
    output_path = tmp_path / "output.stl"
    trimesh.creation.box(extents=(10.0, 10.0, 10.0)).export(input_path)
    trimesh.creation.box(extents=(9.0, 9.0, 9.0)).export(output_path)

    report = compare_mesh_files(input_path, output_path)

    assert report.volume_removed_mm3 > 0
    assert report.volume_removed_percent > 0
    assert report.passed is True
    assert report.warnings == []


def test_compare_mesh_files_warns_when_no_volume_removed(tmp_path) -> None:
    input_path = tmp_path / "input.stl"
    output_path = tmp_path / "output.stl"
    mesh = trimesh.creation.box(extents=(10.0, 10.0, 10.0))
    mesh.export(input_path)
    mesh.export(output_path)

    report = compare_mesh_files(input_path, output_path)

    assert report.passed is False
    assert any("removed very little volume" in warning for warning in report.warnings)


def test_compare_mesh_files_warns_when_too_much_volume_removed(tmp_path) -> None:
    input_path = tmp_path / "input.stl"
    output_path = tmp_path / "output.stl"
    trimesh.creation.box(extents=(10.0, 10.0, 10.0)).export(input_path)
    trimesh.creation.box(extents=(2.0, 2.0, 2.0)).export(output_path)

    report = compare_mesh_files(input_path, output_path)

    assert report.passed is False
    assert any("removed too much volume" in warning for warning in report.warnings)
