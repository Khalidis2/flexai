# flexai/executor/boolean_executor_v2.py

from __future__ import annotations

from pathlib import Path

from flexai.executor.blender_runner import BlenderRunResult
from flexai.executor.boolean_executor import subtract_cutter_with_blender


def subtract_cutter_with_blender_v2(
    target_path: Path,
    cutter_path: Path,
    output_path: Path,
    blender_path: str | None = None,
) -> BlenderRunResult:
    return subtract_cutter_with_blender(
        target_path=target_path,
        cutter_path=cutter_path,
        output_path=output_path,
        blender_path=blender_path,
    )
