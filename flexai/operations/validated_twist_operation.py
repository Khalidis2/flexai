# flexai/operations/validated_twist_operation.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flexai.models import CutterRecommendation
from flexai.operations.twist_operation import TwistOperationResult, apply_twist_operation
from flexai.validation.mesh_validator import MeshValidationReport, validate_mesh_file


@dataclass(frozen=True)
class ValidatedTwistOperationResult:
    operation: TwistOperationResult
    validation: MeshValidationReport

    @property
    def passed(self) -> bool:
        return self.validation.passed


def apply_validated_twist_operation(
    input_path: Path,
    output_path: Path,
    recommendation: CutterRecommendation,
    blender_path: str | None = None,
    keep_cutter: bool = False,
    cutter_output_path: Path | None = None,
) -> ValidatedTwistOperationResult:
    operation = apply_twist_operation(
        input_path=input_path,
        output_path=output_path,
        recommendation=recommendation,
        blender_path=blender_path,
        keep_cutter=keep_cutter,
        cutter_output_path=cutter_output_path,
    )
    validation = validate_mesh_file(operation.output_path)
    return ValidatedTwistOperationResult(operation=operation, validation=validation)
