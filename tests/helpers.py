# tests/helpers.py

from __future__ import annotations

from pathlib import Path

import trimesh

from flexai.models import MeshAsset


def sphere_asset(radius: float = 20.0) -> MeshAsset:
    mesh = trimesh.creation.icosphere(subdivisions=3, radius=radius)
    return MeshAsset(path=Path("generated_sphere.stl"), file_type="stl", mesh=mesh)


def flat_panel_asset(width: float = 80.0, depth: float = 40.0, thickness: float = 4.0) -> MeshAsset:
    mesh = trimesh.creation.box(extents=(width, depth, thickness))
    return MeshAsset(path=Path("generated_panel.stl"), file_type="stl", mesh=mesh)


def long_strip_asset(length: float = 120.0, width: float = 18.0, thickness: float = 4.0) -> MeshAsset:
    mesh = trimesh.creation.box(extents=(length, width, thickness))
    return MeshAsset(path=Path("generated_strip.stl"), file_type="stl", mesh=mesh)
