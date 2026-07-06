# flexai/perception/model_interpreter.py

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from flexai.models import ModelReport


@dataclass(frozen=True)
class OperationSuitability:
    operation: str
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PerceptionReport:
    shape: str
    size_class: str
    symmetry: str
    likely_shell: bool
    print_risk: str
    primary_use_guess: str
    operation_suitability: list[OperationSuitability] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["operation_suitability"] = [item.to_dict() for item in self.operation_suitability]
        return data


def interpret_model(report: ModelReport) -> PerceptionReport:
    dimensions = report.dimensions_mm
    longest = max(dimensions)
    shortest = min(dimensions)
    size_class = _size_class(longest)
    likely_shell = _likely_shell(report)
    primary_use_guess = _primary_use_guess(report.shape, longest, shortest)
    warnings = _warnings(report)

    return PerceptionReport(
        shape=report.shape,
        size_class=size_class,
        symmetry=report.symmetry,
        likely_shell=likely_shell,
        print_risk=report.risk_level,
        primary_use_guess=primary_use_guess,
        operation_suitability=_operation_suitability(report),
        warnings=warnings,
    )


def _size_class(longest_dimension_mm: float) -> str:
    if longest_dimension_mm < 25.0:
        return "small"
    if longest_dimension_mm < 90.0:
        return "medium"
    if longest_dimension_mm < 180.0:
        return "large"
    return "oversized"


def _likely_shell(report: ModelReport) -> bool:
    if not report.watertight or report.volume_mm3 <= 0 or report.surface_area_mm2 <= 0:
        return False

    dimensions = report.dimensions_mm
    longest = max(dimensions)
    compactness = report.volume_mm3 / max(longest**3, 0.001)

    if report.shape == "sphere" and compactness < 0.65:
        return True
    if report.shape in {"flat_panel", "long_strip"}:
        return True
    return False


def _primary_use_guess(shape: str, longest: float, shortest: float) -> str:
    aspect = longest / max(shortest, 0.001)

    if shape == "sphere":
        return "toy_or_fidget"
    if shape == "flat_panel":
        return "panel_lid_or_cover"
    if shape == "long_strip" and aspect > 4.0:
        return "strap_bracelet_or_handle"
    if shape == "cylinder_or_rod":
        return "rotational_or_grip_part"
    if shape == "compact":
        return "compact_decorative_or_functional_part"
    return "unknown_complex_part"


def _operation_suitability(report: ModelReport) -> list[OperationSuitability]:
    mapping = {
        "sphere": [
            OperationSuitability("twist", 96.0, "Radial symmetry and rounded body match twist-style cutting."),
            OperationSuitability("honeycomb", 35.0, "Honeycomb is possible only on selected curved regions."),
        ],
        "flat_panel": [
            OperationSuitability("living_hinge", 92.0, "Flat panels are ideal for repeated hinge slots."),
            OperationSuitability("honeycomb", 88.0, "Broad panels can accept honeycomb lightening cuts."),
            OperationSuitability("zigzag", 70.0, "Elongated flat panels may support zigzag flexibility."),
        ],
        "long_strip": [
            OperationSuitability("zigzag", 94.0, "Long strips are ideal for offset slot flexibility."),
            OperationSuitability("living_hinge", 84.0, "Repeated hinge slots can create controlled bending."),
        ],
        "cylinder_or_rod": [
            OperationSuitability("twist", 84.0, "Axial geometry may support twist cutting."),
            OperationSuitability("zigzag", 52.0, "Zigzag cuts may work with careful alignment."),
        ],
    }
    items = mapping.get(report.shape, [OperationSuitability("manual_review", 40.0, "Complex geometry needs manual region selection.")])

    if not report.watertight:
        return [
            OperationSuitability(item.operation, max(0.0, item.score - 25.0), item.reason + " Mesh is not watertight.")
            for item in items
        ]
    return items


def _warnings(report: ModelReport) -> list[str]:
    warnings: list[str] = []
    if not report.watertight:
        warnings.append("Mesh is not watertight; boolean operations are higher risk.")
    if report.face_count < 20:
        warnings.append("Mesh has very few faces; analysis confidence is low.")
    if report.risk_level == "high":
        warnings.append("Model is high risk for automatic cutting.")
    return warnings
