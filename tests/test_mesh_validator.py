# tests/test_mesh_validator.py

from __future__ import annotations

import trimesh

from flexai.validation.mesh_validator import validate_mesh_file


def test_validate_existing_mesh_file(tmp_path) -> None:
    path = tmp_path / "box.stl"
    mesh = trimesh.creation.box(extents=(10.0, 10.0, 10.0))
    mesh.export(path)

    report = validate_mesh_file(path)

    assert report.exists is True
    assert report.loadable is True
    assert report.watertight is True
    assert report.face_count > 0
    assert report.vertex_count > 0
    assert report.surface_area_mm2 > 0
    assert report.passed is True


def test_validate_missing_mesh_file(tmp_path) -> None:
    path = tmp_path / "missing.stl"

    report = validate_mesh_file(path)

    assert report.exists is False
    assert report.loadable is False
    assert report.passed is False
    assert report.warnings == ["Output file does not exist."]
