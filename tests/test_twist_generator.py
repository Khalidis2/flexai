# tests/test_twist_generator.py

from __future__ import annotations

import pytest

from flexai.cutters.twist_generator import (
    MIN_PRINTABLE_SLOT_WIDTH_MM,
    MIN_SEGMENTS,
    TwistCutterParameters,
    generate_twist_cutter,
    normalize_twist_parameters,
)


def test_twist_generator_creates_mesh() -> None:
    params = TwistCutterParameters(
        diameter_mm=44.0,
        height_mm=44.0,
        core_hole_mm=9.0,
        slot_width_mm=1.2,
        turns=1.0,
        blade_count=4,
        segments=32,
    )

    mesh = generate_twist_cutter(params)

    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0
    assert mesh.extents[0] <= params.diameter_mm + 0.5
    assert mesh.extents[1] <= params.diameter_mm + 0.5
    assert mesh.extents[2] <= params.height_mm + 0.5


def test_twist_parameters_reject_invalid_core_hole() -> None:
    params = TwistCutterParameters(diameter_mm=20.0, height_mm=20.0, core_hole_mm=20.0)

    with pytest.raises(ValueError, match="core_hole_mm"):
        params.validate()


def test_twist_parameters_reject_too_few_segments() -> None:
    params = TwistCutterParameters(diameter_mm=20.0, height_mm=20.0, segments=4)

    with pytest.raises(ValueError, match="segments"):
        params.validate()


def test_twist_parameters_reject_unprintable_slot_width() -> None:
    params = TwistCutterParameters(diameter_mm=20.0, height_mm=20.0, slot_width_mm=0.4)

    with pytest.raises(ValueError, match="slot_width_mm"):
        params.validate()


def test_twist_parameter_normalization_clamps_printable_limits() -> None:
    params = TwistCutterParameters(
        diameter_mm=20.0,
        height_mm=20.0,
        core_hole_mm=3.0,
        slot_width_mm=0.3,
        segments=4,
    )

    normalized = normalize_twist_parameters(params)

    assert normalized.core_hole_mm == 6.0
    assert normalized.slot_width_mm == MIN_PRINTABLE_SLOT_WIDTH_MM
    assert normalized.segments == MIN_SEGMENTS


def test_twist_parameter_normalization_caps_large_core_hole() -> None:
    params = TwistCutterParameters(diameter_mm=20.0, height_mm=20.0, core_hole_mm=19.5)

    normalized = normalize_twist_parameters(params)

    assert normalized.core_hole_mm == pytest.approx(18.4)
    assert normalized.core_hole_mm < normalized.diameter_mm
