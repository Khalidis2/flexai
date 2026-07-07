# flexai/operations/twist_operation.py

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flexai.cutters.twist_generator import TwistCutterParameters, generate_twist_cutter
from flexai.executor.blender_runner import BlenderRunResult
from flexai.executor.boolean_executor import subtract_cutter_with_blender
from flexai.importer.mesh_loader import load_mesh
from flexai.models import CutterRecommendation


@dataclass(frozen=True)
class TwistOperationResult:
    input_path: Path
    cutter_path: Path
    output_path: Path
    blender_result: BlenderRunResult


def twist_parameters_from_recommendation(recommendation: CutterRecommendation) -> TwistCutterParameters:
    params: dict[str, Any] = recommendation.parameters
    return TwistCutterParameters(
        diameter_mm=float(params["diameter_mm"]),
        height_mm=float(params["height_mm"]),
        core_hole_mm=float(params.get("core_hole_mm", 8.0)),
        slot_width_mm=float(params.get("slot_width_mm", 1.2)),
        turns=float(params.get("turns", 1.0)),
        blade_count=int(params.get("blade_count", 4)),
        segments=int(params.get("segments", 96)),
    )


def apply_twist_operation(
    input_path: Path,
    output_path: Path,
    recommendation: CutterRecommendation,
    blender_path: str | None = None,
    keep_cutter: bool = False,
    cutter_output_path: Path | None = None,
) -> TwistOperationResult:
    if recommendation.plugin_id != "twist":
        raise ValueError(f"Twist operation requires a twist recommendation, got: {recommendation.plugin_id}")

    output_path = output_path.expanduser().resolve()
    input_path = input_path.expanduser().resolve()
    params = twist_parameters_from_recommendation(recommendation)
    cutter_mesh = generate_twist_cutter(params)

    with tempfile.TemporaryDirectory(prefix="flexai_twist_") as tmpdir:
        tmpdir_path = Path(tmpdir)
        target_path = _prepare_blender_target(input_path, tmpdir_path)
        cutter_path = _export_cutter(cutter_mesh, output_path, keep_cutter, cutter_output_path, tmpdir_path)
        blender_result = subtract_cutter_with_blender(
            target_path=target_path,
            cutter_path=cutter_path,
            output_path=output_path,
            blender_path=blender_path,
        )
        return TwistOperationResult(
            input_path=target_path,
            cutter_path=cutter_path,
            output_path=output_path,
            blender_result=blender_result,
        )


def _prepare_blender_target(input_path: Path, tmpdir_path: Path) -> Path:
    if input_path.suffix.lower() in {".stl", ".obj"}:
        return input_path

    target_path = tmpdir_path / "target.stl"
    asset = load_mesh(input_path)
    asset.mesh.export(target_path)
    return target_path


def _export_cutter(
    cutter_mesh,
    output_path: Path,
    keep_cutter: bool,
    cutter_output_path: Path | None,
    tmpdir_path: Path,
) -> Path:
    if keep_cutter:
        cutter_path = (cutter_output_path or output_path.with_name(output_path.stem + "_cutter.stl")).expanduser().resolve()
        cutter_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        cutter_path = tmpdir_path / "twist_cutter.stl"

    cutter_mesh.export(cutter_path)
    return cutter_path