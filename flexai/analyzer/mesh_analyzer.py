# flexai/analyzer/mesh_analyzer.py

from __future__ import annotations

from pathlib import Path

import numpy as np

from flexai.analyzer.shape_classifier import classify_shape, classify_symmetry
from flexai.models import CandidateRegion, MeshAsset, ModelReport, vec3


def analyze_model(asset: MeshAsset, path: Path) -> ModelReport:
    mesh = asset.mesh
    bounds = np.asarray(mesh.bounds, dtype=float)
    extents = np.asarray(mesh.extents, dtype=float)
    shape = classify_shape(mesh)
    symmetry = classify_symmetry(mesh, shape)
    candidate_regions = _candidate_regions(shape, mesh.bounding_box.centroid, extents)
    risk_level = _risk_level(mesh.is_watertight, shape)

    return ModelReport(
        file_name=path.name,
        file_type=asset.file_type,
        dimensions_mm=vec3(extents),
        bounding_box_min_mm=vec3(bounds[0]),
        bounding_box_max_mm=vec3(bounds[1]),
        volume_mm3=float(abs(mesh.volume)) if mesh.is_volume else 0.0,
        surface_area_mm2=float(mesh.area),
        watertight=bool(mesh.is_watertight),
        face_count=int(len(mesh.faces)),
        vertex_count=int(len(mesh.vertices)),
        shape=shape,
        symmetry=symmetry,
        risk_level=risk_level,
        candidate_regions=candidate_regions,
        protected_regions=[],
    )


def _candidate_regions(shape: str, center: np.ndarray, extents: np.ndarray) -> list[CandidateRegion]:
    base = CandidateRegion(
        id="main-body",
        region_type=shape,
        center_mm=vec3(center),
        size_mm=vec3(extents),
        score=_base_region_score(shape),
        reason=_region_reason(shape),
    )
    return [base]


def _base_region_score(shape: str) -> float:
    scores = {
        "sphere": 96.0,
        "cylinder_or_rod": 88.0,
        "flat_panel": 84.0,
        "long_strip": 90.0,
        "compact": 68.0,
        "organic_or_complex": 50.0,
        "unknown": 20.0,
    }
    return scores.get(shape, 20.0)


def _region_reason(shape: str) -> str:
    reasons = {
        "sphere": "Uniform rounded body; good candidate for centered twist-style cutting.",
        "cylinder_or_rod": "Axial body; may support twist or repeated slot patterns.",
        "flat_panel": "Flat region; good candidate for hinge or honeycomb cutting.",
        "long_strip": "Long narrow body; good candidate for zigzag or living hinge cutting.",
        "compact": "Compact object; needs cautious cutting because function is unclear.",
        "organic_or_complex": "Complex object; automatic cutting should be conservative.",
        "unknown": "Insufficient geometric confidence for aggressive cutting.",
    }
    return reasons.get(shape, reasons["unknown"])


def _risk_level(watertight: bool, shape: str) -> str:
    if not watertight:
        return "high"
    if shape in {"organic_or_complex", "unknown"}:
        return "medium"
    return "low"
