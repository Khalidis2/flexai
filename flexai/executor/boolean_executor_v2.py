# flexai/executor/boolean_executor_v2.py

from __future__ import annotations

from pathlib import Path

from flexai.executor.blender_runner import BlenderRunResult, run_blender_script
from flexai.executor.boolean_executor import BooleanExecutionError


def subtract_cutter_with_blender_v2(
    target_path: Path,
    cutter_path: Path,
    output_path: Path,
    blender_path: str | None = None,
) -> BlenderRunResult:
    script_path = Path(__file__).resolve().parent / "scripts" / "boolean_subtract_v2.py"
    result = run_blender_script(
        script_path=script_path,
        args=[
            "--target",
            str(target_path),
            "--cutter",
            str(cutter_path),
            "--output",
            str(output_path),
        ],
        output_path=output_path,
        blender_path=blender_path,
    )

    if result.return_code != 0:
        raise BooleanExecutionError(
            "Blender boolean subtraction failed.\n"
            f"Return code: {result.return_code}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    if not output_path.exists():
        raise BooleanExecutionError(f"Blender reported success but output file was not created: {output_path}")

    return result
