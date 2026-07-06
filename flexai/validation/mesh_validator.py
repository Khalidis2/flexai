# flexai/validation/mesh_validator.py

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import trimesh


@dataclass(frozen=True)
class MeshValidationReport:
    path: Path
    exists: bool
    loadable: bool
    watertight: bool
    face_count: int
    vertex_count: int
    volume_mm3: float
    surface_area_mm2: float
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.exists and self.loadable and len(self.warnings) == 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        data["passed"] = self.passed
        return data


def validate_mesh_file(path: Path) -> MeshValidationReport:
    path = path.expanduser().resolve()
    if not path.exists():
        return MeshValidationReport(
            path=path,
            exists=False,
            loadable=False,
            watertight=False,
            face_count=0,
            vertex_count=0,
            volume_mm3=0.0,
            surface_area_mm2=0.0,
            warnings=["Output file does not exist."],
        )

    try:
        loaded = trimesh.load(path, force="mesh")
    except Exception as exc:
        return MeshValidationReport(
            path=path,
            exists=True,
            loadable=False,
            watertight=False,
            face_count=0,
            vertex_count=0,
            volume_mm3=0.0,
            surface_area_mm2=0.0,
            warnings=[f"Output file could not be loaded: {exc}"],
        )

    warnings: list[str] = []
    if not isinstance(loaded, trimesh.Trimesh):
        warnings.append(f"Loaded object is not a Trimesh: {type(loaded).__name__}")
        return MeshValidationReport(
            path=path,
            exists=True,
            loadable=False,
            watertight=False,
            face_count=0,
            vertex_count=0,
            volume_mm3=0.0,
            surface_area_mm2=0.0,
            warnings=warnings,
        )

    if len(loaded.faces) == 0:
        warnings.append("Mesh has no faces.")
    if len(loaded.vertices) == 0:
        warnings.append("Mesh has no vertices.")
    if not loaded.is_watertight:
        warnings.append("Mesh is not watertight.")
    if loaded.area <= 0:
        warnings.append("Mesh surface area is zero or negative.")
    if loaded.is_volume and abs(float(loaded.volume)) <= 0:
        warnings.append("Mesh volume is zero.")

    return MeshValidationReport(
        path=path,
        exists=True,
        loadable=True,
        watertight=bool(loaded.is_watertight),
        face_count=int(len(loaded.faces)),
        vertex_count=int(len(loaded.vertices)),
        volume_mm3=float(abs(loaded.volume)) if loaded.is_volume else 0.0,
        surface_area_mm2=float(loaded.area),
        warnings=warnings,
    )
