# flexai/perception/candidate_regions.py

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from flexai.models import ModelReport


@dataclass(frozen=True)
class CutterCandidateRegion:
    id: str
    region_type: str
    preferred_operations: list[str]
    center_mm: tuple[float, float, float]
    size_mm: tuple[float, float, float]
    confidence: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def find_candidate_regions(report: ModelReport) -> list[CutterCandidateRegion]:
    dimensions = report.dimensions_mm
    center = _center_from_bounds(report)

    if report.shape == "sphere":
        return [
            CutterCandidateRegion(
                id="centered-radial-body",
                region_type="radial_volume",
                preferred_operations=["twist"],
                center_mm=center,
                size_mm=dimensions,
                confidence=96.0 if report.watertight else 70.0,
                reason="Centered radial region is the safest initial region for twist cutting.",
            )
        ]

    if report.shape == "flat_panel":
        return [
            CutterCandidateRegion(
                id="broad-flat-face",
                region_type="flat_face",
                preferred_operations=["living_hinge", "honeycomb"],
                center_mm=center,
                size_mm=dimensions,
                confidence=88.0 if report.watertight else 62.0,
                reason="Broad flat panel can accept through-cut slot or honeycomb patterns.",
            )
        ]

    if report.shape == "long_strip":
        return [
            CutterCandidateRegion(
                id="long-flex-strip",
                region_type="strip_body",
                preferred_operations=["zigzag", "living_hinge"],
                center_mm=center,
                size_mm=dimensions,
                confidence=92.0 if report.watertight else 66.0,
                reason="Long narrow body is suitable for repeated alternating flex slots.",
            )
        ]

    if report.shape == "cylinder_or_rod":
        return [
            CutterCandidateRegion(
                id="axial-body",
                region_type="axial_volume",
                preferred_operations=["twist", "zigzag"],
                center_mm=center,
                size_mm=dimensions,
                confidence=78.0 if report.watertight else 54.0,
                reason="Axial body may support centered twist cuts or carefully aligned slots.",
            )
        ]

    return [
        CutterCandidateRegion(
            id="manual-review-main-body",
            region_type="unknown_body",
            preferred_operations=["manual_review"],
            center_mm=center,
            size_mm=dimensions,
            confidence=35.0,
            reason="Complex shape needs manual region review before automatic cutting.",
        )
    ]


def _center_from_bounds(report: ModelReport) -> tuple[float, float, float]:
    low = report.bounding_box_min_mm
    high = report.bounding_box_max_mm
    return (
        (low[0] + high[0]) / 2.0,
        (low[1] + high[1]) / 2.0,
        (low[2] + high[2]) / 2.0,
    )
