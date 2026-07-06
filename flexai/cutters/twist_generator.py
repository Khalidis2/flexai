# flexai/cutters/twist_generator.py

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix, translation_matrix


@dataclass(frozen=True)
class TwistCutterParameters:
    diameter_mm: float
    height_mm: float
    core_hole_mm: float = 8.0
    slot_width_mm: float = 1.2
    turns: float = 1.0
    blade_count: int = 4
    segments: int = 96

    def validate(self) -> None:
        if self.diameter_mm <= 0:
            raise ValueError("diameter_mm must be greater than zero")
        if self.height_mm <= 0:
            raise ValueError("height_mm must be greater than zero")
        if self.core_hole_mm < 0:
            raise ValueError("core_hole_mm cannot be negative")
        if self.core_hole_mm >= self.diameter_mm:
            raise ValueError("core_hole_mm must be smaller than diameter_mm")
        if self.slot_width_mm <= 0:
            raise ValueError("slot_width_mm must be greater than zero")
        if self.blade_count < 1:
            raise ValueError("blade_count must be at least 1")
        if self.segments < 8:
            raise ValueError("segments must be at least 8")


def generate_twist_cutter(params: TwistCutterParameters) -> trimesh.Trimesh:
    params.validate()

    outer_radius = params.diameter_mm / 2.0
    inner_radius = params.core_hole_mm / 2.0
    radial_length = outer_radius - inner_radius
    radial_center = inner_radius + radial_length / 2.0
    segment_height = params.height_mm / params.segments
    segment_overlap = 1.25
    meshes: list[trimesh.Trimesh] = []

    for blade_index in range(params.blade_count):
        base_angle = (2.0 * np.pi * blade_index) / params.blade_count
        for segment_index in range(params.segments):
            t = (segment_index + 0.5) / params.segments
            z = -params.height_mm / 2.0 + t * params.height_mm
            angle = base_angle + (2.0 * np.pi * params.turns * t)
            box = trimesh.creation.box(
                extents=(
                    radial_length,
                    params.slot_width_mm,
                    segment_height * segment_overlap,
                )
            )
            transform = rotation_matrix(angle, (0, 0, 1)) @ translation_matrix((radial_center, 0, z))
            box.apply_transform(transform)
            meshes.append(box)

    cutter = trimesh.util.concatenate(meshes)
    cutter.remove_unreferenced_vertices()
    return cutter
