# tests/test_twist_operation.py

from __future__ import annotations

import pytest

from flexai.models import CutterRecommendation
from flexai.operations.twist_operation import twist_parameters_from_recommendation


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
