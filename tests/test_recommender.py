# tests/test_recommender.py

from __future__ import annotations

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.planner.recommender import recommend_cutter
from flexai.plugins.registry import load_plugins
from tests.helpers import flat_panel_asset, long_strip_asset, sphere_asset


def test_recommender_prefers_twist_for_sphere() -> None:
    asset = sphere_asset()
    report = analyze_model(asset, asset.path)
    recommendation = recommend_cutter(report, load_plugins())

    assert recommendation.plugin_id == "twist"
    assert recommendation.score >= 90.0


def test_recommender_prefers_living_hinge_for_flat_panel() -> None:
    asset = flat_panel_asset()
    report = analyze_model(asset, asset.path)
    recommendation = recommend_cutter(report, load_plugins())

    assert recommendation.plugin_id == "living_hinge"
    assert recommendation.score >= 85.0


def test_recommender_prefers_zigzag_for_long_strip() -> None:
    asset = long_strip_asset()
    report = analyze_model(asset, asset.path)
    recommendation = recommend_cutter(report, load_plugins())

    assert recommendation.plugin_id == "zigzag"
    assert recommendation.score >= 90.0
