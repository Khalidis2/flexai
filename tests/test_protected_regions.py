# tests/test_protected_regions.py

from __future__ import annotations

import trimesh

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.models import MeshAsset
from flexai.perception.protected_regions import detect_protected_regions
from tests.helpers import sphere_asset


def test_watertight_sphere_has_no_protected_regions() -> None:
    asset = sphere_asset()
    report = analyze_model(asset, asset.path)
    regions = detect_protected_regions(report)

    assert regions == []


def test_non_watertight_mesh_gets_global_review_region(tmp_path) -> None:
    mesh = trimesh.creation.box(extents=(10.0, 10.0, 10.0))
    mesh.update_faces([True] * (len(mesh.faces) - 1) + [False])
    mesh.remove_unreferenced_vertices()
    asset = MeshAsset(path=tmp_path / "open_box.stl", file_type="stl", mesh=mesh)
    report = analyze_model(asset, asset.path)
    regions = detect_protected_regions(report)

    assert any(region.feature_type == "global_risk" for region in regions)


def test_low_detail_mesh_gets_review_region(tmp_path) -> None:
    mesh = trimesh.creation.box(extents=(10.0, 10.0, 10.0))
    asset = MeshAsset(path=tmp_path / "box.stl", file_type="stl", mesh=mesh)
    report = analyze_model(asset, asset.path)
    regions = detect_protected_regions(report)

    assert any(region.feature_type == "low_detail_mesh" for region in regions)
