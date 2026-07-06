# flexai/executor/blender_runner.py

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BlenderRunResult:
    return_code: int
    stdout: str
    stderr: str
    output_path: Path


class BlenderNotFoundError(RuntimeError):
    pass


def find_blender_executable(explicit_path: str | None = None) -> str:
    if explicit_path:
        path = Path(explicit_path).expanduser()
        if path.exists():
            return str(path)
        raise BlenderNotFoundError(f"Blender executable was not found at: {path}")

    executable = shutil.which("blender")
    if executable:
        return executable

    mac_path = Path("/Applications/Blender.app/Contents/MacOS/Blender")
    if mac_path.exists():
        return str(mac_path)

    windows_candidates = [
        Path("C:/Program Files/Blender Foundation/Blender 4.3/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
    ]
    for candidate in windows_candidates:
        if candidate.exists():
            return str(candidate)

    raise BlenderNotFoundError(
        "Blender executable was not found. Install Blender or pass an explicit blender path."
    )


def run_blender_script(
    script_path: Path,
    args: list[str],
    output_path: Path,
    blender_path: str | None = None,
    timeout_seconds: int = 240,
) -> BlenderRunResult:
    blender = find_blender_executable(blender_path)
    command = [
        blender,
        "--background",
        "--factory-startup",
        "--python",
        str(script_path),
        "--",
        *args,
    ]

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )

    return BlenderRunResult(
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        output_path=output_path,
    )
