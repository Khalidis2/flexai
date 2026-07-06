# tests/test_model_interpreter.py

from __future__ import annotations

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.perception.model_interpreter import interpret_model
from tests.helpers import flat_panel_asset, long_strip_asset, sphere_asset


def test_interpreter_identifies_sphere_as_toy_or_fidget() -> None:
    asset = sphere_asset(radius=20.0)
    report = analyze_model(asset, asset.path)
    perception = interpret_model(report)

    assert perception.shape == "sphere"
    assert perception.size_class == "medium"
    assert perception.primary_use_guess == "toy_or_fidget"
    assert perception.operation_suitability[0].operation == "twist"


def test_interpreter_identifies_flat_panel_options() -> None:
    asset = flat_panel_asset()
    report = analyze_model(asset, asset.path)
    perception = interpret_model(report)
    operations = {item.operation for item in perception.operation_suitability}

    assert perception.shape == "flat_panel"
    assert perception.primary_use_guess == "panel_lid_or_cover"
    assert {"living_hinge", "honeycomb"}.issubset(operations)


def test_interpreter_identifies_long_strip_options() -> None:
    asset = long_strip_asset()
    report = analyze_model(asset, asset.path)
    perception = interpret_model(report)

    assert perception.shape == "long_strip"
    assert perception.primary_use_guess == "strap_bracelet_or_handle"
    assert perception.operation_suitability[0].operation == "zigzag"
