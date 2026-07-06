# flexai/perception/protected_regions.py

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from flexai.models import ModelReport


@dataclass(frozen=True)
class ProtectedModelRegion:
    id: str
    feature_type: str
    center_mm: tuple[float, float, float]
    size_mm: tuple[float, float, float]
    confidence: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_protected_regions(report: ModelReport) -> list[ProtectedModelRegion]:
    regions: list[ProtectedModelRegion] = []
    dimensions = report.dimensions_mm
    center = _center_from_bounds(report)

    if not report.watertight:
        regions.append(
            ProtectedModelRegion(
                id="non-watertight-global-review",
                feature_type="global_risk",
                center_mm=center,
                size_mm=dimensions,
                confidence=90.0,
                reason="Mesh is not watertight; automatic cuts should require review.",
            )
        )

    if report.face_count < 50:
        regions.append(
            ProtectedModelRegion(
                id="low-detail-global-review",
                feature_type="low_detail_mesh",
                center_mm=center,
                size_mm=dimensions,
                confidence=75.0,
                reason="Mesh has very few faces; feature detection confidence is low.",
            )
        )

    if report.shape in {"organic_or_complex", "unknown"}:
        regions.append(
            ProtectedModelRegion(
                id="complex-shape-manual-review",
                feature_type="complex_geometry",
                center_mm=center,
                size_mm=dimensions,
                confidence=80.0,
                reason="Complex geometry may contain decorative or functional features that should not be cut automatically.",
            )
        )

    if _has_extreme_aspect_ratio(report):
        regions.append(
            ProtectedModelRegion(
                id="extreme-aspect-edge-risk",
                feature_type="thin_or_extreme_aspect",
                center_mm=center,
                size_mm=dimensions,
                confidence=70.0,
                reason="Extreme aspect ratio can indicate thin walls or fragile features.",
            )
        )

    return regions


def _center_from_bounds(report: ModelReport) -> tuple[float, float, float]:
    low = report.bounding_box_min_mm
    high = report.bounding_box_max_mm
    return (
        (low[0] + high[0]) / 2.0,
        (low[1] + high[1]) / 2.0,
        (low[2] + high[2]) / 2.0,
    )


def _has_extreme_aspect_ratio(report: ModelReport) -> bool:
    dimensions = sorted(report.dimensions_mm)
    shortest = max(dimensions[0], 0.001)
    longest = dimensions[-1]
    return longest / shortest > 18.0
