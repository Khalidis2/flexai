# flexai/operations/scored_twist_operation.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flexai.models import CutterRecommendation
from flexai.operations.compared_twist_operation import ComparedTwistOperationResult, apply_compared_twist_operation
from flexai.validation.operation_score import OperationScore, score_operation


@dataclass(frozen=True)
class ScoredTwistOperationResult:
    compared_result: ComparedTwistOperationResult
    score: OperationScore

    @property
    def passed(self) -> bool:
        return self.score.passed


def apply_scored_twist_operation(
    input_path: Path,
    output_path: Path,
    recommendation: CutterRecommendation,
    blender_path: str | None = None,
    keep_cutter: bool = False,
    cutter_output_path: Path | None = None,
    min_removed_percent: float = 0.1,
    max_removed_percent: float = 65.0,
) -> ScoredTwistOperationResult:
    compared_result = apply_compared_twist_operation(
        input_path=input_path,
        output_path=output_path,
        recommendation=recommendation,
        blender_path=blender_path,
        keep_cutter=keep_cutter,
        cutter_output_path=cutter_output_path,
        min_removed_percent=min_removed_percent,
        max_removed_percent=max_removed_percent,
    )
    operation_score = score_operation(compared_result.comparison)
    return ScoredTwistOperationResult(
        compared_result=compared_result,
        score=operation_score,
    )
