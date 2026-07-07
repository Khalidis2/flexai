# flexai/cutters/twist_generator.py

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix, translation_matrix

MIN_PRINTABLE_SLOT_WIDTH_MM = 0.8
MIN_CORE_HOLE_MM = 6.0
MIN_SEGMENTS = 16
DEFAULT_SEGMENTS = 96
MAX_SEGMENTS = 192


@dataclass(frozen=True)
class TwistCutterParameters:
    diameter_mm: float
    height_mm: float
    core_hole_mm: float = 8.0
    slot_width_mm: float = 1.2
    turns: float = 1.0
    blade_count: int = 4
    segments: int = DEFAULT_SEGMENTS

    def normalized(self) -> "TwistCutterParameters":
        diameter = float(self.diameter_mm)
        max_core_hole = max(0.0, diameter - (MIN_PRINTABLE_SLOT_WIDTH_MM * 2.0))
        core_hole = min(max(float(self.core_hole_mm), MIN_CORE_HOLE_MM), max_core_hole)
        slot_width = max(float(self.slot_width_mm), MIN_PRINTABLE_SLOT_WIDTH_MM)
        segments = min(max(int(self.segments), MIN_SEGMENTS), MAX_SEGMENTS)
        return TwistCutterParameters(
            diameter_mm=diameter,
            height_mm=float(self.height_mm),
            core_hole_mm=core_hole,
            slot_width_mm=slot_width,
            turns=float(self.turns),
            blade_count=int(self.blade_count),
            segments=segments,
        )

    def validate(self) -> None:
        if self.diameter_mm <= 0:
            raise ValueError("diameter_mm must be greater than zero")
        if self.height_mm <= 0:
            raise ValueError("height_mm must be greater than zero")
        if self.core_hole_mm < 0:
            raise ValueError("core_hole_mm cannot be negative")
        if self.core_hole_mm >= self.diameter_mm:
            raise ValueError("core_hole_mm must be smaller than diameter_mm")
        if self.slot_width_mm < MIN_PRINTABLE_SLOT_WIDTH_MM:
            raise ValueError(f"slot_width_mm must be at least {MIN_PRINTABLE_SLOT_WIDTH_MM:.1f} mm")
        if self.blade_count < 1:
            raise ValueError("blade_count must be at least 1")
        if self.segments < MIN_SEGMENTS:
            raise ValueError(f"segments must be at least {MIN_SEGMENTS}")


def normalize_twist_parameters(params: TwistCutterParameters) -> TwistCutterParameters:
    normalized = params.normalized()
    normalized.validate()
    return normalized


def generate_twist_cutter(params: TwistCutterParameters) -> trimesh.Trimesh:
    params = normalize_twist_parameters(params)

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
