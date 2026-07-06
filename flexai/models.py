# flexai/models.py

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


@dataclass(frozen=True)
class MeshAsset:
    path: Path
    file_type: str
    mesh: trimesh.Trimesh


@dataclass(frozen=True)
class CandidateRegion:
    id: str
    region_type: str
    center_mm: tuple[float, float, float]
    size_mm: tuple[float, float, float]
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProtectedRegion:
    id: str
    feature_type: str
    center_mm: tuple[float, float, float]
    size_mm: tuple[float, float, float]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ModelReport:
    file_name: str
    file_type: str
    dimensions_mm: tuple[float, float, float]
    bounding_box_min_mm: tuple[float, float, float]
    bounding_box_max_mm: tuple[float, float, float]
    volume_mm3: float
    surface_area_mm2: float
    watertight: bool
    face_count: int
    vertex_count: int
    shape: str
    symmetry: str
    risk_level: str
    candidate_regions: list[CandidateRegion] = field(default_factory=list)
    protected_regions: list[ProtectedRegion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["candidate_regions"] = [region.to_dict() for region in self.candidate_regions]
        result["protected_regions"] = [region.to_dict() for region in self.protected_regions]
        return result


@dataclass(frozen=True)
class CutterRecommendation:
    plugin_id: str
    plugin_name: str
    score: float
    reason: str
    parameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def vec3(values: np.ndarray | list[float] | tuple[float, float, float]) -> tuple[float, float, float]:
    arr = np.asarray(values, dtype=float).reshape(3)
    return (float(arr[0]), float(arr[1]), float(arr[2]))
