# flexai/analyzer/shape_classifier.py

from __future__ import annotations

import numpy as np
import trimesh


def classify_shape(mesh: trimesh.Trimesh) -> str:
    extents = np.asarray(mesh.extents, dtype=float)
    if np.any(extents <= 0):
        return "unknown"

    sorted_extents = np.sort(extents)
    longest = float(sorted_extents[2])
    middle = float(sorted_extents[1])
    shortest = float(sorted_extents[0])

    uniform_ratio = shortest / longest
    flat_ratio = shortest / middle if middle > 0 else 0.0
    long_ratio = longest / middle if middle > 0 else 0.0

    if uniform_ratio > 0.88:
        if _is_sphere_like(mesh):
            return "sphere"
        return "compact"

    if flat_ratio < 0.22:
        return "flat_panel"

    if long_ratio > 2.4 and shortest / middle > 0.55:
        return "cylinder_or_rod"

    if long_ratio > 2.0:
        return "long_strip"

    return "organic_or_complex"


def classify_symmetry(mesh: trimesh.Trimesh, shape: str) -> str:
    if shape == "sphere":
        return "radial"
    if shape == "cylinder_or_rod":
        return "axial"
    if shape in {"flat_panel", "long_strip"}:
        return "planar"
    return "unknown"


def _is_sphere_like(mesh: trimesh.Trimesh) -> bool:
    center = mesh.bounding_box.centroid
    distances = np.linalg.norm(mesh.vertices - center, axis=1)
    mean_distance = float(np.mean(distances))
    if mean_distance <= 0:
        return False
    relative_std = float(np.std(distances) / mean_distance)
    return relative_std < 0.18
