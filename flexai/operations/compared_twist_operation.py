# flexai/operations/compared_twist_operation.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flexai.models import CutterRecommendation
from flexai.operations.twist_operation import TwistOperationResult, apply_twist_operation
from flexai.validation.mesh_comparison import MeshComparisonReport, compare_mesh_files


@dataclass(frozen=True)
class ComparedTwistOperationResult:
    operation: TwistOperationResult
    comparison: MeshComparisonReport

    @property
    def passed(self) -> bool:
        return self.comparison.passed


def apply_compared_twist_operation(
    input_path: Path,
    output_path: Path,
    recommendation: CutterRecommendation,
    blender_path: str | None = None,
    keep_cutter: bool = False,
    cutter_output_path: Path | None = None,
    min_removed_percent: float = 0.1,
    max_removed_percent: float = 65.0,
) -> ComparedTwistOperationResult:
    operation = apply_twist_operation(
        input_path=input_path,
        output_path=output_path,
        recommendation=recommendation,
        blender_path=blender_path,
        keep_cutter=keep_cutter,
        cutter_output_path=cutter_output_path,
    )
    comparison = compare_mesh_files(
        input_path=operation.input_path,
        output_path=operation.output_path,
        min_removed_percent=min_removed_percent,
        max_removed_percent=max_removed_percent,
    )
    return ComparedTwistOperationResult(operation=operation, comparison=comparison)
