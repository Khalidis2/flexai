# tests/test_analyzer.py

from __future__ import annotations

from flexai.analyzer.mesh_analyzer import analyze_model
from tests.helpers import flat_panel_asset, long_strip_asset, sphere_asset


def test_analyzer_classifies_sphere() -> None:
    asset = sphere_asset()
    report = analyze_model(asset, asset.path)

    assert report.shape == "sphere"
    assert report.symmetry == "radial"
    assert report.watertight is True
    assert report.risk_level == "low"


def test_analyzer_classifies_flat_panel() -> None:
    asset = flat_panel_asset()
    report = analyze_model(asset, asset.path)

    assert report.shape == "flat_panel"
    assert report.symmetry == "planar"
    assert report.watertight is True


def test_analyzer_classifies_long_strip() -> None:
    asset = long_strip_asset()
    report = analyze_model(asset, asset.path)

    assert report.shape == "long_strip"
    assert report.symmetry == "planar"
    assert report.watertight is True
