# flexai/importer/mesh_loader.py

from __future__ import annotations

from pathlib import Path

import trimesh

from flexai.models import MeshAsset

SUPPORTED_EXTENSIONS = {".stl", ".obj", ".3mf"}


def load_mesh(path: Path) -> MeshAsset:
    if not path.exists():
        raise FileNotFoundError(f"Model file does not exist: {path}")

    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type '{extension}'. Supported types: {supported}")

    loaded = trimesh.load(path, force=None)
    mesh = _coerce_to_single_mesh(loaded)
    if mesh.vertices.size == 0 or mesh.faces.size == 0:
        raise ValueError(f"No mesh geometry found in: {path}")

    mesh.remove_unreferenced_vertices()
    return MeshAsset(path=path, file_type=extension.lstrip("."), mesh=mesh)


def _coerce_to_single_mesh(loaded: object) -> trimesh.Trimesh:
    if isinstance(loaded, trimesh.Trimesh):
        return loaded

    if isinstance(loaded, trimesh.Scene):
        meshes = [geometry for geometry in loaded.geometry.values() if isinstance(geometry, trimesh.Trimesh)]
        if not meshes:
            raise ValueError("Scene contains no mesh geometry")
        return trimesh.util.concatenate(meshes)

    raise TypeError(f"Unsupported loaded geometry type: {type(loaded).__name__}")
