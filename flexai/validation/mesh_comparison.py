# flexai/validation/mesh_comparison.py

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from flexai.validation.mesh_validator import MeshValidationReport, validate_mesh_file


@dataclass(frozen=True)
class MeshComparisonReport:
    input_report: MeshValidationReport
    output_report: MeshValidationReport
    volume_removed_mm3: float
    volume_removed_percent: float
    face_count_delta: int
    vertex_count_delta: int
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.input_report.passed and self.output_report.passed and len(self.warnings) == 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["input_report"] = self.input_report.to_dict()
        data["output_report"] = self.output_report.to_dict()
        data["passed"] = self.passed
        return data


def compare_mesh_files(
    input_path: Path,
    output_path: Path,
    min_removed_percent: float = 0.1,
    max_removed_percent: float = 65.0,
) -> MeshComparisonReport:
    input_report = validate_mesh_file(input_path)
    output_report = validate_mesh_file(output_path)

    input_volume = input_report.volume_mm3
    output_volume = output_report.volume_mm3
    volume_removed = max(0.0, input_volume - output_volume)
    volume_removed_percent = (volume_removed / input_volume * 100.0) if input_volume > 0 else 0.0
    warnings: list[str] = []

    if not input_report.passed:
        warnings.append("Input mesh validation did not pass.")
    if not output_report.passed:
        warnings.append("Output mesh validation did not pass.")
    if input_volume > 0 and volume_removed_percent < min_removed_percent:
        warnings.append("Boolean operation removed very little volume; cutter may not have intersected the model.")
    if input_volume > 0 and volume_removed_percent > max_removed_percent:
        warnings.append("Boolean operation removed too much volume; result is likely damaged.")
    if output_report.face_count <= 0:
        warnings.append("Output mesh has no faces after operation.")

    return MeshComparisonReport(
        input_report=input_report,
        output_report=output_report,
        volume_removed_mm3=float(volume_removed),
        volume_removed_percent=float(volume_removed_percent),
        face_count_delta=int(output_report.face_count - input_report.face_count),
        vertex_count_delta=int(output_report.vertex_count - input_report.vertex_count),
        warnings=warnings,
    )
