# tests/test_candidate_regions.py

from __future__ import annotations

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.perception.candidate_regions import find_candidate_regions
from tests.helpers import flat_panel_asset, long_strip_asset, sphere_asset


def test_candidate_region_for_sphere_prefers_twist() -> None:
    asset = sphere_asset()
    report = analyze_model(asset, asset.path)
    regions = find_candidate_regions(report)

    assert len(regions) == 1
    assert regions[0].region_type == "radial_volume"
    assert regions[0].preferred_operations == ["twist"]
    assert regions[0].confidence >= 90.0


def test_candidate_region_for_flat_panel_prefers_hinge_and_honeycomb() -> None:
    asset = flat_panel_asset()
    report = analyze_model(asset, asset.path)
    regions = find_candidate_regions(report)

    assert len(regions) == 1
    assert regions[0].region_type == "flat_face"
    assert regions[0].preferred_operations == ["living_hinge", "honeycomb"]


def test_candidate_region_for_long_strip_prefers_zigzag_and_hinge() -> None:
    asset = long_strip_asset()
    report = analyze_model(asset, asset.path)
    regions = find_candidate_regions(report)

    assert len(regions) == 1
    assert regions[0].region_type == "strip_body"
    assert regions[0].preferred_operations == ["zigzag", "living_hinge"]
