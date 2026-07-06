# flexai/validation/operation_score.py

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from flexai.validation.mesh_comparison import MeshComparisonReport


@dataclass(frozen=True)
class OperationScore:
    score: float
    passed: bool
    grade: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def score_operation(comparison: MeshComparisonReport) -> OperationScore:
    score = 100.0
    warnings: list[str] = []

    if not comparison.input_report.exists:
        score -= 40.0
        warnings.append("Input file does not exist.")
    if not comparison.input_report.loadable:
        score -= 40.0
        warnings.append("Input mesh is not loadable.")
    if not comparison.output_report.exists:
        score -= 60.0
        warnings.append("Output file does not exist.")
    if not comparison.output_report.loadable:
        score -= 60.0
        warnings.append("Output mesh is not loadable.")
    if comparison.output_report.loadable and not comparison.output_report.watertight:
        score -= 25.0
        warnings.append("Output mesh is not watertight.")
    if comparison.volume_removed_percent < 0.1:
        score -= 25.0
        warnings.append("Operation removed too little material.")
    if comparison.volume_removed_percent > 65.0:
        score -= 45.0
        warnings.append("Operation removed too much material.")
    if comparison.output_report.face_count <= 0:
        score -= 60.0
        warnings.append("Output mesh has no faces.")

    warnings.extend(comparison.warnings)
    normalized_score = max(0.0, min(100.0, score))
    unique_warnings = list(dict.fromkeys(warnings))

    return OperationScore(
        score=normalized_score,
        passed=normalized_score >= 70.0 and not unique_warnings,
        grade=_grade(normalized_score),
        warnings=unique_warnings,
    )


def _grade(score: float) -> str:
    if score >= 90.0:
        return "excellent"
    if score >= 80.0:
        return "good"
    if score >= 70.0:
        return "acceptable"
    if score >= 50.0:
        return "risky"
    return "failed"
